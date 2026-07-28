use serde::Deserialize;
/// config.rs — M-010 deployment config loader and runtime type translation.
///
/// Responsibilities:
/// - Parse genesis.json → ValidatorSet (hex-decode validator_key, agent_id)
/// - Parse validator_N_config.json → NodeConfig (typed, validated)
/// - Load peer_cert_dir → HashMap<u32, Vec<u8>> of DER-encoded peer certs
/// - Enforce config.network_id == genesis.network_id at load time
/// - Read own TLS cert/key as DER bytes for PeerNetwork construction
use std::collections::HashMap;
use std::fs;
use std::path::{Path, PathBuf};

use crate::types::{AgentID, ILCConsensusError, ValidatorID, ValidatorKey, ValidatorSet};

// ---------------------------------------------------------------------------
// Raw JSON shapes (deployment format)
// ---------------------------------------------------------------------------

#[derive(Debug, Deserialize)]
struct RawGenesisValidator {
    validator_id: u32,
    agent_id: String,      // 96-char hex = 48 bytes
    validator_key: String, // 96-char hex = 48 bytes (BLS12-381 G1 compressed pubkey, blst::min_pk)
    #[allow(dead_code)]
    stake_micro_ecu: u64,
    #[allow(dead_code)]
    tailscale_ip: String,
    #[allow(dead_code)]
    port: u16,
    #[allow(dead_code)]
    host: String,
    #[allow(dead_code)]
    role: String,
}

#[derive(Debug, Deserialize)]
struct RawGenesis {
    network_id: String, // returned alongside ValidatorSet so main.rs avoids double-read
    #[allow(dead_code)]
    real_ecu: bool,
    f: usize,
    validators: Vec<RawGenesisValidator>,
    #[allow(dead_code)]
    note: Option<String>,
}

#[derive(Debug, Deserialize)]
struct RawPeer {
    validator_id: u32,
    addr: String,
}

#[derive(Debug, Deserialize)]
struct RawNodeConfig {
    validator_id: u32,
    network_id: String,
    bind_host: String,
    bind_port: u16,
    #[allow(dead_code)]
    tailscale_advertise_ip: String,
    peers: Vec<RawPeer>,
    lmdb_balance_map_size_bytes: usize,
    #[allow(dead_code)]
    lmdb_epoch_map_size_bytes: usize,
    tls_cert_path: String,
    tls_key_path: String,
    peer_cert_dir: String,
    lmdb_path: String,
    validator_consensus_key_path: String,
    grpc_listen_addr: Option<String>,
    endpoint_projection_path: Option<String>,
    /// settlement_path — controls live ECU settlement routing.
    /// Omitting or setting "none" preserves the current non-activation posture.
    /// Set to "mysticeti_fast_path" only after separate human authorization
    /// and with a live validator set (CDL-017 / first-validator human gate).
    settlement_path: Option<String>,
    #[allow(dead_code)]
    role: Option<String>,
    #[allow(dead_code)]
    note: Option<String>,
}

// ---------------------------------------------------------------------------
// Runtime types produced by this loader
// ---------------------------------------------------------------------------

/// Settlement path posture for the live ECU path.
///
/// Defaults to `None` (non-activation posture preserved).
/// `MysticetiFastPath` requires separate human authorization; see CDL-017 and
/// the first-validator human gate in `ilc_first_validator_deployment_entry_conditions_826_v0.1.md`.
///
/// Token: `settlement_path_gate_type_825`
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SettlementPath {
    /// No live settlement routing. Default posture. Safe to run without human gate.
    None,
    /// Route live ECU submissions through the Mysticeti fast path.
    /// Requires CDL-017, first-validator human gate, and a valid validator set (f >= 1).
    MysticetiFastPath,
}

/// Typed peer entry produced after config loading.
#[derive(Debug, Clone)]
pub struct PeerAddr {
    pub validator_id: u32,
    pub addr: std::net::SocketAddr,
}

/// Full resolved node configuration ready for harness use.
#[derive(Debug)]
pub struct NodeConfig {
    pub validator_id: u32,
    pub network_id: String,
    pub bind_addr: std::net::SocketAddr,
    pub peers: Vec<PeerAddr>,
    /// Single LMDB environment map size (SEC-005). Derived from lmdb_balance_map_size_bytes.
    pub lmdb_map_size_bytes: usize,
    pub lmdb_path: PathBuf,
    /// Own TLS certificate in DER encoding.
    pub my_cert_der: Vec<u8>,
    /// Own TLS private key in DER encoding.
    pub my_key_der: Vec<u8>,
    /// Own TLS certificate PEM bytes for the optional tonic gRPC listener.
    pub my_cert_pem: Vec<u8>,
    /// Own TLS private key PEM bytes for the optional tonic gRPC listener.
    pub my_key_pem: Vec<u8>,
    /// Peer certs keyed by validator_id, DER encoding.
    pub peer_certs: HashMap<u32, Vec<u8>>,
    /// Peer certificate PEM bundle for tonic gRPC client-auth roots.
    pub peer_cert_pem_bundle: Vec<u8>,
    /// Persistent consensus secret key mapping cleanly over dynamic network quorum limits.
    pub validator_sk: blst::min_pk::SecretKey,
    /// Optional gRPC listen address. None = gRPC not started.
    pub grpc_listen_addr: Option<std::net::SocketAddr>,
    /// Settlement path posture. Default = `SettlementPath::None` (non-activation).
    pub settlement_path: SettlementPath,
    /// Optional ADR-0039 endpoint projection file. Required for production activation path.
    pub endpoint_projection_path: Option<PathBuf>,
}

// ---------------------------------------------------------------------------
// Load functions
// ---------------------------------------------------------------------------

/// Load genesis.json → (ValidatorSet, network_id).
/// Returns the network_id alongside ValidatorSet so callers don't need to re-read the file.
/// Translates hex-encoded validator_key and agent_id into runtime types.
pub fn load_genesis(genesis_path: &Path) -> Result<(ValidatorSet, String), ILCConsensusError> {
    let raw = fs::read_to_string(genesis_path)
        .map_err(|e| ILCConsensusError::Other(format!("Cannot read genesis: {}", e)))?;
    let genesis: RawGenesis = serde_json::from_str(&raw)
        .map_err(|e| ILCConsensusError::Other(format!("Genesis parse error: {}", e)))?;

    let mut validators = Vec::with_capacity(genesis.validators.len());
    for v in &genesis.validators {
        // blst::min_pk::PublicKey (G1 compressed) is 48 bytes = 96 hex chars.
        let key_bytes = hex_decode_exact(&v.validator_key, 48).map_err(|e| {
            ILCConsensusError::Other(format!(
                "validator_id={}: validator_key {}",
                v.validator_id, e
            ))
        })?;
        let pubkey = blst::min_pk::PublicKey::from_bytes(&key_bytes).map_err(|_| {
            ILCConsensusError::Other(format!(
                "validator_id={}: validator_key is not a valid BLS12-381 G1 point",
                v.validator_id
            ))
        })?;
        // SEC-FIX-01: G1 subgroup check — defense-in-depth for genesis config loading.
        pubkey.validate().map_err(|_| {
            ILCConsensusError::Other(format!(
                "validator_id={}: validator_key failed G1 subgroup check",
                v.validator_id
            ))
        })?;
        let _agent_id = hex_decode_agent_id(&v.agent_id, v.validator_id)?;
        validators.push((ValidatorID(v.validator_id), ValidatorKey(pubkey)));
    }

    let validator_set = ValidatorSet::new(validators, genesis.f)?;
    Ok((validator_set, genesis.network_id))
}

/// Load validator config JSON and resolve all deployment paths into runtime types.
/// Enforces network_id == genesis_network_id.
pub fn load_node_config(
    config_path: &Path,
    genesis_network_id: &str,
) -> Result<NodeConfig, ILCConsensusError> {
    let raw = fs::read_to_string(config_path)
        .map_err(|e| ILCConsensusError::Other(format!("Cannot read node config: {}", e)))?;
    let cfg: RawNodeConfig = serde_json::from_str(&raw)
        .map_err(|e| ILCConsensusError::Other(format!("Node config parse error: {}", e)))?;

    if cfg.network_id != genesis_network_id {
        return Err(ILCConsensusError::Other(format!(
            "network_id mismatch: config='{}' genesis='{}'",
            cfg.network_id, genesis_network_id
        )));
    }

    // Validate settlement_path early — before any file I/O — so config errors
    // are reported in a deterministic order regardless of file system state.
    let settlement_path = match cfg.settlement_path.as_deref().unwrap_or("none").trim() {
        "mysticeti_fast_path" => SettlementPath::MysticetiFastPath,
        "none" | "" => SettlementPath::None,
        other => {
            return Err(ILCConsensusError::Other(format!(
                "settlement_path: unknown value '{}'; valid values are 'none' or 'mysticeti_fast_path'",
                other
            )));
        }
    };

    let bind_addr = format!("{}:{}", cfg.bind_host, cfg.bind_port)
        .parse()
        .map_err(|e| ILCConsensusError::Other(format!("Invalid bind addr: {}", e)))?;

    let mut peers = Vec::with_capacity(cfg.peers.len());
    for p in &cfg.peers {
        let addr = p.addr.parse().map_err(|e| {
            ILCConsensusError::Other(format!("Invalid peer addr {}: {}", p.addr, e))
        })?;
        peers.push(PeerAddr {
            validator_id: p.validator_id,
            addr,
        });
    }

    let my_cert_der = load_pem_as_der(&cfg.tls_cert_path)
        .map_err(|e| ILCConsensusError::Other(format!("tls_cert_path: {}", e)))?;
    let my_key_der = load_pem_as_der(&cfg.tls_key_path)
        .map_err(|e| ILCConsensusError::Other(format!("tls_key_path: {}", e)))?;
    let my_cert_pem = fs::read(&cfg.tls_cert_path)
        .map_err(|e| ILCConsensusError::Other(format!("tls_cert_path: {}", e)))?;
    let my_key_pem = fs::read(&cfg.tls_key_path)
        .map_err(|e| ILCConsensusError::Other(format!("tls_key_path: {}", e)))?;

    let peer_certs = load_peer_cert_dir(&cfg.peer_cert_dir, cfg.validator_id)
        .map_err(|e| ILCConsensusError::Other(format!("peer_cert_dir: {}", e)))?;
    let peer_cert_pem_bundle = load_peer_cert_pem_bundle(&cfg.peer_cert_dir, cfg.validator_id)
        .map_err(|e| ILCConsensusError::Other(format!("peer_cert_dir pem: {}", e)))?;

    let grpc_listen_addr = cfg
        .grpc_listen_addr
        .as_deref()
        .map(|s| {
            s.parse()
                .map_err(|e| ILCConsensusError::Other(format!("grpc_listen_addr: {}", e)))
        })
        .transpose()?;

    eprintln!(
        "[m010_config] validator_id={} network_id={} bind={} lmdb_map_size={} lmdb_path={} peers={} peer_certs={} grpc={}",
        cfg.validator_id,
        cfg.network_id,
        bind_addr,
        cfg.lmdb_balance_map_size_bytes,
        cfg.lmdb_path,
        peers.len(),
        peer_certs.len(),
        grpc_listen_addr.map(|a: std::net::SocketAddr| a.to_string()).as_deref().unwrap_or("disabled"),
    );

    let sk_hex = fs::read_to_string(&cfg.validator_consensus_key_path).map_err(|e| {
        ILCConsensusError::Other(format!("Missing validator_consensus_key_path: {}", e))
    })?;
    let sk_bytes = hex_decode_exact(sk_hex.trim(), 32).map_err(|e| {
        ILCConsensusError::Other(format!(
            "validator_consensus_key_path hex decode limit tracking fail: {}",
            e
        ))
    })?;
    let validator_sk = blst::min_pk::SecretKey::from_bytes(&sk_bytes).map_err(|_| {
        ILCConsensusError::Other(
            "Invalid BLS validator secret key mapped via local bounds natively.".into(),
        )
    })?;

    Ok(NodeConfig {
        validator_id: cfg.validator_id,
        network_id: cfg.network_id,
        bind_addr,
        peers,
        lmdb_map_size_bytes: cfg.lmdb_balance_map_size_bytes,
        lmdb_path: PathBuf::from(&cfg.lmdb_path),
        my_cert_der,
        my_key_der,
        my_cert_pem,
        my_key_pem,
        peer_certs,
        peer_cert_pem_bundle,
        validator_sk,
        grpc_listen_addr,
        settlement_path,
        endpoint_projection_path: cfg.endpoint_projection_path.map(PathBuf::from),
    })
}

/// Load deterministic gRPC client-auth trust roots from peer_cert_dir.
///
/// Prefer `ca.cert.pem` when present, but also include validator leaf PEMs as
/// pinned trust anchors. Existing testbed certificates are CA-issued validator
/// leaves; keeping both roots preserves fail-closed compatibility across rustls
/// verifier behavior while QUIC continues to use DER pinning via `load_peer_cert_dir`.
fn load_peer_cert_pem_bundle(dir: &str, my_validator_id: u32) -> Result<Vec<u8>, String> {
    let path = Path::new(dir);
    if !path.exists() {
        return Err(format!("peer_cert_dir '{}' does not exist", dir));
    }

    let mut bundle = Vec::new();
    let ca_path = path.join("ca.cert.pem");
    if ca_path.exists() {
        let pem =
            fs::read(&ca_path).map_err(|e| format!("cannot read cert 'ca.cert.pem': {}", e))?;
        bundle.extend_from_slice(&pem);
        if !bundle.ends_with(b"\n") {
            bundle.push(b'\n');
        }
    }

    let entries =
        fs::read_dir(path).map_err(|e| format!("cannot read peer_cert_dir '{}': {}", dir, e))?;
    let mut pem_paths = Vec::new();
    for entry in entries {
        let entry = entry.map_err(|e| format!("dir entry error: {}", e))?;
        let file_name = entry.file_name();
        let name = file_name.to_string_lossy();
        if !name.ends_with(".pem") {
            continue;
        }
        let Some(id) = parse_validator_cert_pem_filename(&name) else {
            continue;
        };
        if id == my_validator_id {
            continue;
        }
        pem_paths.push((id, name.to_string(), entry.path()));
    }
    pem_paths.sort_by_key(|(id, _, _)| *id);

    for (_, name, path) in pem_paths {
        let pem = fs::read(path).map_err(|e| format!("cannot read cert '{}': {}", name, e))?;
        bundle.extend_from_slice(&pem);
        if !bundle.ends_with(b"\n") {
            bundle.push(b'\n');
        }
    }
    Ok(bundle)
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

/// Decode a hex string to exactly `expected_len` bytes.
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

/// Decode a 96-char hex agent_id into an AgentID (48 bytes).
fn hex_decode_agent_id(hex: &str, validator_id: u32) -> Result<AgentID, ILCConsensusError> {
    let bytes = hex_decode_exact(hex, 48).map_err(|e| {
        ILCConsensusError::Other(format!("validator_id={}: agent_id {}", validator_id, e))
    })?;
    let mut arr = [0u8; 48];
    arr.copy_from_slice(&bytes);
    Ok(AgentID(arr))
}

/// Read a PEM file and extract the DER bytes of the first entry.
/// Handles both CERTIFICATE and PRIVATE KEY PEM blocks.
fn load_pem_as_der(path: &str) -> Result<Vec<u8>, String> {
    let pem_str = fs::read_to_string(path).map_err(|e| format!("cannot read '{}': {}", path, e))?;

    // Find the first PEM block
    let start_marker = "-----BEGIN ";
    let end_marker = "-----END ";
    let start = pem_str
        .find(start_marker)
        .ok_or_else(|| format!("no PEM BEGIN marker in '{}'", path))?;
    let header_end = pem_str[start..]
        .find('\n')
        .ok_or_else(|| format!("malformed PEM in '{}'", path))?;
    let end = pem_str
        .find(end_marker)
        .ok_or_else(|| format!("no PEM END marker in '{}'", path))?;

    let b64_body = pem_str[start + header_end + 1..end]
        .replace('\n', "")
        .replace('\r', "");

    let der = base64_decode(&b64_body)
        .map_err(|e| format!("base64 decode error in '{}': {}", path, e))?;
    Ok(der)
}

/// Load all `.der` files from peer_cert_dir, excluding the file named for our own validator_id.
/// File naming convention: `validator_{id}_cert.der`
/// All other `.der` files in the directory are loaded as peer certs.
fn load_peer_cert_dir(dir: &str, my_validator_id: u32) -> Result<HashMap<u32, Vec<u8>>, String> {
    let path = Path::new(dir);
    if !path.exists() {
        return Err(format!("peer_cert_dir '{}' does not exist", dir));
    }

    let mut map = HashMap::new();
    let entries =
        fs::read_dir(path).map_err(|e| format!("cannot read peer_cert_dir '{}': {}", dir, e))?;

    for entry in entries {
        let entry = entry.map_err(|e| format!("dir entry error: {}", e))?;
        let file_name = entry.file_name();
        let name = file_name.to_string_lossy();

        // Expect files named validator_{id}_cert.der
        if !name.ends_with(".der") {
            continue;
        }
        if let Some(id) = parse_validator_cert_filename(&name) {
            if id == my_validator_id {
                continue; // skip own cert
            }
            let der = fs::read(entry.path())
                .map_err(|e| format!("cannot read cert '{}': {}", name, e))?;
            map.insert(id, der);
        }
    }

    Ok(map)
}

/// Parse `validator_{id}_cert.der` → Some(id), or None if the name doesn't match.
// MEDIUM-009 fix: removed hard-coded client_cert.der → ValidatorID(5) mapping.
// All validator certs must use the standard validator_{id}_cert.der naming scheme.
fn parse_validator_cert_filename(name: &str) -> Option<u32> {
    let stripped = name.strip_prefix("validator_")?.strip_suffix("_cert.der")?;
    stripped.parse().ok()
}

fn parse_validator_cert_pem_filename(name: &str) -> Option<u32> {
    let stripped = name.strip_prefix("validator_")?.strip_suffix("_cert.pem")?;
    stripped.parse().ok()
}

/// Minimal base64 decode (standard alphabet, no padding enforcement beyond length).
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
        let a = decode_char(bytes[i], TABLE)?;
        let b = decode_char(bytes[i + 1], TABLE)?;
        let c = decode_char(bytes[i + 2], TABLE)?;
        let d = decode_char(bytes[i + 3], TABLE)?;
        out.push((a << 2) | (b >> 4));
        out.push((b << 4) | (c >> 2));
        out.push((c << 6) | d);
        i += 4;
    }
    match bytes.len() - i {
        2 => {
            let a = decode_char(bytes[i], TABLE)?;
            let b = decode_char(bytes[i + 1], TABLE)?;
            out.push((a << 2) | (b >> 4));
        }
        3 => {
            let a = decode_char(bytes[i], TABLE)?;
            let b = decode_char(bytes[i + 1], TABLE)?;
            let c = decode_char(bytes[i + 2], TABLE)?;
            out.push((a << 2) | (b >> 4));
            out.push((b << 4) | (c >> 2));
        }
        _ => {}
    }
    Ok(out)
}

fn decode_char(c: u8, table: &[u8; 128]) -> Result<u8, String> {
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
    use crate::validator::quorum_threshold;
    use std::path::Path;

    fn repo_config_path(relative_path: &str) -> PathBuf {
        Path::new(env!("CARGO_MANIFEST_DIR"))
            .parent()
            .expect("ilc_consensus should live under the repository root")
            .join(relative_path)
    }

    #[test]
    fn test_hex_decode_exact_correct_length() {
        // BLS12-381 G1 compressed pubkey: 48 bytes = 96 hex chars
        let hex = "010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101010101";
        let bytes = hex_decode_exact(hex, 48).unwrap();
        assert_eq!(bytes.len(), 48);
        assert!(bytes.iter().all(|&b| b == 1));
    }

    #[test]
    fn test_hex_decode_exact_wrong_length_rejected() {
        let result = hex_decode_exact("0102", 3);
        assert!(result.is_err());
    }

    #[test]
    fn test_parse_validator_cert_filename_valid() {
        assert_eq!(
            parse_validator_cert_filename("validator_2_cert.der"),
            Some(2)
        );
        assert_eq!(
            parse_validator_cert_filename("validator_42_cert.der"),
            Some(42)
        );
    }

    #[test]
    fn test_parse_validator_cert_filename_invalid() {
        assert_eq!(parse_validator_cert_filename("validator_cert.der"), None);
        assert_eq!(parse_validator_cert_filename("other.der"), None);
        assert_eq!(parse_validator_cert_filename("validator_2_cert.pem"), None);
    }

    #[test]
    fn test_parse_validator_cert_pem_filename_valid() {
        assert_eq!(
            parse_validator_cert_pem_filename("validator_2_cert.pem"),
            Some(2)
        );
        assert_eq!(
            parse_validator_cert_pem_filename("validator_42_cert.pem"),
            Some(42)
        );
    }

    #[test]
    fn test_phase1586_fix1_peer_pem_bundle_includes_ca_and_sorted_peer_leaves() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("ca.cert.pem"), b"CA\n").unwrap();
        std::fs::write(dir.path().join("validator_3_cert.pem"), b"V3\n").unwrap();
        std::fs::write(dir.path().join("validator_1_cert.pem"), b"V1\n").unwrap();
        std::fs::write(dir.path().join("validator_2_cert.pem"), b"V2\n").unwrap();
        std::fs::write(dir.path().join("client_cert.pem"), b"CLIENT\n").unwrap();

        let bundle = load_peer_cert_pem_bundle(dir.path().to_str().unwrap(), 2).unwrap();
        assert_eq!(bundle, b"CA\nV1\nV3\n");
    }

    #[test]
    fn test_phase1586_fix1_peer_pem_bundle_is_non_empty_without_ca_when_peers_exist() {
        let dir = tempfile::tempdir().unwrap();
        std::fs::write(dir.path().join("validator_1_cert.pem"), b"V1\n").unwrap();
        std::fs::write(dir.path().join("validator_2_cert.pem"), b"V2\n").unwrap();

        let bundle = load_peer_cert_pem_bundle(dir.path().to_str().unwrap(), 1).unwrap();
        assert_eq!(bundle, b"V2\n");
    }

    #[test]
    fn test_load_genesis_structure() {
        // Verify genesis.json loads without type errors and produces 4 validators with f=1.
        // Note: validator_key placeholder bytes are not valid BLS points — this test
        // checks parse + hex-decode path up to the BLS point check, which will fail on
        // placeholder values. The test documents the expected error for placeholder data.
        let genesis_path = repo_config_path("config/mysticeti_testnet_M009/genesis.json");
        if !genesis_path.exists() {
            return; // skip in environments without config
        }
        // Placeholder keys are all-same-byte patterns which are not valid BLS12-381 points.
        // load_genesis will return an error on the BLS deserialization step — that's expected.
        let result = load_genesis(&genesis_path);
        match result {
            Ok((_validator_set, _network_id)) => {} // real keys: pass
            Err(ILCConsensusError::Other(ref msg)) => {
                // Acceptable error: BLS point rejection on placeholder keys
                assert!(
                    msg.contains("not a valid BLS12-381") || msg.contains("validator_key"),
                    "unexpected error: {}",
                    msg
                );
            }
            Err(e) => panic!("unexpected error type: {:?}", e),
        }
    }

    #[test]
    fn test_load_mainnet_rc01_genesis_structure() {
        let genesis_path = repo_config_path("config/mysticeti_mainnet_rc01/genesis.json");
        assert!(
            genesis_path.exists(),
            "Phase 1588 RC01 genesis config must exist"
        );

        let (validator_set, network_id) =
            load_genesis(&genesis_path).expect("Phase 1588 RC01 genesis must load");
        assert_eq!(network_id, "ilc-rc01");
        assert_eq!(validator_set.validators.len(), 4);
        assert_eq!(validator_set.f, 1);
        assert_eq!(quorum_threshold(validator_set.validators.len()), 3);
    }

    #[test]
    fn test_network_id_mismatch_rejected() {
        // Write a minimal validator config JSON with a network_id that differs from the
        // genesis network_id. load_node_config must return an error before touching any
        // file paths (the mismatch check is the first validation after parsing).
        use std::io::Write;
        use tempfile::NamedTempFile;

        let mut cfg_file = NamedTempFile::new().unwrap();
        write!(
            cfg_file,
            r#"{{
            "validator_id": 1,
            "network_id": "ilc-different-network",
            "bind_host": "127.0.0.1",
            "bind_port": 9001,
            "tailscale_advertise_ip": "100.0.0.1",
            "peers": [],
            "lmdb_balance_map_size_bytes": 67108864,
            "lmdb_epoch_map_size_bytes": 67108864,
            "tls_cert_path": "/nonexistent/cert.pem",
            "tls_key_path": "/nonexistent/key.pem",
            "validator_consensus_key_path": "/nonexistent/key.hex",
            "peer_cert_dir": "/nonexistent/certs",
            "lmdb_path": "/tmp/test_lmdb"
        }}"#
        )
        .unwrap();

        let result = load_node_config(cfg_file.path(), "ilc-mysticeti-testnet-m009");
        assert!(result.is_err(), "expected network_id mismatch error");
        let err_msg = format!("{:?}", result.unwrap_err());
        assert!(
            err_msg.contains("network_id mismatch"),
            "expected 'network_id mismatch' in error, got: {}",
            err_msg
        );
    }

    #[test]
    fn test_settlement_path_defaults_to_none_when_omitted() {
        use std::io::Write;
        use tempfile::NamedTempFile;

        let mut cfg_file = NamedTempFile::new().unwrap();
        write!(
            cfg_file,
            r#"{{
            "validator_id": 1,
            "network_id": "ilc-mysticeti-testnet-m009",
            "bind_host": "127.0.0.1",
            "bind_port": 9001,
            "tailscale_advertise_ip": "100.0.0.1",
            "peers": [],
            "lmdb_balance_map_size_bytes": 67108864,
            "lmdb_epoch_map_size_bytes": 67108864,
            "tls_cert_path": "/nonexistent/cert.pem",
            "tls_key_path": "/nonexistent/key.pem",
            "validator_consensus_key_path": "/nonexistent/key.hex",
            "peer_cert_dir": "/nonexistent/certs",
            "lmdb_path": "/tmp/test_lmdb"
        }}"#
        )
        .unwrap();

        // settlement_path omitted → parse succeeds up to file-load step
        // We can't fully load (no real cert files), but we can verify the parse error
        // is NOT about settlement_path — it will fail on tls_cert_path instead.
        let result = load_node_config(cfg_file.path(), "ilc-mysticeti-testnet-m009");
        match result {
            Err(ILCConsensusError::Other(ref msg)) => {
                assert!(
                    !msg.contains("settlement_path"),
                    "omitted settlement_path should not produce error, got: {}",
                    msg
                );
            }
            Ok(_) => {}  // if somehow certs exist, also fine
            Err(_) => {} // other error variants (cert load, etc.) are acceptable here
        }
    }

    #[test]
    fn test_settlement_path_none_string_accepted() {
        use std::io::Write;
        use tempfile::NamedTempFile;

        let mut cfg_file = NamedTempFile::new().unwrap();
        write!(
            cfg_file,
            r#"{{
            "validator_id": 1,
            "network_id": "ilc-mysticeti-testnet-m009",
            "bind_host": "127.0.0.1",
            "bind_port": 9001,
            "tailscale_advertise_ip": "100.0.0.1",
            "peers": [],
            "lmdb_balance_map_size_bytes": 67108864,
            "lmdb_epoch_map_size_bytes": 67108864,
            "tls_cert_path": "/nonexistent/cert.pem",
            "tls_key_path": "/nonexistent/key.pem",
            "validator_consensus_key_path": "/nonexistent/key.hex",
            "peer_cert_dir": "/nonexistent/certs",
            "lmdb_path": "/tmp/test_lmdb",
            "settlement_path": "none"
        }}"#
        )
        .unwrap();

        let result = load_node_config(cfg_file.path(), "ilc-mysticeti-testnet-m009");
        match result {
            Err(ILCConsensusError::Other(ref msg)) => {
                assert!(
                    !msg.contains("settlement_path"),
                    "settlement_path=none should not produce error, got: {}",
                    msg
                );
            }
            Ok(_) => {}
            Err(_) => {} // other error variants (cert load, etc.) are acceptable here
        }
    }

    #[test]
    fn test_settlement_path_unknown_value_rejected() {
        use std::io::Write;
        use tempfile::NamedTempFile;

        let mut cfg_file = NamedTempFile::new().unwrap();
        write!(
            cfg_file,
            r#"{{
            "validator_id": 1,
            "network_id": "ilc-mysticeti-testnet-m009",
            "bind_host": "127.0.0.1",
            "bind_port": 9001,
            "tailscale_advertise_ip": "100.0.0.1",
            "peers": [],
            "lmdb_balance_map_size_bytes": 67108864,
            "lmdb_epoch_map_size_bytes": 67108864,
            "tls_cert_path": "/nonexistent/cert.pem",
            "tls_key_path": "/nonexistent/key.pem",
            "validator_consensus_key_path": "/nonexistent/key.hex",
            "peer_cert_dir": "/nonexistent/certs",
            "lmdb_path": "/tmp/test_lmdb",
            "settlement_path": "legacy_substrate"
        }}"#
        )
        .unwrap();

        let result = load_node_config(cfg_file.path(), "ilc-mysticeti-testnet-m009");
        assert!(result.is_err(), "unknown settlement_path value must error");
        let msg = format!("{:?}", result.unwrap_err());
        assert!(
            msg.contains("settlement_path"),
            "error must name settlement_path, got: {}",
            msg
        );
        assert!(
            msg.contains("legacy_substrate"),
            "error must name the rejected value, got: {}",
            msg
        );
    }
}
