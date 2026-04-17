/// main.rs — M-010 validator_harness binary entry point.
///
/// Architecture (decided before M-010 execution):
///   - #[tokio::main] async runtime
///   - Orchestration in async fn run() → Result<()>
///   - Config parsing and genesis translation are synchronous helpers (config.rs)
///   - SEC-005: single LMDB environment with set_map_size() from lmdb_balance_map_size_bytes
///   - gRPC optional: started only if grpc_listen_addr is set in config
///
/// Usage:
///   validator_harness --config <path> --genesis <path>
///
/// The binary requires real BLS12-381 G1 public keys in genesis.json validator_key fields.
/// Placeholder test values will be rejected by blst::min_pk::PublicKey::from_bytes.
///
/// `m010_validator_harness_binary_present`
use std::path::PathBuf;
use std::sync::Arc;

use ilc_consensus::{
    balance_store::BalanceStore,
    config::{load_genesis, load_node_config},
    epoch_settlement::EpochStore,
    fast_path::FastPathProtocol,
    network::PeerNetwork,
    node::{generate_ephemeral_validator_sk, NodeRunner},
    types::{ILCConsensusError, ValidatorID},
};

mod args {
    pub struct Args {
        pub config: std::path::PathBuf,
        pub genesis: std::path::PathBuf,
    }

    pub fn parse() -> Result<Args, String> {
        let raw: Vec<String> = std::env::args().collect();
        let mut config: Option<std::path::PathBuf> = None;
        let mut genesis: Option<std::path::PathBuf> = None;

        let mut i = 1;
        while i < raw.len() {
            match raw[i].as_str() {
                "--config" => {
                    i += 1;
                    config = Some(std::path::PathBuf::from(
                        raw.get(i).ok_or("--config requires a path argument")?,
                    ));
                }
                "--genesis" => {
                    i += 1;
                    genesis = Some(std::path::PathBuf::from(
                        raw.get(i).ok_or("--genesis requires a path argument")?,
                    ));
                }
                "--help" | "-h" => {
                    eprintln!("Usage: validator_harness --config <path> --genesis <path>");
                    std::process::exit(0);
                }
                other => {
                    return Err(format!("Unknown argument: {}", other));
                }
            }
            i += 1;
        }

        Ok(Args {
            config: config.ok_or("--config is required")?,
            genesis: genesis.ok_or("--genesis is required")?,
        })
    }
}

#[tokio::main]
async fn main() {
    let args = match args::parse() {
        Ok(a) => a,
        Err(e) => {
            eprintln!("Error: {}", e);
            eprintln!("Usage: validator_harness --config <path> --genesis <path>");
            std::process::exit(1);
        }
    };

    if let Err(e) = run(args.config, args.genesis).await {
        eprintln!("[m010_harness] fatal: {}", e);
        std::process::exit(1);
    }
}

async fn run(config_path: PathBuf, genesis_path: PathBuf) -> Result<(), ILCConsensusError> {
    // -----------------------------------------------------------------------
    // 1. Load genesis → ValidatorSet
    // -----------------------------------------------------------------------
    let validator_set = load_genesis(&genesis_path)?;
    let genesis_network_id = {
        let raw = std::fs::read_to_string(&genesis_path)
            .map_err(|e| ILCConsensusError::Other(format!("Cannot re-read genesis: {}", e)))?;
        let v: serde_json::Value = serde_json::from_str(&raw)
            .map_err(|e| ILCConsensusError::Other(format!("Genesis json error: {}", e)))?;
        v["network_id"]
            .as_str()
            .ok_or_else(|| ILCConsensusError::Other("genesis missing network_id".into()))?
            .to_string()
    };

    // -----------------------------------------------------------------------
    // 2. Load node config — enforces network_id == genesis_network_id
    // -----------------------------------------------------------------------
    let cfg = load_node_config(&config_path, &genesis_network_id)?;

    // -----------------------------------------------------------------------
    // 3. SEC-005: Construct single LMDB environment with explicit map size.
    // One environment-wide set_map_size(), derived from lmdb_balance_map_size_bytes.
    // The epoch store shares this environment; the config's lmdb_epoch_map_size_bytes
    // documents the intended epoch data ceiling but cannot be independently enforced
    // with a shared LMDB environment. This is the SEC-005 M-010 closure decision:
    // one env, one size, both stores. Future: split envs if independent sizing is needed.
    // -----------------------------------------------------------------------
    std::fs::create_dir_all(&cfg.lmdb_path)
        .map_err(|e| ILCConsensusError::Other(format!("Cannot create lmdb_path: {}", e)))?;

    eprintln!(
        "[m010_harness] sec_005_lmdb_env_map_size_bytes={} lmdb_path={}",
        cfg.lmdb_map_size_bytes,
        cfg.lmdb_path.display()
    );

    let lmdb_env = Arc::new(
        lmdb_rkv::Environment::new()
            .set_max_dbs(2)
            .set_map_size(cfg.lmdb_map_size_bytes)
            .open(&cfg.lmdb_path)
            .map_err(|e| ILCConsensusError::Other(format!("LMDB open error: {}", e)))?,
    );

    eprintln!("[m010_harness] m010_sec005_lmdb_env_opened");

    // -----------------------------------------------------------------------
    // 4. Construct stores and protocols
    // -----------------------------------------------------------------------
    let balance_store = Arc::new(BalanceStore::new(Arc::clone(&lmdb_env))?);
    let epoch_store = Arc::new(EpochStore::new(Arc::clone(&lmdb_env))?);

    let validator_set_arc = Arc::new(validator_set);
    let fast_path = Arc::new(FastPathProtocol::new(
        Arc::clone(&validator_set_arc),
        Arc::clone(&balance_store),
        genesis_network_id.clone(),
    ));

    // -----------------------------------------------------------------------
    // 5. Construct PeerNetwork (mTLS QUIC, SEC-006)
    // -----------------------------------------------------------------------
    let network = Arc::new(PeerNetwork::new_server(
        cfg.bind_addr,
        cfg.peer_certs,
        cfg.my_cert_der,
        cfg.my_key_der,
    )?);

    eprintln!(
        "[m010_harness] validator_id={} network_id={} listening on {}",
        cfg.validator_id,
        genesis_network_id,
        cfg.bind_addr,
    );

    // -----------------------------------------------------------------------
    // 6. Ephemeral validator signing key (testnet only).
    // In the actual multi-machine run this must be a persistent, pre-generated key
    // whose public key is registered in genesis.json validator_key.
    // -----------------------------------------------------------------------
    let validator_sk = generate_ephemeral_validator_sk()?;
    eprintln!(
        "[m010_harness] validator_id={} signing key generated (testnet ephemeral)",
        cfg.validator_id
    );

    // -----------------------------------------------------------------------
    // 7. Build peer address list for outbound connections
    // -----------------------------------------------------------------------
    let peer_addrs: Vec<(ValidatorID, std::net::SocketAddr)> = cfg.peers
        .iter()
        .map(|p| (ValidatorID(p.validator_id), p.addr))
        .collect();

    // -----------------------------------------------------------------------
    // 8. Optional: gRPC AppReadService
    // -----------------------------------------------------------------------
    if let Some(grpc_addr) = cfg.grpc_listen_addr {
        eprintln!(
            "[m010_harness] grpc_listen_addr={} — gRPC start is a stub in M-010; skipping",
            grpc_addr
        );
        // gRPC server wiring is a follow-on M-series workload.
        // app_interface.rs provides the service impl; tonic transport wiring is M-011+.
    }

    // -----------------------------------------------------------------------
    // 9. Start node control plane
    // -----------------------------------------------------------------------
    let runner = NodeRunner::new(
        ValidatorID(cfg.validator_id),
        genesis_network_id,
        validator_set_arc.f,
        validator_sk,
        network,
        fast_path,
        balance_store,
        epoch_store,
        peer_addrs,
    );

    eprintln!("[m010_harness] m010_harness_startup_complete validator_id={}", cfg.validator_id);

    runner.run().await
}
