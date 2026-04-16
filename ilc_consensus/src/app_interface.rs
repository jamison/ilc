use tonic::{Request, Response, Status};
use std::sync::Arc;

pub mod ilc_app {
    tonic::include_proto!("ilc_app");
}

use ilc_app::ilc_app_read_service_server::IlcAppReadService;
use ilc_app::{GetBalanceRequest, GetBalanceResponse, GetEpochRequest, GetEpochResponse};
use crate::balance_store::BalanceStore;
use crate::types::AgentID;

/// The singular external interface allowed for the Python Epistemic layer.
/// Inherently bans writes by omitting any mutation capabilities, strictly decoupling
/// state generation (Python) from state settlement and execution (Rust Mysticti DAG).
pub struct ApplicationInterface {
    balance_store: Arc<BalanceStore>,
}

impl ApplicationInterface {
    pub fn new(balance_store: Arc<BalanceStore>) -> Self {
        Self { balance_store }
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
        // Global epoch mapping.
        // Return 0 as M-006's Shared-Object Epoch Path is not yet instantiated.
        Ok(Response::new(GetEpochResponse {
            current_epoch: 0,
        }))
    }
}
