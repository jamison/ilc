# SPDX-License-Identifier: AGPL-3.0-only
"""Public-safe invite gate for local OpenClaw bootstrap rehearsal.

This helper intentionally does not import the private invitation provenance
runtime. It mirrors only the public-safe nullifier and nonce-root calculations
needed to rehearse the OpenClaw invite boundary.
"""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ilc_core.genesis.invite_nullifier_registry import InviteNullifierRegistry
from ilc_core.network.d2d.invite_nullifier_gossip import build_nullifier_gossip_message

OPENCLAW_INVITE_BOOTSTRAP_VERSION = "openclaw_invite_bootstrap_1575b_fix2d.v0.1"
NULLIFIER_STORE_SCHEMA_VERSION = "openclaw_invite_nullifiers.v0.1"

INVITE_NULLIFIER_DOMAIN = b"ilc-invite-nullifier-v1:"
INVITE_NONCE_LEAF_DOMAIN = b"ilc-invite-nonce-leaf-v1:"
INVITE_NONCE_NODE_DOMAIN = b"ilc-invite-nonce-node-v1:"

MAX_STRING_CHARS = 8192
MAX_MAPPING_KEYS = 64
MAX_SEQUENCE_ITEMS = 64
MAX_DEPTH = 8
NONCE_HEX_CHARS = 64
SHA256_HEX_CHARS = 64
MAX_NULLIFIER_STORE_BYTES = 4 * 1024 * 1024

NO_INVITE_ALLOWED_ACTIONS = ("docs", "status", "request_invite", "local_help")
LOCAL_BOOTSTRAP_ALLOWED_ACTIONS = (
    "docs",
    "status",
    "request_invite",
    "local_help",
    "verify_invite",
    "fetch_signed_bootstrap_manifest",
    "install_ilc_core",
    "run_local_setup",
)
BLOCKED_ACTIONS = (
    "create_production_identity",
    "idle_mining",
    "ilc_init_without_invite",
    "install_sidecars_without_manifest",
    "mint_ecu",
    "publish_nodes",
    "public_graph_write",
    "public_rc_activation",
    "settle_ilc",
    "wallet_setup",
    "wallet_write",
)
CROSS_NODE_REPLAY_PREVENTION_GAP = (
    "local_detection_implemented_phase_1576p;"
    "cross_node_replay_prevention_phase_1576pb"
)
# cross_node_replay_prevention_phase_1576pb: cross-node D2D gossip closed by Phase 1576p-b


@dataclass(frozen=True)
class BootstrapDecision:
    bootstrap_allowed: bool
    allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    defect_token: str | None
    redemption_nullifier: str | None
    signature_authority_status: str
    nonce_membership_status: str
    nullifier_status: str
    redeemer_key_binding_status: str
    production_ready: bool
    cross_node_replay_prevention_gap: str
    nullifier_gossip_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "allowed_actions": list(self.allowed_actions),
            "blocked_actions": list(self.blocked_actions),
            "bootstrap_allowed": self.bootstrap_allowed,
            "cross_node_replay_prevention_gap": self.cross_node_replay_prevention_gap,
            "defect_token": self.defect_token,
            "nonce_membership_status": self.nonce_membership_status,
            "nullifier_gossip_status": self.nullifier_gossip_status,
            "nullifier_status": self.nullifier_status,
            "production_ready": self.production_ready,
            "redeemer_key_binding_status": self.redeemer_key_binding_status,
            "redemption_nullifier": self.redemption_nullifier,
            "signature_authority_status": self.signature_authority_status,
            "version": OPENCLAW_INVITE_BOOTSTRAP_VERSION,
        }


class InviteNullifierStore:
    """Small atomic JSON store for per-node used invite nullifiers."""

    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path is not None else Path.home() / ".ilc" / "invite_nullifiers.json"
        self._used = _load_nullifier_map(self.path)
        self.local_registry = InviteNullifierRegistry()

    def contains(self, nullifier: str) -> bool:
        _require_sha256_hex(nullifier, "openclaw_invite_nullifier_invalid")
        return nullifier in self._used

    def add(self, nullifier: str, metadata: Mapping[str, Any] | None = None) -> None:
        _require_sha256_hex(nullifier, "openclaw_invite_nullifier_invalid")
        entry = dict(metadata or {})
        _validate_json_value(entry)
        self._used[nullifier] = entry
        _write_nullifier_map(self.path, self._used)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": NULLIFIER_STORE_SCHEMA_VERSION,
            "used_nullifiers": dict(sorted(self._used.items())),
        }


def derive_redemption_nullifier(batch_id: str, nonce_hex: str) -> str:
    _require_non_empty_string(batch_id, "openclaw_invite_batch_id_invalid")
    nonce_bytes = _nonce_bytes(nonce_hex)
    return hashlib.sha256(INVITE_NULLIFIER_DOMAIN + batch_id.encode("utf-8") + b":" + nonce_bytes).hexdigest()


def verify_invite_bootstrap(
    invite_bundle: Mapping[str, Any] | None,
    *,
    expected_profile: str,
    current_epoch: int,
    nullifier_store: InviteNullifierStore | None = None,
    local_nullifier_registry: InviteNullifierRegistry | None = None,
    persist_nullifier: bool = True,
    production_required: bool = False,
    nullifier_gossip_broadcaster: Callable[[Mapping[str, str]], object] | None = None,
    nullifier_gossip_claimed_actor: str | None = None,
) -> BootstrapDecision:
    _require_non_empty_string(expected_profile, "openclaw_expected_profile_invalid")
    epoch = _require_non_negative_int(current_epoch, "openclaw_current_epoch_invalid")
    if invite_bundle is None:
        return _deny("missing_invite", None, "not_checked", "not_checked", "not_checked")
    try:
        _validate_json_value(invite_bundle)
        batch = _require_mapping(invite_bundle.get("invite_batch_record"), "openclaw_invite_batch_record_missing")
        batch_id = _required_str(batch, "batch_id", "openclaw_invite_batch_id_invalid")
        inviter_cid = _required_str(batch, "inviter_cid", "openclaw_inviter_cid_invalid")
        count = _required_int(batch, "count", "openclaw_invite_count_invalid")
        nonce_merkle_root = _required_hex(batch, "nonce_merkle_root", "openclaw_nonce_merkle_root_invalid")
        created_epoch = _required_int(batch, "created_epoch", "openclaw_invite_created_epoch_invalid")
        inviter_sig = _required_str(batch, "inviter_sig", "openclaw_inviter_sig_invalid")
        if count < 1:
            raise ValueError("openclaw_invite_count_invalid")
        nonce_hex = _required_str(invite_bundle, "private_invite_nonce", "openclaw_invite_nonce_invalid")
        nullifier = derive_redemption_nullifier(batch_id, nonce_hex)
        profile = _required_str(invite_bundle, "intended_profile", "openclaw_invite_profile_invalid")
        intended_epoch = _required_int(invite_bundle, "intended_epoch", "openclaw_invite_epoch_invalid")
        if profile != expected_profile:
            return _deny("wrong_profile", nullifier, "not_checked", "not_checked", "not_checked")
        if intended_epoch != epoch or created_epoch > epoch:
            return _deny("wrong_epoch_window", nullifier, "not_checked", "not_checked", "not_checked")
        store = nullifier_store or InviteNullifierStore()
        local_registry = local_nullifier_registry if local_nullifier_registry is not None else store.local_registry
        if local_registry.is_known(nullifier):
            return _deny("invite_nullifier_already_seen", nullifier, "not_checked", "used", "not_checked")
        membership_status = _verify_nonce_membership(
            nonce_hex=nonce_hex,
            nonce_merkle_root=nonce_merkle_root,
            count=count,
            proof=invite_bundle.get("nonce_membership_proof"),
        )
        if membership_status != "verified":
            return _deny(membership_status, nullifier, membership_status, "not_checked", "not_checked")
        if store.contains(nullifier):
            return _deny("replayed_nullifier", nullifier, "verified", "used", "not_checked")
        signature_status = _signature_status(inviter_sig)
        redeemer_status = _redeemer_binding_status(invite_bundle)
        if production_required and signature_status != "verified":
            return _deny("invite_signature_authority_unverified", nullifier, "verified", "unused", redeemer_status)
        if production_required and redeemer_status != "verified":
            return _deny("redeemer_key_binding_required", nullifier, "verified", "unused", redeemer_status)
        if persist_nullifier:
            store.add(
                nullifier,
                {
                    "batch_id": batch_id,
                    "created_epoch": created_epoch,
                    "expected_profile": expected_profile,
                    "intended_epoch": intended_epoch,
                    "inviter_cid": inviter_cid,
                    "signature_authority_status": signature_status,
                },
            )
        local_registry.register_nullifier(nullifier)
        nullifier_gossip_status = _broadcast_nullifier_gossip(
            nullifier,
            nullifier_gossip_broadcaster,
            claimed_actor=nullifier_gossip_claimed_actor,
        )
        production_ready = signature_status == "verified" and redeemer_status == "verified"
        return BootstrapDecision(
            bootstrap_allowed=True,
            allowed_actions=LOCAL_BOOTSTRAP_ALLOWED_ACTIONS,
            blocked_actions=BLOCKED_ACTIONS,
            defect_token=None if production_ready else "invite_signature_authority_gap_recorded_phase_1575b_fix2d",
            redemption_nullifier=nullifier,
            signature_authority_status=signature_status,
            nonce_membership_status="verified",
            nullifier_status="recorded" if persist_nullifier else "local_recorded_not_persisted",
            redeemer_key_binding_status=redeemer_status,
            production_ready=production_ready,
            cross_node_replay_prevention_gap=CROSS_NODE_REPLAY_PREVENTION_GAP,
            nullifier_gossip_status=nullifier_gossip_status,
        )
    except (KeyError, TypeError, ValueError, OSError):
        return _deny("malformed_invite", None, "not_checked", "not_checked", "not_checked")


def build_synthetic_invite_bundle(
    *,
    batch_id: str = "openclaw-fix2d-batch",
    nonce_hex: str = "11" * 32,
    intended_profile: str = "openclaw_public_rc_bootstrap",
    intended_epoch: int = 0,
    inviter_cid: str = "genesis_agent:01",
    inviter_sig: str = "synthetic-local-signature",
) -> dict[str, Any]:
    _require_non_empty_string(batch_id, "openclaw_invite_batch_id_invalid")
    _require_non_empty_string(intended_profile, "openclaw_invite_profile_invalid")
    epoch = _require_non_negative_int(intended_epoch, "openclaw_invite_epoch_invalid")
    nonce_bytes = _nonce_bytes(nonce_hex)
    return {
        "intended_epoch": epoch,
        "intended_profile": intended_profile,
        "invite_batch_record": {
            "batch_id": batch_id,
            "count": 1,
            "created_epoch": epoch,
            "inviter_cid": inviter_cid,
            "inviter_sig": inviter_sig,
            "nonce_merkle_root": _invite_nonce_leaf_hash(nonce_bytes).hex(),
        },
        "private_invite_nonce": nonce_hex,
    }


def canonical_json_bytes(payload: Mapping[str, Any]) -> bytes:
    _validate_json_value(payload, allow_bool=True)
    return json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True).encode("utf-8")


def _deny(
    token: str,
    nullifier: str | None,
    membership_status: str,
    nullifier_status: str,
    redeemer_status: str,
) -> BootstrapDecision:
    return BootstrapDecision(
        bootstrap_allowed=False,
        allowed_actions=NO_INVITE_ALLOWED_ACTIONS,
        blocked_actions=BLOCKED_ACTIONS,
        defect_token=token,
        redemption_nullifier=nullifier,
        signature_authority_status="unverified_gap",
        nonce_membership_status=membership_status,
        nullifier_status=nullifier_status,
        redeemer_key_binding_status=redeemer_status,
        production_ready=False,
        cross_node_replay_prevention_gap=CROSS_NODE_REPLAY_PREVENTION_GAP,
        nullifier_gossip_status="not_configured",
    )


def _broadcast_nullifier_gossip(
    nullifier_hex: str,
    broadcaster: Callable[[Mapping[str, str]], object] | None,
    *,
    claimed_actor: str | None,
) -> str:
    if broadcaster is None:
        return "not_configured"
    if claimed_actor is None:
        return "broadcast_not_configured_claimed_actor_required"
    try:
        message = build_nullifier_gossip_message(
            nullifier_hex,
            claimed_actor=claimed_actor,
        )
        broadcaster(message)
    except Exception as exc:  # noqa: BLE001 - gossip failure must not unwind an accepted local redemption.
        return f"broadcast_failed:{exc.__class__.__name__}"
    return "broadcast_requested"


def _verify_nonce_membership(
    *,
    nonce_hex: str,
    nonce_merkle_root: str,
    count: int,
    proof: object,
) -> str:
    # Mirrors canonical verify_nonce_membership_proof without importing the
    # private provenance module, preserving this sidecar's public-safe boundary.
    nonce_bytes = _nonce_bytes(nonce_hex)
    leaf = _invite_nonce_leaf_hash(nonce_bytes)
    if count == 1:
        return "verified" if leaf.hex() == nonce_merkle_root else "nonce_membership_mismatch"
    if proof in (None, (), []):
        return "nonce_membership_proof_required"
    if not isinstance(proof, Sequence) or isinstance(proof, (str, bytes, bytearray)):
        return "nonce_membership_proof_invalid"
    if len(proof) != _invite_nonce_merkle_proof_length(count):
        return "nonce_membership_proof_length_invalid"
    digest = leaf
    for item in proof:
        if not isinstance(item, Mapping):
            return "nonce_membership_proof_invalid"
        sibling = item.get("sibling")
        position = item.get("position")
        if not isinstance(sibling, str) or not _is_sha256_hex(sibling):
            return "nonce_membership_proof_invalid"
        sibling_bytes = bytes.fromhex(sibling)
        if position == "left":
            digest = hashlib.sha256(INVITE_NONCE_NODE_DOMAIN + sibling_bytes + digest).digest()
        elif position == "right":
            digest = hashlib.sha256(INVITE_NONCE_NODE_DOMAIN + digest + sibling_bytes).digest()
        else:
            return "nonce_membership_proof_invalid"
    return "verified" if digest.hex() == nonce_merkle_root else "nonce_membership_mismatch"


def _signature_status(inviter_sig: str) -> str:
    _require_non_empty_string(inviter_sig, "openclaw_inviter_sig_invalid")
    # No public verifier is wired in this phase. Synthetic fixtures may unlock
    # local bootstrap, but production/public bootstrap remains fail-closed.
    return "unverified_gap"


def _redeemer_binding_status(invite_bundle: Mapping[str, Any]) -> str:
    intended = invite_bundle.get("intended_redeemer_pubkey")
    actual = invite_bundle.get("redeemer_pubkey")
    if intended is None and actual is None:
        return "not_implemented_gap"
    if type(intended) is str and intended and actual == intended:
        return "verified"
    return "mismatch"


def _invite_nonce_leaf_hash(nonce: bytes) -> bytes:
    return hashlib.sha256(INVITE_NONCE_LEAF_DOMAIN + nonce).digest()


def _invite_nonce_merkle_proof_length(count: int) -> int:
    if type(count) is not int or count < 1:
        raise ValueError("openclaw_invite_count_invalid")
    length = 0
    width = count
    while width > 1:
        length += 1
        width = (width + 1) // 2
    return length


def _nonce_bytes(value: object) -> bytes:
    if type(value) is not str or len(value) != NONCE_HEX_CHARS:
        raise ValueError("openclaw_invite_nonce_invalid")
    if any(char not in "0123456789abcdef" for char in value):
        raise ValueError("openclaw_invite_nonce_invalid")
    return bytes.fromhex(value)


def _load_nullifier_map(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    if path.stat().st_size > MAX_NULLIFIER_STORE_BYTES:
        raise ValueError("openclaw_nullifier_store_too_large")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("openclaw_nullifier_store_invalid") from exc
    if not isinstance(data, Mapping):
        raise ValueError("openclaw_nullifier_store_invalid")
    if data.get("schema_version") != NULLIFIER_STORE_SCHEMA_VERSION:
        raise ValueError("openclaw_nullifier_store_schema_invalid")
    used = data.get("used_nullifiers")
    if not isinstance(used, Mapping):
        raise ValueError("openclaw_nullifier_store_used_invalid")
    if len(used) > InviteNullifierRegistry._MAX_REGISTRY_SIZE:
        raise ValueError("openclaw_nullifier_store_too_many_entries")
    result: dict[str, Any] = {}
    for key, value in used.items():
        _require_sha256_hex(key, "openclaw_nullifier_store_key_invalid")
        if not isinstance(value, Mapping):
            raise ValueError("openclaw_nullifier_store_value_invalid")
        _validate_json_value(value)
        result[key] = dict(value)
    return result


def _write_nullifier_map(path: Path, used: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": NULLIFIER_STORE_SCHEMA_VERSION,
        "used_nullifiers": dict(sorted(used.items())),
    }
    body = canonical_json_bytes(payload)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(body)
            handle.write(b"\n")
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _required_str(payload: Mapping[str, Any], key: str, token: str) -> str:
    value = payload.get(key)
    return _require_non_empty_string(value, token)


def _required_int(payload: Mapping[str, Any], key: str, token: str) -> int:
    return _require_non_negative_int(payload.get(key), token)


def _required_hex(payload: Mapping[str, Any], key: str, token: str) -> str:
    value = payload.get(key)
    _require_sha256_hex(value, token)
    return str(value)


def _require_mapping(value: object, token: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise ValueError(token)
    return value


def _require_non_negative_int(value: object, token: str) -> int:
    if type(value) is not int or value < 0:
        raise ValueError(token)
    return value


def _require_non_empty_string(value: object, token: str) -> str:
    if type(value) is not str:
        raise ValueError(token)
    normalized = value.strip()
    if not normalized or normalized != value or len(normalized) > MAX_STRING_CHARS:
        raise ValueError(token)
    return normalized


def _require_sha256_hex(value: object, token: str) -> None:
    if type(value) is not str or not _is_sha256_hex(value):
        raise ValueError(token)


def _is_sha256_hex(value: str) -> bool:
    return len(value) == SHA256_HEX_CHARS and all(char in "0123456789abcdef" for char in value)


def _validate_json_value(value: Any, *, depth: int = 0, allow_bool: bool = False) -> None:
    if depth > MAX_DEPTH:
        raise ValueError("openclaw_invite_payload_depth_exceeded")
    if isinstance(value, bool):
        if allow_bool:
            return
        raise ValueError("openclaw_invite_bool_as_int_rejected")
    if isinstance(value, float):
        raise ValueError("openclaw_invite_float_not_allowed")
    if isinstance(value, str):
        if len(value) > MAX_STRING_CHARS:
            raise ValueError("openclaw_invite_string_too_long")
        return
    if value is None or type(value) is int:
        return
    if isinstance(value, Mapping):
        if len(value) > MAX_MAPPING_KEYS:
            raise ValueError("openclaw_invite_mapping_too_wide")
        for key, nested in value.items():
            _require_non_empty_string(key, "openclaw_invite_mapping_key_invalid")
            _validate_json_value(nested, depth=depth + 1, allow_bool=allow_bool)
        return
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        if len(value) > MAX_SEQUENCE_ITEMS:
            raise ValueError("openclaw_invite_sequence_too_long")
        for nested in value:
            _validate_json_value(nested, depth=depth + 1, allow_bool=allow_bool)
        return
    raise ValueError("openclaw_invite_payload_type_invalid")


__all__ = [
    "BLOCKED_ACTIONS",
    "BootstrapDecision",
    "CROSS_NODE_REPLAY_PREVENTION_GAP",
    "INVITE_NULLIFIER_DOMAIN",
    "InviteNullifierRegistry",
    "InviteNullifierStore",
    "LOCAL_BOOTSTRAP_ALLOWED_ACTIONS",
    "MAX_NULLIFIER_STORE_BYTES",
    "NO_INVITE_ALLOWED_ACTIONS",
    "OPENCLAW_INVITE_BOOTSTRAP_VERSION",
    "build_synthetic_invite_bundle",
    "canonical_json_bytes",
    "derive_redemption_nullifier",
    "verify_invite_bootstrap",
]
