use std::sync::Arc;
use tonic::{Request, Response, Status};

pub mod ilc_app {
    tonic::include_proto!("ilc_app");
}

use crate::balance_store::BalanceStore;
use crate::epoch_settlement::EpochStore;
use crate::types::AgentID;
use ilc_app::ilc_app_read_service_server::IlcAppReadService;
use ilc_app::{
    GetBalanceRequest, GetBalanceResponse, GetEpochChainRequest, GetEpochChainResponse,
    GetEpochRecordRequest, GetEpochRecordResponse, GetEpochRequest, GetEpochResponse,
};

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
                }))
            }
            Ok(None) => Ok(Response::new(GetEpochRecordResponse {
                epoch,
                state_root: vec![],
                agg_sig: vec![],
                found: false,
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

        let mut records = Vec::new();
        for ep in from..=to {
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
                    });
                }
                Ok(None) => break,
                Err(e) => return Err(Status::internal(format!("{:?}", e))),
            }
        }

        let chain_complete = records.len() as u64 == (to - from + 1);
        Ok(Response::new(GetEpochChainResponse {
            chain_complete,
            records,
            edges: vec![],
            hyperedges: vec![],
        }))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::epoch_settlement::EpochSettlementProtocol;
    use crate::types::{
        AggSig, AttributionBatch, CIDv1Root, EpochCheckpoint, EpochSeq, EpochSettlementRecord,
        ValidatorID, ValidatorSet,
    };
    use blst::min_pk::{AggregateSignature, SecretKey};
    use lmdb_rkv::Environment;
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
