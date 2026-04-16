use tonic::{Request, Response, Status};
use std::sync::Arc;

pub mod ilc_app {
    tonic::include_proto!("ilc_app");
}

use ilc_app::ilc_app_read_service_server::IlcAppReadService;
use ilc_app::{GetBalanceRequest, GetBalanceResponse, GetEpochRequest, GetEpochResponse};
use crate::balance_store::BalanceStore;
use crate::epoch_settlement::EpochStore;
use crate::types::AgentID;

/// The singular external interface allowed for the Python Epistemic layer.
/// Inherently bans writes by omitting any mutation capabilities, strictly decoupling
/// state generation (Python) from state settlement and execution (Rust Mysticti DAG).
pub struct ApplicationInterface {
    balance_store: Arc<BalanceStore>,
    epoch_store: Arc<EpochStore>,
}

impl ApplicationInterface {
    pub fn new(balance_store: Arc<BalanceStore>, epoch_store: Arc<EpochStore>) -> Self {
        Self { balance_store, epoch_store }
    }
}

#[tonic::async_trait]
impl IlcAppReadService for ApplicationInterface {
    async fn get_balance(&self, request: Request<GetBalanceRequest>) -> Result<Response<GetBalanceResponse>, Status> {
        let req = request.into_inner();
        
        let agent_bytes: [u8; 32] = req.agent_id.try_into()
            .map_err(|_| Status::invalid_argument("AgentID must be exactly 32 bytes"))?;
            
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

    async fn get_epoch(&self, _request: Request<GetEpochRequest>) -> Result<Response<GetEpochResponse>, Status> {
        match self.epoch_store.get_current_epoch() {
            Ok(epoch) => Ok(Response::new(GetEpochResponse { current_epoch: epoch })),
            Err(e) => Err(Status::internal(format!("Epoch lookup failed: {:?}", e))),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::tempdir;
    use lmdb_rkv::Environment;
    use crate::types::{AttributionBatch, EpochSeq, CIDv1Root, EpochSettlementRecord, EpochCheckpoint, AggSig};
    use crate::epoch_settlement::EpochSettlementProtocol;
    use blst::min_pk::{AggregateSignature, SecretKey};

    fn setup_env() -> (Arc<Environment>, tempfile::TempDir) {
        let dir = tempdir().unwrap();
        let env = Arc::new(
            Environment::new()
                .set_max_dbs(2)
                .open(dir.path())
                .unwrap()
        );
        (env, dir)
    }

    #[tokio::test]
    async fn test_get_balance_request_valid() {
        let (env, _dir) = setup_env();
        let balance_store = Arc::new(BalanceStore::new(env.clone()).unwrap());
        let epoch_store = Arc::new(EpochStore::new(env.clone()).unwrap());

        let agent_id = AgentID([5; 32]);
        balance_store.apply_attribution(AttributionBatch {
            epoch: EpochSeq(1),
            attributions: vec![(agent_id, 999_000)],
        }).unwrap();

        let app = ApplicationInterface::new(balance_store, epoch_store);

        let req = Request::new(GetBalanceRequest {
            agent_id: vec![5; 32],
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
            agent_id: vec![5; 31], // Intentionally missing 1 byte
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
        
        let sk = SecretKey::key_gen(&[1; 32], &[]).unwrap();
        let sig = sk.sign(b"dummy", b"DST", &[]);
        let agg = AggregateSignature::aggregate(&[&sig], false).unwrap();

        let checkpoint = EpochCheckpoint {
            record: EpochSettlementRecord {
                epoch: EpochSeq(5),
                state_root: CIDv1Root::new([5u8; 36]),
            },
            sigs: AggSig(agg),
        };

        protocol.process_epoch_checkpoint(checkpoint).unwrap();

        // Validate retrieving actual global epoch representation dynamically from LMDB
        let req2 = Request::new(GetEpochRequest {});
        let resp2 = app.get_epoch(req2).await.unwrap().into_inner();
        assert_eq!(resp2.current_epoch, 5); // Successfully returns 5, validating the M-006 integration
    }
}
