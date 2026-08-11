use sha2::{Digest, Sha256};
use std::sync::Arc;
use tonic::{Request, Response, Status};

pub mod ilc_app {
    tonic::include_proto!("ilc_app");
}

use crate::balance_store::BalanceStore;
use crate::epoch_settlement::EpochStore;
use crate::network::EpochProposal;
use crate::node::{EpochProposalOutcome, NodeRunner};
use crate::types::{AgentID, CIDv1Root, EpochSeq, ILCConsensusError};
use ilc_app::ilc_app_attribution_ingress_service_server::IlcAppAttributionIngressService;
use ilc_app::ilc_app_proposal_ingress_service_server::IlcAppProposalIngressService;
use ilc_app::ilc_app_read_service_server::IlcAppReadService;
use ilc_app::{
    GetBalanceRequest, GetBalanceResponse, GetEpochChainRequest, GetEpochChainResponse,
    GetEpochRecordRequest, GetEpochRecordResponse, GetEpochRequest, GetEpochResponse,
    SubmitAttributionBatchRequest, SubmitAttributionBatchResponse, SubmitEpochProposalRequest,
    SubmitEpochProposalResponse,
};

pub const MAX_EPOCH_CHAIN_BATCH: u64 = 128;
const ATTRIBUTION_BATCH_ACCEPTED_TOKEN: &str = "attribution_batch_accepted";
const ATTRIBUTION_BATCH_PREIMAGE_DOMAIN: &[u8] = b"ILC_SUBMIT_ATTRIBUTION_BATCH_V1";

/// The singular external interface allowed for the Python Epistemic layer.
/// Inherently bans writes by omitting any mutation capabilities, strictly decoupling
/// state generation (Python) from state settlement and execution (Rust Mysticti DAG).
pub struct ApplicationInterface {
    balance_store: Arc<BalanceStore>,
    epoch_store: Arc<EpochStore>,
}

impl ApplicationInterface {
    pub fn new(balance_store: Arc<BalanceStore>, epoch_store: Arc<EpochStore>) -> Self {
        Self {
            balance_store,
            epoch_store,
        }
    }
}

#[tonic::async_trait]
impl IlcAppReadService for ApplicationInterface {
    async fn get_balance(
        &self,
        request: Request<GetBalanceRequest>,
    ) -> Result<Response<GetBalanceResponse>, Status> {
        let req = request.into_inner();

        let agent_bytes: [u8; 48] = req
            .agent_id
            .try_into()
            .map_err(|_| Status::invalid_argument("AgentID must be exactly 48 bytes"))?;

        let agent_id = AgentID(agent_bytes);

        match self.balance_store.get_balance(&agent_id) {
            Ok(balance) => {
                // Provides full deterministic mapping allowing Python to reconstruct Owned-Object
                // prerequisites automatically over gRPC.
                Ok(Response::new(GetBalanceResponse {
                    amount_micro_ecu: balance.amount_micro_ecu,
                    version: balance.version,
                    epoch: balance.epoch.0,
                }))
            }
            Err(e) => Err(Status::internal(format!("Balance lookup failed: {:?}", e))),
        }
    }

    async fn get_epoch(
        &self,
        _request: Request<GetEpochRequest>,
    ) -> Result<Response<GetEpochResponse>, Status> {
        match self.epoch_store.get_current_epoch() {
            Ok(epoch) => Ok(Response::new(GetEpochResponse {
                current_epoch: epoch,
            })),
            Err(e) => Err(Status::internal(format!("Epoch lookup failed: {:?}", e))),
        }
    }

    async fn get_epoch_record(
        &self,
        request: Request<GetEpochRecordRequest>,
    ) -> Result<Response<GetEpochRecordResponse>, Status> {
        let epoch = request.into_inner().epoch;
        match self.epoch_store.get_checkpoint(epoch) {
            Ok(Some(stored)) => {
                let mut state_root = [0u8; 36];
                state_root[..32].copy_from_slice(&stored.record.state_root.p1);
                state_root[32..].copy_from_slice(&stored.record.state_root.p2);
                Ok(Response::new(GetEpochRecordResponse {
                    epoch: stored.record.epoch.0,
                    state_root: state_root.to_vec(),
                    agg_sig: stored.agg_sig_bytes,
                    found: true,
                    spectral_hash: stored.record.spectral_hash.to_vec(),
                }))
            }
            Ok(None) => Ok(Response::new(GetEpochRecordResponse {
                epoch,
                state_root: vec![],
                agg_sig: vec![],
                found: false,
                spectral_hash: vec![],
            })),
            Err(e) => Err(Status::internal(format!("LMDB read error: {:?}", e))),
        }
    }

    async fn get_epoch_chain(
        &self,
        request: Request<GetEpochChainRequest>,
    ) -> Result<Response<GetEpochChainResponse>, Status> {
        let req = request.into_inner();
        let from = if req.from_epoch == 0 {
            1
        } else {
            req.from_epoch
        };
        let current = self
            .epoch_store
            .get_current_epoch()
            .map_err(|e| Status::internal(format!("Epoch read error: {:?}", e)))?;
        let to = if req.to_epoch == 0 || req.to_epoch > current {
            current
        } else {
            req.to_epoch
        };

        let effective_to = if from <= to {
            to.min(from.saturating_add(MAX_EPOCH_CHAIN_BATCH - 1))
        } else {
            to
        };

        let mut records = Vec::new();
        if from <= to {
            for ep in from..=effective_to {
                match self.epoch_store.get_checkpoint(ep) {
                    Ok(Some(stored)) => {
                        let mut state_root = [0u8; 36];
                        state_root[..32].copy_from_slice(&stored.record.state_root.p1);
                        state_root[32..].copy_from_slice(&stored.record.state_root.p2);
                        records.push(GetEpochRecordResponse {
                            epoch: stored.record.epoch.0,
                            state_root: state_root.to_vec(),
                            agg_sig: stored.agg_sig_bytes,
                            found: true,
                            spectral_hash: stored.record.spectral_hash.to_vec(),
                        });
                    }
                    Ok(None) => break,
                    Err(e) => return Err(Status::internal(format!("{:?}", e))),
                }
            }
        }

        let expected_count = if from <= to { to - from + 1 } else { 0 };
        let chain_complete = records.len() as u64 == expected_count;
        Ok(Response::new(GetEpochChainResponse {
            chain_complete,
            records,
            edges: vec![],
            hyperedges: vec![],
        }))
    }
}

pub struct ProposalIngressService {
    runner: Arc<NodeRunner>,
    require_tls_client_cert: bool,
    allowed_client_cert_sha256_fingerprints: Vec<[u8; 32]>,
}

impl ProposalIngressService {
    pub fn new(
        runner: Arc<NodeRunner>,
        allowed_client_cert_sha256_fingerprints: Vec<[u8; 32]>,
    ) -> Self {
        Self {
            runner,
            require_tls_client_cert: true,
            allowed_client_cert_sha256_fingerprints,
        }
    }

    #[cfg(test)]
    fn new_for_tests_without_tls(runner: Arc<NodeRunner>) -> Self {
        Self {
            runner,
            require_tls_client_cert: false,
            allowed_client_cert_sha256_fingerprints: vec![],
        }
    }
}

#[tonic::async_trait]
impl IlcAppProposalIngressService for ProposalIngressService {
    async fn submit_epoch_proposal(
        &self,
        request: Request<SubmitEpochProposalRequest>,
    ) -> Result<Response<SubmitEpochProposalResponse>, Status> {
        if self.require_tls_client_cert
            && !has_allowed_tls_peer_certificate(
                &request,
                &self.allowed_client_cert_sha256_fingerprints,
            )
        {
            return Ok(Response::new(error_response(
                "submit_epoch_proposal_unauthenticated_phase_1586",
            )));
        }

        let req = request.into_inner();
        let proposal = match request_to_epoch_proposal(req) {
            Ok(proposal) => proposal,
            Err(code) => return Ok(Response::new(error_response(code))),
        };

        match self.runner.submit_epoch_proposal(proposal).await {
            Ok(outcome) => Ok(Response::new(outcome_response(outcome))),
            Err(e) => Ok(Response::new(error_response(error_code_for(e).as_str()))),
        }
    }
}

pub struct AttributionIngressService {
    balance_store: Arc<BalanceStore>,
    network_id: String,
    require_tls_client_cert: bool,
    allowed_client_cert_sha256_fingerprints: Vec<[u8; 32]>,
}

impl AttributionIngressService {
    pub fn new(
        balance_store: Arc<BalanceStore>,
        network_id: String,
        allowed_client_cert_sha256_fingerprints: Vec<[u8; 32]>,
    ) -> Self {
        Self {
            balance_store,
            network_id,
            require_tls_client_cert: true,
            allowed_client_cert_sha256_fingerprints,
        }
    }

    #[cfg(test)]
    fn new_for_tests_without_tls(balance_store: Arc<BalanceStore>) -> Self {
        Self {
            balance_store,
            network_id: "ilc-rc01".to_string(),
            require_tls_client_cert: false,
            allowed_client_cert_sha256_fingerprints: vec![],
        }
    }
}

#[tonic::async_trait]
impl IlcAppAttributionIngressService for AttributionIngressService {
    async fn submit_attribution_batch(
        &self,
        request: Request<SubmitAttributionBatchRequest>,
    ) -> Result<Response<SubmitAttributionBatchResponse>, Status> {
        if self.require_tls_client_cert
            && !has_allowed_tls_peer_certificate(
                &request,
                &self.allowed_client_cert_sha256_fingerprints,
            )
        {
            return Ok(Response::new(attribution_error_response(
                "submit_attribution_batch_unauthenticated_phase_1594",
            )));
        }

        let req = request.into_inner();
        let normalized = match validate_attribution_request(req, &self.network_id) {
            Ok(normalized) => normalized,
            Err(code) => return Ok(Response::new(attribution_error_response(code))),
        };
        if let Some(root) = normalized.backward_root {
            if let Err(err) = self
                .balance_store
                .store_backward_attribution_batch_root(EpochSeq(normalized.epoch), root)
            {
                return Ok(Response::new(attribution_error_response(
                    attribution_error_code_for(err).as_str(),
                )));
            }
        }
        Ok(Response::new(SubmitAttributionBatchResponse {
            status_token: ATTRIBUTION_BATCH_ACCEPTED_TOKEN.to_string(),
            error_code: String::new(),
            accepted_epoch_number: normalized.epoch,
            accepted_backward_root: normalized.backward_root_hex,
        }))
    }
}

struct NormalizedAttributionRequest {
    epoch: u64,
    backward_root: Option<[u8; 32]>,
    backward_root_hex: String,
}

fn validate_attribution_request(
    req: SubmitAttributionBatchRequest,
    expected_network_id: &str,
) -> Result<NormalizedAttributionRequest, &'static str> {
    if req.submitter_agent_id.len() != 48 {
        return Err("submit_attribution_batch_invalid_submitter_agent_id_phase_1594");
    }
    if req.attribution_entries_hash.len() != 32 {
        return Err("submit_attribution_batch_invalid_entries_hash_phase_1594");
    }
    if req.network_id.trim().is_empty() {
        return Err("submit_attribution_batch_invalid_network_id_phase_1594");
    }
    if req.network_id != expected_network_id {
        return Err("submit_attribution_batch_wrong_network_phase_1594_fix1");
    }
    if !is_lower_sha256_hex(&req.idempotency_key) {
        return Err("submit_attribution_batch_invalid_idempotency_key_phase_1594");
    }
    let now_ms = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_millis() as u64)
        .unwrap_or(0);
    if req.not_before_unix_ms
        > now_ms.saturating_add(crate::epoch_settlement::CLOCK_SKEW_TOLERANCE_MS)
    {
        return Err("submit_attribution_batch_not_before_too_far_future_phase_1594_fix1");
    }
    let backward_root = if req.backward_attribution_batch_root.is_empty() {
        None
    } else {
        Some(parse_lower_sha256_hex(
            &req.backward_attribution_batch_root,
        )?)
    };
    let expected_key = attribution_batch_idempotency_key(&req);
    if req.idempotency_key != expected_key {
        return Err("submit_attribution_batch_idempotency_preimage_mismatch_phase_1594_fix1");
    }
    Ok(NormalizedAttributionRequest {
        epoch: req.epoch_number,
        backward_root,
        backward_root_hex: req.backward_attribution_batch_root,
    })
}

fn parse_lower_sha256_hex(value: &str) -> Result<[u8; 32], &'static str> {
    if !is_lower_sha256_hex(value) {
        return Err("submit_attribution_batch_invalid_backward_root_phase_1594");
    }
    let mut out = [0u8; 32];
    for index in 0..32 {
        let hi = hex_nibble(value.as_bytes()[index * 2])?;
        let lo = hex_nibble(value.as_bytes()[index * 2 + 1])?;
        out[index] = (hi << 4) | lo;
    }
    Ok(out)
}

fn is_lower_sha256_hex(value: &str) -> bool {
    value.len() == 64
        && value
            .as_bytes()
            .iter()
            .all(|byte| byte.is_ascii_digit() || (*byte >= b'a' && *byte <= b'f'))
}

fn attribution_batch_idempotency_key(req: &SubmitAttributionBatchRequest) -> String {
    let mut hasher = Sha256::new();
    hasher.update(ATTRIBUTION_BATCH_PREIMAGE_DOMAIN);
    hasher.update(req.network_id.as_bytes());
    hasher.update(req.epoch_number.to_be_bytes());
    hasher.update(&req.submitter_agent_id);
    hasher.update(req.backward_attribution_batch_root.as_bytes());
    hasher.update(&req.attribution_entries_hash);
    hasher.update(req.not_before_unix_ms.to_be_bytes());
    lower_hex(&hasher.finalize())
}

fn lower_hex(bytes: &[u8]) -> String {
    const HEX: &[u8; 16] = b"0123456789abcdef";
    let mut out = String::with_capacity(bytes.len() * 2);
    for &byte in bytes {
        out.push(HEX[(byte >> 4) as usize] as char);
        out.push(HEX[(byte & 0x0f) as usize] as char);
    }
    out
}

fn hex_nibble(byte: u8) -> Result<u8, &'static str> {
    match byte {
        b'0'..=b'9' => Ok(byte - b'0'),
        b'a'..=b'f' => Ok(byte - b'a' + 10),
        _ => Err("submit_attribution_batch_invalid_backward_root_phase_1594"),
    }
}

fn attribution_error_response(code: &str) -> SubmitAttributionBatchResponse {
    SubmitAttributionBatchResponse {
        status_token: String::new(),
        error_code: code.to_string(),
        accepted_epoch_number: 0,
        accepted_backward_root: String::new(),
    }
}

fn attribution_error_code_for(err: ILCConsensusError) -> String {
    match err {
        ILCConsensusError::Other(msg)
            if msg.contains("backward_attribution_batch_root_conflict") =>
        {
            "submit_attribution_batch_backward_root_conflict_phase_1594".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("LMDB") => {
            "submit_attribution_batch_lmdb_write_failed_phase_1594".into()
        }
        _ => "submit_attribution_batch_rejected_phase_1594".into(),
    }
}

fn request_to_epoch_proposal(
    req: SubmitEpochProposalRequest,
) -> Result<EpochProposal, &'static str> {
    if req.submitter_agent_id.len() != 48 {
        return Err("submit_epoch_proposal_invalid_submitter_agent_id_phase_1586");
    }
    if req.state_root_cidv1.len() != 36 {
        return Err("submit_epoch_proposal_invalid_state_root_phase_1586");
    }
    if req.epoch_data_hash.len() != 32 {
        return Err("submit_epoch_proposal_invalid_epoch_data_hash_phase_1586");
    }
    if req.spectral_hash.len() != 32 {
        return Err("submit_epoch_proposal_invalid_spectral_hash_phase_1582");
    }
    let mut root = [0u8; 36];
    root.copy_from_slice(&req.state_root_cidv1);
    let mut spectral_hash = [0u8; 32];
    spectral_hash.copy_from_slice(&req.spectral_hash);
    Ok(EpochProposal {
        submitter_agent_id: req.submitter_agent_id,
        epoch_number: req.epoch_number,
        state_root: CIDv1Root::new(root),
        spectral_hash,
        epoch_data_hash: req.epoch_data_hash,
        settlement_record_bytes: req.settlement_record_bytes,
        idempotency_key: req.idempotency_key,
        not_before_unix_ms: req.not_before_unix_ms,
        network_id: req.network_id,
    })
}

fn outcome_response(outcome: EpochProposalOutcome) -> SubmitEpochProposalResponse {
    let mut root = [0u8; 36];
    root[..32].copy_from_slice(&outcome.state_root.p1);
    root[32..].copy_from_slice(&outcome.state_root.p2);
    SubmitEpochProposalResponse {
        status_token: outcome.status_token,
        error_code: String::new(),
        accepted_epoch_number: outcome.epoch_number,
        accepted_state_root_cidv1: root.to_vec(),
        proposal_id: outcome.proposal_id,
    }
}

fn error_response(code: &str) -> SubmitEpochProposalResponse {
    SubmitEpochProposalResponse {
        status_token: String::new(),
        error_code: code.to_string(),
        accepted_epoch_number: 0,
        accepted_state_root_cidv1: vec![],
        proposal_id: String::new(),
    }
}

fn error_code_for(err: ILCConsensusError) -> String {
    match err {
        ILCConsensusError::InvalidEpoch => "submit_epoch_proposal_invalid_epoch_phase_1586".into(),
        ILCConsensusError::InvalidSignature | ILCConsensusError::BLSVerificationFailed => {
            "submit_epoch_proposal_invalid_bls_phase_1586".into()
        }
        ILCConsensusError::InsufficientSignatures => {
            "submit_epoch_proposal_bft_rejected_phase_1586".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("bft_rejected") => {
            "submit_epoch_proposal_bft_rejected_phase_1586".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("duplicate") => {
            "submit_epoch_proposal_duplicate_phase_1586".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("settlement_path") => {
            "submit_epoch_proposal_settlement_path_not_mysticeti_phase_1586".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("wrong_network") => {
            "submit_epoch_proposal_wrong_network_phase_1586".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("body_too_large") => {
            "submit_epoch_proposal_body_too_large_phase_1586".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("inflight_body_bytes_cap_exceeded") => {
            "submit_epoch_proposal_inflight_body_bytes_cap_exceeded_phase_1586_fix2".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("empty_body") => {
            "submit_epoch_proposal_empty_body_phase_1586".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("epoch_data_hash_mismatch") => {
            "submit_epoch_proposal_epoch_data_hash_mismatch_phase_1586_fix1".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("idempotency_preimage_mismatch") => {
            "submit_epoch_proposal_idempotency_preimage_mismatch_phase_1586_fix1".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("durable") => {
            "submit_epoch_proposal_duplicate_phase_1586_fix2_durable".into()
        }
        ILCConsensusError::Other(msg) if msg.contains("idempotency_key") => {
            "submit_epoch_proposal_invalid_idempotency_key_phase_1586".into()
        }
        _ => "submit_epoch_proposal_bft_rejected_phase_1586".into(),
    }
}

fn has_allowed_tls_peer_certificate<T>(
    request: &Request<T>,
    allowed_fingerprints: &[[u8; 32]],
) -> bool {
    use tonic::transport::server::{TcpConnectInfo, TlsConnectInfo};
    if allowed_fingerprints.is_empty() {
        return false;
    }
    request
        .extensions()
        .get::<TlsConnectInfo<TcpConnectInfo>>()
        .and_then(|info| info.peer_certs())
        .map(|certs| {
            let der_refs: Vec<&[u8]> = certs.iter().map(|cert| cert.as_ref()).collect();
            peer_cert_leaf_matches_fingerprint_allowlist(&der_refs, allowed_fingerprints)
        })
        .unwrap_or(false)
}

fn peer_cert_leaf_matches_fingerprint_allowlist(
    certs: &[&[u8]],
    allowed_fingerprints: &[[u8; 32]],
) -> bool {
    if allowed_fingerprints.is_empty() {
        return false;
    }
    let Some(leaf) = certs.first() else {
        return false;
    };
    let fingerprint: [u8; 32] = Sha256::digest(*leaf).into();
    allowed_fingerprints.contains(&fingerprint)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::epoch_settlement::{test_epoch_not_before_unix_ms, EpochSettlementProtocol};
    use crate::fast_path::FastPathProtocol;
    use crate::network::PeerNetwork;
    use crate::node::NodeRunner;
    use crate::types::{
        AggSig, AttributionBatch, CIDv1Root, EpochCheckpoint, EpochSeq, EpochSettlementRecord,
        ValidatorID, ValidatorSet,
    };
    use blst::min_pk::{AggregateSignature, SecretKey};
    use lmdb_rkv::Environment;
    use sha2::{Digest, Sha256};
    use std::collections::HashMap;
    use std::net::{Ipv4Addr, SocketAddr, SocketAddrV4};
    use tempfile::tempdir;

    fn setup_env() -> (Arc<Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Arc::new(Environment::new().set_max_dbs(2).open(dir.path()).unwrap());
        (env, dir)
    }

    fn setup_validators() -> (ValidatorSet, Vec<(ValidatorID, SecretKey)>) {
        let mut entries = Vec::new();
        let mut validators = Vec::new();
        for i in 1..=2u32 {
            let sk = SecretKey::key_gen(&[i as u8; 32], &[]).unwrap();
            let pk = sk.sk_to_pk();
            let id = ValidatorID(i);
            entries.push((id, sk));
            validators.push((id, crate::types::ValidatorKey(pk)));
        }
        (ValidatorSet::new(validators, 0).unwrap(), entries)
    }

    fn generate_ephemeral_cert() -> (Vec<u8>, Vec<u8>) {
        let rcgen::CertifiedKey { cert, key_pair } =
            rcgen::generate_simple_self_signed(vec!["localhost".into()]).unwrap();
        (cert.der().to_vec(), key_pair.serialize_der())
    }

    fn mock_socket() -> SocketAddr {
        SocketAddr::V4(SocketAddrV4::new(Ipv4Addr::new(127, 0, 0, 1), 0))
    }

    fn proposal_request(idempotency_key: &str) -> SubmitEpochProposalRequest {
        let settlement_record_bytes = b"canonical-economic-evidence".to_vec();
        let epoch_data_hash = Sha256::digest(&settlement_record_bytes).to_vec();
        let idempotency_key = if idempotency_key == "auto" {
            proposal_idempotency_key(
                b"ILC_SUBMIT_EPOCH_PROPOSAL_V1",
                "ilc-rc01",
                1,
                &[9; 48],
                &[7; 36],
                &[13; 32],
                &epoch_data_hash,
                &settlement_record_bytes,
                0,
            )
        } else {
            idempotency_key.to_string()
        };
        SubmitEpochProposalRequest {
            submitter_agent_id: vec![9; 48],
            epoch_number: 1,
            state_root_cidv1: vec![7; 36],
            spectral_hash: vec![13; 32],
            epoch_data_hash,
            settlement_record_bytes,
            idempotency_key,
            not_before_unix_ms: 0,
            network_id: "ilc-rc01".to_string(),
        }
    }

    fn attribution_request(root: &str) -> SubmitAttributionBatchRequest {
        let mut req = SubmitAttributionBatchRequest {
            epoch_number: 7,
            submitter_agent_id: vec![8; 48],
            backward_attribution_batch_root: root.to_string(),
            idempotency_key: String::new(),
            network_id: "ilc-rc01".to_string(),
            not_before_unix_ms: 0,
            attribution_entries_hash: vec![9; 32],
        };
        req.idempotency_key = attribution_batch_idempotency_key(&req);
        req
    }

    fn proposal_idempotency_key(
        domain: &[u8],
        network_id: &str,
        epoch_number: u64,
        submitter_agent_id: &[u8],
        state_root: &[u8],
        spectral_hash: &[u8],
        epoch_data_hash: &[u8],
        settlement_record_bytes: &[u8],
        not_before_unix_ms: u64,
    ) -> String {
        let settlement_hash = Sha256::digest(settlement_record_bytes);
        let mut hasher = Sha256::new();
        hasher.update(domain);
        hasher.update(network_id.as_bytes());
        hasher.update(epoch_number.to_be_bytes());
        hasher.update(submitter_agent_id);
        hasher.update(state_root);
        hasher.update(spectral_hash);
        hasher.update(epoch_data_hash);
        hasher.update(settlement_hash);
        hasher.update(not_before_unix_ms.to_be_bytes());
        bytes_to_lower_hex(&hasher.finalize())
    }

    fn bytes_to_lower_hex(bytes: &[u8]) -> String {
        const HEX: &[u8; 16] = b"0123456789abcdef";
        let mut out = String::with_capacity(bytes.len() * 2);
        for &byte in bytes {
            out.push(HEX[(byte >> 4) as usize] as char);
            out.push(HEX[(byte & 0x0f) as usize] as char);
        }
        out
    }

    fn setup_single_validator_proposal_service() -> ProposalIngressService {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env).unwrap());
        let sk = SecretKey::key_gen(&[71u8; 32], &[]).unwrap();
        let vk = crate::types::ValidatorKey(sk.sk_to_pk());
        let validator_set = ValidatorSet::new(vec![(ValidatorID(1), vk)], 0).unwrap();
        let fast_path = Arc::new(FastPathProtocol::new(
            validator_set,
            Arc::clone(&balance_store),
            "ilc-rc01".to_string(),
        ));
        let (cert, key) = generate_ephemeral_cert();
        let network =
            Arc::new(PeerNetwork::new_client(mock_socket(), HashMap::new(), cert, key).unwrap());
        let runner = Arc::new(
            NodeRunner::new(
                ValidatorID(1),
                "ilc-rc01".to_string(),
                0,
                sk,
                network,
                fast_path,
                balance_store,
                epoch_store,
                vec![],
            )
            .with_proposal_ingress_enabled(true),
        );
        ProposalIngressService::new_for_tests_without_tls(runner)
    }

    fn setup_attribution_service() -> (AttributionIngressService, Arc<BalanceStore>) {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env).unwrap());
        (
            AttributionIngressService::new_for_tests_without_tls(Arc::clone(&balance_store)),
            balance_store,
        )
    }

    fn agg_sig_all(
        record: &EpochSettlementRecord,
        entries: &[(ValidatorID, SecretKey)],
    ) -> (AggSig, Vec<ValidatorID>) {
        let msg = bincode::serialize(record).unwrap();
        let sigs: Vec<_> = entries
            .iter()
            .map(|(_, sk)| sk.sign(&msg, crate::types::ILC_EPOCH_SIG_DST, &[]))
            .collect();
        let sig_refs: Vec<_> = sigs.iter().collect();
        let agg = AggregateSignature::aggregate(&sig_refs, false).unwrap();
        let signers: Vec<ValidatorID> = entries.iter().map(|(id, _)| *id).collect();
        (AggSig(agg), signers)
    }

    #[tokio::test]
    async fn test_get_balance_request_valid() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());

        let agent_id = AgentID([5; 48]);
        balance_store
            .apply_attribution(AttributionBatch {
                epoch: EpochSeq(1),
                attributions: vec![(agent_id, 999_000)],
                backward_attribution_batch_root: None,
                agent_reputation_root: None,
            })
            .unwrap();

        let app = ApplicationInterface::new(balance_store, epoch_store);

        let req = Request::new(GetBalanceRequest {
            agent_id: vec![5; 48],
        });

        let resp = app.get_balance(req).await.unwrap().into_inner();
        assert_eq!(resp.amount_micro_ecu, 999_000);
        assert_eq!(resp.version, 0);
        assert_eq!(resp.epoch, 1);
    }

    #[tokio::test]
    async fn test_submit_epoch_proposal_valid_single_validator_commits() {
        let service = setup_single_validator_proposal_service();
        let resp = service
            .submit_epoch_proposal(Request::new(proposal_request("auto")))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            resp.status_token,
            "submit_epoch_proposal_accepted_phase_1586"
        );
        assert_eq!(resp.error_code, "");
        assert_eq!(resp.accepted_epoch_number, 1);
        assert_eq!(resp.accepted_state_root_cidv1, vec![7; 36]);
    }

    #[tokio::test]
    async fn test_submit_epoch_proposal_duplicate_rejected() {
        let service = setup_single_validator_proposal_service();
        let key = proposal_request("auto").idempotency_key;
        let first = service
            .submit_epoch_proposal(Request::new(proposal_request(&key)))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            first.status_token,
            "submit_epoch_proposal_accepted_phase_1586"
        );

        let second = service
            .submit_epoch_proposal(Request::new(proposal_request(&key)))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            second.error_code,
            "submit_epoch_proposal_duplicate_phase_1586"
        );
    }

    #[tokio::test]
    async fn test_submit_epoch_proposal_requires_tls_client_cert() {
        let service = {
            let mut service = setup_single_validator_proposal_service();
            service.require_tls_client_cert = true;
            service
        };
        let resp = service
            .submit_epoch_proposal(Request::new(proposal_request("auto")))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            resp.error_code,
            "submit_epoch_proposal_unauthenticated_phase_1586"
        );
    }

    #[tokio::test]
    async fn test_submit_attribution_batch_stores_backward_root() {
        let (service, store) = setup_attribution_service();
        let root = "b".repeat(64);
        let resp = service
            .submit_attribution_batch(Request::new(attribution_request(&root)))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(resp.status_token, "attribution_batch_accepted");
        assert_eq!(resp.error_code, "");
        assert_eq!(resp.accepted_epoch_number, 7);
        assert_eq!(resp.accepted_backward_root, root);
        let stored = store
            .get_backward_attribution_batch_root(EpochSeq(7))
            .unwrap()
            .unwrap();
        assert_eq!(bytes_to_lower_hex(&stored), root);
    }

    #[tokio::test]
    async fn test_submit_attribution_batch_rejects_bad_root_and_hash() {
        let (service, _store) = setup_attribution_service();
        let mut bad_root = attribution_request(&"B".repeat(64));
        let resp = service
            .submit_attribution_batch(Request::new(bad_root))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            resp.error_code,
            "submit_attribution_batch_invalid_backward_root_phase_1594"
        );

        bad_root = attribution_request("");
        bad_root.attribution_entries_hash = vec![1; 31];
        let resp = service
            .submit_attribution_batch(Request::new(bad_root))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            resp.error_code,
            "submit_attribution_batch_invalid_entries_hash_phase_1594"
        );
    }

    #[tokio::test]
    async fn test_submit_attribution_batch_rejects_epoch_root_conflict() {
        let (service, _store) = setup_attribution_service();
        let first = service
            .submit_attribution_batch(Request::new(attribution_request(&"b".repeat(64))))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(first.status_token, "attribution_batch_accepted");

        let second = service
            .submit_attribution_batch(Request::new(attribution_request(&"c".repeat(64))))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            second.error_code,
            "submit_attribution_batch_backward_root_conflict_phase_1594"
        );
    }

    #[tokio::test]
    async fn test_submit_attribution_batch_rejects_wrong_network() {
        let (service, _store) = setup_attribution_service();
        let mut req = attribution_request(&"b".repeat(64));
        req.network_id = "wrong-network".to_string();
        req.idempotency_key = attribution_batch_idempotency_key(&req);

        let resp = service
            .submit_attribution_batch(Request::new(req))
            .await
            .unwrap()
            .into_inner();

        assert_eq!(
            resp.error_code,
            "submit_attribution_batch_wrong_network_phase_1594_fix1"
        );
    }

    #[tokio::test]
    async fn test_submit_attribution_batch_rejects_not_before_too_far_future() {
        let (service, _store) = setup_attribution_service();
        let now_ms = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map(|d| d.as_millis() as u64)
            .unwrap_or(0);
        let mut req = attribution_request(&"b".repeat(64));
        req.not_before_unix_ms = now_ms
            .saturating_add(crate::epoch_settlement::CLOCK_SKEW_TOLERANCE_MS)
            .saturating_add(60_000);
        req.idempotency_key = attribution_batch_idempotency_key(&req);

        let resp = service
            .submit_attribution_batch(Request::new(req))
            .await
            .unwrap()
            .into_inner();

        assert_eq!(
            resp.error_code,
            "submit_attribution_batch_not_before_too_far_future_phase_1594_fix1"
        );
    }

    #[tokio::test]
    async fn test_submit_attribution_batch_rejects_idempotency_preimage_mismatch() {
        let (service, _store) = setup_attribution_service();
        let mut req = attribution_request(&"b".repeat(64));
        req.attribution_entries_hash = vec![7; 32];

        let resp = service
            .submit_attribution_batch(Request::new(req))
            .await
            .unwrap()
            .into_inner();

        assert_eq!(
            resp.error_code,
            "submit_attribution_batch_idempotency_preimage_mismatch_phase_1594_fix1"
        );
    }

    #[tokio::test]
    async fn test_submit_attribution_batch_requires_tls_client_cert() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env).unwrap());
        let service = AttributionIngressService::new(balance_store, "ilc-rc01".to_string(), vec![]);
        let resp = service
            .submit_attribution_batch(Request::new(attribution_request("")))
            .await
            .unwrap()
            .into_inner();
        assert_eq!(
            resp.error_code,
            "submit_attribution_batch_unauthenticated_phase_1594"
        );
    }

    #[test]
    fn test_phase1586_fix2_peer_cert_fingerprint_allowlist_matches_only_known_leaf_cert() {
        let known = b"validator-2-der-cert";
        let unknown = b"unknown-client-cert";
        let allowed = vec![Sha256::digest(known).into()];

        assert!(peer_cert_leaf_matches_fingerprint_allowlist(
            &[known.as_slice()],
            &allowed
        ));
        assert!(!peer_cert_leaf_matches_fingerprint_allowlist(
            &[unknown.as_slice()],
            &allowed
        ));
        assert!(!peer_cert_leaf_matches_fingerprint_allowlist(
            &[unknown.as_slice(), known.as_slice()],
            &allowed
        ));
        assert!(!peer_cert_leaf_matches_fingerprint_allowlist(
            &[known.as_slice()],
            &[]
        ));
    }

    #[tokio::test]
    async fn test_get_balance_request_wrong_length() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());
        let app = ApplicationInterface::new(balance_store, epoch_store);

        let req = Request::new(GetBalanceRequest {
            agent_id: vec![5; 47], // Intentionally missing 1 byte
        });

        let err = app.get_balance(req).await.unwrap_err();
        assert_eq!(err.code(), tonic::Code::InvalidArgument);
    }

    #[tokio::test]
    async fn test_get_epoch_returns_stub_and_real() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());
        let app = ApplicationInterface::new(balance_store, epoch_store.clone());

        // 1. Initial State should organically map to Epoch 0 natively without panic
        let req = Request::new(GetEpochRequest {});
        let resp = app.get_epoch(req).await.unwrap().into_inner();
        assert_eq!(resp.current_epoch, 0);

        // 2. We inject a valid EpochSettlement sequence via the M-006 domain logic mapped over LMDB
        let protocol = EpochSettlementProtocol::new(epoch_store.clone());

        let (vset, entries) = setup_validators();
        // SEC-FIX-02: commit epochs sequentially from 1.
        for ep in 1u64..=3 {
            let r = EpochSettlementRecord {
                epoch: EpochSeq(ep),
                state_root: CIDv1Root::new([ep as u8; 36]),
                spectral_hash: [0u8; 32],
                proposal_commitment_sha256: [ep as u8; 32],
                not_before_unix_ms: test_epoch_not_before_unix_ms(ep),
            };
            let (sigs, signers) = agg_sig_all(&r, &entries);
            let cp = EpochCheckpoint {
                record: r.clone(),
                sigs,
                signers,
            };
            protocol.process_epoch_checkpoint(cp, &vset).unwrap();
        }

        // Validate retrieving actual global epoch representation dynamically from LMDB
        let req2 = Request::new(GetEpochRequest {});
        let resp2 = app.get_epoch(req2).await.unwrap().into_inner();
        assert_eq!(resp2.current_epoch, 3);
    }

    #[tokio::test]
    async fn test_get_epoch_chain_zero_sentinel_at_genesis_returns_empty_complete() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());
        let app = ApplicationInterface::new(balance_store, epoch_store);

        let req = Request::new(GetEpochChainRequest {
            from_epoch: 0,
            to_epoch: 0,
            include_edges: false,
        });
        let resp = app.get_epoch_chain(req).await.unwrap().into_inner();

        assert!(resp.chain_complete);
        assert!(resp.records.is_empty());
        assert!(resp.edges.is_empty());
        assert!(resp.hyperedges.is_empty());
    }

    #[tokio::test]
    async fn test_get_epoch_record_returns_stored_agg_sig() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());
        let app = ApplicationInterface::new(balance_store, epoch_store.clone());
        let protocol = EpochSettlementProtocol::new(epoch_store.clone());
        let (vset, entries) = setup_validators();

        // SEC-FIX-02: commit sequentially.
        let record = EpochSettlementRecord {
            epoch: EpochSeq(1),
            state_root: CIDv1Root::new([1u8; 36]),
            spectral_hash: [0u8; 32],
            proposal_commitment_sha256: [1u8; 32],
            not_before_unix_ms: 0,
        };
        let (sigs, signers) = agg_sig_all(&record, &entries);
        let checkpoint = EpochCheckpoint {
            record: record.clone(),
            sigs,
            signers,
        };
        protocol
            .process_epoch_checkpoint(checkpoint, &vset)
            .unwrap();

        let req = Request::new(GetEpochRecordRequest { epoch: 1 });
        let resp = app.get_epoch_record(req).await.unwrap().into_inner();
        assert!(resp.found);
        assert_eq!(resp.agg_sig.len(), 96);
        assert_eq!(resp.state_root, [1u8; 36].to_vec());
    }

    #[tokio::test]
    async fn test_get_epoch_chain_chain_complete() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());
        let app = ApplicationInterface::new(balance_store, epoch_store.clone());
        let protocol = EpochSettlementProtocol::new(epoch_store.clone());
        let (vset, entries) = setup_validators();

        for i in 1..=5 {
            let record = EpochSettlementRecord {
                epoch: EpochSeq(i),
                state_root: CIDv1Root::new([i as u8; 36]),
                spectral_hash: [0u8; 32],
                proposal_commitment_sha256: [i as u8; 32],
                not_before_unix_ms: test_epoch_not_before_unix_ms(i),
            };
            let (sigs, signers) = agg_sig_all(&record, &entries);
            protocol
                .process_epoch_checkpoint(
                    EpochCheckpoint {
                        record: record.clone(),
                        sigs,
                        signers,
                    },
                    &vset,
                )
                .unwrap();
        }

        let req = Request::new(GetEpochChainRequest {
            from_epoch: 1,
            to_epoch: 5,
            include_edges: false,
        });
        let resp = app.get_epoch_chain(req).await.unwrap().into_inner();
        assert!(resp.chain_complete);
        assert_eq!(resp.records.len(), 5);
    }

    #[tokio::test]
    async fn test_get_epoch_chain_caps_batch_size() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());
        let app = ApplicationInterface::new(balance_store, epoch_store.clone());
        let protocol = EpochSettlementProtocol::new(epoch_store.clone());
        let (vset, entries) = setup_validators();

        for i in 1..=(MAX_EPOCH_CHAIN_BATCH + 2) {
            let record = EpochSettlementRecord {
                epoch: EpochSeq(i),
                state_root: CIDv1Root::new([i as u8; 36]),
                spectral_hash: [0u8; 32],
                proposal_commitment_sha256: [i as u8; 32],
                not_before_unix_ms: test_epoch_not_before_unix_ms(i),
            };
            let (sigs, signers) = agg_sig_all(&record, &entries);
            protocol
                .process_epoch_checkpoint(
                    EpochCheckpoint {
                        record: record.clone(),
                        sigs,
                        signers,
                    },
                    &vset,
                )
                .unwrap();
        }

        let req = Request::new(GetEpochChainRequest {
            from_epoch: 1,
            to_epoch: MAX_EPOCH_CHAIN_BATCH + 2,
            include_edges: false,
        });
        let resp = app.get_epoch_chain(req).await.unwrap().into_inner();
        assert!(!resp.chain_complete);
        assert_eq!(resp.records.len(), MAX_EPOCH_CHAIN_BATCH as usize);
        assert_eq!(resp.records.last().unwrap().epoch, MAX_EPOCH_CHAIN_BATCH);
    }

    #[cfg(feature = "testnet_fault_sim")]
    #[tokio::test]
    async fn test_get_epoch_chain_gap_returns_partial() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());
        let app = ApplicationInterface::new(balance_store, epoch_store.clone());
        let protocol = EpochSettlementProtocol::new(epoch_store.clone());
        let (vset, entries) = setup_validators();

        // Commit 1-3 via the sequential protocol path, then inject epoch 5 directly
        // via commit_epoch_record (testnet write, no +1 guard) to simulate a gap
        // as might exist after partial recovery. Epoch 4 is intentionally absent.
        use crate::epoch_settlement::EpochStore;
        for i in 1u64..=3 {
            let record = EpochSettlementRecord {
                epoch: EpochSeq(i),
                state_root: CIDv1Root::new([i as u8; 36]),
                spectral_hash: [0u8; 32],
                proposal_commitment_sha256: [i as u8; 32],
                not_before_unix_ms: test_epoch_not_before_unix_ms(i),
            };
            let (sigs, signers) = agg_sig_all(&record, &entries);
            protocol
                .process_epoch_checkpoint(
                    EpochCheckpoint {
                        record: record.clone(),
                        sigs,
                        signers,
                    },
                    &vset,
                )
                .unwrap();
        }
        // Direct write of epoch 5 (skip 4) to simulate a gap in the store.
        epoch_store
            .commit_epoch_record(EpochSettlementRecord {
                epoch: EpochSeq(5),
                state_root: CIDv1Root::new([5u8; 36]),
                spectral_hash: [0u8; 32],
                proposal_commitment_sha256: [5u8; 32],
                not_before_unix_ms: test_epoch_not_before_unix_ms(5),
            })
            .unwrap();

        let req = Request::new(GetEpochChainRequest {
            from_epoch: 1,
            to_epoch: 5,
            include_edges: false,
        });
        let resp = app.get_epoch_chain(req).await.unwrap().into_inner();
        assert!(!resp.chain_complete); // Because it stopped at 3 missing 4
        assert_eq!(resp.records.len(), 3);
        assert_eq!(resp.records[2].epoch, 3);
    }
}
