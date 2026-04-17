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
///     --msg broadcast --sender-key <file> --to <96hex> --amount <u64> --version <u64>
///
/// `m011_testnet_client_binary_present`
use std::collections::HashMap;
use std::fs;
use std::net::SocketAddr;
use std::path::PathBuf;

use ilc_consensus::{
    network::{GossipEnvelope, GossipMessage, PeerNetwork},
    types::{AgentID, AgentSig, CIDv1Root, ECUTransfer, EpochSeq, EpochSettlementTx, ObjectRef, ValidatorID, ValidatorSig, TransferCertificate, AGENT_TRANSFER_DST},
};

// ---------------------------------------------------------------------------
// Args
// ---------------------------------------------------------------------------

#[derive(Debug)]
enum MsgType {
    Broadcast,
    EpochSettlement,
    FullTransfer,
}

#[derive(Debug)]
struct Args {
    validator_addr: SocketAddr,
    cert_pem: PathBuf,
    key_pem: PathBuf,
    peer_cert_der: PathBuf,
    /// ValidatorID to claim in GossipEnvelope.peer_id (default 0).
    peer_id: u32,
    msg_type: MsgType,
    // broadcast params
    sender_key_file: Option<PathBuf>,
    to_hex: Option<String>,
    amount_micro_ecu: u64,
    version: u64,
    // epoch_settlement params
    start_epoch: u64,
    count: u64,
    // full_transfer params
    listen_addr: Option<SocketAddr>,
    validators: Vec<(u32, SocketAddr)>,
    validator_certs: Vec<PathBuf>,
    f: usize,
}

fn parse_args() -> Result<Args, String> {
    let raw: Vec<String> = std::env::args().collect();
    let mut validator_addr: Option<SocketAddr> = None;
    let mut cert_pem: Option<PathBuf> = None;
    let mut key_pem: Option<PathBuf> = None;
    let mut peer_cert_der: Option<PathBuf> = None;
    let mut peer_id: u32 = 0;
    let mut msg_type: Option<MsgType> = None;
    let mut sender_key_file: Option<PathBuf> = None;
    let mut to_hex: Option<String> = None;
    let mut amount_micro_ecu: u64 = 1000;
    let mut version: u64 = 0;
    let mut start_epoch: u64 = 0;
    let mut count: u64 = 1;
    let mut listen_addr: Option<SocketAddr> = None;
    let mut validators: Vec<(u32, SocketAddr)> = Vec::new();
    let mut validator_certs: Vec<PathBuf> = Vec::new();
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
                peer_cert_der = Some(PathBuf::from(raw.get(i).ok_or("--peer-cert requires a path")?));
            }
            "--peer-id" => {
                i += 1;
                peer_id = raw.get(i).ok_or("--peer-id requires a number")?
                    .parse().map_err(|e| format!("--peer-id: {}", e))?;
            }
            "--msg" => {
                i += 1;
                msg_type = Some(match raw.get(i).ok_or("--msg requires a type")?.as_str() {
                    "broadcast" => MsgType::Broadcast,
                    "epoch_settlement" => MsgType::EpochSettlement,
                    "full_transfer" => MsgType::FullTransfer,
                    other => return Err(format!("unknown --msg type '{}' (broadcast|epoch_settlement|full_transfer)", other)),
                });
            }
            "--sender-key" => {
                i += 1;
                sender_key_file = Some(PathBuf::from(raw.get(i).ok_or("--sender-key requires a path")?));
            }
            "--to" => {
                i += 1;
                to_hex = Some(raw.get(i).ok_or("--to requires a 96-char hex string")?.clone());
            }
            "--amount" => {
                i += 1;
                amount_micro_ecu = raw.get(i).ok_or("--amount requires a number")?
                    .parse().map_err(|e| format!("--amount: {}", e))?;
            }
            "--version" => {
                i += 1;
                version = raw.get(i).ok_or("--version requires a number")?
                    .parse().map_err(|e| format!("--version: {}", e))?;
            }
            "--epoch" => {
                i += 1;
                start_epoch = raw.get(i).ok_or("--epoch requires a number")?
                    .parse().map_err(|e| format!("--epoch: {}", e))?;
            }
            "--count" => {
                i += 1;
                count = raw.get(i).ok_or("--count requires a number")?
                    .parse().map_err(|e| format!("--count: {}", e))?;
            }
            "--listen-addr" => {
                i += 1;
                let s = raw.get(i).ok_or("--listen-addr requires an addr argument")?;
                listen_addr = Some(s.parse().map_err(|e| format!("--listen-addr: {}", e))?);
            }
            "--f" => {
                i += 1;
                f = raw.get(i).ok_or("--f requires a number")?
                    .parse().map_err(|e| format!("--f: {}", e))?;
            }
            "--validators" => {
                i += 1;
                let list = raw.get(i).ok_or("--validators requires a comma-separated list")?;
                for (idx, addr_str) in list.split(',').enumerate() {
                    let id = (idx + 1) as u32; // Assuming 1-indexed validator IDs dynamically mapping 1,2,3,4
                    let addr = addr_str.parse().map_err(|e| format!("--validators parse '{}': {}", addr_str, e))?;
                    validators.push((id, addr));
                }
            }
            "--validator-certs" => {
                i += 1;
                let list = raw.get(i).ok_or("--validator-certs requires a comma-separated list")?;
                for p in list.split(',') {
                    validator_certs.push(PathBuf::from(p));
                }
            }
            "--help" | "-h" => {
                eprintln!("Usage:");
                eprintln!("  testnet_client --validator <addr> --cert <pem> --key <pem> --peer-cert <der> --msg <broadcast|epoch_settlement>");
                eprintln!("  testnet_client --msg full_transfer --listen-addr <addr> --f <N> --validators <addr,addr..> --validator-certs <der,der..> --sender-key <file> --to <hex> --amount <u64> --version <u64> --cert <pem> --key <pem>");
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
        msg_type: msg_type.ok_or("--msg is required")?,
        sender_key_file,
        to_hex,
        amount_micro_ecu,
        version,
        start_epoch,
        count,
        listen_addr,
        validators,
        validator_certs,
        f,
    })
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------

#[tokio::main]
async fn main() {
    rustls::crypto::ring::default_provider().install_default().ok();

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
        "[testnet_client] connecting to {} (peer_id claim={})",
        args.validator_addr, args.peer_id
    );

    // -----------------------------------------------------------------------
    // 3. Connect
    // -----------------------------------------------------------------------
    let conn = network.endpoint
        .connect(args.validator_addr, "localhost")?
        .await
        .map_err(|e| format!("QUIC connect: {}", e))?;

    eprintln!("[testnet_client] connected");

    // -----------------------------------------------------------------------
    // 4. Send messages
    // -----------------------------------------------------------------------
    match args.msg_type {
        MsgType::EpochSettlement => {
            for i in 0..args.count {
                let epoch = args.start_epoch + i;
                let tx = EpochSettlementTx {
                    epoch: EpochSeq(epoch),
                    state_root: CIDv1Root::new([0u8; 36]), // testnet placeholder
                };
                let envelope = GossipEnvelope {
                    frame_type: 0x00,
                    peer_id: ValidatorID(args.peer_id),
                    payload: GossipMessage::EpochSettlementTx(tx),
                };
                let (send, _recv) = conn.open_bi().await
                    .map_err(|e| format!("open_bi: {}", e))?;
                network.transmit(send, envelope).await
                    .map_err(|e| format!("transmit epoch {}: {}", epoch, e))?;
                eprintln!("[testnet_client] sent EpochSettlementTx epoch={}", epoch);
            }
        }
        MsgType::Broadcast => {
            let sk_file = args.sender_key_file
                .as_ref()
                .ok_or("--sender-key is required for --msg broadcast")?;
            let to_hex = args.to_hex
                .as_ref()
                .ok_or("--to is required for --msg broadcast")?;

            let sender_sk = load_bls_secret_key(sk_file)?;
            let sender_pk = sender_sk.sk_to_pk();
            let sender_agent_id = AgentID(sender_pk.compress());

            let to_bytes = hex_decode_exact(to_hex, 48)
                .map_err(|e| format!("--to: {}", e))?;
            let mut to_arr = [0u8; 48];
            to_arr.copy_from_slice(&to_bytes);
            let to_agent_id = AgentID(to_arr);

            for i in 0..args.count {
                let ver = args.version + i;
                let object_ref = ObjectRef {
                    agent: sender_agent_id,
                    version: ver,
                };

                // Sign per AGENT_TRANSFER_DST (matches handle_broadcast_honest verification)
                let sender_msg = bincode::serialize(&(&object_ref, &to_agent_id, &args.amount_micro_ecu))
                    .map_err(|e| format!("serialize sender_msg: {}", e))?;
                let sig = sender_sk.sign(&sender_msg, AGENT_TRANSFER_DST, &[]);

                let transfer = ECUTransfer {
                    object_ref,
                    to: to_agent_id,
                    amount_micro_ecu: args.amount_micro_ecu,
                    sender_sig: AgentSig(sig),
                };

                let envelope = GossipEnvelope {
                    frame_type: 0x00,
                    peer_id: ValidatorID(args.peer_id),
                    payload: GossipMessage::BroadcastHonest(transfer),
                };

                let (send, _recv) = conn.open_bi().await
                    .map_err(|e| format!("open_bi: {}", e))?;
                network.transmit(send, envelope).await
                    .map_err(|e| format!("transmit broadcast ver {}: {}", ver, e))?;
                eprintln!(
                    "[testnet_client] sent BroadcastHonest agent={} version={}",
                    hex_encode(&sender_agent_id.0), ver
                );
            }
        }
        MsgType::FullTransfer => unreachable!(),
    }

    eprintln!("[testnet_client] done — {} message(s) sent", args.count);
    Ok(())
}

async fn run_full_transfer(args: Args, my_cert_der: Vec<u8>, my_key_der: Vec<u8>) -> Result<(), Box<dyn std::error::Error>> {
    let listen_addr = args.listen_addr.ok_or("--listen-addr is required for full_transfer")?;
    let mut all_validator_cert_map = HashMap::new();
    for (i, p) in args.validator_certs.iter().enumerate() {
        let der = fs::read(p).map_err(|e| format!("read cert {}: {}", p.display(), e))?;
        all_validator_cert_map.insert((i + 1) as u32, der);
    }

    let sk_file = args.sender_key_file.as_ref().ok_or("--sender-key is required for full_transfer")?;
    let to_hex = args.to_hex.as_ref().ok_or("--to is required for full_transfer")?;
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
    ).map_err(|e| format!("new_server: {}", e))?;

    // 3. Build an outbound client endpoint
    let outbound = PeerNetwork::new_client(
        "0.0.0.0:0".parse()?,
        all_validator_cert_map.clone(),
        my_cert_der,
        my_key_der,
    ).map_err(|e| format!("new_client: {}", e))?;

    let object_ref = ObjectRef {
        agent: sender_agent_id,
        version: args.version,
    };

    let sender_msg = bincode::serialize(&(&object_ref, &to_agent_id, &args.amount_micro_ecu))?;
    let sig = sender_sk.sign(&sender_msg, AGENT_TRANSFER_DST, &[]);
    let transfer = ECUTransfer {
        object_ref,
        to: to_agent_id,
        amount_micro_ecu: args.amount_micro_ecu,
        sender_sig: AgentSig(sig),
    };

    let envelope = GossipEnvelope {
        frame_type: 0x00,
        peer_id: ValidatorID(args.peer_id), // e.g. 5
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
    let mut acks: Vec<(ValidatorID, ValidatorSig)> = Vec::new();

    while acks.len() < quorum {
        let incoming = client_server.endpoint.accept().await.ok_or("server endpoint closed")?;
        let conn = incoming.await?;
        let (_, recv) = conn.accept_bi().await?;
        let envelope = client_server.receive(&conn, recv).await?;

        if let GossipMessage::AckFor { object_ref: ack_ref, sig } = envelope.payload {
            if ack_ref == object_ref {
                let from = envelope.peer_id;
                if !acks.iter().any(|(id, _)| *id == from) {
                    acks.push((from, sig));
                    eprintln!("[m012_client] received AckFor from validator {} ({}/{})", from.0, acks.len(), quorum);
                }
            }
        }
    }

    // 6. Assemble TransferCertificate
    let cert = TransferCertificate { transfer, sigs: acks };
    eprintln!("[m012_client] certificate assembled — broadcasting to all validators");

    // 7. Broadcast Certificate
    let cert_envelope = GossipEnvelope {
        frame_type: 0x00,
        peer_id: ValidatorID(args.peer_id),
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
    blst::min_pk::SecretKey::from_bytes(&bytes)
        .map_err(|_| "invalid BLS secret key bytes".into())
}

fn hex_decode_exact(hex: &str, expected_len: usize) -> Result<Vec<u8>, String> {
    if hex.len() != expected_len * 2 {
        return Err(format!(
            "expected {} hex chars ({} bytes), got {}",
            expected_len * 2, expected_len, hex.len()
        ));
    }
    (0..hex.len())
        .step_by(2)
        .map(|i| u8::from_str_radix(&hex[i..i + 2], 16).map_err(|_| format!("invalid hex at offset {}", i)))
        .collect::<Result<Vec<u8>, _>>()
}

fn hex_encode(bytes: &[u8]) -> String {
    bytes.iter().map(|b| format!("{:02x}", b)).collect()
}

/// Read a PEM file and extract the DER bytes of the first block.
/// Handles CERTIFICATE and PRIVATE KEY PEM blocks.
fn load_pem_as_der(path: &PathBuf) -> Result<Vec<u8>, String> {
    let pem_str = fs::read_to_string(path)
        .map_err(|e| format!("cannot read '{}': {}", path.display(), e))?;

    let start_marker = "-----BEGIN ";
    let end_marker = "-----END ";
    let start = pem_str.find(start_marker)
        .ok_or_else(|| format!("no PEM BEGIN marker in '{}'", path.display()))?;
    let header_end = pem_str[start..].find('\n')
        .ok_or_else(|| format!("malformed PEM in '{}'", path.display()))?;
    let end = pem_str.find(end_marker)
        .ok_or_else(|| format!("no PEM END marker in '{}'", path.display()))?;

    let b64_body = pem_str[start + header_end + 1..end].replace('\n', "").replace('\r', "");
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
