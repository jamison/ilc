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

use ilc_consensus::app_interface::ilc_app::{
    ilc_app_proposal_ingress_service_server, ilc_app_read_service_server,
};
use ilc_consensus::app_interface::{ApplicationInterface, ProposalIngressService};
use ilc_consensus::{
    balance_store::BalanceStore,
    config::{load_genesis, load_node_config, SettlementPath},
    epoch_settlement::EpochStore,
    fast_path::FastPathProtocol,
    network::PeerNetwork,
    node::NodeRunner,
    persistent_quic::{load_endpoint_projection_from_path, PersistentQuicSessionManager},
    types::{ILCConsensusError, ValidatorID},
};
use tonic::transport::{Certificate, Identity, ServerTlsConfig};

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

/// Validate the settlement path configuration and emit an operator-visible log.
///
/// Enforces pre-deployment invariants (Phase 825 / Phase 830):
/// - `MysticetiFastPath` requires a non-empty network_id.
/// - `MysticetiFastPath` with f == 0 emits a BFT-safety warning and returns an
///   error: a single-validator set cannot provide Byzantine fault tolerance and
///   must not be used for live ECU settlement without explicit hardening (HIGH-002).
/// - `None` always succeeds (non-activation posture preserved).
///
/// Rollback instruction is included in the `MysticetiFastPath` log so operators
/// always have the recovery path visible at activation time.
///
/// Token: `settlement_path_gate_check_830`
fn check_settlement_path_gate(
    path: &SettlementPath,
    network_id: &str,
    f: usize,
) -> Result<(), ILCConsensusError> {
    match path {
        SettlementPath::None => {
            eprintln!(
                "[settlement_gate] settlement_path=none \
                 — non-activation posture preserved; \
                 no live ECU settlement routing active. \
                 Token: settlement_path_none_posture_preserved"
            );
            Ok(())
        }
        SettlementPath::MysticetiFastPath => {
            if network_id.is_empty() {
                return Err(ILCConsensusError::Other(
                    "settlement_path=mysticeti_fast_path requires a non-empty network_id".into(),
                ));
            }
            if f == 0 {
                eprintln!(
                    "[settlement_gate][sec_warn] settlement_path=mysticeti_fast_path \
                     with f=0 — BFT fault tolerance is zero; \
                     a single validator can finalize transfers. \
                     HIGH-002 hardening is required before independently operated \
                     production validator sets. \
                     Token: sec_warn_settlement_gate_f_zero"
                );
                return Err(ILCConsensusError::Other(
                    "settlement_path=mysticeti_fast_path with f=0 is not permitted; \
                     HIGH-002 hardening required before single-validator live settlement. \
                     Set settlement_path=none or provision a validator set with N >= 4, f >= 1."
                        .into(),
                ));
            }
            eprintln!(
                "[settlement_gate] settlement_path=mysticeti_fast_path ACTIVATED \
                 network_id={} validator_set_f={} \
                 — live ECU submission routing through Mysticeti fast path. \
                 Rollback: set settlement_path=none (or omit field) in node config and restart. \
                 Token: settlement_path_mysticeti_fast_path_activated",
                network_id, f
            );
            Ok(())
        }
    }
}

#[tokio::main]
async fn main() {
    rustls::crypto::ring::default_provider()
        .install_default()
        .ok();

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
    // 1. Load genesis → (ValidatorSet, network_id) in one read.
    // -----------------------------------------------------------------------
    let (validator_set, genesis_network_id) = load_genesis(&genesis_path)?;

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

    let fast_path = Arc::new(FastPathProtocol::new(
        validator_set,
        Arc::clone(&balance_store),
        genesis_network_id.clone(),
    ));
    let f_for_gate = fast_path.validator_set.read().unwrap().f;

    // -----------------------------------------------------------------------
    // 4b. Settlement path gate — validate and emit operator-visible activation log.
    //
    // Design-only pre-deployment work (Phase 825 / Phase 830).
    // Live ECU submission routing is NOT wired here; that requires:
    //   (a) separate human authorization,
    //   (b) first-validator human gate (CDL-017),
    //   (c) a live non-Genesis validator set (f >= 1 before production).
    //
    // This gate enforces the config posture at startup and emits an unambiguous
    // operator log so the activation state is always visible in node output.
    // Rollback: remove or set settlement_path=none in the node config and restart.
    //
    // Token: `settlement_path_gate_check_830`
    // -----------------------------------------------------------------------
    check_settlement_path_gate(&cfg.settlement_path, &genesis_network_id, f_for_gate)?;

    // -----------------------------------------------------------------------
    // 5. Construct PeerNetwork (mTLS QUIC, SEC-006)
    // -----------------------------------------------------------------------
    let network = Arc::new(PeerNetwork::new_server(
        cfg.bind_addr,
        cfg.peer_certs,
        cfg.my_cert_der.clone(),
        cfg.my_key_der.clone(),
    )?);

    eprintln!(
        "[m010_harness] validator_id={} network_id={} listening on {}",
        cfg.validator_id, genesis_network_id, cfg.bind_addr,
    );

    // -----------------------------------------------------------------------
    // 6. Persistent validator signing key (testnet bounds verified via SEC-010 mapping).
    // The key safely tracks from genesis configurations avoiding memory drift structurally.
    // -----------------------------------------------------------------------
    let validator_sk = cfg.validator_sk;
    eprintln!(
        "[m010_harness] validator_id={} signing key persistently activated",
        cfg.validator_id
    );

    // -----------------------------------------------------------------------
    // 7. Build peer address list for outbound connections
    // -----------------------------------------------------------------------
    let mut persistent_sessions: Option<Arc<PersistentQuicSessionManager>> = None;
    let peer_addrs: Vec<(ValidatorID, std::net::SocketAddr)> = match cfg.settlement_path {
        SettlementPath::MysticetiFastPath => {
            let projection_path = cfg.endpoint_projection_path.as_ref().ok_or_else(|| {
                ILCConsensusError::Other(
                    "settlement_path=mysticeti_fast_path requires endpoint_projection_path; \
                     legacy config peers are testnet-only and not valid activation authority"
                        .into(),
                )
            })?;
            let projection = load_endpoint_projection_from_path(projection_path)?;
            let peer_addrs = projection
                .preferred_peer_addrs()
                .into_iter()
                .filter(|(id, _)| *id != ValidatorID(cfg.validator_id))
                .collect();
            persistent_sessions = Some(Arc::new(PersistentQuicSessionManager::new(
                Arc::clone(&network),
                projection,
            )));
            peer_addrs
        }
        SettlementPath::None => cfg
            .peers
            .iter()
            .map(|p| (ValidatorID(p.validator_id), p.addr))
            .collect(),
    };

    let mut runner = NodeRunner::new(
        ValidatorID(cfg.validator_id),
        genesis_network_id,
        f_for_gate,
        validator_sk,
        network,
        fast_path,
        Arc::clone(&balance_store),
        Arc::clone(&epoch_store),
        peer_addrs,
    );
    if let Some(manager) = persistent_sessions {
        runner = runner.with_persistent_sessions(manager);
    }
    runner = runner.with_proposal_ingress_enabled(matches!(
        cfg.settlement_path,
        SettlementPath::MysticetiFastPath
    ));
    let runner = Arc::new(runner);

    // -----------------------------------------------------------------------
    // 8. Optional: gRPC AppReadService + authenticated proposal ingress
    // -----------------------------------------------------------------------
    if let Some(grpc_addr) = cfg.grpc_listen_addr {
        let app_iface =
            ApplicationInterface::new(Arc::clone(&balance_store), Arc::clone(&epoch_store));
        let read_svc = ilc_app_read_service_server::IlcAppReadServiceServer::new(app_iface);
        let proposal_svc =
            ilc_app_proposal_ingress_service_server::IlcAppProposalIngressServiceServer::new(
                ProposalIngressService::new(
                    Arc::clone(&runner),
                    cfg.peer_cert_sha256_fingerprints.clone(),
                ),
            );
        let grpc_tls_identity = Identity::from_pem(cfg.my_cert_pem.clone(), cfg.my_key_pem.clone());
        let peer_ca_pem = cfg.peer_cert_pem_bundle.clone();
        tokio::spawn(async move {
            eprintln!("[m018] TLS gRPC server listening on {}", grpc_addr);
            let tls_config = if peer_ca_pem.is_empty() {
                ServerTlsConfig::new().identity(grpc_tls_identity)
            } else {
                ServerTlsConfig::new()
                    .identity(grpc_tls_identity)
                    .client_ca_root(Certificate::from_pem(peer_ca_pem))
            };
            tonic::transport::Server::builder()
                .tls_config(tls_config)
                .expect("[m018] TLS gRPC server config failed")
                .add_service(read_svc)
                .add_service(proposal_svc)
                .serve(grpc_addr)
                .await
                .expect("[m018] gRPC server failed");
        });
    }

    // -----------------------------------------------------------------------
    // 9. Start node control plane
    // -----------------------------------------------------------------------

    eprintln!(
        "[m010_harness] m010_harness_startup_complete validator_id={}",
        cfg.validator_id
    );

    runner.run().await
}

#[cfg(test)]
mod tests {
    use super::*;
    use ilc_consensus::config::SettlementPath;

    #[test]
    fn test_settlement_gate_none_always_passes() {
        assert!(check_settlement_path_gate(&SettlementPath::None, "ilc-testnet", 0).is_ok());
        assert!(check_settlement_path_gate(&SettlementPath::None, "ilc-testnet", 1).is_ok());
        assert!(check_settlement_path_gate(&SettlementPath::None, "", 0).is_ok());
    }

    #[test]
    fn test_settlement_gate_fast_path_requires_non_empty_network_id() {
        let result = check_settlement_path_gate(&SettlementPath::MysticetiFastPath, "", 1);
        assert!(result.is_err());
        let msg = format!("{:?}", result.unwrap_err());
        assert!(msg.contains("non-empty network_id"), "got: {}", msg);
    }

    #[test]
    fn test_settlement_gate_fast_path_requires_f_ge_1() {
        let result =
            check_settlement_path_gate(&SettlementPath::MysticetiFastPath, "ilc-testnet", 0);
        assert!(result.is_err());
        let msg = format!("{:?}", result.unwrap_err());
        assert!(msg.contains("f=0"), "got: {}", msg);
        assert!(msg.contains("HIGH-002"), "got: {}", msg);
    }

    #[test]
    fn test_settlement_gate_fast_path_passes_with_valid_f() {
        let result =
            check_settlement_path_gate(&SettlementPath::MysticetiFastPath, "ilc-testnet", 1);
        assert!(result.is_ok(), "f=1 should pass: {:?}", result.unwrap_err());
    }

    #[test]
    fn test_settlement_gate_fast_path_passes_with_larger_f() {
        let result =
            check_settlement_path_gate(&SettlementPath::MysticetiFastPath, "ilc-mainnet", 2);
        assert!(result.is_ok());
    }
}
