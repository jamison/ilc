from fastapi import APIRouter, FastAPI, HTTPException, Request
import hashlib
import json
import logging
from contextlib import asynccontextmanager
from decimal import Decimal, InvalidOperation
from pathlib import Path
import shutil
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
from ilc_core.protocol.public_wallet_runtime import PublicWalletRuntime
from ilc_core.storage.lmdb_public_runtime import LmdbAdmissionStore, LmdbWalletStore
from ilc_core.ledger.ecu_active_layer_runtime import EcuActiveLayerRuntime
from ilc_core.ledger.ecu_ilc_lifecycle_runtime import EcuIlcLifecycleRuntime
from ilc_core.sidecars.claim_nullifier_registry_v1 import ClaimNullifierRegistry
from ilc_core.sidecars.claimability_receipt_verifier import (
    ACCEPTED_LOCAL_ONLY_DECISION,
    MAX_CLAIMABILITY_VERIFIER_PAYLOAD_BYTES,
    verify_claimability_receipt_presentation,
)
from ilc_core.sidecars.public_verifier_api_activation import (
    ACCEPTED_PUBLIC_VERIFIER_API_DECISION,
    PHASE_1439_PUBLIC_VERIFIER_API_TOKENS,
)
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
    agent.wallet_balance = Decimal("1000")
    peer_manager = PeerManager(local_port=8000)
    public_runtime_root = Path(tempfile.mkdtemp(prefix="ilc-public-runtime-"))
    public_admission_store = LmdbAdmissionStore(public_runtime_root / "admission")
    public_wallet_store = LmdbWalletStore(public_runtime_root / "wallet")
    ecu_active_layer_runtime = EcuActiveLayerRuntime()
    public_lifecycle_runtime = EcuIlcLifecycleRuntime(
        wallet_store=public_wallet_store,
        ecu_runtime=ecu_active_layer_runtime,
    )
    claimability_registry = ClaimNullifierRegistry()
    public_wallet_runtime = PublicWalletRuntime(
        wallet_store=public_wallet_store,
        lifecycle_runtime=public_lifecycle_runtime,
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
    app_obj.state.public_wallet_runtime = public_wallet_runtime
    app_obj.state.claimability_registry = claimability_registry


def _close_runtime_state(app_obj: FastAPI) -> None:
    state = app_obj.state
    closeable_attrs = (
        "public_admission_store",
        "public_wallet_store",
    )
    closed_ids: set[int] = set()
    for attr in closeable_attrs:
        value = getattr(state, attr, None)
        if value is None or id(value) in closed_ids:
            continue
        close = getattr(value, "close", None)
        if callable(close):
            close()
            closed_ids.add(id(value))
    runtime_root = getattr(state, "public_runtime_root", None)
    if isinstance(runtime_root, Path):
        shutil.rmtree(runtime_root, ignore_errors=True)


@asynccontextmanager
async def lifespan(app_obj: FastAPI):
    """Initialize runtime resources for the app lifespan."""
    _init_runtime_state(app_obj)
    try:
        yield
    finally:
        _close_runtime_state(app_obj)

router = APIRouter()


def _state(request: Request):
    """Convenience accessor for runtime state."""
    state = request.app.state
    # TestClient startup hooks run on context enter; lazily initialize for direct use.
    if not hasattr(state, "graph"):
        _init_runtime_state(request.app)
    return state


def _parse_decimal_amount(raw: object, error_token: str) -> Decimal:
    if isinstance(raw, bool):
        raise ValueError(error_token)
    if not isinstance(raw, (Decimal, int, str)):
        raise ValueError(error_token)
    try:
        amount = raw if isinstance(raw, Decimal) else Decimal(str(raw))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(error_token) from exc
    if not amount.is_finite():
        raise ValueError(f"{error_token}_non_finite")
    if amount < Decimal("0"):
        raise ValueError(f"{error_token}_negative")
    return amount


def _require_non_negative_int_or_none(raw: object, error_token: str) -> int | None:
    if raw is None:
        return None
    if isinstance(raw, bool) or not isinstance(raw, int) or raw < 0:
        raise ValueError(error_token)
    return raw


def _append_unique_tokens(tokens: object, extra_tokens: tuple[str, ...]) -> list[str]:
    if not isinstance(tokens, list) or not all(isinstance(item, str) for item in tokens):
        raise ValueError("claimability_public_api_tokens_invalid_phase_1439")
    merged = list(tokens)
    for token in extra_tokens:
        if token not in merged:
            merged.append(token)
    return merged


def _sha256_payload(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _public_claimability_decision(decision: dict[str, object]) -> dict[str, object]:
    body = dict(decision)
    body.pop("canonical_decision_sha256", None)
    if body.get("decision") == ACCEPTED_LOCAL_ONLY_DECISION:
        body["decision"] = ACCEPTED_PUBLIC_VERIFIER_API_DECISION
    body["non_loopback_claimability_api_enabled"] = True
    body["public_api_enabled"] = True
    body["public_claimability_activated"] = True
    body["receipt_verifier_public_serving_enabled"] = True
    body["ecu_mint_authorized"] = False
    body["ilc_settlement_authorized"] = False
    body["wallet_spend_enabled"] = False
    body["wallet_transfer_enabled"] = False
    body["wallet_withdrawal_enabled"] = False
    body["tokens"] = _append_unique_tokens(
        body.get("tokens"),
        PHASE_1439_PUBLIC_VERIFIER_API_TOKENS,
    )
    body["canonical_decision_sha256"] = _sha256_payload(body)
    return body


# Request Models
class ClaimRequest(BaseModel):
    content: str
    parent_id: str
    stake: str

class ProtocolClaimRequest(BaseModel):
    agent_id: str
    content: str
    parent_ids: Optional[List[str]] = None
    net_stake: Optional[str] = None

class ProtocolRefuteRequest(BaseModel):
    agent_id: str
    content: str
    target_claim_id: str
    net_stake: Optional[str] = None

class ProtocolTaskOutcomeRequest(BaseModel):
    task_type: str
    domain: str
    agent_id: str
    epoch: Optional[int] = None
    stake_spent: str
    reward_paid: str
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
    try:
        stake = _parse_decimal_amount(req.stake, "mine_claim_stake_invalid")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    node = state.agent.mine_thought(req.content, req.parent_id, stake)
    if not node:
        raise HTTPException(status_code=400, detail="Mining failed (insufficient funds?)")
    
    # NEW: Gossip the success!
    state.peer_manager.broadcast("/gossip/receive", node.model_dump())
    
    return {
        "status": "success",
        "node_id": node.id,
        "content": node.content,
        "net_stake": str(state.consensus.node_stakes.get(node.id, Decimal("0")))
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
    try:
        net_stake = (
            _parse_decimal_amount(req.net_stake, "protocol_claim_net_stake_invalid")
            if req.net_stake is not None
            else Decimal("0")
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    node = Node(
        id="", # Will be computed
        type="claim",
        content=req.content,
        agent_id=req.agent_id,
        signature="api_signed",
        net_stake=net_stake,
    )
    node.id = node.compute_id()

    # Inject parent_ids if provided (mapper looks for attribute)
    if req.parent_ids:
        node.parent_ids = req.parent_ids

    proto = node_to_protocol_claim(node)
    return {"claim": proto}

@router.post("/v1/protocol/refute")
def submit_protocol_refute(req: ProtocolRefuteRequest):
    try:
        net_stake = (
            _parse_decimal_amount(req.net_stake, "protocol_refute_net_stake_invalid")
            if req.net_stake is not None
            else Decimal("0")
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    node = Node(
        id="",
        type="refutation",
        content=req.content,
        agent_id=req.agent_id,
        signature="api_signed",
        net_stake=net_stake,
        target_id=req.target_claim_id
    )
    node.id = node.compute_id()
    
    proto = node_to_protocol_refute(node)
    return {"refute": proto}

@router.post("/v1/protocol/task_outcome")
def submit_protocol_task_outcome(req: ProtocolTaskOutcomeRequest):
    try:
        stake_spent = _parse_decimal_amount(
            req.stake_spent, "protocol_task_outcome_stake_spent_invalid"
        )
        reward_paid = _parse_decimal_amount(
            req.reward_paid, "protocol_task_outcome_reward_paid_invalid"
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    outcome = TaskOutcome(
        task_type=req.task_type,
        domain=req.domain,
        stake_spent=stake_spent,
        reward_paid=reward_paid,
        success=req.success,
    )
    proto = outcome_to_protocol_task_outcome(
        outcome,
        epoch=req.epoch,
        agent_id=req.agent_id,
    )
    return {"task_outcome": proto}


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


@router.post("/api/v1/claimability/verify")
async def verify_claimability_public_api(request: Request):
    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            declared_size = int(content_length)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail="claimability_public_api_content_length_invalid_phase_1439",
            ) from exc
        if declared_size > MAX_CLAIMABILITY_VERIFIER_PAYLOAD_BYTES:
            raise HTTPException(
                status_code=413,
                detail="claimability_public_api_payload_too_large_phase_1439",
            )

    body = await request.body()
    if len(body) > MAX_CLAIMABILITY_VERIFIER_PAYLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail="claimability_public_api_payload_too_large_phase_1439",
        )
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="claimability_public_api_json_invalid_phase_1439",
        ) from exc
    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=400,
            detail="claimability_public_api_payload_not_object_phase_1439",
        )

    if "presentation" in payload:
        presentation = payload["presentation"]
        try:
            current_epoch = _require_non_negative_int_or_none(
                payload.get("current_issuance_epoch"),
                "claimability_public_api_current_epoch_invalid_phase_1439",
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    else:
        presentation = payload
        current_epoch = None

    state = _state(request)
    registry = getattr(state, "claimability_registry", None)
    if registry is None:
        registry = ClaimNullifierRegistry()
        state.claimability_registry = registry

    decision = verify_claimability_receipt_presentation(
        presentation,
        claim_registry=registry,
        current_issuance_epoch=current_epoch,
    )
    return JSONResponse(_public_claimability_decision(decision))


def create_app() -> FastAPI:
    app_obj = FastAPI(title="ILC Node Daemon", version="0.1.0", lifespan=lifespan)
    app_obj.include_router(router)
    return app_obj
