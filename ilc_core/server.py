from fastapi import APIRouter, FastAPI, HTTPException, Request
import logging
from contextlib import asynccontextmanager
from pathlib import Path
import tempfile
from pydantic import BaseModel
from .graph import EpistemicGraph
from .consensus.engine import ConsensusEngine
from .agent import EveAgent
from .types import Node
from .network.peer import PeerManager
from .config import load_governance_config
from .logging_config import configure_logging
from .exceptions import GossipValidationError
from fastapi.responses import JSONResponse
from typing import List, Optional
from ilc_core.economics.outcome import TaskOutcome
from ilc_core.protocol.schema import load_protocol_schema
from ilc_core.protocol.mapper import (
    node_to_protocol_claim,
    node_to_protocol_refute,
    outcome_to_protocol_task_outcome,
)
from ilc_core.genesis.work_task import EpistemicWorkTask, ep_task_to_json
from ilc_core.genesis.schema import load_epistemic_work_task_schema
from ilc_core.protocol.public_init_admission_runtime import (
    PublicInitAdmissionRuntimeError,
    issue_public_init_admission_receipt,
)
from ilc_core.protocol.public_receipt_runtime import (
    PublicReceiptRuntimeError,
    issue_public_receipt,
    query_public_receipts,
)
from ilc_core.storage.lmdb_public_runtime import LmdbAdmissionStore, LmdbWalletStore
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.work.task_queue import TaskDescriptor

configure_logging()
logger = logging.getLogger(__name__)


def _init_runtime_state(app_obj: FastAPI) -> None:
    """Initialize runtime state in app.state."""
    graph = EpistemicGraph()
    graph.load_genesis()
    cfg = load_governance_config()
    consensus = ConsensusEngine(graph, governance_config=cfg)
    agent = EveAgent("agent:local_node", graph, consensus)
    agent.wallet_balance = 1000.0
    peer_manager = PeerManager(local_port=8000)
    public_runtime_root = Path(tempfile.mkdtemp(prefix="ilc-public-runtime-"))
    public_admission_store = LmdbAdmissionStore(public_runtime_root / "admission")
    public_wallet_store = LmdbWalletStore(public_runtime_root / "wallet")
    ecu_active_layer_runtime = EcuActiveLayerRuntime()
    public_lifecycle_runtime = EcuIlcLifecycleRuntime(
        wallet_store=public_wallet_store,
        ecu_runtime=ecu_active_layer_runtime,
    )
    app_obj.state.graph = graph
    app_obj.state.consensus = consensus
    app_obj.state.agent = agent
    app_obj.state.peer_manager = peer_manager
    app_obj.state.public_runtime_root = public_runtime_root
    app_obj.state.public_receipt_store = public_admission_store
    app_obj.state.public_admission_store = public_admission_store
    app_obj.state.public_wallet_store = public_wallet_store
    app_obj.state.ecu_active_layer_runtime = ecu_active_layer_runtime
    app_obj.state.public_lifecycle_runtime = public_lifecycle_runtime


@asynccontextmanager
async def lifespan(app_obj: FastAPI):
    """Initialize runtime resources for the app lifespan."""
    _init_runtime_state(app_obj)
    yield

router = APIRouter()


def _state(request: Request):
    """Convenience accessor for runtime state."""
    state = request.app.state
    # TestClient startup hooks run on context enter; lazily initialize for direct use.
    if not hasattr(state, "graph"):
        _init_runtime_state(request.app)
    return state


# Request Models
class ClaimRequest(BaseModel):
    content: str
    parent_id: str
    stake: float

class ProtocolClaimRequest(BaseModel):
    agent_id: str
    content: str
    parent_ids: Optional[List[str]] = None
    net_stake: Optional[float] = None

class ProtocolRefuteRequest(BaseModel):
    agent_id: str
    content: str
    target_claim_id: str
    net_stake: Optional[float] = None

class ProtocolTaskOutcomeRequest(BaseModel):
    task_type: str
    domain: str
    agent_id: str
    epoch: Optional[int] = None
    stake_spent: float
    reward_paid: float
    success: bool

@router.get("/")
def read_root(request: Request):
    state = _state(request)
    return {
        "system": "Intelligent Labor Coin",
        "status": "online",
        "agent_id": state.agent.id,
        "graph_size": len(state.graph.nodes),
        "genesis_hash": state.graph.nodes["axiom:math:01"].id if "axiom:math:01" in state.graph.nodes else "unknown"
    }

@router.post("/mine")
def mine_claim(req: ClaimRequest, request: Request):
    """
    Public Endpoint: Ask the internal agent to perform labor.
    """
    state = _state(request)
    node = state.agent.mine_thought(req.content, req.parent_id, req.stake)
    if not node:
        raise HTTPException(status_code=400, detail="Mining failed (insufficient funds?)")
    
    # NEW: Gossip the success!
    state.peer_manager.broadcast("/gossip/receive", node.model_dump())
    
    return {
        "status": "success",
        "node_id": node.id,
        "content": node.content,
        "net_stake": state.consensus.node_stakes.get(node.id, 0.0)
    }

@router.get("/node/{node_id}")
def get_node(node_id: str, request: Request):
    state = _state(request)
    if node_id not in state.graph.nodes:
        raise HTTPException(status_code=404, detail="Node not found")
    return state.graph.nodes[node_id]

@router.post("/gossip/receive")
def receive_gossip(node_data: dict, request: Request):
    """
    Endpoint for other nodes to push data to us.
    """
    state = _state(request)
    try:
        node = Node(**node_data)
        node_id = node.id
        logger.info("gossip_receive_inbound node=%s", node_id)

        if not node.signature:
            raise GossipValidationError("gossip_signature_missing")
        canonical_node_id = node.compute_canonical_id()
        if node_id != canonical_node_id:
            raise GossipValidationError("gossip_node_id_mismatch")

        if node_id in state.graph.nodes:
            return {"status": "ignored", "reason": "already_have"}

        state.graph.add_node(node)
        logger.info("gossip_receive_accepted node=%s node_id_mode=canonical", node_id)
        return {"status": "accepted"}
    except GossipValidationError as exc:
        logger.warning("gossip_receive_rejected token=%s", exc.token)
        raise HTTPException(status_code=400, detail="Invalid Gossip")
    except Exception:
        logger.exception("gossip_receive_failed token=gossip_unexpected_error")
        raise HTTPException(status_code=400, detail="Invalid Gossip")

@router.post("/peers/add")
def add_peer_endpoint(host: str, port: int, request: Request):
    state = _state(request)
    state.peer_manager.add_peer(host, port)
    return {"status": "added", "total_peers": len(state.peer_manager.peers)}

# --- Protocol Surface (MVP) ---
# NOTE: These /v1/protocol/* endpoints expose the MVP protocol schema over HTTP.
# They do not persist to a real chain or run consensus; they just:
#   - accept simple request models
#   - construct internal Node/TaskOutcome objects
#   - map them to protocol-shaped dicts via ilc_core.protocol.mapper
# This keeps the API in lockstep with protocol/ilc_protocol_mvp.json without
# hard-coding JSON structures here.

@router.get("/v1/protocol/schema")
def get_protocol_schema():
    schema = load_protocol_schema()
    return JSONResponse(schema)

@router.post("/v1/protocol/claim")
def submit_protocol_claim(req: ProtocolClaimRequest):
    # Build a Node; keep it simple and deterministic
    node = Node(
        id="", # Will be computed
        type="claim",
        content=req.content,
        agent_id=req.agent_id,
        signature="api_signed",
        net_stake=req.net_stake or 0.0,
    )
    node.id = node.compute_id()

    # Inject parent_ids if provided (mapper looks for attribute)
    if req.parent_ids:
        node.parent_ids = req.parent_ids

    proto = node_to_protocol_claim(node)
    return {"claim": proto}

@router.post("/v1/protocol/refute")
def submit_protocol_refute(req: ProtocolRefuteRequest):
    node = Node(
        id="",
        type="refutation",
        content=req.content,
        agent_id=req.agent_id,
        signature="api_signed",
        net_stake=req.net_stake or 0.0,
        target_id=req.target_claim_id
    )
    node.id = node.compute_id()
    
    proto = node_to_protocol_refute(node)
    return {"refute": proto}

@router.post("/v1/protocol/task_outcome")
def submit_protocol_task_outcome(req: ProtocolTaskOutcomeRequest):
    outcome = TaskOutcome(
        task_type=req.task_type,
        domain=req.domain,
        stake_spent=req.stake_spent,
        reward_paid=req.reward_paid,
        success=req.success,
    )
    proto = outcome_to_protocol_task_outcome(
        outcome,
        epoch=req.epoch,
        agent_id=req.agent_id,
    )
    return {"task_outcome": proto}


@router.post("/v1/public/init/admission")
def submit_public_init_admission(payload: dict, request: Request):
    state = _state(request)
    epoch_id = f"public-init-admission::{state.consensus.epoch_index}"
    try:
        result = issue_public_init_admission_receipt(
            payload=payload,
            epoch_id=epoch_id,
            store=state.public_admission_store,
        )
    except PublicInitAdmissionRuntimeError as exc:
        return JSONResponse({"ok": False, "token": exc.token}, status_code=400)
    return JSONResponse(result, status_code=200)


@router.post("/v1/public/receipt")
def submit_public_receipt(payload: dict, request: Request):
    state = _state(request)
    try:
        result = issue_public_receipt(
            payload=payload,
            store=state.public_receipt_store,
        )
    except PublicReceiptRuntimeError as exc:
        return JSONResponse({"ok": False, "token": exc.token}, status_code=400)
    return JSONResponse(result, status_code=200)


@router.get("/v1/public/receipt/{receipt_id}")
def query_public_receipt_by_id(receipt_id: str, request: Request):
    state = _state(request)
    try:
        result = query_public_receipts(
            store=state.public_receipt_store,
            receipt_id=receipt_id,
        )
    except PublicReceiptRuntimeError as exc:
        return JSONResponse({"ok": False, "token": exc.token}, status_code=400)
    return JSONResponse(result, status_code=200)


@router.get("/v1/public/receipts")
def query_public_receipt_collection(
    request: Request,
    signer_agent_id: str | None = None,
    artifact_kind: str | None = None,
    epoch_id: str | None = None,
):
    state = _state(request)
    try:
        result = query_public_receipts(
            store=state.public_receipt_store,
            signer_agent_id=signer_agent_id,
            artifact_kind=artifact_kind,
            epoch_id=epoch_id,
        )
    except PublicReceiptRuntimeError as exc:
        return JSONResponse({"ok": False, "token": exc.token}, status_code=400)
    return JSONResponse(result, status_code=200)


@router.get("/v1/public/lifecycle/coupling-invariants")
def get_coupling_invariants_diagnostic(request: Request):
    state = _state(request)
    result = state.public_lifecycle_runtime.coupling_invariants_diagnostic(
        graph_node_count=len(state.graph.nodes),
    )
    return JSONResponse(result, status_code=200)


@router.get("/v1/public/lifecycle/{agent_id}")
def get_public_lifecycle_status(agent_id: str, request: Request):
    state = _state(request)
    result = state.public_lifecycle_runtime.lifecycle_status(agent_id=agent_id)
    return JSONResponse(result, status_code=200)

@router.get("/v1/protocol/ep_task_schema")
def get_ep_task_schema():
    """
    Return the canonical JSON schema for EpistemicWorkTask.

    This is the same schema used by the EpistemicWorkTask Pydantic model
    and is suitable for external validation / code generation.
    """
    schema = load_epistemic_work_task_schema()
    return JSONResponse(schema)

@router.post("/v1/protocol/ep_task")
def submit_ep_task(ep_task: EpistemicWorkTask):
    """
    Intake endpoint for a single EpistemicWorkTask.

    MVP behavior:
    - Validate the incoming JSON against EpistemicWorkTask.
    - Wrap it into a TaskDescriptor via TaskDescriptor.from_epistemic_work_task(...).
    - Return both the canonical ep_task JSON and the TaskDescriptor
      to show how the scheduler would view it.

    This endpoint does *not* enqueue the task into any global worker
    or trigger a reward loop. It is a shaping + validation surface only.
    """
    # Canonical JSON view of the EpistemicWorkTask
    ep_json = ep_task_to_json(ep_task)

    # Bridge into TaskDescriptor
    td = TaskDescriptor.from_epistemic_work_task(ep_task)

    # If TaskDescriptor is a dataclass, convert to dict appropriately
    try:
        from dataclasses import asdict
        td_dict = asdict(td)
    except TypeError:
        # If it's a pydantic model or has .dict(), use that
        if hasattr(td, "dict"):
            td_dict = td.dict()
        else:
            td_dict = td.__dict__

    return {
        "ep_task": ep_json,
        "task_descriptor": td_dict,
    }


def create_app() -> FastAPI:
    app_obj = FastAPI(title="ILC Node Daemon", version="0.1.0", lifespan=lifespan)
    app_obj.include_router(router)
    return app_obj
