/// testnet_client_main.rs — M-011 testnet injection client.
///
/// Connects to a running validator_harness instance via mTLS QUIC and injects
/// one or more messages for liveness testing (Workload A).
///
/// Two message types are supported:
///
///   broadcast          — Sends GossipMessage::BroadcastHonest(ECUTransfer).
///                        Requires a BLS agent secret key (--sender-key) to produce
///                        a valid sender_sig. The validator records the transfer in
///                        its in-flight table; no ack round-trip is performed by this
///                        tool (acks flow between validators via AckFor).
///
///   epoch_settlement   — Sends GossipMessage::EpochSettlementTx.
///                        The validator commits an EpochSettlementRecord to LMDB and
///                        emits `epoch_record_committed:epoch=N` to stderr.
///                        This is the primary M-011 liveness evidence path.
///
/// mTLS identity:
///   The client cert (--cert / --key) MUST be pre-registered in the target validator's
///   peer_cert_dir. For M-011 testnet, pass one of the other validator's TLS cert and key
///   (e.g., use validator_2_cert.pem / validator_2_key.pem to connect to validator 1).
///
/// Usage:
///   testnet_client --validator <addr> --cert <pem> --key <pem> --peer-cert <der> \
///     --msg epoch_settlement --epoch <N> [--count <C>]
///
///   testnet_client --validator <addr> --cert <pem> --key <pem> --peer-cert <der> \
///     --msg broadcast --sender-key <file> --to <96hex> --amount <u64> --version <u64> \
///     [--batch-window-ms <N> --relay-count <N> --relay-route <id,id,..> --validators <id@addr,...>]
///
/// `m011_testnet_client_binary_present`
use std::collections::{HashMap, HashSet};
use std::fs;
use std::net::SocketAddr;
use std::path::PathBuf;

use ilc_consensus::{
    network::{GossipEnvelope, GossipMessage, PeerNetwork},
    types::{
        AgentID, AgentSig, AggSig, CIDv1Root, ECUTransfer, EpochCheckpoint, EpochSeq,
        EpochSettlementRecord, EpochSettlementTx, ObjectRef, TransferCertificate, TransferClass,
        ValidatorSig, AGENT_TRANSFER_DST, ILC_EPOCH_SIG_DST,
    },
};
use sha2::{Digest, Sha256};

// ---------------------------------------------------------------------------
// Args
// ---------------------------------------------------------------------------

#[derive(Debug)]
enum MsgType {
    Broadcast,
    EpochSettlement,
    EpochCheckpoint,
    FullTransfer,
}

const MAX_TESTNET_RELAY_HOPS: usize = 4;

#[derive(Debug)]
struct Args {
    validator_addr: SocketAddr,
    cert_pem: PathBuf,
    key_pem: PathBuf,
    peer_cert_der: PathBuf,
    /// AgentID to claim in GossipEnvelope.peer_id (default 0).
    peer_id: u32,
    /// Real 48-byte AgentID to claim in GossipEnvelope.peer_id.
    ///
    /// Public-RC validators bind the envelope peer_id to the authenticated
    /// mTLS certificate. The legacy numeric --peer-id is retained for old
    /// testnet-only paths, but live public-RC sends must pass this value.
    peer_agent_id: Option<AgentID>,
    msg_type: MsgType,
    // broadcast params
    sender_key_file: Option<PathBuf>,
    to_hex: Option<String>,
    amount_micro_ecu: u64,
    version: u64,
    batch_window_ms: u64,
    relay_count: usize,
    relay_route: Vec<AgentID>,
    // epoch_settlement params
    start_epoch: Option<u64>,
    state_root_hex: Option<String>,
    count: u64,
    // full_transfer params
    listen_addr: Option<SocketAddr>,
    validators: Vec<(u32, SocketAddr)>,
    validator_certs: Vec<PathBuf>,
    quorum_keys: Vec<PathBuf>,
    f: usize,
}

fn parse_args() -> Result<Args, String> {
    let raw: Vec<String> = std::env::args().collect();
    let mut validator_addr: Option<SocketAddr> = None;
    let mut cert_pem: Option<PathBuf> = None;
    let mut key_pem: Option<PathBuf> = None;
    let mut peer_cert_der: Option<PathBuf> = None;
    let mut peer_id: u32 = 0;
    let mut peer_agent_id: Option<AgentID> = None;
    let mut msg_type: Option<MsgType> = None;
    let mut sender_key_file: Option<PathBuf> = None;
    let mut to_hex: Option<String> = None;
    let mut amount_micro_ecu: u64 = 1000;
    let mut version: u64 = 0;
    let mut batch_window_ms: u64 = 500;
    let mut relay_count: usize = 0;
    let mut relay_route: Vec<AgentID> = Vec::new();
    let mut start_epoch: Option<u64> = None;
    let mut state_root_hex: Option<String> = None;
    let mut count: u64 = 1;
    let mut listen_addr: Option<SocketAddr> = None;
    let mut validators: Vec<(u32, SocketAddr)> = Vec::new();
    let mut validator_certs: Vec<PathBuf> = Vec::new();
    let mut quorum_keys: Vec<PathBuf> = Vec::new();
    let mut f: usize = 1;

    let mut i = 1;
    while i < raw.len() {
        match raw[i].as_str() {
            "--validator" => {
                i += 1;
                let s = raw.get(i).ok_or("--validator requires an addr argument")?;
                validator_addr = Some(s.parse().map_err(|e| format!("--validator parse: {}", e))?);
            }
            "--cert" => {
                i += 1;
                cert_pem = Some(PathBuf::from(raw.get(i).ok_or("--cert requires a path")?));
            }
            "--key" => {
                i += 1;
                key_pem = Some(PathBuf::from(raw.get(i).ok_or("--key requires a path")?));
            }
            "--peer-cert" => {
                i += 1;
                peer_cert_der = Some(PathBuf::from(
                    raw.get(i).ok_or("--peer-cert requires a path")?,
                ));
            }
            "--peer-id" => {
                i += 1;
                peer_id = raw
                    .get(i)
                    .ok_or("--peer-id requires a number")?
                    .parse()
                    .map_err(|e| format!("--peer-id: {}", e))?;
            }
            "--peer-agent-id" => {
                i += 1;
                let value = raw
                    .get(i)
                    .ok_or("--peer-agent-id requires a 96-char hex AgentID")?;
                peer_agent_id =
                    Some(parse_agent_id_hex(value).map_err(|e| format!("--peer-agent-id: {}", e))?);
            }
            "--msg" => {
                i += 1;
                msg_type = Some(match raw.get(i).ok_or("--msg requires a type")?.as_str() {
                    "broadcast" => MsgType::Broadcast,
                    "epoch_settlement" => MsgType::EpochSettlement,
                    "epoch_checkpoint" => MsgType::EpochCheckpoint,
                    "full_transfer" => MsgType::FullTransfer,
                    other => return Err(format!("unknown --msg type '{}' (broadcast|epoch_settlement|epoch_checkpoint|full_transfer)", other)),
                });
            }
            "--sender-key" => {
                i += 1;
                sender_key_file = Some(PathBuf::from(
                    raw.get(i).ok_or("--sender-key requires a path")?,
                ));
            }
            "--to" => {
                i += 1;
                to_hex = Some(
                    raw.get(i)
                        .ok_or("--to requires a 96-char hex string")?
                        .clone(),
                );
            }
            "--amount" => {
                i += 1;
                amount_micro_ecu = raw
                    .get(i)
                    .ok_or("--amount requires a number")?
                    .parse()
                    .map_err(|e| format!("--amount: {}", e))?;
            }
            "--version" => {
                i += 1;
                version = raw
                    .get(i)
                    .ok_or("--version requires a number")?
                    .parse()
                    .map_err(|e| format!("--version: {}", e))?;
            }
            "--batch-window-ms" => {
                i += 1;
                batch_window_ms = raw
                    .get(i)
                    .ok_or("--batch-window-ms requires a number")?
                    .parse()
                    .map_err(|e| format!("--batch-window-ms: {}", e))?;
            }
            "--relay-count" => {
                i += 1;
                relay_count = raw
                    .get(i)
                    .ok_or("--relay-count requires a number")?
                    .parse()
                    .map_err(|e| format!("--relay-count: {}", e))?;
            }
            "--relay-route" => {
                i += 1;
                let list = raw
                    .get(i)
                    .ok_or("--relay-route requires a comma-separated list")?;
                relay_route = parse_relay_route(list)?;
            }
            "--epoch" => {
                i += 1;
                start_epoch = Some(
                    raw.get(i)
                        .ok_or("--epoch requires a number")?
                        .parse()
                        .map_err(|e| format!("--epoch: {}", e))?,
                );
            }
            "--state-root" => {
                i += 1;
                state_root_hex = Some(
                    raw.get(i)
                        .ok_or("--state-root requires a 72-char dag-cbor CIDv1Root hex string")?
                        .clone(),
                );
            }
            "--count" => {
                i += 1;
                count = raw
                    .get(i)
                    .ok_or("--count requires a number")?
                    .parse()
                    .map_err(|e| format!("--count: {}", e))?;
            }
            "--listen-addr" => {
                i += 1;
                let s = raw
                    .get(i)
                    .ok_or("--listen-addr requires an addr argument")?;
                listen_addr = Some(s.parse().map_err(|e| format!("--listen-addr: {}", e))?);
            }
            "--f" => {
                i += 1;
                f = raw
                    .get(i)
                    .ok_or("--f requires a number")?
                    .parse()
                    .map_err(|e| format!("--f: {}", e))?;
            }
            "--validators" => {
                i += 1;
                let list = raw
                    .get(i)
                    .ok_or("--validators requires a comma-separated list")?;
                for (idx, addr_str) in list.split(',').enumerate() {
                    validators.push(parse_validator_spec(addr_str, (idx + 1) as u32)?);
                }
            }
            "--validator-certs" => {
                i += 1;
                let list = raw
                    .get(i)
                    .ok_or("--validator-certs requires a comma-separated list")?;
                for p in list.split(',') {
                    validator_certs.push(PathBuf::from(p));
                }
            }
            "--quorum-keys" => {
                i += 1;
                let list = raw
                    .get(i)
                    .ok_or("--quorum-keys requires a comma-separated list")?;
                for p in list.split(',') {
                    quorum_keys.push(PathBuf::from(p));
                }
            }
            "--help" | "-h" => {
                eprintln!("Usage:");
                eprintln!("  testnet_client --validator <addr> --cert <pem> --key <pem> --peer-cert <der> --msg <broadcast|epoch_settlement|epoch_checkpoint>");
                eprintln!("  testnet_client --msg epoch_checkpoint --epoch <N> --state-root <72hex> --quorum-keys <csv> --peer-agent-id <96hex> ...");
                eprintln!("  testnet_client --msg broadcast --sender-key <file> --to <hex> --amount <u64> --version <u64> [--batch-window-ms <N>] [--relay-count <N> --relay-route <id,id,..> --validators <id@addr,id@addr,..>]");
                eprintln!("  testnet_client --msg full_transfer --listen-addr <addr> --f <N> --validators <addr,addr..> --validator-certs <der,der..> --sender-key <file> --to <hex> --amount <u64> --version <u64> --epoch <N> --cert <pem> --key <pem>");
                std::process::exit(0);
            }
            other => return Err(format!("Unknown argument: {}", other)),
        }
        i += 1;
    }

    Ok(Args {
        validator_addr: validator_addr.unwrap_or_else(|| "0.0.0.0:0".parse().unwrap()), // optional for FullTransfer
        cert_pem: cert_pem.ok_or("--cert is required")?,
        key_pem: key_pem.ok_or("--key is required")?,
        peer_cert_der: peer_cert_der.unwrap_or_else(|| PathBuf::from("")), // optional for FullTransfer
        peer_id,
        peer_agent_id,
        msg_type: msg_type.ok_or("--msg is required")?,
        sender_key_file,
        to_hex,
        amount_micro_ecu,
        version,
        batch_window_ms,
        relay_count,
        relay_route,
        start_epoch,
        state_root_hex,
        count,
        listen_addr,
        validators,
        validator_certs,
        quorum_keys,
        f,
    })
}

#[derive(Debug, Clone, PartialEq, Eq)]
struct RelayPlan {
    first_hop_id: AgentID,
    first_hop_addr: SocketAddr,
    full_path: Vec<AgentID>,
    remaining_route: Vec<AgentID>,
}

fn parse_validator_spec(spec: &str, default_id: u32) -> Result<(u32, SocketAddr), String> {
    if let Some((id_str, addr_str)) = spec.split_once('@') {
        let id = id_str
            .parse()
            .map_err(|e| format!("--validators id '{}': {}", id_str, e))?;
        let addr = addr_str
            .parse()
            .map_err(|e| format!("--validators addr '{}': {}", addr_str, e))?;
        Ok((id, addr))
    } else {
        let addr = spec
            .parse()
            .map_err(|e| format!("--validators addr '{}': {}", spec, e))?;
        Ok((default_id, addr))
    }
}

fn parse_relay_route(spec: &str) -> Result<Vec<AgentID>, String> {
    if spec.trim().is_empty() {
        return Ok(Vec::new());
    }
    spec.split(',')
        .map(|value| {
            let id = value
                .trim()
                .parse()
                .map_err(|e| format!("--relay-route '{}': {}", value, e))?;
            Ok(AgentID::from_testnet_validator_index(id))
        })
        .collect()
}

fn compute_relay_plan(
    target_addr: SocketAddr,
    validators: &[(u32, SocketAddr)],
    relay_route: &[AgentID],
    relay_count: usize,
) -> Result<Option<RelayPlan>, String> {
    if relay_count == 0 {
        if !relay_route.is_empty() {
            return Err("--relay-route requires --relay-count > 0".into());
        }
        return Ok(None);
    }

    if relay_count > MAX_TESTNET_RELAY_HOPS {
        return Err(format!(
            "--relay-count exceeds max hop cap of {}",
            MAX_TESTNET_RELAY_HOPS
        ));
    }
    if relay_route.len() != relay_count {
        return Err(format!(
            "--relay-route length {} must match --relay-count {}",
            relay_route.len(),
            relay_count
        ));
    }

    let mut seen_validator_ids = HashSet::new();
    let mut seen_validator_addrs = HashSet::new();
    for (id, addr) in validators {
        if !seen_validator_ids.insert(*id) {
            return Err(format!(
                "--validators contains duplicate validator id {}",
                id
            ));
        }
        if !seen_validator_addrs.insert(*addr) {
            return Err(format!(
                "--validators contains duplicate validator address {}",
                addr
            ));
        }
    }

    let validator_map: HashMap<AgentID, SocketAddr> = validators
        .iter()
        .map(|(id, addr)| (AgentID::from_testnet_validator_index(*id), *addr))
        .collect();
    let target_id = validators
        .iter()
        .find(|(_, addr)| *addr == target_addr)
        .map(|(id, _)| AgentID::from_testnet_validator_index(*id))
        .ok_or(
            "--validators must include the final --validator target when relay mode is enabled",
        )?;

    let mut seen = HashSet::new();
    let mut full_path = Vec::with_capacity(relay_route.len() + 1);
    for hop in relay_route {
        if *hop == target_id {
            return Err("--relay-route must not include the final target validator".into());
        }
        if !validator_map.contains_key(hop) {
            return Err(format!(
                "--relay-route references unknown validator {}",
                hop
            ));
        }
        if !seen.insert(*hop) {
            return Err(format!(
                "--relay-route contains duplicate validator {}",
                hop
            ));
        }
        full_path.push(*hop);
    }
    full_path.push(target_id);

    let first_hop_id = *full_path
        .first()
        .ok_or("relay mode requires at least one hop")?;
    let first_hop_addr = *validator_map
        .get(&first_hop_id)
        .ok_or_else(|| format!("missing address for relay validator {}", first_hop_id))?;

    Ok(Some(RelayPlan {
        first_hop_id,
        first_hop_addr,
        full_path,
        remaining_route: relay_route
            .iter()
            .copied()
            .skip(1)
            .chain(std::iter::once(target_id))
            .collect(),
    }))
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

#[tokio::main]
async fn main() {
    rustls::crypto::ring::default_provider()
        .install_default()
        .ok();

    let args = match parse_args() {
        Ok(a) => a,
        Err(e) => {
            eprintln!("Error: {}", e);
            std::process::exit(1);
        }
    };

    if let Err(e) = run(args).await {
        eprintln!("[testnet_client] fatal: {}", e);
        std::process::exit(1);
    }
}

async fn run(args: Args) -> Result<(), Box<dyn std::error::Error>> {
    // -----------------------------------------------------------------------
    // 1. Load TLS credentials
    // -----------------------------------------------------------------------
    let my_cert_der = load_pem_as_der(&args.cert_pem)?;
    let my_key_der = load_pem_as_der(&args.key_pem)?;

    if matches!(args.msg_type, MsgType::FullTransfer) {
        return run_full_transfer(args, my_cert_der, my_key_der).await;
    }

    let peer_cert_der_bytes = fs::read(&args.peer_cert_der)?;

    // Peer cert map: validator_id → DER bytes.
    // We only know the one target validator here; the PinnedCertVerifier will accept it.
    let peer_certs: HashMap<u32, Vec<u8>> = HashMap::from([(999u32, peer_cert_der_bytes)]);

    // -----------------------------------------------------------------------
    // 2. Construct client QUIC endpoint
    // -----------------------------------------------------------------------
    let bind_addr: SocketAddr = "0.0.0.0:0".parse().unwrap();
    let network = PeerNetwork::new_client(bind_addr, peer_certs, my_cert_der, my_key_der)
        .map_err(|e| format!("PeerNetwork::new_client: {}", e))?;

    eprintln!(
        "[testnet_client] endpoint ready for target {} (peer_id claim={}, peer_agent_id claim={})",
        args.validator_addr,
        args.peer_id,
        args.peer_agent_id
            .map(|id| id.to_string())
            .unwrap_or_else(|| "legacy_numeric_mapping".into())
    );

    // -----------------------------------------------------------------------
    // 4. Send messages
    // -----------------------------------------------------------------------
    match args.msg_type {
        MsgType::EpochSettlement => {
            let conn = network
                .endpoint
                .connect(args.validator_addr, "localhost")?
                .await
                .map_err(|e| format!("QUIC connect: {}", e))?;
            let start_epoch = args
                .start_epoch
                .ok_or("--epoch is required for --msg epoch_settlement")?;
            if args.count != 1 {
                return Err(
                    "--count must be 1 for --msg epoch_settlement with --state-root".into(),
                );
            }
            let state_root = cidv1_root_from_required_arg(
                args.state_root_hex.as_deref(),
                "--state-root is required for --msg epoch_settlement",
            )?;
            for i in 0..args.count {
                let epoch = start_epoch + i;
                let tx = EpochSettlementTx {
                    epoch: EpochSeq(epoch),
                    state_root,
                };
                let envelope = GossipEnvelope {
                    frame_type: 0x00,
                    peer_id: args
                        .peer_agent_id
                        .unwrap_or_else(|| AgentID::from_testnet_validator_index(args.peer_id)),
                    payload: GossipMessage::EpochSettlementTx(tx),
                };
                let (send, _recv) = conn
                    .open_bi()
                    .await
                    .map_err(|e| format!("open_bi: {}", e))?;
                network
                    .transmit(send, envelope)
                    .await
                    .map_err(|e| format!("transmit epoch {}: {}", epoch, e))?;
                eprintln!("[testnet_client] sent EpochSettlementTx epoch={}", epoch);
            }
        }
        MsgType::EpochCheckpoint => {
            let direct_conn = network
                .endpoint
                .connect(args.validator_addr, "localhost")?
                .await
                .map_err(|e| format!("QUIC connect: {}", e))?;
            let start_epoch = args
                .start_epoch
                .ok_or("--epoch is required for --msg epoch_checkpoint")?;
            if args.count != 1 {
                return Err(
                    "--count must be 1 for --msg epoch_checkpoint with --state-root".into(),
                );
            }
            let state_root = cidv1_root_from_required_arg(
                args.state_root_hex.as_deref(),
                "--state-root is required for --msg epoch_checkpoint",
            )?;
            let mut bls_keys = Vec::new();
            if args.quorum_keys.is_empty() {
                return Err("--quorum-keys is required for epoch_checkpoint".into());
            }
            for key_path in &args.quorum_keys {
                let sk = load_bls_secret_key(key_path).map_err(|e| {
                    format!(
                        "EpochCheckpoint failed to load {}: {:?}",
                        key_path.display(),
                        e
                    )
                })?;
                bls_keys.push(sk);
            }

            let targets = if !args.validators.is_empty() {
                args.validators
                    .iter()
                    .map(|(_, addr)| *addr)
                    .collect::<Vec<_>>()
            } else {
                vec![args.validator_addr]
            };

            for i in 0..args.count {
                let epoch = start_epoch + i;
                let not_before_unix_ms = 0;
                let spectral_hash = [0u8; 32];
                let record = EpochSettlementRecord {
                    epoch: EpochSeq(epoch),
                    state_root,
                    spectral_hash,
                    proposal_commitment_sha256: testnet_direct_checkpoint_commitment(
                        epoch,
                        &state_root,
                        &spectral_hash,
                        not_before_unix_ms,
                    ),
                    not_before_unix_ms,
                };

                let msg_bytes = bincode::serialize(&record).unwrap();
                let mut sigs = Vec::new();
                for sk in &bls_keys {
                    sigs.push(sk.sign(&msg_bytes, ILC_EPOCH_SIG_DST, &[]));
                }
                let sig_refs: Vec<&blst::min_pk::Signature> = sigs.iter().collect();
                let agg = blst::min_pk::AggregateSignature::aggregate(&sig_refs, false).unwrap();

                let signers: Vec<AgentID> = bls_keys
                    .iter()
                    .map(|sk| AgentID(sk.sk_to_pk().compress()))
                    .collect();
                let checkpoint = EpochCheckpoint {
                    record,
                    sigs: AggSig(agg),
                    signers,
                };

                let envelope = GossipEnvelope {
                    frame_type: 0x00,
                    peer_id: args
                        .peer_agent_id
                        .unwrap_or_else(|| AgentID::from_testnet_validator_index(args.peer_id)),
                    payload: GossipMessage::EpochCheckpointMsg(checkpoint),
                };

                for addr in &targets {
                    let c = if *addr == args.validator_addr {
                        direct_conn.clone()
                    } else {
                        network
                            .endpoint
                            .connect(*addr, "localhost")?
                            .await
                            .map_err(|e| format!("connect: {}", e))?
                    };

                    let (send, _recv) = c.open_bi().await.map_err(|e| format!("open_bi: {}", e))?;
                    network
                        .transmit(send, envelope.clone())
                        .await
                        .map_err(|e| format!("transmit epoch {}: {}", epoch, e))?;
                    tokio::time::sleep(tokio::time::Duration::from_millis(250)).await;
                }
                eprintln!(
                    "[testnet_client] sent EpochCheckpointMsg epoch={} to {} targets",
                    epoch,
                    targets.len()
                );
            }
        }
        MsgType::Broadcast => {
            let sk_file = args
                .sender_key_file
                .as_ref()
                .ok_or("--sender-key is required for --msg broadcast")?;
            let to_hex = args
                .to_hex
                .as_ref()
                .ok_or("--to is required for --msg broadcast")?;
            let relay_plan = compute_relay_plan(
                args.validator_addr,
                &args.validators,
                &args.relay_route,
                args.relay_count,
            )
            .map_err(|e| format!("relay plan: {}", e))?;

            let sender_sk = load_bls_secret_key(sk_file)?;
            let sender_pk = sender_sk.sk_to_pk();
            let sender_agent_id = AgentID(sender_pk.compress());

            let to_bytes = hex_decode_exact(to_hex, 48).map_err(|e| format!("--to: {}", e))?;
            let mut to_arr = [0u8; 48];
            to_arr.copy_from_slice(&to_bytes);
            let to_agent_id = AgentID(to_arr);

            let target_addr = relay_plan
                .as_ref()
                .map(|plan| plan.first_hop_addr)
                .unwrap_or(args.validator_addr);
            let conn = network
                .endpoint
                .connect(target_addr, "localhost")?
                .await
                .map_err(|e| format!("QUIC connect: {}", e))?;

            if let Some(plan) = &relay_plan {
                let path = plan
                    .full_path
                    .iter()
                    .map(|id| id.to_string())
                    .collect::<Vec<_>>()
                    .join("->");
                eprintln!(
                    "[testnet_client] layer2 relay mode enabled (testnet_only) target={} first_hop={} batch_window_ms={} relay_path={}",
                    args.validator_addr,
                    plan.first_hop_id,
                    args.batch_window_ms,
                    path
                );
            } else {
                eprintln!("[testnet_client] direct broadcast mode enabled");
            }

            for i in 0..args.count {
                let ver = args.version + i;
                let object_ref = ObjectRef {
                    agent: sender_agent_id,
                    version: ver,
                };

                // Sign per AGENT_TRANSFER_DST (matches handle_broadcast_honest verification)
                let transfer_class = TransferClass::Contribution;
                let sender_msg = bincode::serialize(&(
                    &object_ref,
                    &to_agent_id,
                    &args.amount_micro_ecu,
                    &transfer_class,
                ))
                .map_err(|e| format!("serialize sender_msg: {}", e))?;
                let sig = sender_sk.sign(&sender_msg, AGENT_TRANSFER_DST, &[]);

                let transfer = ECUTransfer {
                    object_ref,
                    to: to_agent_id,
                    amount_micro_ecu: args.amount_micro_ecu,
                    transfer_class,
                    sender_sig: AgentSig(sig),
                };

                if relay_plan.is_some() && args.batch_window_ms > 0 {
                    tokio::time::sleep(tokio::time::Duration::from_millis(args.batch_window_ms))
                        .await;
                }

                let envelope = GossipEnvelope {
                    frame_type: 0x00,
                    peer_id: AgentID::from_testnet_validator_index(args.peer_id),
                    payload: if let Some(plan) = &relay_plan {
                        GossipMessage::RelaySubmit {
                            transfer,
                            remaining_route: plan.remaining_route.clone(),
                        }
                    } else {
                        GossipMessage::BroadcastHonest(transfer)
                    },
                };

                let (send, _recv) = conn
                    .open_bi()
                    .await
                    .map_err(|e| format!("open_bi: {}", e))?;
                network
                    .transmit(send, envelope)
                    .await
                    .map_err(|e| format!("transmit broadcast ver {}: {}", ver, e))?;
                if let Some(plan) = &relay_plan {
                    let path = plan
                        .full_path
                        .iter()
                        .map(|id| id.to_string())
                        .collect::<Vec<_>>()
                        .join("->");
                    eprintln!(
                        "[testnet_client] sent RelaySubmit(testnet_only) agent={} version={} relay_path={}",
                        hex_encode(&sender_agent_id.0),
                        ver,
                        path
                    );
                } else {
                    eprintln!(
                        "[testnet_client] sent BroadcastHonest agent={} version={}",
                        hex_encode(&sender_agent_id.0),
                        ver
                    );
                }
            }
        }
        MsgType::FullTransfer => unreachable!(),
    }

    eprintln!("[testnet_client] done — {} message(s) sent", args.count);
    tokio::time::sleep(tokio::time::Duration::from_millis(1500)).await;
    Ok(())
}

async fn run_full_transfer(
    args: Args,
    my_cert_der: Vec<u8>,
    my_key_der: Vec<u8>,
) -> Result<(), Box<dyn std::error::Error>> {
    let listen_addr = args
        .listen_addr
        .ok_or("--listen-addr is required for full_transfer")?;
    let mut all_validator_cert_map = HashMap::new();
    for (i, p) in args.validator_certs.iter().enumerate() {
        let der = fs::read(p).map_err(|e| format!("read cert {}: {}", p.display(), e))?;
        all_validator_cert_map.insert((i + 1) as u32, der);
    }

    let sk_file = args
        .sender_key_file
        .as_ref()
        .ok_or("--sender-key is required for full_transfer")?;
    let to_hex = args
        .to_hex
        .as_ref()
        .ok_or("--to is required for full_transfer")?;
    let sender_sk = load_bls_secret_key(sk_file)?;
    let sender_pk = sender_sk.sk_to_pk();
    let sender_agent_id = AgentID(sender_pk.compress());

    let to_bytes = hex_decode_exact(to_hex, 48)?;
    let mut to_arr = [0u8; 48];
    to_arr.copy_from_slice(&to_bytes);
    let to_agent_id = AgentID(to_arr);

    // 2. Bind a QUIC server endpoint at --listen-addr using client cert
    let client_server = PeerNetwork::new_server(
        listen_addr,
        all_validator_cert_map.clone(),
        my_cert_der.clone(),
        my_key_der.clone(),
    )
    .map_err(|e| format!("new_server: {}", e))?;

    // 3. Build an outbound client endpoint
    let outbound = PeerNetwork::new_client(
        "0.0.0.0:0".parse()?,
        all_validator_cert_map.clone(),
        my_cert_der,
        my_key_der,
    )
    .map_err(|e| format!("new_client: {}", e))?;

    let object_ref = ObjectRef {
        agent: sender_agent_id,
        version: args.version,
    };

    let transfer_class = TransferClass::Contribution;
    let sender_msg = bincode::serialize(&(
        &object_ref,
        &to_agent_id,
        &args.amount_micro_ecu,
        &transfer_class,
    ))?;
    let sig = sender_sk.sign(&sender_msg, AGENT_TRANSFER_DST, &[]);
    let transfer = ECUTransfer {
        object_ref,
        to: to_agent_id,
        amount_micro_ecu: args.amount_micro_ecu,
        transfer_class,
        sender_sig: AgentSig(sig),
    };

    let envelope = GossipEnvelope {
        frame_type: 0x00,
        peer_id: AgentID::from_testnet_validator_index(args.peer_id), // e.g. 5
        payload: GossipMessage::BroadcastHonest(transfer.clone()),
    };

    // 4. Send BroadcastHonest to all validators
    for (vid, addr) in &args.validators {
        let conn = outbound.endpoint.connect(*addr, "localhost")?.await?;
        let (send, _recv) = conn.open_bi().await?;
        outbound.transmit(send, envelope.clone()).await?;
        eprintln!("[m012_client] sent BroadcastHonest to validator {}", vid);
    }

    // 5. Accept AckFor responses
    let quorum = 2 * args.f + 1;
    let mut acks: Vec<(AgentID, ValidatorSig)> = Vec::new();

    while acks.len() < quorum {
        let incoming = client_server
            .endpoint
            .accept()
            .await
            .ok_or("server endpoint closed")?;
        let conn = incoming.await?;
        let (_, recv) = conn.accept_bi().await?;
        let envelope = client_server.receive(&conn, recv).await?;

        if let GossipMessage::AckFor {
            object_ref: ack_ref,
            sig,
        } = envelope.payload
        {
            if ack_ref == object_ref {
                let from = envelope.peer_id;
                if !acks.iter().any(|(id, _)| *id == from) {
                    acks.push((from, sig));
                    eprintln!(
                        "[m012_client] received AckFor from validator {} ({}/{})",
                        from,
                        acks.len(),
                        quorum
                    );
                }
            }
        }
    }

    // 6. Assemble TransferCertificate
    // Phase 768 / Audit Finding D (M-015): stamp the certificate from the
    // client's explicit epoch context.  When --epoch is absent, default to
    // epoch 1 for backward compatibility with runner scripts, but emit a
    // visible warning so operators know to pass --epoch explicitly on
    // multi-epoch testnets.  Token: sec_warn_full_transfer_epoch_defaulted_to_1
    let cert_epoch = EpochSeq(args.start_epoch.unwrap_or_else(|| {
        eprintln!(
            "[m012_client] WARNING: --epoch not provided for full_transfer; \
             defaulting to epoch 1.  Pass --epoch explicitly on multi-epoch \
             testnets to avoid mis-stamping certificates. \
             Token: sec_warn_full_transfer_epoch_defaulted_to_1"
        );
        1
    }));
    let cert = TransferCertificate {
        transfer,
        sigs: acks,
        epoch: cert_epoch,
    };
    eprintln!("[m012_client] certificate assembled — broadcasting to all validators");

    // 7. Broadcast Certificate
    let cert_envelope = GossipEnvelope {
        frame_type: 0x00,
        peer_id: AgentID::from_testnet_validator_index(args.peer_id),
        payload: GossipMessage::Certificate(cert),
    };

    for (vid, addr) in &args.validators {
        let conn = outbound.endpoint.connect(*addr, "localhost")?.await?;
        let (send, _recv) = conn.open_bi().await?;
        outbound.transmit(send, cert_envelope.clone()).await?;
        eprintln!("[m012_client] sent Certificate to validator {}", vid);
    }

    eprintln!("[m012_client] full_transfer_round_trip_complete");
    Ok(())
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

fn load_bls_secret_key(path: &PathBuf) -> Result<blst::min_pk::SecretKey, String> {
    let hex = fs::read_to_string(path)
        .map_err(|e| format!("cannot read sender key '{}': {}", path.display(), e))?;
    let bytes = hex_decode_exact(hex.trim(), 32)?;
    blst::min_pk::SecretKey::from_bytes(&bytes).map_err(|_| "invalid BLS secret key bytes".into())
}

fn cidv1_root_from_required_arg(
    value: Option<&str>,
    missing_message: &'static str,
) -> Result<CIDv1Root, String> {
    let root_hex = value.ok_or(missing_message)?;
    let bytes = hex_decode_exact_lowercase(root_hex, 36)?;
    if bytes.iter().all(|byte| *byte == 0) {
        return Err("--state-root must not be all zeros".into());
    }
    if !bytes.starts_with(&[0x01, 0x71, 0x12, 0x20]) {
        return Err("--state-root must be CIDv1 dag-cbor sha2-256 bytes".into());
    }
    let mut fixed = [0u8; 36];
    fixed.copy_from_slice(&bytes);
    Ok(CIDv1Root::new(fixed))
}

fn testnet_direct_checkpoint_commitment(
    epoch: u64,
    state_root: &CIDv1Root,
    spectral_hash: &[u8; 32],
    not_before_unix_ms: u64,
) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(b"ILC_TESTNET_DIRECT_EPOCH_CHECKPOINT_V1");
    hasher.update(epoch.to_be_bytes());
    hasher.update(state_root.p1);
    hasher.update(state_root.p2);
    hasher.update(spectral_hash);
    hasher.update(not_before_unix_ms.to_be_bytes());
    hasher.finalize().into()
}

fn hex_decode_exact_lowercase(hex: &str, expected_len: usize) -> Result<Vec<u8>, String> {
    if hex.chars().any(|c| !matches!(c, '0'..='9' | 'a'..='f')) {
        return Err("expected lowercase hex".into());
    }
    hex_decode_exact(hex, expected_len)
}

fn parse_agent_id_hex(hex: &str) -> Result<AgentID, String> {
    let bytes = hex_decode_exact_lowercase(hex, 48)?;
    let mut fixed = [0u8; 48];
    fixed.copy_from_slice(&bytes);
    Ok(AgentID(fixed))
}

fn hex_decode_exact(hex: &str, expected_len: usize) -> Result<Vec<u8>, String> {
    if hex.len() != expected_len * 2 {
        return Err(format!(
            "expected {} hex chars ({} bytes), got {}",
            expected_len * 2,
            expected_len,
            hex.len()
        ));
    }
    (0..hex.len())
        .step_by(2)
        .map(|i| {
            u8::from_str_radix(&hex[i..i + 2], 16)
                .map_err(|_| format!("invalid hex at offset {}", i))
        })
        .collect::<Result<Vec<u8>, _>>()
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

/// Read a PEM file and extract the DER bytes of the first block.
/// Handles CERTIFICATE and PRIVATE KEY PEM blocks.
fn load_pem_as_der(path: &PathBuf) -> Result<Vec<u8>, String> {
    let pem_str =
        fs::read_to_string(path).map_err(|e| format!("cannot read '{}': {}", path.display(), e))?;

    let start_marker = "-----BEGIN ";
    let end_marker = "-----END ";
    let start = pem_str
        .find(start_marker)
        .ok_or_else(|| format!("no PEM BEGIN marker in '{}'", path.display()))?;
    let header_end = pem_str[start..]
        .find('\n')
        .ok_or_else(|| format!("malformed PEM in '{}'", path.display()))?;
    let end = pem_str
        .find(end_marker)
        .ok_or_else(|| format!("no PEM END marker in '{}'", path.display()))?;

    let b64_body = pem_str[start + header_end + 1..end]
        .replace('\n', "")
        .replace('\r', "");
    base64_decode(&b64_body).map_err(|e| format!("base64 decode '{}': {}", path.display(), e))
}

/// Minimal base64 decode (standard alphabet).
fn base64_decode(s: &str) -> Result<Vec<u8>, String> {
    const TABLE: &[u8; 128] = b"\
        \xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\
        \xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\
        \xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x3e\xff\xff\xff\x3f\
        \x34\x35\x36\x37\x38\x39\x3a\x3b\x3c\x3d\xff\xff\xff\xff\xff\xff\
        \xff\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\
        \x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\xff\xff\xff\xff\xff\
        \xff\x1a\x1b\x1c\x1d\x1e\x1f\x20\x21\x22\x23\x24\x25\x26\x27\x28\
        \x29\x2a\x2b\x2c\x2d\x2e\x2f\x30\x31\x32\x33\xff\xff\xff\xff\xff";

    let s = s.trim_end_matches('=');
    let mut out = Vec::with_capacity(s.len() * 3 / 4);
    let bytes = s.as_bytes();
    let mut i = 0;
    while i + 3 < bytes.len() {
        let a = dc(bytes[i], TABLE)?;
        let b = dc(bytes[i + 1], TABLE)?;
        let c = dc(bytes[i + 2], TABLE)?;
        let d = dc(bytes[i + 3], TABLE)?;
        out.push((a << 2) | (b >> 4));
        out.push((b << 4) | (c >> 2));
        out.push((c << 6) | d);
        i += 4;
    }
    match bytes.len() - i {
        2 => {
            let a = dc(bytes[i], TABLE)?;
            let b = dc(bytes[i + 1], TABLE)?;
            out.push((a << 2) | (b >> 4));
        }
        3 => {
            let a = dc(bytes[i], TABLE)?;
            let b = dc(bytes[i + 1], TABLE)?;
            let c = dc(bytes[i + 2], TABLE)?;
            out.push((a << 2) | (b >> 4));
            out.push((b << 4) | (c >> 2));
        }
        _ => {}
    }
    Ok(out)
}

fn dc(c: u8, table: &[u8; 128]) -> Result<u8, String> {
    if c as usize >= 128 {
        return Err(format!("invalid base64 char {}", c));
    }
    let v = table[c as usize];
    if v == 0xff {
        return Err(format!("invalid base64 char '{}'", c as char));
    }
    Ok(v)
}

#[cfg(test)]
mod tests {
    use super::*;

    fn testnet_agent_id(id: u32) -> AgentID {
        AgentID::from_testnet_validator_index(id)
    }

    #[test]
    fn test_compute_relay_plan_builds_first_hop_and_remaining_route() {
        let validators = vec![
            (1u32, "127.0.0.1:9001".parse().unwrap()),
            (2u32, "127.0.0.1:9002".parse().unwrap()),
            (3u32, "127.0.0.1:9003".parse().unwrap()),
        ];

        let plan = compute_relay_plan(
            "127.0.0.1:9001".parse().unwrap(),
            &validators,
            &[testnet_agent_id(2), testnet_agent_id(3)],
            2,
        )
        .unwrap()
        .unwrap();

        assert_eq!(plan.first_hop_id, testnet_agent_id(2));
        assert_eq!(
            plan.first_hop_addr,
            "127.0.0.1:9002".parse::<SocketAddr>().unwrap()
        );
        assert_eq!(
            plan.full_path,
            vec![
                testnet_agent_id(2),
                testnet_agent_id(3),
                testnet_agent_id(1)
            ]
        );
        assert_eq!(
            plan.remaining_route,
            vec![testnet_agent_id(3), testnet_agent_id(1)]
        );
    }

    #[test]
    fn test_compute_relay_plan_rejects_target_in_relay_route() {
        let validators = vec![
            (1u32, "127.0.0.1:9001".parse().unwrap()),
            (2u32, "127.0.0.1:9002".parse().unwrap()),
            (3u32, "127.0.0.1:9003".parse().unwrap()),
        ];

        let err = compute_relay_plan(
            "127.0.0.1:9001".parse().unwrap(),
            &validators,
            &[testnet_agent_id(2), testnet_agent_id(1)],
            2,
        )
        .unwrap_err();

        assert!(err.contains("must not include the final target validator"));
    }

    #[test]
    fn test_compute_relay_plan_rejects_duplicate_validator_ids() {
        let validators = vec![
            (1u32, "127.0.0.1:9001".parse().unwrap()),
            (2u32, "127.0.0.1:9002".parse().unwrap()),
            (2u32, "127.0.0.1:9003".parse().unwrap()),
        ];

        let err = compute_relay_plan(
            "127.0.0.1:9001".parse().unwrap(),
            &validators,
            &[testnet_agent_id(2)],
            1,
        )
        .unwrap_err();

        assert!(err.contains("duplicate validator id 2"));
    }

    #[test]
    fn test_compute_relay_plan_rejects_duplicate_validator_addresses() {
        let validators = vec![
            (1u32, "127.0.0.1:9001".parse().unwrap()),
            (2u32, "127.0.0.1:9002".parse().unwrap()),
            (3u32, "127.0.0.1:9002".parse().unwrap()),
        ];

        let err = compute_relay_plan(
            "127.0.0.1:9001".parse().unwrap(),
            &validators,
            &[testnet_agent_id(2)],
            1,
        )
        .unwrap_err();

        assert!(err.contains("duplicate validator address 127.0.0.1:9002"));
    }
}
