# SPDX-License-Identifier: AGPL-3.0-only
"""D2e-03 JSON-first CLI prototype.

This module implements the Phase-264 prototype runtime aligned to the locked
command surface. DAG-CBOR encoding remains deferred to later phases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen


SCHEMA_VERSION = "254.v0.1"
QUERY_SCHEMA_VERSION = "299.v0.1"
VERIFY_SCHEMA_VERSION = "301.v0.1"
BUNDLE_SCHEMA_VERSION = "303.v0.1"
INSTALL_INVITE_MAX_BYTES = 1_048_576
INSTALL_BOOTSTRAP_ATTACHMENT_MAX_BYTES = 1_048_576
INSTALL_KNOWN_PEER_HINTS_MAX_COUNT = 8
INSTALL_PROBE_OBSERVER_MAX_COUNT = 16
INSTALL_RELAY_BOOTSTRAP_RECORD_MAX_COUNT = 8
INSTALL_RELAY_DEFAULT_INTERNAL_PORT = 50151
INSTALL_RELAY_DEFAULT_NETWORK_ID = "public-rc"
UPDATE_MANIFEST_MAX_BYTES = 1_048_576
UPDATE_HTTP_CHUNK_BYTES = 64 * 1024
DEFAULT_UPDATE_MANIFEST_URL = "https://ilc.network/release/manifest.json"
_ILC_CORE_PY3_ANY_WHEEL_RE = re.compile(
    r"^ilc_core-[0-9]+(?:\.[0-9]+){1,2}-py3-none-any\.whl$"
)
_AGENT_ID_HEX_RE = re.compile(r"^[0-9a-f]{96}$")
_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")

PRIMITIVE_COMMANDS = (
    "assert",
    "validate",
    "contradict",
    "refute",
    "revise",
    "link",
    "epoch",
)

OPERATIONAL_COMMANDS = (
    "query",
    "verify",
    "balance",
    "identity",
    "install",
    "update",
    "bundle",
    "shard",
    "capproof",
    "config",
    "agent",
    "agent-bootstrap",
    "node",
    "sidecar",
    "skills",
    "wallet",
    "ccss",
    "atlas",
    "doctor",
    "network-doctor",
    "relay",
    "bootstrap",
    "bootstrap-census",
    "bootstrap-receipt",
    "submit",
    "validator",
    "version",
)

ALL_COMMANDS = PRIMITIVE_COMMANDS + OPERATIONAL_COMMANDS


class QueryCommandError(Exception):
    """Typed error carrying query contract error token and message."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class VerifyCommandError(Exception):
    """Typed error carrying verify contract error token and message."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


class BundleCommandError(Exception):
    """Typed error carrying bundle contract error token and message."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def _version_data() -> dict[str, Any]:
    return {
        "schema_versions": {
            "primary": SCHEMA_VERSION,
            "query": QUERY_SCHEMA_VERSION,
            "verify": VERIFY_SCHEMA_VERSION,
            "bundle": BUNDLE_SCHEMA_VERSION,
        },
        "supported_commands": sorted(ALL_COMMANDS),
    }


def _now_rfc3339_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _success_payload(command: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "ok": True,
        "ts_utc": _now_rfc3339_utc(),
        "data": data,
    }


def _error_payload(
    command: str,
    code: int,
    message: str,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "ok": False,
        "error": True,
        "code": str(code),
        "message": message,
        "details": details or {},
    }


def _infer_command_from_argv() -> str:
    if len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        return sys.argv[1]
    return "unknown"


def _infer_query_command_token_from_argv() -> str:
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
        return f"query {sys.argv[2]}"
    return "query"


def _infer_verify_command_token_from_argv() -> str:
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
        return f"verify {sys.argv[2]}"
    return "verify"


def _infer_bundle_command_token_from_argv() -> str:
    if len(sys.argv) >= 3 and not sys.argv[2].startswith("-"):
        return f"bundle {sys.argv[2]}"
    return "bundle"


def _query_success_payload(command_token: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "meta": {
            "command": command_token,
            "schema_version": QUERY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _query_error_payload(command_token: str, code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "meta": {
            "command": command_token,
            "schema_version": QUERY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _verify_success_payload(command_token: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "meta": {
            "command": command_token,
            "schema_version": VERIFY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _verify_error_payload(command_token: str, code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "meta": {
            "command": command_token,
            "schema_version": VERIFY_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _bundle_success_payload(command_token: str, data: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "data": data,
        "meta": {
            "command": command_token,
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


def _bundle_error_payload(command_token: str, code: str, message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "error": {"code": code, "message": message},
        "meta": {
            "command": command_token,
            "schema_version": BUNDLE_SCHEMA_VERSION,
            "generated_at": _now_rfc3339_utc(),
        },
    }


class JsonArgumentParser(argparse.ArgumentParser):
    """ArgumentParser that emits JSON errors with exit code 2."""

    def error(self, message: str) -> None:  # pragma: no cover - exercised via subprocess
        command = _infer_command_from_argv()
        if command == "query":
            payload = _query_error_payload(
                command_token=_infer_query_command_token_from_argv(),
                code="query_invalid_input",
                message=message,
            )
        elif command == "verify":
            payload = _verify_error_payload(
                command_token=_infer_verify_command_token_from_argv(),
                code="verify_invalid_input",
                message=message,
            )
        elif command == "bundle":
            payload = _bundle_error_payload(
                command_token=_infer_bundle_command_token_from_argv(),
                code="bundle_invalid_input",
                message=message,
            )
        else:
            payload = _error_payload(
                command=command,
                code=2,
                message=message,
                details={"usage": self.format_usage().strip()},
            )
        print(json.dumps(payload), file=sys.stderr)
        raise SystemExit(2)


def _prototype_data_for_command(command: str) -> dict[str, Any]:
    data_by_command: dict[str, dict[str, Any]] = {
        "assert": {
            "claim_cid": "bafy-prototype-claim",
            "epoch_id": "epoch-local",
            "lineage_id": "lineage-local",
        },
        "validate": {
            "target_cid": "bafy-target",
            "validation_cid": "bafy-validation",
            "accepted": True,
        },
        "contradict": {
            "target_cid": "bafy-target",
            "contradiction_cid": "bafy-contradiction",
            "accepted": True,
        },
        "refute": {
            "target_cid": "bafy-target",
            "refutation_cid": "bafy-refutation",
            "accepted": True,
        },
        "revise": {
            "target_cid": "bafy-original",
            "revision_cid": "bafy-revision",
            "supersedes": "bafy-original",
        },
        "link": {
            "source_cid": "bafy-source",
            "target_cid": "bafy-target",
            "edge_type": "supports",
            "edge_cid": "bafy-edge",
        },
        "epoch": {
            "epoch_id": "epoch-local",
            "state": "open",
            "finalization_hash": "sha256:prototype",
        },
        "query": {
            "query": "prototype",
            "results": [],
            "count": 0,
        },
        "verify": {
            "subject": "prototype",
            "verified": True,
            "verification_type": "prototype",
        },
        "balance": {
            "account_id": "prototype_compat",
            "balance_ilc": "0",
            "pending_balance_ilc": "0",
            "report_mode": "prototype_compat",
        },
        "identity": {
            "lineage_id": "lineage-local",
            "status": "active",
            "export_ref": "identity-local",
        },
        "bundle": {
            "bundle_cid": "bafy-bundle",
            "valid": True,
            "manifest_ref": "manifest-local",
        },
        "shard": {
            "shard_id": "shard-local",
            "assignment": "local",
            "routing_status": "deferred_star_map",
        },
        "capproof": {
            "probe_set": "phase-264-prototype",
            "overall_pass": True,
            "probe_results": [],
        },
        "config": {
            "profile": "default",
            "changed_keys": [],
            "effective_config_ref": "config-local",
        },
    }
    if command not in data_by_command:
        raise ValueError(f"unknown_command: {command}")
    return data_by_command[command]


def _default_graph_state_path() -> Path:
    return Path(os.environ.get("ILC_CLI_GRAPH_STATE_PATH", ".ilc_d2e03_graph.json"))


def _default_bundle_state_path() -> Path:
    return Path(os.environ.get("ILC_BUNDLE_STATE_PATH", ".ilc_d2e07_bundle_state.json"))


def _default_balance_state_path() -> Path:
    return Path(os.environ.get("ILC_BALANCE_STATE_PATH", "out/ecu_live_smoke_1561.json"))


def _ensure_local_graph_state(path: Path, command: str) -> None:
    if path.exists():
        raw = path.read_text(encoding="utf-8")
        obj = _loads_json_no_constants(raw)
        if not isinstance(obj, dict):
            raise ValueError("graph_state_not_object")
    else:
        obj = {
            "schema_version": "d2e03.v0.1",
            "nodes": [],
            "edges": [],
            "epochs": [],
        }

    obj["last_command"] = command
    obj["updated_at"] = _now_rfc3339_utc()

    path.parent.mkdir(parents=True, exist_ok=True)
    _write_json_file_atomic(path, obj, indent=2, mode=0o644)


def _identity_state_path(graph_state_path: Path) -> Path:
    env_override = os.environ.get("ILC_IDENTITY_STATE_PATH")
    if env_override:
        return Path(env_override)
    return graph_state_path.with_name(".ilc_d2e04_identity_state.json")


def _home_ilc_state_path(filename: str) -> Path:
    return Path.home() / ".ilc" / filename


def _ccss_home_path() -> Path:
    return Path.home() / ".ilc" / "ccss"


def _load_identity_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8")
    data = _loads_json_no_constants(raw)
    if not isinstance(data, dict):
        raise ValueError("identity_state_not_object")
    return data


def _write_identity_state(path: Path, state: dict[str, Any]) -> None:
    _write_json_file_atomic(path, state, indent=2, mode=0o600)


def _write_local_json_file(path: str, payload: dict[str, Any]) -> str:
    target = Path(path)
    _write_json_file_atomic(target, payload, indent=2, mode=0o644)
    return str(target)


def _write_json_file_atomic(
    path: Path,
    payload: dict[str, Any],
    *,
    indent: int | None = None,
    mode: int = 0o600,
) -> None:
    data = json.dumps(
        payload,
        sort_keys=True,
        indent=indent,
        separators=None if indent is not None else (",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.chmod(temp_name, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = -1
            handle.write(data)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        if fd != -1:
            os.close(fd)
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            _temp_file_already_removed = True
        raise


def _loads_json_no_constants(raw: str) -> Any:
    def _reject_constant(value: str) -> None:
        raise ValueError(f"json_non_finite_constant_not_allowed:{value}")

    return json.loads(raw, parse_constant=_reject_constant)


def _read_local_json_file(path: str) -> dict[str, Any]:
    data = _loads_json_no_constants(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("json_payload_not_object")
    return data


def _read_local_json_file_bounded(
    path: str,
    *,
    max_bytes: int,
    too_large_token: str,
    invalid_token: str,
    object_token: str,
) -> dict[str, Any]:
    target = Path(path)
    try:
        with target.open("rb") as handle:
            raw = handle.read(max_bytes + 1)
    except OSError as exc:
        raise ValueError(invalid_token) from exc
    if len(raw) > max_bytes:
        raise ValueError(too_large_token)
    try:
        data = _loads_json_no_constants(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(invalid_token) from exc
    if not isinstance(data, dict):
        raise ValueError(object_token)
    _reject_float(data, f"{invalid_token}:float_not_allowed")
    return data


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = _loads_json_no_constants(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _require_invite_cli_enabled(args: argparse.Namespace) -> None:
    if not bool(getattr(args, "enable_invites", False)):
        raise ValueError("invite_cli_not_enabled_use_enable_invites")


def _run_identity_invite_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    invite_subcommand = getattr(args, "identity_invite_subcommand", None)
    if invite_subcommand == "generate":
        return _run_identity_invite_generate_subcommand(args)
    _require_invite_cli_enabled(args)
    if invite_subcommand == "hint":
        return _run_identity_invite_hint_subcommand(args)
    if invite_subcommand == "bundle":
        return _run_identity_invite_bundle_subcommand(args)
    if invite_subcommand != "create":
        raise ValueError(f"unknown_identity_invite_subcommand:{invite_subcommand}")

    from ilc_core.genesis.invitation_provenance_record import build_invite_batch_record

    record, private_nonces = build_invite_batch_record(
        inviter_cid=str(args.inviter_cid),
        batch_id=str(args.batch_id),
        count=int(args.count),
        created_epoch=int(args.created_epoch),
        inviter_sig=str(args.inviter_sig),
    )
    output = {
        "private_invite_nonces": list(private_nonces),
        "record_cid": record.canonical_cid(),
        "record_type": "InviteBatchRecord",
        "runtime_version": "invite_batch_runtime_1573z.v0.1",
        "invite_batch_record": record.to_dict(),
        "production_graph_write": False,
    }
    output_path = getattr(args, "output", "") or ""
    if output_path:
        return {"action": "invite-create", "output_path": _write_local_json_file(output_path, output)}
    return {"action": "invite-create", "output": output}


def _run_identity_invite_hint_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    """Generate a signed bootstrap peer-hints file for invite-bundle assembly."""

    import secrets
    from urllib.parse import urlsplit

    from cryptography.hazmat.primitives.asymmetric.mldsa import MLDSA65PrivateKey

    from ilc_core.crypto.pq_signature_verify import verify_mldsa65_signature
    from ilc_core.network.d2d.peer_advertisement import (
        MAX_PEER_ADVERTISEMENT_EPOCH,
        MAX_TTL_EPOCHS,
        PEER_ADVERTISEMENT_SCHEMA_VERSION,
        PeerAdvertisement,
        TransportEndpoint,
    )

    def require_uint_arg(value: object, token: str, *, min_value: int, max_value: int) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(token)
        if value < min_value or value > max_value:
            raise ValueError(token)
        return value

    relay_url = (getattr(args, "relay_url", None) or "").strip()
    if not relay_url:
        raise ValueError("peer_hint_relay_url_required")
    output_path_str = (getattr(args, "output", None) or "").strip()
    if not output_path_str:
        raise ValueError("peer_hint_output_required")

    peer_epoch = require_uint_arg(
        getattr(args, "peer_epoch", 0),
        "peer_hint_peer_epoch_invalid",
        min_value=0,
        max_value=MAX_PEER_ADVERTISEMENT_EPOCH,
    )
    ttl_epochs = require_uint_arg(
        getattr(args, "ttl_epochs", MAX_TTL_EPOCHS),
        "peer_hint_ttl_epochs_out_of_range",
        min_value=1,
        max_value=MAX_TTL_EPOCHS,
    )
    protocol_version = (getattr(args, "protocol_version", None) or "ilc.v0.4").strip()
    if (
        not protocol_version
        or len(protocol_version) > 64
        or any(char.isspace() for char in protocol_version)
    ):
        raise ValueError("peer_hint_protocol_version_invalid")
    label = (getattr(args, "label", None) or "bootstrap-hint").strip()
    if (
        not label
        or len(label) > 64
        or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]*", label) is None
    ):
        raise ValueError("peer_hint_label_invalid")

    parsed = urlsplit(relay_url)
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("peer_hint_relay_url_invalid") from exc
    if (
        parsed.scheme != "https"
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path not in ("", "/")
        or not parsed.hostname
        or port is None
    ):
        if parsed.scheme != "https":
            raise ValueError("peer_hint_relay_url_must_be_https")
        raise ValueError("peer_hint_relay_url_invalid")

    endpoint = TransportEndpoint.from_mapping(
        {
            "host": parsed.hostname.lower(),
            "port": port,
            "scheme": "https",
        },
        allow_private_address_literals=True,
    )

    private_key = MLDSA65PrivateKey.generate()
    public_key = private_key.public_key().public_bytes_raw()
    pubkey_hex = public_key.hex()
    key_binding_ref = f"{label}-{secrets.token_hex(8)}"
    agent_id = hashlib.sha384(
        b"bootstrap_peer_hint_agent_pubkey:" + public_key
    ).hexdigest()
    installed_slices_digest = hashlib.sha384(
        b"bootstrap_peer_hint_installed_slices:" + protocol_version.encode("utf-8")
    ).hexdigest()
    body_for_signing: dict[str, Any] = {
        "agent_id": agent_id,
        "content_availability_count": 0,
        "installed_slices_digest": installed_slices_digest,
        "peer_timestamp_epoch": peer_epoch,
        "protocol_version": protocol_version,
        "transport_endpoint": endpoint.to_dict(),
        "ttl_epochs": ttl_epochs,
    }
    body_bytes = json.dumps(
        body_for_signing,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    sig_hex = private_key.sign(body_bytes).hex()
    advert = PeerAdvertisement(
        agent_id=agent_id,
        transport_endpoint=endpoint,
        protocol_version=protocol_version,
        installed_slices_digest=installed_slices_digest,
        content_availability_count=0,
        peer_timestamp_epoch=peer_epoch,
        ttl_epochs=ttl_epochs,
        ml_dsa_signature=sig_hex,
        key_binding_ref=key_binding_ref,
        schema_version=PEER_ADVERTISEMENT_SCHEMA_VERSION,
    )
    if advert.to_canonical_json() != body_bytes:
        raise ValueError("peer_hint_internal_body_mismatch")
    if not advert.verify(verify_mldsa65_signature, pubkey_hex=pubkey_hex):
        raise ValueError("peer_hint_internal_signature_verification_failed")

    hints_payload: dict[str, Any] = {
        "known_peer_hint_key_bindings": {key_binding_ref: pubkey_hex},
        "known_peer_hints": [advert.to_dict()],
        "schema_version": "bootstrap_peer_hints.v0.1",
    }
    output_path = Path(output_path_str).expanduser()
    _write_json_file_atomic(output_path, hints_payload, indent=2, mode=0o644)

    return {
        "action": "peer_hint_created",
        "agent_id": agent_id,
        "key_binding_ref": key_binding_ref,
        "mldsa_pubkey_hex": pubkey_hex,
        "output_path": str(output_path),
        "peer_timestamp_epoch": peer_epoch,
        "transport_endpoint": endpoint.to_url(),
        "ttl_epochs": ttl_epochs,
    }


def _run_identity_invite_bundle_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    from ilc_core.bundle.atlas_slice_verifier import (
        AtlasSliceVerifierError,
        verify_portable_manifest_witness,
    )
    from ilc_core.bundle.default_public_rc_starmap import (
        build_default_public_rc_starmap_payload,
        build_default_public_rc_starmap_witness,
    )
    from ilc_core.genesis.invitation_provenance_record import (
        InvitationProvenanceError,
        build_nonce_membership_proof,
        invite_batch_record_from_dict,
        verify_nonce_membership_proof,
    )
    from ilc_core.sidecars.starmap_installer import (
        StarMapInstallerError,
        verify_starmap_manifest,
    )

    batch_payload = _read_local_json_file(str(args.batch_json_path))
    invite_batch_record = _required_mapping(
        batch_payload.get("invite_batch_record"),
        "invite_bundle_batch_record_missing",
    )
    private_nonce_values = batch_payload.get("private_invite_nonces")
    if not isinstance(private_nonce_values, list) or not private_nonce_values:
        raise ValueError("invite_bundle_private_nonces_missing")
    nonce_index = int(getattr(args, "nonce_index"))
    if nonce_index < 0 or nonce_index >= len(private_nonce_values):
        raise ValueError("invite_bundle_nonce_index_invalid")
    nonces = tuple(_invite_bundle_nonce_bytes(value) for value in private_nonce_values)
    try:
        batch = invite_batch_record_from_dict(invite_batch_record)
        if int(batch.count) != len(nonces):
            raise InvitationProvenanceError("invite_bundle_nonce_count_mismatch")
        proof = build_nonce_membership_proof(nonces=nonces, nonce_index=nonce_index)
        verify_nonce_membership_proof(
            nonce_bytes=nonces[nonce_index],
            nonce_merkle_root=batch.nonce_merkle_root,
            count=batch.count,
            proof=proof,
        )
    except InvitationProvenanceError as exc:
        raise ValueError(f"invite_bundle_nonce_proof_invalid:{exc}") from exc

    starmap_path = str(getattr(args, "starmap_path", "") or "")
    starmap_payload = (
        _read_local_json_file(starmap_path)
        if starmap_path
        else build_default_public_rc_starmap_payload()
    )
    try:
        verify_starmap_manifest(starmap_payload)
        witness = build_default_public_rc_starmap_witness(starmap_payload)
        verify_portable_manifest_witness(witness)
    except (AtlasSliceVerifierError, StarMapInstallerError) as exc:
        raise ValueError(f"invite_bundle_starmap_invalid:{exc}") from exc

    intended_epoch = getattr(args, "intended_epoch")
    if isinstance(intended_epoch, bool) or not isinstance(intended_epoch, int) or intended_epoch < 0:
        raise ValueError("invite_bundle_intended_epoch_invalid")
    intended_profile = str(getattr(args, "intended_profile"))
    if not intended_profile:
        raise ValueError("invite_bundle_intended_profile_invalid")
    output = {
        "atlas_slice_manifest_witness": witness,
        "intended_epoch": intended_epoch,
        "intended_profile": intended_profile,
        "invite_batch_record": batch.to_dict(),
        "invite_id": str(batch.batch_id),
        "nonce_membership_proof": [dict(item) for item in proof],
        "private_invite_nonce": nonces[nonce_index].hex(),
        "starmap_manifest_payload": starmap_payload,
    }
    output.update(_invite_bundle_optional_bootstrap_fields(args))
    output_path = getattr(args, "output", "") or ""
    if output_path:
        return {"action": "invite-bundle", "output_path": _write_local_json_file(output_path, output)}
    return {"action": "invite-bundle", "output": output}


def _run_identity_invite_generate_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    """Generate local or relay-hosted invite bundles with zero required flags."""

    import secrets
    import tempfile

    from ilc_core.genesis.invitation_provenance_record import build_invite_batch_record
    from ilc_core.identity.bls_backend import (
        public_key_from_secret_key_hex,
        sign_relay_invite_store_digest,
    )
    from ilc_core.identity.first_run_provisioning import identity_root
    from ilc_core.network.relay.relay_server import (
        attach_shortcode_invite_bundle_auth,
        encode_shortcode_invite_bundle,
        relay_invite_store_payload_ref,
    )

    slots = _require_uint_arg(
        getattr(args, "slots", 1),
        "invite_generate_slots_invalid",
        min_value=1,
        max_value=10_000,
    )
    ttl_seconds = _parse_invite_duration_seconds(str(getattr(args, "ttl", "24h")))
    relay_url = str(getattr(args, "relay_url", "") or "").strip()
    relay_tls_pin = str(getattr(args, "relay_tls_cert_der_sha256", "") or "").strip()
    bundled_records = _load_bundled_relay_records_for_generate()
    if relay_url:
        matches = [
            record for record in bundled_records if record.get("control_url") == relay_url
        ]
        if matches:
            bundled_tls_pin = _install_relay_record_tls_pin(matches[0])
            if relay_tls_pin and relay_tls_pin != bundled_tls_pin:
                raise ValueError("invite_generate_relay_tls_pin_mismatch")
            relay_tls_pin = bundled_tls_pin
        elif not relay_tls_pin:
            raise ValueError("invite_generate_relay_tls_cert_der_sha256_required")
    elif bundled_records:
        selected = sorted(
            bundled_records,
            key=lambda record: (
                str(record.get("control_url")),
                str(record.get("relay_agent_id")),
            ),
        )[0]
        relay_url = str(selected.get("control_url") or "")
        relay_tls_pin = _install_relay_record_tls_pin(selected)
    if not relay_url:
        raise ValueError("invite_generate_no_relay_url_and_no_bundled_capsule")

    root = identity_root(Path.home())
    signing_key_path = root / "signing_key.hex"
    agent_id_path = root / "agent_id"
    try:
        secret_key_hex = signing_key_path.read_text(encoding="utf-8").strip()
        inviting_agent_id = agent_id_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError("invite_generate_identity_required") from exc
    inviting_bls_public_key_hex = public_key_from_secret_key_hex(secret_key_hex)
    if not _AGENT_ID_HEX_RE.fullmatch(inviting_agent_id):
        raise ValueError("invite_generate_inviting_agent_id_invalid")

    batch_id = str(getattr(args, "batch_id", "") or f"invite-generate-{secrets.token_hex(8)}")
    record, private_nonces = build_invite_batch_record(
        inviter_cid=inviting_agent_id,
        batch_id=batch_id,
        count=slots,
        created_epoch=0,
        inviter_sig="shortcode-bundle-auth-required",
    )
    bundles: list[dict[str, Any]] = []
    with tempfile.TemporaryDirectory(prefix="ilc-invite-generate-") as tmp:
        tmp_path = Path(tmp)
        hints_path = tmp_path / "bootstrap_peer_hints.json"
        _run_identity_invite_hint_subcommand(
            argparse.Namespace(
                relay_url=relay_url,
                output=str(hints_path),
                peer_epoch=0,
                ttl_epochs=4,
                protocol_version="ilc.v0.4",
                label="invite-generate",
            )
        )
        relay_capsule = _load_bundled_relay_capsule_payload()
        for index, nonce in enumerate(private_nonces):
            proof = _build_invite_generate_nonce_proof(private_nonces, index)
            bundle = {
                "atlas_slice_manifest_witness": _default_public_rc_starmap_witness(),
                "intended_epoch": 0,
                "intended_profile": str(
                    getattr(args, "intended_profile", "public_rc_invitee_bootstrap")
                    or "public_rc_invitee_bootstrap"
                ),
                "invite_batch_record": record.to_dict(),
                "invite_id": record.batch_id,
                "known_peer_hint_key_bindings": _read_local_json_file(str(hints_path))[
                    "known_peer_hint_key_bindings"
                ],
                "known_peer_hints": _read_local_json_file(str(hints_path))[
                    "known_peer_hints"
                ],
                "nonce_membership_proof": [dict(item) for item in proof],
                "private_invite_nonce": nonce,
                "relay_bootstrap_capsule": relay_capsule,
                "starmap_manifest_payload": _default_public_rc_starmap_payload(),
            }
            bundles.append(
                attach_shortcode_invite_bundle_auth(
                    bundle,
                    inviting_agent_id=inviting_agent_id,
                    inviting_bls_public_key_hex=inviting_bls_public_key_hex,
                    inviting_bls_secret_key_hex=secret_key_hex,
                )
            )

    store_request = {
        "bundles": [encode_shortcode_invite_bundle(bundle) for bundle in bundles],
        "inviting_agent_id": inviting_agent_id,
        "inviting_bls_public_key_hex": inviting_bls_public_key_hex,
        "ttl_seconds": ttl_seconds,
    }
    store_request["request_signature"] = sign_relay_invite_store_digest(
        secret_key_hex,
        relay_invite_store_payload_ref(store_request),
    )
    output_path = str(getattr(args, "output", "") or "")
    if bool(getattr(args, "stdout", False)):
        return {"action": "invite-generate", "output": bundles[0] if slots == 1 else {"bundles": bundles}}
    if output_path:
        payload = bundles[0] if slots == 1 else {"bundles": bundles}
        _write_json_file_atomic(Path(output_path).expanduser(), payload, indent=2, mode=0o600)
    result: dict[str, Any] = {
        "action": "invite-generate",
        "bundle_count": slots,
        "inviting_agent_id": inviting_agent_id,
        "inviting_bls_public_key_hex": inviting_bls_public_key_hex,
        "output_path": output_path or "",
        "relay_url": relay_url,
        "store_request": store_request if bool(getattr(args, "emit_store_request", False)) else None,
        "upload": bool(getattr(args, "upload", False)),
    }
    if bool(getattr(args, "upload", False)):
        if not relay_tls_pin:
            raise ValueError("invite_generate_relay_tls_cert_der_sha256_required")
        store_response = _post_invite_store_request(
            relay_url=relay_url,
            tls_cert_der_sha256=relay_tls_pin,
            store_request=store_request,
        )
        result["code"] = store_response["code"]
        result["install_command"] = f"curl -fsSL https://ilc.network/install.sh | bash -s -- --invite-code {store_response['code']}"
        result["status_url"] = store_response.get("status_url", "")
        result["store_response"] = store_response
    return result


def _require_uint_arg(value: object, token: str, *, min_value: int, max_value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(token)
    if value < min_value or value > max_value:
        raise ValueError(token)
    return value


def _parse_invite_duration_seconds(value: str) -> int:
    text = value.strip().lower()
    match = re.fullmatch(r"([1-9][0-9]*)([smhd])", text)
    if match is None:
        raise ValueError("invite_generate_ttl_invalid")
    amount = int(match.group(1))
    multiplier = {"s": 1, "m": 60, "h": 3600, "d": 86400}[match.group(2)]
    seconds = amount * multiplier
    if seconds > 30 * 24 * 60 * 60:
        raise ValueError("invite_generate_ttl_invalid")
    return seconds


def _load_bundled_relay_capsule_payload() -> dict[str, Any]:
    import importlib.resources as importlib_resources

    resource = importlib_resources.files("ilc_core.data").joinpath(
        "relay_bootstrap_capsule.json"
    )
    return _loads_json_no_constants(resource.read_text(encoding="utf-8"))


def _load_bundled_relay_records_for_generate() -> tuple[dict[str, Any], ...]:
    try:
        capsule = _load_bundled_relay_capsule_payload()
        if not isinstance(capsule, dict):
            return ()
        return _install_verified_relay_bootstrap_records(
            capsule,
            expected_network_id=INSTALL_RELAY_DEFAULT_NETWORK_ID,
            current_epoch=0,
        )
    except (FileNotFoundError, ValueError):
        return ()


def _post_invite_store_request(
    *,
    relay_url: str,
    tls_cert_der_sha256: str,
    store_request: dict[str, Any],
) -> dict[str, Any]:
    import http.client
    import ssl

    from ilc_core.network.relay.relay_server import RELAY_INVITE_STORE_PATH

    parsed = urlparse(relay_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("invite_generate_relay_url_invalid")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("invite_generate_relay_url_invalid")
    if parsed.path not in ("", "/"):
        raise ValueError("invite_generate_relay_url_invalid")
    clean_tls_pin = _install_relay_tls_pin(
        tls_cert_der_sha256,
        "invite_generate_relay_tls_cert_der_sha256_invalid",
    )
    body = json.dumps(
        store_request,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode("utf-8")
    if len(body) > 16 * 1024 * 1024:
        raise ValueError("invite_generate_store_request_too_large")

    context = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection(
        parsed.hostname,
        port=parsed.port or 443,
        timeout=15,
        context=context,
    )
    try:
        conn.connect()
        if conn.sock is None:
            raise ValueError("invite_generate_relay_tls_connection_failed")
        cert_der = conn.sock.getpeercert(binary_form=True)
        actual_pin = hashlib.sha256(cert_der).hexdigest()
        if actual_pin != clean_tls_pin:
            raise ValueError("invite_generate_relay_tls_pin_mismatch")
        conn.request(
            "POST",
            RELAY_INVITE_STORE_PATH,
            body=body,
            headers={
                "Accept": "application/json",
                "Content-Length": str(len(body)),
                "Content-Type": "application/json",
                "User-Agent": "ilc-invite-generate/1",
            },
        )
        response = conn.getresponse()
        raw = response.read(65_537)
        if len(raw) > 65_536:
            raise ValueError("invite_generate_store_response_too_large")
        try:
            payload = _loads_json_no_constants(raw.decode("utf-8"))
        except (UnicodeDecodeError, ValueError) as exc:
            raise ValueError("invite_generate_store_response_invalid") from exc
        if not isinstance(payload, dict):
            raise ValueError("invite_generate_store_response_invalid")
        if response.status != 200:
            token = payload.get("error")
            if not isinstance(token, str) or not token:
                token = "invite_generate_store_failed"
            raise ValueError(f"invite_generate_store_failed:{response.status}:{token}")
        code = payload.get("code")
        if not isinstance(code, str) or not code:
            raise ValueError("invite_generate_store_response_code_missing")
        return dict(payload)
    finally:
        conn.close()


def _load_first_bundled_relay_url() -> str:
    records = _load_bundled_relay_records_for_generate()
    if not records:
        return ""
    selected = sorted(records, key=lambda record: str(record.get("control_url")))[0]
    return str(selected.get("control_url") or "")


def _default_public_rc_starmap_payload() -> dict[str, Any]:
    from ilc_core.bundle.default_public_rc_starmap import (
        build_default_public_rc_starmap_payload,
    )

    return build_default_public_rc_starmap_payload()


def _default_public_rc_starmap_witness() -> dict[str, Any]:
    from ilc_core.bundle.default_public_rc_starmap import (
        build_default_public_rc_starmap_payload,
        build_default_public_rc_starmap_witness,
    )

    return build_default_public_rc_starmap_witness(
        build_default_public_rc_starmap_payload()
    )


def _build_invite_generate_nonce_proof(
    private_nonces: tuple[str, ...],
    nonce_index: int,
) -> tuple[dict[str, str], ...]:
    from ilc_core.genesis.invitation_provenance_record import build_nonce_membership_proof

    nonces = tuple(bytes.fromhex(value) for value in private_nonces)
    return build_nonce_membership_proof(nonces=nonces, nonce_index=nonce_index)


def _invite_bundle_optional_bootstrap_fields(args: argparse.Namespace) -> dict[str, Any]:
    fields: dict[str, Any] = {}
    genesis_state_root = str(getattr(args, "genesis_state_root", "") or "")
    if genesis_state_root:
        from ilc_core.identity.first_run_provisioning import GENESIS_ROOT_ENVELOPE_HASH

        if genesis_state_root != GENESIS_ROOT_ENVELOPE_HASH:
            raise ValueError("invite_bundle_genesis_state_root_mismatch")
        fields["genesis_state_root"] = genesis_state_root
    inviter_connectivity_mode = str(getattr(args, "inviter_connectivity_mode", "") or "")
    if inviter_connectivity_mode:
        try:
            from ilc_core.network.connectivity_mode import ConnectivityMode

            fields["inviter_connectivity_mode"] = ConnectivityMode(
                inviter_connectivity_mode
            ).value
        except Exception as exc:
            raise ValueError("invite_bundle_inviter_connectivity_mode_invalid") from exc

    peer_hints_path = str(getattr(args, "known_peer_hints_path", "") or "")
    if peer_hints_path:
        hints_payload = _read_local_json_file_bounded(
            peer_hints_path,
            max_bytes=INSTALL_BOOTSTRAP_ATTACHMENT_MAX_BYTES,
            too_large_token="invite_bundle_known_peer_hints_too_large",
            invalid_token="invite_bundle_known_peer_hints_json_invalid",
            object_token="invite_bundle_known_peer_hints_payload_invalid",
        )
        hints = hints_payload.get("known_peer_hints")
        bindings = hints_payload.get("known_peer_hint_key_bindings")
        if not isinstance(hints, list):
            raise ValueError("invite_bundle_known_peer_hints_invalid")
        if len(hints) > INSTALL_KNOWN_PEER_HINTS_MAX_COUNT:
            raise ValueError("invite_bundle_known_peer_hints_too_many")
        if any(not isinstance(hint, dict) for hint in hints):
            raise ValueError("invite_bundle_known_peer_hint_invalid")
        if not isinstance(bindings, dict):
            raise ValueError("invite_bundle_known_peer_hint_key_bindings_invalid")
        if any(
            not isinstance(key, str) or not isinstance(value, str)
            for key, value in bindings.items()
        ):
            raise ValueError("invite_bundle_known_peer_hint_key_bindings_invalid")
        fields["known_peer_hints"] = hints
        fields["known_peer_hint_key_bindings"] = bindings

    relay_capsule_path = str(getattr(args, "relay_bootstrap_capsule_path", "") or "")
    if relay_capsule_path:
        fields["relay_bootstrap_capsule"] = _read_local_json_file_bounded(
            relay_capsule_path,
            max_bytes=INSTALL_BOOTSTRAP_ATTACHMENT_MAX_BYTES,
            too_large_token="invite_bundle_relay_bootstrap_capsule_too_large",
            invalid_token="invite_bundle_relay_bootstrap_capsule_json_invalid",
            object_token="invite_bundle_relay_bootstrap_capsule_invalid",
        )

    fetch_fields = {
        "bootstrap_fetch_bundle_cid": str(
            getattr(args, "bootstrap_fetch_bundle_cid", "") or ""
        ),
        "bootstrap_fetch_genesis_authority_pubkey_hex": str(
            getattr(args, "bootstrap_fetch_genesis_authority_pubkey_hex", "") or ""
        ),
        "bootstrap_fetch_seed_peer_endpoint": str(
            getattr(args, "bootstrap_fetch_seed_peer_endpoint", "") or ""
        ),
    }
    present_fetch = {key for key, value in fetch_fields.items() if value}
    if present_fetch and present_fetch != set(fetch_fields):
        raise ValueError("invite_bundle_bootstrap_fetch_material_incomplete")
    if present_fetch:
        from ilc_core.crypto.pq_signature_verify import _MLDSA_PK_HEX_LENGTH
        from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint

        try:
            seed_peer_endpoint = validate_peer_endpoint(
                fetch_fields["bootstrap_fetch_seed_peer_endpoint"]
            )
        except Exception as exc:
            raise ValueError("invite_bundle_bootstrap_fetch_seed_peer_endpoint_invalid") from exc
        bundle_cid = fetch_fields["bootstrap_fetch_bundle_cid"]
        if (
            not bundle_cid
            or bundle_cid.strip() != bundle_cid
            or any(char.isspace() for char in bundle_cid)
            or len(bundle_cid) > 512
        ):
            raise ValueError("invite_bundle_bootstrap_fetch_bundle_cid_invalid")
        genesis_pubkey = fetch_fields["bootstrap_fetch_genesis_authority_pubkey_hex"]
        if (
            len(genesis_pubkey) != _MLDSA_PK_HEX_LENGTH
            or _LOWER_HEX_RE.fullmatch(genesis_pubkey) is None
        ):
            raise ValueError(
                "invite_bundle_bootstrap_fetch_genesis_authority_pubkey_hex_invalid"
            )
        fields.update(
            {
                "bootstrap_fetch_bundle_cid": bundle_cid,
                "bootstrap_fetch_genesis_authority_pubkey_hex": genesis_pubkey,
                "bootstrap_fetch_seed_peer_endpoint": seed_peer_endpoint,
            }
        )
    _reject_float(fields, "invite_bundle_optional_bootstrap_float_not_allowed")
    return fields


def _invite_bundle_nonce_bytes(value: object) -> bytes:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError("invite_bundle_private_nonce_invalid")
    if any(char not in "0123456789abcdef" for char in value):
        raise ValueError("invite_bundle_private_nonce_invalid")
    try:
        return bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError("invite_bundle_private_nonce_invalid") from exc


def _identity_seed_bytes_from_hex(identity_seed_hex: object) -> bytes:
    if not isinstance(identity_seed_hex, str) or len(identity_seed_hex) != 64:
        raise ValueError("identity_seed_hex_must_be_64_lower_hex_chars")
    if any(char not in "0123456789abcdef" for char in identity_seed_hex):
        raise ValueError("identity_seed_hex_must_be_64_lower_hex_chars")
    return bytes.fromhex(identity_seed_hex)


def _identity_init_int_arg(args: argparse.Namespace, name: str) -> int:
    value = getattr(args, name)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name}_must_be_int")
    return value


def _apply_validator_candidate_enrollment_state(
    args: argparse.Namespace,
    state: dict[str, Any],
    enrollment_agent_id: str,
) -> None:
    validator_participation_enabled = not bool(getattr(args, "no_validator", False))
    state["validator_participation_enabled"] = validator_participation_enabled
    if not validator_participation_enabled:
        state["validator_role_record_status"] = "opted_out"
        return

    validator_key = getattr(args, "validator_key", "") or ""
    validator_endpoint = getattr(args, "validator_endpoint", "") or ""
    validator_material_supplied = bool(validator_key or validator_endpoint)
    if not validator_material_supplied:
        state["validator_role_record_status"] = "candidate_pending_validator_key_material"
        return
    if not validator_key or not validator_endpoint:
        raise ValueError("validator_candidate_material_incomplete")

    identity_seed_hex = getattr(args, "identity_seed_hex", "") or ""
    if not identity_seed_hex:
        raise ValueError("identity_seed_hex_required_for_validator_candidate")

    from ilc_core.identity.agent_id_runtime import derive_agent_id_v2
    from ilc_core.validator.admission_ejection_runtime import build_validator_role_record
    from ilc_core.validator.validator_key_derivation import (
        build_validator_key_derivation_record,
    )

    identity_seed = _identity_seed_bytes_from_hex(identity_seed_hex)
    derived_agent_id = derive_agent_id_v2(identity_seed)
    if enrollment_agent_id and enrollment_agent_id != derived_agent_id:
        raise ValueError("validator_candidate_agent_id_invite_mismatch")

    derivation_record = build_validator_key_derivation_record(identity_seed)
    role_record = build_validator_role_record(
        agent_id=derived_agent_id,
        validator_id=_identity_init_int_arg(args, "validator_id"),
        validator_key=validator_key,
        validator_endpoint=validator_endpoint,
        effective_from_epoch=_identity_init_int_arg(
            args,
            "validator_effective_from_epoch",
        ),
        network_id=getattr(args, "validator_network_id", "public-rc"),
        validator_participation_enabled=True,
        identity_seed_commitment=derivation_record["identity_seed_commitment"],
    )
    state["agent_id"] = derived_agent_id
    state["identity_seed_commitment"] = derivation_record["identity_seed_commitment"]
    state["validator_key_derivation_record"] = derivation_record
    state["validator_role_record"] = role_record.to_canonical_record()
    state["validator_role_record_status"] = "candidate_materialized"


def _run_identity_subcommand(args: argparse.Namespace, graph_state_path: Path) -> dict[str, Any]:
    state_path = _identity_state_path(graph_state_path)
    subcommand = getattr(args, "identity_subcommand", None)

    # Preserve D2e-03 compatibility for bare `ilc identity`.
    if not subcommand:
        return {
            "lineage_id": "lineage-local",
            "status": "active",
            "export_ref": "identity-local",
            "mode": "prototype_compat",
        }

    current = _load_identity_state(state_path)

    if subcommand == "invite":
        return _run_identity_invite_subcommand(args)

    if subcommand == "init":
        if current is not None:
            raise ValueError("identity_already_initialized")
        lineage_id = getattr(args, "lineage_id", None) or "lineage-local"
        key_ref = getattr(args, "key_ref", None) or "key-local-0"
        state = {
            "lineage_id": lineage_id,
            "status": "active",
            "key_ref": key_ref,
            "rotation_count": 0,
            "updated_at": _now_rfc3339_utc(),
        }
        invite_path = getattr(args, "invite", None)
        if invite_path:
            _require_invite_cli_enabled(args)
            from ilc_core.genesis.invitation_provenance_record import (
                build_invite_redemption_record,
                invite_batch_record_from_dict,
            )

            invite_payload = _read_local_json_file(invite_path)
            batch_payload = invite_payload.get("invite_batch_record")
            nonce_values = invite_payload.get("private_invite_nonces")
            if not isinstance(batch_payload, dict):
                raise ValueError("invite_batch_record_missing")
            if not isinstance(nonce_values, list) or len(nonce_values) == 0:
                raise ValueError("invite_nonce_missing")
            identity_seed_hex = getattr(args, "identity_seed_hex", "") or ""
            redeemer_pubkey_cid = getattr(args, "redeemer_pubkey_cid", "") or ""
            if not identity_seed_hex:
                raise ValueError("identity_seed_hex_required_for_invite_redemption")
            if not redeemer_pubkey_cid:
                raise ValueError("redeemer_pubkey_cid_required_for_invite_redemption")
            batch = invite_batch_record_from_dict(batch_payload)
            redemption = build_invite_redemption_record(
                batch=batch,
                nonce=str(nonce_values[0]),
                nonce_membership_proof=(),
                redeemer_pubkey_cid=redeemer_pubkey_cid,
                identity_seed=identity_seed_hex,
                redemption_epoch=int(getattr(args, "redemption_epoch", 0)),
            )
            state["invite_redemption_record"] = redemption.to_dict()
            state["invite_redemption_record_cid"] = redemption.canonical_cid()
            state["invite_runtime_version"] = "invite_batch_runtime_1573z.v0.1"
            state["production_graph_write"] = False

        enrollment_agent_id = ""
        if "invite_redemption_record" in state:
            invite_record = state["invite_redemption_record"]
            if isinstance(invite_record, dict):
                maybe_agent_id = invite_record.get("redeemer_agent_id")
                if isinstance(maybe_agent_id, str):
                    enrollment_agent_id = maybe_agent_id
        else:
            enrollment_agent_id = ""

        # Phase 1578a found no general enrollment runtime yet; identity init is
        # the current concrete enrollment hook until that runtime exists.
        from ilc_core.genesis.invite_enforcement import require_invite_for_enrollment

        require_invite_for_enrollment(
            enrollment_agent_id,
            state.get("invite_redemption_record"),
        )
        _apply_validator_candidate_enrollment_state(args, state, enrollment_agent_id)
        _write_identity_state(state_path, state)
        return {"action": "init", "state_path": str(state_path), "state": state}

    if current is None:
        raise ValueError("identity_not_initialized")

    if subcommand == "show":
        return {"action": "show", "state_path": str(state_path), "state": current}

    if subcommand == "rotate":
        new_key_ref = getattr(args, "new_key_ref", None)
        next_count = int(current.get("rotation_count", 0)) + 1
        current["rotation_count"] = next_count
        current["key_ref"] = new_key_ref or f"key-local-{next_count}"
        current["status"] = "active"
        current["updated_at"] = _now_rfc3339_utc()
        _write_identity_state(state_path, current)
        return {"action": "rotate", "state_path": str(state_path), "state": current}

    if subcommand == "export":
        return {
            "action": "export",
            "state_path": str(state_path),
            "export": {
                "lineage_id": current.get("lineage_id"),
                "status": current.get("status"),
                "rotation_count": current.get("rotation_count"),
                "key_ref": current.get("key_ref"),
            },
        }

    raise ValueError(f"unknown_identity_subcommand:{subcommand}")


def _doctor_check_json_object(path: Path, required_field: str | None = None) -> bool:
    data = _read_json_object(path)
    if data is None:
        return False
    if required_field is not None:
        value = data.get(required_field)
        return isinstance(value, str) and bool(value)
    return True


def _run_doctor_subcommand(args: argparse.Namespace, graph_state_path: Path) -> dict[str, Any]:
    identity_path = _identity_state_path(graph_state_path)
    graph_path = graph_state_path
    balance_path = _default_balance_state_path()
    invite_nullifier_path = _home_ilc_state_path("invite_nullifiers.json")
    consent_gate_path = _home_ilc_state_path("consent_gate.json")
    sidecar_registry_path = _home_ilc_state_path("sidecar_registry.json")
    ccss_path = _ccss_home_path()

    checks = {
        "ilc_core_importable": True,
        "identity_initialized": _doctor_check_json_object(identity_path, "lineage_id"),
        "invite_nullifier_store_present": invite_nullifier_path.exists(),
        "consent_gate_configured": _doctor_check_json_object(consent_gate_path, "autonomy_level"),
        "sidecar_registry_present": sidecar_registry_path.exists(),
        "local_graph_state_readable": _doctor_check_json_object(graph_path),
        "balance_state_present": balance_path.exists(),
        "ccss_identity_present": ccss_path.is_dir(),
    }
    if not checks["identity_initialized"]:
        verdict = "not_setup"
        next_action = "ilc identity init"
        exit_code = 1
    elif all(checks.values()):
        verdict = "ready"
        next_action = "none"
        exit_code = 0
    else:
        verdict = "partial_setup"
        next_action = "ilc sidecar recipe apply"
        exit_code = 0
    return {
        "_exit_code": exit_code,
        "checks": checks,
        "next_action": next_action,
        "paths": {
            "balance_state": str(balance_path),
            "ccss_home": str(ccss_path),
            "consent_gate": str(consent_gate_path),
            "graph_state": str(graph_path),
            "identity_state": str(identity_path),
            "invite_nullifiers": str(invite_nullifier_path),
            "sidecar_registry": str(sidecar_registry_path),
        },
        "pretty_requested": bool(getattr(args, "pretty", False)),
        "read_only": True,
        "subcommand": "doctor",
        "verdict": verdict,
    }


def _format_doctor_pretty(data: dict[str, Any]) -> str:
    checks = data.get("checks")
    if not isinstance(checks, dict):
        checks = {}
    lines = [
        "ILC doctor",
        f"verdict: {data.get('verdict', 'unknown')}",
        f"next_action: {data.get('next_action', 'unknown')}",
        "",
        "checks:",
    ]
    for key in sorted(checks):
        lines.append(f"  {key:<32} {'pass' if checks[key] else 'missing'}")
    return "\n".join(lines)


def _load_balance_state(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8")
    data = _loads_json_no_constants(raw)
    if not isinstance(data, dict):
        raise ValueError("balance_state_not_object")
    return data


def _require_balance_decimal_string(value: Any, *, field_name: str) -> str:
    from decimal import Decimal, InvalidOperation

    if isinstance(value, float) or isinstance(value, bool):
        raise ValueError(f"{field_name}_must_be_exact_decimal_string")
    if not isinstance(value, str):
        raise ValueError(f"{field_name}_must_be_exact_decimal_string")
    try:
        amount = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name}_must_be_exact_decimal_string") from exc
    if not amount.is_finite():
        raise ValueError(f"{field_name}_must_be_finite")
    if amount < Decimal("0"):
        raise ValueError(f"{field_name}_must_be_non_negative")
    return format(amount.normalize(), "f")


def _phase_1561_smoke_balance_report(
    agent_id: str,
    state: dict[str, Any],
    state_path: Path,
) -> dict[str, Any]:
    claiming_agent_id = state.get("claiming_agent_id")
    verifying_agent_id = state.get("verifying_agent_id")
    known_agent_ids = [
        value for value in (claiming_agent_id, verifying_agent_id) if isinstance(value, str)
    ]
    if agent_id not in known_agent_ids:
        raise ValueError("balance_agent_not_found")

    amounts = state.get("amounts")
    if not isinstance(amounts, dict):
        raise ValueError("balance_state_amounts_missing")
    scheduled_emission = _require_balance_decimal_string(
        amounts.get("scheduled_emission_pool_ilc"),
        field_name="scheduled_emission_pool_ilc",
    )

    role = "claiming_agent" if agent_id == claiming_agent_id else "verifying_agent"
    return {
        "agent_id": agent_id,
        "balance_ilc": "0",
        "balance_status": "not_settled_no_ledger_write",
        "claim_id": state.get("claim_id"),
        "pending_smoke_report": {
            "amount_ilc": scheduled_emission if role == "claiming_agent" else "0",
            "event_hash": state.get("ecu_credit_event_hash"),
            "is_ledger_balance": False,
            "role": role,
            "settlement_root_hash": state.get("settlement_root_hash"),
        },
        "production_emission_activated": state.get("production_emission_activated"),
        "report_mode": "phase_1561_smoke_evidence",
        "state_path": str(state_path),
    }


def _run_balance_command(args: argparse.Namespace) -> dict[str, Any]:
    agent_id = getattr(args, "agent_id", None)
    state_path = Path(getattr(args, "balance_state_json", None) or _default_balance_state_path())
    if not agent_id:
        return {
            "account_id": "prototype_compat",
            "balance_ilc": "0",
            "pending_balance_ilc": "0",
            "report_mode": "prototype_compat",
        }

    state = _load_balance_state(state_path)
    if state is None:
        return {
            "agent_id": agent_id,
            "balance_ilc": "0",
            "balance_status": "state_file_absent",
            "pending_smoke_report": None,
            "report_mode": "no_local_state",
            "state_path": str(state_path),
        }
    if state.get("phase") == "1561":
        return _phase_1561_smoke_balance_report(agent_id, state, state_path)

    balances = state.get("balances")
    if isinstance(balances, dict) and agent_id in balances:
        return {
            "agent_id": agent_id,
            "balance_ilc": _require_balance_decimal_string(
                balances[agent_id],
                field_name="balance_ilc",
            ),
            "balance_status": "local_state_balance",
            "report_mode": "local_balance_state",
            "state_path": str(state_path),
        }
    raise ValueError("balance_agent_not_found")


def _read_graph_state(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"graph_state_read_failed:{exc}") from exc
    try:
        data = _loads_json_no_constants(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        detail = exc.msg if isinstance(exc, json.JSONDecodeError) else str(exc)
        raise ValueError(f"graph_state_invalid_json:{detail}") from exc
    if not isinstance(data, dict):
        raise ValueError("graph_state_not_object")
    return data


def _load_graph_state_for_query(path: Path) -> dict[str, Any]:
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise QueryCommandError("query_backend_unavailable", str(exc)) from exc


def _load_graph_state_for_verify(path: Path) -> dict[str, Any]:
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise VerifyCommandError("verify_backend_unavailable", str(exc)) from exc


def _load_graph_state_for_bundle(path: Path) -> dict[str, Any]:
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise BundleCommandError("bundle_backend_unavailable", str(exc)) from exc


def _load_bundle_state_for_bundle(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "d2e07.v0.1", "bundles": []}
    try:
        return _read_graph_state(path)
    except ValueError as exc:
        raise BundleCommandError("bundle_backend_unavailable", str(exc)) from exc


def _sorted_mapping(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {key: _sorted_mapping(obj[key]) for key in sorted(obj)}
    if isinstance(obj, list):
        return [_sorted_mapping(item) for item in obj]
    return obj


def _coerce_list(
    obj: Any,
    error_cls: type[QueryCommandError] | type[VerifyCommandError] | type[BundleCommandError],
    code: str,
    message: str,
) -> list[dict[str, Any]]:
    if obj is None:
        return []
    if not isinstance(obj, list):
        raise error_cls(code, message)
    rows: list[dict[str, Any]] = []
    for item in obj:
        if isinstance(item, dict):
            rows.append(item)
    return rows


def _query_node(state: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = _coerce_list(
        state.get("nodes"), QueryCommandError, "query_backend_unavailable", "graph_nodes_not_list"
    )
    node: dict[str, Any] | None = None
    for candidate in nodes:
        token = candidate.get("node_id", candidate.get("id"))
        if token is not None and str(token) == node_id:
            node = candidate
            break
    if node is None:
        raise QueryCommandError("query_not_found", f"node_not_found:{node_id}")
    return {"node_id": node_id, "node": _sorted_mapping(node), "query": "node"}


def _query_epoch(state: dict[str, Any], epoch_token: int) -> dict[str, Any]:
    epochs = _coerce_list(
        state.get("epochs"), QueryCommandError, "query_backend_unavailable", "graph_epochs_not_list"
    )
    epoch: dict[str, Any] | None = None
    for candidate in epochs:
        value = candidate.get("epoch")
        if value is None:
            value = candidate.get("epoch_id")
        if value is None:
            continue
        if str(value) == str(epoch_token):
            epoch = candidate
            break
    if epoch is None:
        raise QueryCommandError("query_not_found", f"epoch_not_found:{epoch_token}")
    return {"epoch": _sorted_mapping(epoch), "query": "epoch", "requested_epoch": epoch_token}


def _query_claim(state: dict[str, Any], claim_id: str) -> dict[str, Any]:
    nodes = _coerce_list(
        state.get("nodes"), QueryCommandError, "query_backend_unavailable", "graph_nodes_not_list"
    )
    matches: list[dict[str, Any]] = []
    for candidate in nodes:
        token = candidate.get("claim_id")
        if token is not None and str(token) == claim_id:
            matches.append(candidate)
    if not matches:
        raise QueryCommandError("query_not_found", f"claim_not_found:{claim_id}")
    stable_matches = sorted(
        (_sorted_mapping(match) for match in matches),
        key=lambda item: json.dumps(item, sort_keys=True),
    )
    return {
        "claim_id": claim_id,
        "count": len(stable_matches),
        "matches": stable_matches,
        "query": "claim",
    }


def _query_receipt(state: dict[str, Any], receipt_token: str) -> dict[str, Any]:
    from ilc_core.graph.sidecar_query_runtime import lookup_submission_receipt

    try:
        result = lookup_submission_receipt(receipt_token, state)
    except ValueError as exc:
        raise QueryCommandError("query_invalid_input", str(exc)) from exc
    return {"query": "receipt", "receipt": _sorted_mapping(result)}


def _query_command_token(args: argparse.Namespace) -> str:
    subcommand = getattr(args, "query_subcommand", None)
    if subcommand:
        return f"query {subcommand}"
    return "query"


def _run_query_subcommand(args: argparse.Namespace, graph_state_path: Path) -> tuple[str, dict[str, Any]]:
    subcommand = getattr(args, "query_subcommand", None)

    # CDL-075 truth primitive read path — does not load JSON graph state.
    if subcommand in {"truth-node", "truth-edges"}:
        from ilc_core.cli.d2e_query_truth_cli import (
            handle_query_truth_node,
            handle_query_truth_edges,
            QueryTruthCommandError,
        )
        try:
            if subcommand == "truth-node":
                data = handle_query_truth_node(str(args.node_id))
            else:
                data = handle_query_truth_edges(str(args.node_id))
        except QueryTruthCommandError as exc:
            raise QueryCommandError(exc.token, exc.message) from exc
        return _query_command_token(args), data

    state = _load_graph_state_for_query(graph_state_path)
    if subcommand == "node":
        return _query_command_token(args), _query_node(state, str(args.node_id))
    if subcommand == "epoch":
        return _query_command_token(args), _query_epoch(state, args.epoch)
    if subcommand == "claim":
        return _query_command_token(args), _query_claim(state, str(args.claim_id))
    if subcommand == "receipt":
        return _query_command_token(args), _query_receipt(state, str(args.receipt_token))
    raise QueryCommandError("query_invalid_input", "query_subcommand_missing")


def _verify_command_token(args: argparse.Namespace) -> str:
    subcommand = getattr(args, "verify_subcommand", None)
    if subcommand:
        return f"verify {subcommand}"
    return "verify"


def _check(check_type: str, passed: bool, detail: dict[str, Any] | None = None) -> dict[str, Any]:
    item = {"check_type": check_type, "passed": bool(passed)}
    if detail:
        item["detail"] = _sorted_mapping(detail)
    return item


def _verify_claim(state: dict[str, Any], claim_id: str) -> dict[str, Any]:
    nodes = _coerce_list(
        state.get("nodes"), VerifyCommandError, "verify_backend_unavailable", "graph_nodes_not_list"
    )
    matches = [candidate for candidate in nodes if str(candidate.get("claim_id", "")) == claim_id]
    checks = [
        _check("subject_exists", len(matches) > 0),
        _check("multi_match_supported", True, {"match_count": len(matches)}),
    ]
    if not matches:
        raise VerifyCommandError("verify_not_found", f"claim_not_found:{claim_id}")
    return {
        "subject": {"claim_id": claim_id},
        "verdict": {"verified": True, "verdict_code": "verify_claim_passed"},
        "checks": checks,
    }


def _verify_node(state: dict[str, Any], node_id: str) -> dict[str, Any]:
    nodes = _coerce_list(
        state.get("nodes"), VerifyCommandError, "verify_backend_unavailable", "graph_nodes_not_list"
    )
    node: dict[str, Any] | None = None
    for candidate in nodes:
        token = candidate.get("node_id", candidate.get("id"))
        if token is not None and str(token) == node_id:
            node = candidate
            break
    checks = [
        _check("subject_exists", node is not None),
        _check("node_identifier_consistency", True, {"accepted_keys": ["node_id", "id"]}),
    ]
    if node is None:
        raise VerifyCommandError("verify_not_found", f"node_not_found:{node_id}")
    return {
        "subject": {"node_id": node_id},
        "verdict": {"verified": True, "verdict_code": "verify_node_passed"},
        "checks": checks,
    }


def _verify_lineage(args: argparse.Namespace, graph_state_path: Path) -> dict[str, Any]:
    lineage_id = str(args.lineage_id)
    state_path = _identity_state_path(graph_state_path)
    current = _load_identity_state(state_path)
    if current is None:
        raise VerifyCommandError("verify_not_found", f"lineage_not_initialized:{lineage_id}")

    observed_lineage = str(current.get("lineage_id", ""))
    matched = observed_lineage == lineage_id
    checks = [
        _check("identity_state_present", True, {"state_path": str(state_path)}),
        _check("lineage_id_match", matched, {"observed_lineage_id": observed_lineage}),
    ]
    if not matched:
        raise VerifyCommandError("verify_not_found", f"lineage_not_found:{lineage_id}")

    return {
        "subject": {"lineage_id": lineage_id},
        "verdict": {"verified": True, "verdict_code": "verify_lineage_passed"},
        "checks": checks,
    }


def _run_verify_subcommand(args: argparse.Namespace, graph_state_path: Path) -> tuple[str, dict[str, Any]]:
    # Lineage verification is intentionally local-state only in Phase 302.
    subcommand = getattr(args, "verify_subcommand", None)
    if subcommand == "lineage":
        return _verify_command_token(args), _verify_lineage(args, graph_state_path)

    state = _load_graph_state_for_verify(graph_state_path)
    if subcommand == "claim":
        return _verify_command_token(args), _verify_claim(state, str(args.claim_id))
    if subcommand == "node":
        return _verify_command_token(args), _verify_node(state, str(args.node_id))
    raise VerifyCommandError("verify_invalid_input", "verify_subcommand_missing")


def _bundle_command_token(args: argparse.Namespace) -> str:
    subcommand = getattr(args, "bundle_subcommand", None)
    if subcommand:
        return f"bundle {subcommand}"
    return "bundle"


def _bundle_entry(
    state: dict[str, Any],
    bundle_cid: str,
) -> dict[str, Any]:
    bundles = _coerce_list(
        state.get("bundles"),
        BundleCommandError,
        "bundle_backend_unavailable",
        "bundle_entries_not_list",
    )
    for candidate in bundles:
        token = candidate.get("bundle_cid")
        if token is not None and str(token) == bundle_cid:
            return candidate
    raise BundleCommandError("bundle_not_found", f"bundle_not_found:{bundle_cid}")


def _canonical_sha256(value: Any) -> str:
    stable = json.dumps(_sorted_mapping(value), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()


def _bundle_inspect(bundle_cid: str, entry: dict[str, Any], bundle_state_path: Path) -> dict[str, Any]:
    provider = str(entry.get("provider", "local"))
    if provider == "blocked":
        raise BundleCommandError("bundle_provider_blocked", f"bundle_provider_blocked:{bundle_cid}")

    manifest = entry.get("manifest")
    checks = [
        _check("subject_exists", True),
        _check("manifest_object_present", isinstance(manifest, dict)),
        _check("provider_policy_allowed", True, {"provider": provider}),
    ]
    if not isinstance(manifest, dict):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_manifest_missing:{bundle_cid}")

    return {
        "subject": {
            "bundle_cid": bundle_cid,
            "bundle_state_path": str(bundle_state_path),
            "provider": provider,
            "subcommand": "inspect",
        },
        "result": {
            "status": "inspected",
            "manifest_keys": sorted(str(key) for key in manifest.keys()),
            "manifest_sha256": _canonical_sha256(manifest),
        },
        "checks": checks,
    }


def _bundle_verify(bundle_cid: str, entry: dict[str, Any], bundle_state_path: Path) -> dict[str, Any]:
    provider = str(entry.get("provider", "local"))
    if provider == "blocked":
        raise BundleCommandError("bundle_provider_blocked", f"bundle_provider_blocked:{bundle_cid}")

    manifest = entry.get("manifest")
    if not isinstance(manifest, dict):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_manifest_missing:{bundle_cid}")

    integrity: dict[str, Any] = {}
    raw_integrity = entry.get("integrity")
    if isinstance(raw_integrity, dict):
        integrity = raw_integrity
    expected_digest = None
    if isinstance(entry.get("manifest_sha256"), str):
        expected_digest = str(entry["manifest_sha256"])
    elif isinstance(integrity.get("manifest_sha256"), str):
        expected_digest = str(integrity["manifest_sha256"])

    observed_digest = _canonical_sha256(manifest)
    digest_matches = expected_digest is None or expected_digest == observed_digest
    checks = [
        _check("subject_exists", True),
        _check("manifest_object_present", True),
        _check("integrity_digest_available", expected_digest is not None),
        _check("integrity_digest_matches", digest_matches),
    ]
    if not digest_matches:
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_digest_mismatch:{bundle_cid}")

    return {
        "subject": {
            "bundle_cid": bundle_cid,
            "bundle_state_path": str(bundle_state_path),
            "provider": provider,
            "subcommand": "verify",
        },
        "result": {
            "status": "verified",
            "digest_source": "provided" if expected_digest is not None else "computed",
            "manifest_sha256": observed_digest,
        },
        "checks": checks,
    }


def _bundle_validate_local(
    bundle_cid: str,
    entry: dict[str, Any],
    graph_state_path: Path,
    bundle_state_path: Path,
) -> dict[str, Any]:
    provider = str(entry.get("provider", "local"))
    if provider == "blocked":
        raise BundleCommandError("bundle_provider_blocked", f"bundle_provider_blocked:{bundle_cid}")

    graph_state = _load_graph_state_for_bundle(graph_state_path)
    nodes = _coerce_list(
        graph_state.get("nodes"),
        BundleCommandError,
        "bundle_backend_unavailable",
        "graph_nodes_not_list",
    )

    graph_refs = entry.get("graph_refs")
    if graph_refs is None:
        graph_refs = {}
    if not isinstance(graph_refs, dict):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_graph_refs_invalid:{bundle_cid}")

    referenced_node_ids = graph_refs.get("node_ids", [])
    referenced_claim_ids = graph_refs.get("claim_ids", [])
    if not isinstance(referenced_node_ids, list) or not isinstance(referenced_claim_ids, list):
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_graph_refs_invalid:{bundle_cid}")

    node_id_set = {
        str(item.get("node_id", item.get("id")))
        for item in nodes
        if item.get("node_id", item.get("id")) is not None
    }
    claim_id_set = {str(item.get("claim_id")) for item in nodes if item.get("claim_id") is not None}

    requested_nodes = [str(token) for token in referenced_node_ids]
    requested_claims = [str(token) for token in referenced_claim_ids]
    missing_nodes = sorted(token for token in requested_nodes if token not in node_id_set)
    missing_claims = sorted(token for token in requested_claims if token not in claim_id_set)
    nodes_ok = not missing_nodes
    claims_ok = not missing_claims

    checks = [
        _check("subject_exists", True),
        _check("graph_state_loaded", True, {"graph_state_path": str(graph_state_path)}),
        _check("referenced_nodes_present", nodes_ok, {"missing_nodes": missing_nodes}),
        _check("referenced_claims_present", claims_ok, {"missing_claims": missing_claims}),
    ]
    if not nodes_ok or not claims_ok:
        raise BundleCommandError("bundle_manifest_invalid", f"bundle_graph_refs_missing:{bundle_cid}")

    return {
        "subject": {
            "bundle_cid": bundle_cid,
            "bundle_state_path": str(bundle_state_path),
            "graph_state_path": str(graph_state_path),
            "provider": provider,
            "subcommand": "validate-local",
        },
        "result": {
            "status": "validated_local",
            "validated_node_refs": len(requested_nodes),
            "validated_claim_refs": len(requested_claims),
        },
        "checks": checks,
    }


def _run_bundle_subcommand(args: argparse.Namespace, _graph_state_path: Path) -> tuple[str, dict[str, Any]]:
    bundle_state_path = _default_bundle_state_path()
    subcommand = getattr(args, "bundle_subcommand", None)
    if subcommand == "generate-layer0":
        try:
            from ilc_core.cli.bundle_cli import generate_layer0_bundle_cli

            return _bundle_command_token(args), generate_layer0_bundle_cli(args)
        except ValueError as exc:
            raise BundleCommandError("bundle_invalid_input", str(exc)) from exc

    bundle_cid = str(getattr(args, "bundle_cid", ""))
    if not subcommand or not bundle_cid:
        raise BundleCommandError("bundle_invalid_input", "bundle_subcommand_missing")

    try:
        state = _load_bundle_state_for_bundle(bundle_state_path)
        entry = _bundle_entry(state, bundle_cid)

        if subcommand == "inspect":
            return _bundle_command_token(args), _bundle_inspect(bundle_cid, entry, bundle_state_path)
        if subcommand == "verify":
            return _bundle_command_token(args), _bundle_verify(bundle_cid, entry, bundle_state_path)
        if subcommand == "validate-local":
            graph_state_path = Path(str(args.bundle_graph_state))
            return _bundle_command_token(args), _bundle_validate_local(
                bundle_cid,
                entry,
                graph_state_path,
                bundle_state_path,
            )
        raise BundleCommandError("bundle_invalid_input", "bundle_subcommand_missing")
    except BundleCommandError:
        raise
    except (OSError, PermissionError) as exc:
        raise BundleCommandError("bundle_io_error", type(exc).__name__) from exc
    except json.JSONDecodeError as exc:
        raise BundleCommandError("bundle_json_invalid", f"byte_offset:{exc.pos}") from exc
    except Exception as exc:  # pragma: no cover - defensive mapping to contract token
        raise BundleCommandError("bundle_internal_error", type(exc).__name__) from exc


def _build_parser() -> JsonArgumentParser:
    parser = JsonArgumentParser(
        prog="ilc",
        description="ILC D2e-03 JSON-first CLI prototype",
    )
    parser.add_argument(
        "--graph-state",
        default=str(_default_graph_state_path()),
        help="Path to local JSON graph state file",
    )
    parser.add_argument(
        "--simulate-network-error",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    subparsers = parser.add_subparsers(dest="command", required=False)
    for command in ALL_COMMANDS:
        if command == "query":
            query_parser = subparsers.add_parser("query", help="Prototype `query` command")
            query_subparsers = query_parser.add_subparsers(dest="query_subcommand", required=True)

            p_node = query_subparsers.add_parser("node", help="Query by node identifier")
            p_node.add_argument("--node-id", required=True, help="Node identifier")

            p_epoch = query_subparsers.add_parser("epoch", help="Query by epoch identifier")
            p_epoch.add_argument("--epoch", type=int, required=True, help="Epoch number")

            p_claim = query_subparsers.add_parser("claim", help="Query by claim identifier")
            p_claim.add_argument("--claim-id", required=True, help="Claim identifier")

            p_receipt = query_subparsers.add_parser(
                "receipt",
                help="Look up a local graph submission receipt token",
            )
            p_receipt.add_argument("receipt_token", help="Local submission receipt token")

            p_truth_node = query_subparsers.add_parser(
                "truth-node",
                help="Query a persisted CDL-075 truth primitive node by CIDv1",
            )
            p_truth_node.add_argument(
                "--node-id", required=True, help="CIDv1 node identifier"
            )

            p_truth_edges = query_subparsers.add_parser(
                "truth-edges",
                help="List CDL-075 edges whose source or target matches the given identifier",
            )
            p_truth_edges.add_argument(
                "--node-id", required=True, help="CIDv1 node identifier or agent_id"
            )
            continue

        if command == "verify":
            verify_parser = subparsers.add_parser("verify", help="Prototype `verify` command")
            verify_subparsers = verify_parser.add_subparsers(dest="verify_subcommand", required=True)

            p_verify_claim = verify_subparsers.add_parser("claim", help="Verify by claim identifier")
            p_verify_claim.add_argument("--claim-id", required=True, help="Claim identifier")

            p_verify_node = verify_subparsers.add_parser("node", help="Verify by node identifier")
            p_verify_node.add_argument("--node-id", required=True, help="Node identifier")

            p_verify_lineage = verify_subparsers.add_parser("lineage", help="Verify by lineage identifier")
            p_verify_lineage.add_argument("--lineage-id", required=True, help="Lineage identifier")
            continue

        if command == "bundle":
            bundle_parser = subparsers.add_parser("bundle", help="Prototype `bundle` command")
            bundle_subparsers = bundle_parser.add_subparsers(dest="bundle_subcommand", required=True)

            p_bundle_inspect = bundle_subparsers.add_parser(
                "inspect",
                help="Inspect bundle metadata from local bundle state",
            )
            p_bundle_inspect.add_argument("--bundle-cid", required=True, help="Bundle CID")

            p_bundle_verify = bundle_subparsers.add_parser(
                "verify",
                help="Verify bundle manifest integrity from local bundle state",
            )
            p_bundle_verify.add_argument("--bundle-cid", required=True, help="Bundle CID")

            p_bundle_validate_local = bundle_subparsers.add_parser(
                "validate-local",
                help="Validate bundle graph references against supplied graph state path",
            )
            p_bundle_validate_local.add_argument("--bundle-cid", required=True, help="Bundle CID")
            p_bundle_validate_local.add_argument(
                "--graph-state",
                dest="bundle_graph_state",
                required=True,
                help="Path used only for validate-local graph-state checks",
            )
            p_bundle_generate_layer0 = bundle_subparsers.add_parser(
                "generate-layer0",
                help="Generate an unsigned ADR-0009 Layer0 protocol bundle",
            )
            p_bundle_generate_layer0.add_argument("--bundle-id", required=True, help="Bundle ID")
            p_bundle_generate_layer0.add_argument("--version", required=True, help="Bundle version")
            p_bundle_generate_layer0.add_argument(
                "--schemas",
                default="",
                help="Path to JSON file containing a list of schema records",
            )
            p_bundle_generate_layer0.add_argument(
                "--parameters",
                default="",
                help="Path to JSON file containing a parameters object",
            )
            p_bundle_generate_layer0.add_argument(
                "--include-truth-primitives",
                action="store_true",
                help="Include ratified Layer0 truth primitive schemas",
            )
            p_bundle_generate_layer0.add_argument(
                "--output",
                default="",
                help="Optional path for atomic canonical JSON output",
            )
            continue

        if command == "agent":
            agent_parser = subparsers.add_parser("agent", help="D2e agent identity commands")
            agent_subparsers = agent_parser.add_subparsers(dest="agent_subcommand", required=True)

            p_derive = agent_subparsers.add_parser("derive", help="Derive agent_id from root key hex")
            p_derive.add_argument(
                "--root-key-hex",
                required=True,
                help="Hex-encoded canonical root key bytes",
            )

            p_inspect = agent_subparsers.add_parser("inspect", help="Inspect serialized agent record JSON")
            p_inspect.add_argument(
                "--record-json",
                required=True,
                help="Path to agent record JSON file",
            )

            p_keygen = agent_subparsers.add_parser(
                "keygen",
                help="Generate a local Ed25519 action-signing hotkey",
            )
            p_keygen.add_argument(
                "--output",
                default=None,
                help="Optional output path for the PKCS8 PEM hotkey",
            )
            continue

        if command == "agent-bootstrap":
            agent_bootstrap_parser = subparsers.add_parser(
                "agent-bootstrap",
                help="Build a local agent-bootstrap plan from census intake",
            )
            agent_bootstrap_subparsers = agent_bootstrap_parser.add_subparsers(
                dest="agent_bootstrap_subcommand",
                required=True,
            )
            p_agent_bootstrap_plan = agent_bootstrap_subparsers.add_parser(
                "plan",
                help="Write a local agent-bootstrap readiness plan JSON",
            )
            p_agent_bootstrap_plan.add_argument(
                "--census-intake",
                required=True,
                help="Bootstrap census intake JSON path",
            )
            p_agent_bootstrap_plan.add_argument(
                "--release-manifest",
                default="release_artifacts/genesis_v05/manifest.json",
                help="Genesis v0.5 release artifact manifest JSON path",
            )
            p_agent_bootstrap_plan.add_argument(
                "--json-out",
                required=True,
                help="Path to write the local agent-bootstrap plan JSON",
            )
            p_agent_bootstrap_plan.add_argument(
                "--repo-root",
                default=".",
                help="Local repository root containing release artifacts",
            )
            p_agent_bootstrap_plan.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic tests",
            )
            p_agent_bootstrap_plan.add_argument(
                "--source-label",
                default="local",
                help="Operator label for this local bootstrap plan",
            )
            p_agent_bootstrap_plan.add_argument(
                "--allow-empty",
                action="store_true",
                help="Allow an intake with zero accepted receipts",
            )
            continue

        if command == "install":
            install_parser = subparsers.add_parser(
                "install",
                help="Install a verified local graph slice from an invite bundle",
                description="Install a verified local graph slice from an invite bundle",
            )
            install_parser.add_argument(
                "--from-invite",
                dest="from_invite",
                required=True,
                metavar="INVITE",
                help="Path, file:// URI, '-' stdin, or raw JSON invite bundle",
            )
            install_parser.add_argument(
                "--target-dir",
                default="",
                help="Directory for materialized slice files; defaults to out/installed_slices/<slice_id>",
            )
            install_parser.add_argument(
                "--output-receipt",
                default="",
                help="Path for atomic install receipt JSON; defaults to <target-dir>/install_receipt.json",
            )
            install_parser.add_argument(
                "--force-reprovision",
                action="store_true",
                help="Explicitly replace an existing local onboarding identity after invite install",
            )
            install_parser.add_argument(
                "--probe-observer",
                action="append",
                default=[],
                help="ILC observer URL for first-run connectivity probing; may be repeated",
            )
            install_parser.add_argument(
                "--relay-url",
                default="",
                help="Optional relay/rendezvous HTTPS URL for guarded first-run relay probing",
            )
            install_parser.add_argument(
                "--relay-admission-material",
                default="",
                help="Path to relay admission material JSON for guarded first-run relay probing",
            )
            install_parser.add_argument(
                "--relay-tls-cert-der-sha256",
                default="",
                help=(
                    "Pinned relay TLS certificate DER SHA-256 for ILC-native relay trust. "
                    "Required when --relay-url is used without --relay-admission-material."
                ),
            )
            install_parser.add_argument(
                "--relay-network-id",
                default=INSTALL_RELAY_DEFAULT_NETWORK_ID,
                help="Network identifier bound into auto-generated relay admission material",
            )
            install_parser.add_argument(
                "--relay-internal-port",
                type=int,
                default=INSTALL_RELAY_DEFAULT_INTERNAL_PORT,
                help="Local validator/observer QUIC port requested in relay admission",
            )
            install_parser.add_argument(
                "--enable-upnp",
                action="store_true",
                help=(
                    "Attempt UPnP/NAT-PMP/PCP router port mapping during install. "
                    "Opt-in only; default install performs no router mutation."
                ),
            )
            continue

        if command == "update":
            update_parser = subparsers.add_parser(
                "update",
                help="Update the installed ilc-core wheel from a verified release manifest",
                description=(
                    "Software update only: fetch a release manifest, verify the "
                    "selected wheel hash, then install it. Does not perform graph onboarding."
                ),
            )
            update_parser.add_argument(
                "--channel",
                choices=("stable", "rc", "dev"),
                default="rc",
                help="Release channel to select from the manifest",
            )
            manifest_group = update_parser.add_mutually_exclusive_group()
            manifest_group.add_argument(
                "--manifest-url",
                default="",
                help="HTTPS release manifest URL; defaults to the public RC manifest URL",
            )
            manifest_group.add_argument(
                "--manifest-path",
                default="",
                help="Bare local filesystem path to an installable release manifest JSON",
            )
            update_parser.add_argument(
                "--dry-run",
                action="store_true",
                help="Validate and report the selected artifact without download or install",
            )
            update_parser.add_argument(
                "--yes",
                action="store_true",
                help="Skip interactive confirmation before installing",
            )
            continue

        if command == "validator":
            validator_parser = subparsers.add_parser(
                "validator",
                help="Validator identity and endpoint assertion commands",
            )
            validator_subparsers = validator_parser.add_subparsers(
                dest="validator_subcommand",
                required=True,
            )
            p_validator_status = validator_subparsers.add_parser(
                "status",
                help="Report local validator identity and LMDB readiness status",
            )
            p_validator_status.add_argument(
                "--json",
                action="store_true",
                help="Accepted for operator clarity; CLI output is JSON by default",
            )
            p_validator_status.add_argument(
                "--lmdb-path",
                default="",
                help="Optional LMDB root to check; defaults to ~/.ilc/lmdb",
            )
            p_rotate_endpoint = validator_subparsers.add_parser(
                "rotate-endpoint",
                help="Generate a new ValidatorEndpointAssertion and revised_by edge",
            )
            p_rotate_endpoint.add_argument(
                "--old-assertion",
                required=True,
                help="Path to the current ValidatorEndpointAssertion JSON",
            )
            p_rotate_endpoint.add_argument(
                "--new-endpoint",
                required=True,
                help="New validator gRPC endpoint in host:port form",
            )
            p_rotate_endpoint.add_argument(
                "--network-id",
                required=True,
                help="Network identifier for BLS signing domain separation",
            )
            p_rotate_endpoint.add_argument(
                "--key",
                required=True,
                help="Path to validator BLS secret key hex file",
            )
            p_rotate_endpoint.add_argument(
                "--tls-cert",
                default="",
                help="Optional replacement TLS cert PEM/DER; omitted preserves old cert metadata",
            )
            p_rotate_endpoint.add_argument(
                "--asserted-at-epoch",
                type=int,
                help="Assertion epoch; omitted preserves the old assertion epoch",
            )
            p_rotate_endpoint.add_argument(
                "--output",
                default="",
                help="Output path for the new assertion JSON",
            )
            p_rotate_endpoint.add_argument(
                "--allow-test-stub-signature",
                action="store_true",
                help="Allow test-only BLS-shaped signature without Rust signing",
            )
            continue

        if command == "node":
            node_parser = subparsers.add_parser("node", help="D2e node lifecycle commands")
            node_subparsers = node_parser.add_subparsers(dest="node_subcommand", required=True)

            p_node_init = node_subparsers.add_parser(
                "init",
                help="Generate local validator node operator material",
            )
            p_node_init.add_argument(
                "--root",
                required=True,
                help="Output root for generated config, keys, certs, and init receipt",
            )
            p_node_init.add_argument("--network-id", required=True, help="Network identifier, e.g. ilc-rc01")
            p_node_init.add_argument("--host", required=True, help="Public DNS name or IP for endpoint assertion")
            p_node_init.add_argument("--grpc-port", type=int, required=True, help="gRPC listen/advertised port")
            p_node_init.add_argument("--quic-port", type=int, required=True, help="QUIC/P2P listen/advertised port")
            p_node_init.add_argument(
                "--peer-seed",
                action="append",
                default=[],
                help="Peer seed endpoint host:port; may be repeated",
            )
            p_node_init.add_argument(
                "--valid-days",
                type=int,
                default=365,
                help="TLS certificate validity in days",
            )
            p_node_init.add_argument(
                "--asserted-at-epoch",
                type=int,
                default=0,
                help="Endpoint assertion epoch",
            )
            p_node_init.add_argument(
                "--genesis-witness",
                action="store_true",
                help="Mark endpoint assertion as a genesis witness",
            )
            p_node_init.add_argument(
                "--allow-test-stub-crypto",
                action="store_true",
                help="Allow test-only stub ML-DSA/BLS material if real keygen/signing is unavailable",
            )

            p_node_check = node_subparsers.add_parser(
                "check",
                help="Validate generated node config and TLS certificate freshness",
            )
            p_node_check.add_argument("--config", required=True, help="Path to generated node_config.toml")

            p_node_readiness = node_subparsers.add_parser(
                "readiness",
                help="Run operator node readiness diagnostics",
            )
            p_node_readiness.add_argument("--config", required=True, help="Path to generated node_config.toml")
            p_node_readiness.add_argument(
                "--network",
                action="store_true",
                help="Enable bounded outbound TCP/UDP reachability probes",
            )
            p_node_readiness.add_argument(
                "--peer",
                default=None,
                help="Optional peer host:port for UDP/QUIC layer diagnostic",
            )

            p_node_firewall_plan = node_subparsers.add_parser(
                "firewall-plan",
                help="Generate provider-specific operator firewall rule artifacts",
            )
            p_node_firewall_plan.add_argument("--config", required=True, help="Path to generated node_config.toml")
            p_node_firewall_plan.add_argument(
                "--provider",
                choices=("digitalocean", "generic", "ufw"),
                default="generic",
                help="Firewall output format",
            )
            p_node_firewall_plan.add_argument(
                "--source-mode",
                choices=("public-testnet", "validator-set", "controller-only"),
                default="public-testnet",
                help="Source restriction policy for generated inbound rules",
            )
            p_node_firewall_plan.add_argument(
                "--controller-ip",
                default=None,
                help="Controller source IP for controller-only mode",
            )
            p_node_firewall_plan.add_argument(
                "--validator-ips",
                default=None,
                help="Comma-separated validator source IPs for validator-set/controller-only modes",
            )
            p_node_firewall_plan.add_argument(
                "--output",
                default=None,
                help="Optional path for atomic artifact write",
            )

            node_subparsers.add_parser("constants", help="Show ratified timed-out lifecycle constants")

            p_node_inspect = node_subparsers.add_parser("timed-out-inspect", help="Inspect timed-out lifecycle status from a record")
            p_node_inspect.add_argument(
                "--record-json", required=True, help="Path to node or claim record JSON file"
            )
            p_node_inspect.add_argument(
                "--current-epoch", type=int, required=True, help="Current issuance epoch"
            )

            p_node_d2d = node_subparsers.add_parser("timed-out-d2d", help="Build D2d dissemination envelope for a timed-out claim")
            p_node_d2d.add_argument(
                "--record-json", required=True, help="Path to node or claim record JSON file"
            )
            p_node_d2d.add_argument(
                "--current-epoch", type=int, required=True, help="Current issuance epoch"
            )
            p_node_d2d.add_argument(
                "--channel-id", required=True, help="Opaque D2d channel identifier"
            )
            p_node_d2d.add_argument(
                "--sender-peer-id", required=True, help="D2d sender peer identifier"
            )
            continue

        if command in {"sidecar", "skills"}:
            sidecar_parser = subparsers.add_parser(
                command,
                help="Sidecar discovery and recipe commands"
                if command == "sidecar"
                else "Alias for sidecar discovery and recipe commands",
            )
            sidecar_subparsers = sidecar_parser.add_subparsers(
                dest="sidecar_subcommand",
                required=True,
            )
            sidecar_subparsers.add_parser("list", help="List packaged sidecars")
            p_sidecar_inspect = sidecar_subparsers.add_parser(
                "inspect",
                help="Inspect one packaged sidecar",
            )
            p_sidecar_inspect.add_argument("sidecar_id")

            recipe_parser = sidecar_subparsers.add_parser(
                "recipe",
                help="Sidecar recipe commands",
            )
            recipe_subparsers = recipe_parser.add_subparsers(
                dest="sidecar_recipe_subcommand",
                required=True,
            )
            recipe_subparsers.add_parser("list", help="List sidecar recipes")
            p_recipe_inspect = recipe_subparsers.add_parser(
                "inspect",
                help="Inspect one sidecar recipe",
            )
            p_recipe_inspect.add_argument("recipe_id")
            p_recipe_apply = recipe_subparsers.add_parser(
                "apply",
                help="Apply a local sidecar recipe",
            )
            p_recipe_apply.add_argument("recipe_id")
            p_recipe_apply.add_argument("--home", dest="ccss_home", default="")
            p_recipe_apply.add_argument("--id", default="local-user")
            p_recipe_apply.add_argument("--name", default="Local ILC User")
            p_recipe_apply.add_argument("--peer-endpoint", default="")
            p_recipe_apply.add_argument("--overwrite-identity", action="store_true")
            if command == "skills":
                p_skills_install = sidecar_subparsers.add_parser(
                    "install",
                    help="Reserved ClawHub-backed skill install command",
                )
                p_skills_install.add_argument("skill_id")

            # External sidecars are dispatched via the _SIDECAR_PASSTHROUGH
            # short-circuit in main() before argparse runs — they do NOT
            # appear here as subcommands so ilc sidecar --help stays clean.
            # Use `ilc sidecar list` to discover available sidecars.
            continue

        if command == "doctor":
            doctor_parser = subparsers.add_parser(
                "doctor",
                help="Read-only local ILC health check",
            )
            doctor_parser.add_argument(
                "--pretty",
                action="store_true",
                help="Emit human-readable health output instead of JSON",
            )
            continue

        if command == "network-doctor":
            network_doctor_parser = subparsers.add_parser(
                "network-doctor",
                help="Connectivity mode diagnostic",
                description=(
                    "Connectivity mode diagnostic. Read-only unless --enable-upnp "
                    "is supplied."
                ),
            )
            output_group = network_doctor_parser.add_mutually_exclusive_group()
            output_group.add_argument(
                "--json",
                dest="network_doctor_json",
                action="store_true",
                help="Emit machine-readable JSON output (default)",
            )
            output_group.add_argument(
                "--text",
                action="store_true",
                help="Emit human-readable connectivity output",
            )
            network_doctor_parser.add_argument(
                "--out",
                default="",
                help="Optional path for canonical ConnectivityReceipt JSON",
            )
            network_doctor_parser.add_argument(
                "--probe-observer",
                action="append",
                default=[],
                help="ILC observer URL for direct reachability probing; may be repeated",
            )
            network_doctor_parser.add_argument(
                "--relay-url",
                default="",
                help="Optional relay/rendezvous HTTPS URL for guarded relay probing",
            )
            network_doctor_parser.add_argument(
                "--relay-admission-material",
                default="",
                help="Path to relay admission material JSON for guarded relay probing",
            )
            network_doctor_parser.add_argument(
                "--fetch-peers",
                action="store_true",
                help=(
                    "Fetch and verify a signed CDL-079 bootstrap peer bundle for "
                    "diagnostics. Requires --bootstrap-seed-peer, "
                    "--bootstrap-bundle-cid, and --genesis-authority-pubkey-hex."
                ),
            )
            network_doctor_parser.add_argument(
                "--bootstrap-seed-peer",
                default="",
                help="Seed peer HTTPS endpoint used with --fetch-peers",
            )
            network_doctor_parser.add_argument(
                "--bootstrap-bundle-cid",
                default="",
                help="Bootstrap bundle CID used with --fetch-peers",
            )
            network_doctor_parser.add_argument(
                "--genesis-authority-pubkey-hex",
                default="",
                help="Genesis ML-DSA public key hex used to verify the bootstrap bundle",
            )
            network_doctor_parser.add_argument(
                "--probe-epoch",
                type=int,
                default=0,
                help="Protocol epoch recorded in the connectivity receipt",
            )
            network_doctor_parser.add_argument(
                "--enable-upnp",
                action="store_true",
                help=(
                    "Attempt UPnP/NAT-PMP/PCP router port mapping for direct "
                    "inbound reachability. Opt-in only — not enabled by default. "
                    "Security note: UPnP IGD has no router-side authentication; "
                    "any process on your local network can open ports via UPnP. "
                    "Enable only on trusted home or office networks. Not "
                    "recommended for production validators or shared/enterprise "
                    "environments. Use manual port forwarding for production."
                ),
            )
            continue

        if command == "relay":
            relay_parser = subparsers.add_parser(
                "relay",
                help="Relay/rendezvous server commands",
            )
            relay_subparsers = relay_parser.add_subparsers(
                dest="relay_subcommand",
                required=True,
            )
            p_relay_serve = relay_subparsers.add_parser(
                "serve",
                help="Run the relay/rendezvous control and UDP data plane",
            )
            p_relay_serve.add_argument(
                "--relay-host",
                required=True,
                help="Advertised relay host/IP used in bootstrap records and grants",
            )
            p_relay_serve.add_argument(
                "--bind-host",
                default="0.0.0.0",
                help="Local listener bind address; does not need to match --relay-host",
            )
            p_relay_serve.add_argument(
                "--agent-id",
                required=True,
                help="Relay AgentID as a 96-character lowercase BLS public key hex",
            )
            p_relay_serve.add_argument(
                "--network-id",
                default="public-rc",
                help="Network identifier for relay admission requests",
            )
            p_relay_serve.add_argument(
                "--control-port",
                type=int,
                default=51151,
                help="HTTPS control-plane port",
            )
            p_relay_serve.add_argument(
                "--data-port-range-start",
                type=int,
                default=52000,
                help="First UDP data-plane relay port",
            )
            p_relay_serve.add_argument(
                "--data-port-range-end",
                type=int,
                default=52999,
                help="Last UDP data-plane relay port",
            )
            p_relay_serve.add_argument(
                "--ttl-epochs",
                type=int,
                default=4,
                help="Maximum slot lifetime in protocol epochs",
            )
            p_relay_serve.add_argument(
                "--max-bytes-per-epoch",
                type=int,
                default=64 * 1024 * 1024,
                help="Per-slot byte budget per epoch",
            )
            p_relay_serve.add_argument(
                "--max-concurrent-streams",
                type=int,
                default=8,
                help="Advertised per-slot stream cap",
            )
            p_relay_serve.add_argument(
                "--ssl-certfile",
                default=None,
                help="TLS certificate file; required for non-loopback relay hosts",
            )
            p_relay_serve.add_argument(
                "--ssl-keyfile",
                default=None,
                help="TLS private-key file; required when --ssl-certfile is supplied",
            )
            p_relay_serve.add_argument(
                "--allow-guarded-start",
                action="store_true",
                help="Test-only escape hatch; DEPLOY-00 clears guards instead of using this",
            )
            continue

        if command == "wallet":
            wallet_parser = subparsers.add_parser(
                "wallet",
                help="Read-only wallet query commands",
            )
            wallet_subparsers = wallet_parser.add_subparsers(
                dest="wallet_subcommand",
                required=True,
            )

            for wallet_query in ("status", "history", "identity"):
                p_wallet_query = wallet_subparsers.add_parser(
                    wallet_query,
                    help=f"Show read-only wallet {wallet_query}",
                )
                p_wallet_query.add_argument(
                    "--agent-id",
                    default="",
                    help="ILC-native agent_id account anchor; defaults to ILC_AGENT_ID",
                )
                p_wallet_query.add_argument(
                    "--format",
                    choices=("json", "text"),
                    default="json",
                    help="Output format",
                )
                if wallet_query in {"status", "history"}:
                    p_wallet_query.add_argument(
                        "--wallet-store",
                        default="",
                        help=(
                            "Path to existing local LMDB wallet store; defaults to "
                            "ILC_WALLET_STORE_PATH or out/public_runtime/wallet"
                        ),
                    )
            continue

        if command == "ccss":
            ccss_parser = subparsers.add_parser(
                "ccss",
                help="Confidential Coordination Sidecar Suite message commands",
            )
            ccss_subparsers = ccss_parser.add_subparsers(dest="ccss_subcommand", required=True)

            p_ccss_init = ccss_subparsers.add_parser("init", help="Create local CCSS identity")
            p_ccss_init.add_argument("--home", dest="ccss_home", default="")
            p_ccss_init.add_argument("--id", default="local-user")
            p_ccss_init.add_argument("--name", default="Local ILC User")
            p_ccss_init.add_argument("--peer-endpoint", default="")
            p_ccss_init.add_argument("--onion", default="")
            p_ccss_init.add_argument("--overwrite", action="store_true")

            p_ccss_apply = ccss_subparsers.add_parser(
                "apply-recipe",
                help="Apply the confidential-contact recipe",
            )
            p_ccss_apply.add_argument("--home", dest="ccss_home", default="")
            p_ccss_apply.add_argument("--id", default="local-user")
            p_ccss_apply.add_argument("--name", default="Local ILC User")
            p_ccss_apply.add_argument("--peer-endpoint", default="")
            p_ccss_apply.add_argument("--overwrite-identity", action="store_true")

            p_ccss_contacts = ccss_subparsers.add_parser("contacts", help="List CCSS contacts")
            p_ccss_contacts.add_argument("--home", dest="ccss_home", default="")

            p_ccss_import = ccss_subparsers.add_parser(
                "import-genesis",
                help="Import Genesis contact placeholder or published values",
            )
            p_ccss_import.add_argument("--home", dest="ccss_home", default="")
            p_ccss_import.add_argument("--overwrite", action="store_true")

            p_ccss_add = ccss_subparsers.add_parser("add-contact", help="Add a CCSS contact")
            p_ccss_add.add_argument("--home", dest="ccss_home", default="")
            p_ccss_add.add_argument("--id", required=True)
            p_ccss_add.add_argument("--name", required=True)
            p_ccss_add.add_argument("--pubkey", required=True)
            p_ccss_add.add_argument("--description", default="")
            p_ccss_add.add_argument("--peer-endpoint", default="")
            p_ccss_add.add_argument("--onion", default="")
            p_ccss_add.add_argument("--agent-id", default="")
            p_ccss_add.add_argument("--overwrite", action="store_true")

            p_ccss_send = ccss_subparsers.add_parser("send", help="Send a sealed CCSS message")
            p_ccss_send.add_argument("--home", dest="ccss_home", default="")
            p_ccss_send.add_argument("--allow-reply", action="store_true",
                help="Include your pubkey+endpoint in the encrypted payload so the "
                     "recipient can respond. Once received and decrypted, they have "
                     "your key permanently.")
            p_ccss_send.add_argument("contact_id")
            p_ccss_send.add_argument("message")

            p_ccss_inbox = ccss_subparsers.add_parser("inbox", help="List local CCSS inbox")
            p_ccss_inbox.add_argument("--home", dest="ccss_home", default="")
            p_ccss_inbox.add_argument("--count", action="store_true",
                help="Print only the number of envelopes (machine-readable)")

            p_ccss_status = ccss_subparsers.add_parser(
                "status", help="Print pending inbox count; exits 0 if empty, 1 if messages waiting")
            p_ccss_status.add_argument("--home", dest="ccss_home", default="")

            p_ccss_read = ccss_subparsers.add_parser("read", help="Read/decrypt a CCSS envelope")
            p_ccss_read.add_argument("--home", dest="ccss_home", default="")
            read_group = p_ccss_read.add_mutually_exclusive_group(required=True)
            read_group.add_argument("--latest", action="store_true")
            read_group.add_argument("--envelope", default="")
            p_ccss_read.add_argument("--redact", action="store_true")

            p_ccss_serve = ccss_subparsers.add_parser(
                "serve",
                help="Run a local direct CCSS peer receiver",
            )
            p_ccss_serve.add_argument("--home", dest="ccss_home", default="")
            p_ccss_serve.add_argument("--host", default="127.0.0.1")
            p_ccss_serve.add_argument("--port", type=int, default=9001)
            continue

        if command == "atlas":
            atlas_parser = subparsers.add_parser(
                "atlas",
                help="Local Genesis Atlas LMDB inspection and guarded maintenance commands",
            )
            atlas_subparsers = atlas_parser.add_subparsers(
                dest="atlas_subcommand",
                required=True,
            )

            p_atlas_status = atlas_subparsers.add_parser(
                "status",
                help="Report local Genesis Atlas LMDB counts and metadata",
            )
            p_atlas_status.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")

            p_atlas_validate = atlas_subparsers.add_parser(
                "validate",
                help="Validate local Genesis Atlas LMDB row and payload consistency",
            )
            p_atlas_validate.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")

            p_atlas_node = atlas_subparsers.add_parser(
                "node",
                help="Return one Atlas node by candidate ID",
            )
            p_atlas_node.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")
            p_atlas_node.add_argument("--node-id", required=True, help="Atlas candidate ID")

            p_atlas_edges = atlas_subparsers.add_parser(
                "edges",
                help="Return Atlas edges connected to a candidate ID",
            )
            p_atlas_edges.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")
            p_atlas_edges.add_argument("--node-id", required=True, help="Atlas candidate ID")

            p_atlas_register = atlas_subparsers.add_parser(
                "register-phase-files",
                help="Dry-run or write support-only phase-file registrations",
            )
            p_atlas_register.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")
            p_atlas_register.add_argument("--phase", required=True, help="Phase identifier")
            p_atlas_register.add_argument(
                "--file",
                dest="files",
                action="append",
                required=True,
                help="Repo-relative file to register. May be repeated.",
            )
            p_atlas_register.add_argument(
                "--node-kind",
                default="phase_artifact",
                help="Node kind for all registered files",
            )
            p_atlas_register.add_argument(
                "--graph-projection",
                default="support_candidate_graph",
                help="Graph projection for all registered files",
            )
            p_atlas_register.add_argument(
                "--graph-delta",
                default="support_only",
                help="Graph delta for all registered files",
            )
            p_atlas_register.add_argument(
                "--edge",
                dest="required_edges",
                action="append",
                default=[],
                help="Required edge in EDGE_TYPE:target_id form. May be repeated.",
            )
            p_atlas_register.add_argument(
                "--write",
                action="store_true",
                help="Mutate the local unsigned Atlas LMDB. Default is dry-run.",
            )
            p_atlas_register.add_argument(
                "--dry-run",
                action="store_true",
                help="Validate only; accepted for explicitness and remains the default.",
            )
            p_atlas_register.add_argument("--receipt", default="", help="Optional receipt path")

            p_atlas_edge_batch = atlas_subparsers.add_parser(
                "apply-edge-batch",
                help="Dry-run or write an edge batch through the safe writer",
            )
            p_atlas_edge_batch.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")
            p_atlas_edge_batch.add_argument("--input", required=True, help="JSON edge batch path")
            p_atlas_edge_batch.add_argument(
                "--write",
                action="store_true",
                help="Mutate the local unsigned Atlas LMDB. Default is dry-run.",
            )
            p_atlas_edge_batch.add_argument(
                "--dry-run",
                action="store_true",
                help="Validate only; accepted for explicitness and remains the default.",
            )
            p_atlas_edge_batch.add_argument("--receipt", default="", help="Optional receipt path")

            p_atlas_plan = atlas_subparsers.add_parser(
                "apply-node-edge-plan",
                help="Dry-run or write a node+edge plan through the safe writer",
            )
            p_atlas_plan.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")
            p_atlas_plan.add_argument("--input", required=True, help="JSON node-edge plan path")
            p_atlas_plan.add_argument(
                "--write",
                action="store_true",
                help="Mutate the local unsigned Atlas LMDB. Default is dry-run.",
            )
            p_atlas_plan.add_argument(
                "--dry-run",
                action="store_true",
                help="Validate only; accepted for explicitness and remains the default.",
            )
            p_atlas_plan.add_argument("--receipt", default="", help="Optional receipt path")

            p_atlas_build_slice = atlas_subparsers.add_parser(
                "build-slice",
                help="Build an unsigned local AtlasSliceManifest from an Atlas projection",
            )
            p_atlas_build_slice.add_argument("--lmdb", required=True, help="Path to Atlas LMDB root")
            p_atlas_build_slice.add_argument(
                "--slice-variant",
                required=True,
                choices=("core", "bridge", "full"),
                help="AtlasSliceManifest variant to build",
            )
            p_atlas_build_slice.add_argument(
                "--projection",
                required=True,
                help="Atlas graph_projection label to include",
            )
            p_atlas_build_slice.add_argument(
                "--slice-version",
                default="0.1",
                help="AtlasSliceManifest slice_version value",
            )
            p_atlas_build_slice.add_argument(
                "--output",
                default="",
                help="Optional output JSON path; stdout payload is always emitted",
            )

            p_atlas_sign_manifest = atlas_subparsers.add_parser(
                "sign-manifest",
                help="Dev/test-sign an AtlasSliceManifest with Ed25519 COSE-Sign1",
            )
            p_atlas_sign_manifest.add_argument(
                "--manifest",
                required=True,
                help="Unsigned AtlasSliceManifest JSON path",
            )
            p_atlas_sign_manifest.add_argument(
                "--private-key-hex",
                required=True,
                help="32-byte Ed25519 private key seed hex for dev/test signing",
            )
            p_atlas_sign_manifest.add_argument(
                "--output",
                default="",
                help="Optional signed output JSON path; default overwrites --manifest",
            )

            p_atlas_verify_slice = atlas_subparsers.add_parser(
                "verify-slice",
                help="Verify AtlasSliceManifest deterministic commitments and dev/test signature",
            )
            p_atlas_verify_slice.add_argument(
                "--manifest",
                required=True,
                help="Signed AtlasSliceManifest JSON path",
            )
            p_atlas_verify_slice.add_argument(
                "--public-key-hex",
                default="",
                help="32-byte Ed25519 public key hex for signature verification",
            )
            p_atlas_verify_slice.add_argument(
                "--allow-unsigned",
                dest="require_signature",
                action="store_false",
                help="Verify deterministic commitments without requiring a signature",
            )
            p_atlas_verify_slice.set_defaults(require_signature=True)

            p_atlas_verify_signed_slice = atlas_subparsers.add_parser(
                "verify-signed-slice",
                help="Verify a native signed-slice record and optional portable witness",
            )
            p_atlas_verify_signed_slice.add_argument(
                "--native-record",
                required=True,
                help="Native __signed_slices__ record JSON path",
            )
            p_atlas_verify_signed_slice.add_argument(
                "--portable-witness",
                default="",
                help="Optional portable AtlasSliceManifest witness JSON path",
            )
            p_atlas_verify_signed_slice.add_argument(
                "--json-out",
                default="",
                help="Optional local verification receipt JSON path",
            )
            p_atlas_verify_signed_slice.add_argument(
                "--json-out-root",
                default="",
                help="Optional allowed directory boundary for --json-out",
            )
            p_atlas_verify_signed_slice.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic receipts",
            )
            p_atlas_verify_signed_slice.add_argument(
                "--source-label",
                default="local",
                help="Operator label for this local verification receipt",
            )
            p_atlas_verify_signed_slice.add_argument(
                "--require-signature-status",
                action="store_true",
                help="Require native record signature_status=signature_verified",
            )

            p_atlas_materialize_signed_slice = atlas_subparsers.add_parser(
                "materialize-signed-slice",
                help="Materialize a verifier-passing signed slice from local blob sources only",
            )
            p_atlas_materialize_signed_slice.add_argument(
                "--native-record",
                required=True,
                help="Native __signed_slices__ record JSON path",
            )
            p_atlas_materialize_signed_slice.add_argument(
                "--portable-witness",
                default="",
                help="Optional portable AtlasSliceManifest witness JSON path",
            )
            p_atlas_materialize_signed_slice.add_argument(
                "--local-source-root",
                required=True,
                help="Local-only root directory for blob resolution",
            )
            p_atlas_materialize_signed_slice.add_argument(
                "--json-out",
                default="",
                help="Optional receipt path; must be under out/",
            )
            p_atlas_materialize_signed_slice.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic receipts",
            )
            p_atlas_materialize_signed_slice.add_argument(
                "--allow-missing-blobs",
                action="store_true",
                help="Rehearsal mode: record missing blobs instead of accepting materialization",
            )
            p_atlas_materialize_signed_slice.add_argument(
                "--require-baseline",
                action="store_true",
                help="Fail unless Core Slice 0 and Public-RC Baseline Slice 1 blobs verified",
            )

            p_atlas_reconcile_status = atlas_subparsers.add_parser(
                "reconcile-status",
                help="Read and summarize the local installed-slice registry",
            )
            p_atlas_reconcile_status.add_argument(
                "--registry",
                default="out/installed_slice_registry/registry.json",
                help="Installed AtlasSliceManifest registry JSON path",
            )
            p_atlas_reconcile_status.add_argument(
                "--json-out",
                default="",
                help="Optional reconcile status receipt path; must be under out/",
            )
            p_atlas_reconcile_status.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic receipts",
            )

            p_atlas_local_registry_status = atlas_subparsers.add_parser(
                "local-registry-status",
                help="Read and summarize the local Atlas installed-slice registry",
            )
            p_atlas_local_registry_status.add_argument(
                "--registry",
                default="out/installed_slice_registry/local_registry.json",
                help="Local Atlas registry JSON path",
            )
            p_atlas_local_registry_status.add_argument(
                "--json-out",
                default="out/atlas_local_registry_1576_fix9/registry_status_receipt.json",
                help="Local registry status receipt path; must be under out/",
            )
            p_atlas_local_registry_status.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic receipts",
            )
            p_atlas_local_registry_status.add_argument(
                "--check-availability",
                action="store_true",
                help="Verify local content file existence and SHA-384 in the status receipt only",
            )

            p_atlas_sidecar_profile = atlas_subparsers.add_parser(
                "sidecar-profile",
                help="Validate Atlas sidecar profile descriptors",
            )
            atlas_sidecar_profile_subparsers = p_atlas_sidecar_profile.add_subparsers(
                dest="sidecar_profile_subcommand",
                required=True,
            )
            p_atlas_sidecar_profile_validate = atlas_sidecar_profile_subparsers.add_parser(
                "validate",
                help="Validate a sidecar profile JSON without installing it",
            )
            p_atlas_sidecar_profile_validate.add_argument(
                "--profile",
                required=True,
                help="Atlas sidecar profile JSON path",
            )
            p_atlas_sidecar_profile_validate.add_argument(
                "--json-out",
                default="",
                help="Optional validation receipt path; must be under out/",
            )
            p_atlas_sidecar_profile_validate.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic receipts",
            )
            continue

        if command == "bootstrap":
            bootstrap_parser = subparsers.add_parser(
                "bootstrap",
                help="Materialize a verified ILC package profile into a local tree",
            )
            bootstrap_parser.add_argument(
                "--profile",
                required=True,
                help="Frozen package profile JSON",
            )
            bootstrap_parser.add_argument(
                "--out",
                required=True,
                help="Output directory for the staged materialized tree",
            )
            bootstrap_parser.add_argument(
                "--verify",
                action="store_true",
                help="Recompute SHA-256 for every materialized file",
            )
            bootstrap_parser.add_argument(
                "--receipt",
                required=True,
                help="Path to write the reconstruction receipt JSON",
            )
            bootstrap_parser.add_argument(
                "--repo-root",
                default=".",
                help="Local repository root byte source",
            )
            bootstrap_parser.add_argument(
                "--cache-dir",
                default="",
                help="Optional content-addressed cache directory",
            )
            bootstrap_parser.add_argument(
                "--tarball",
                default="",
                help="Optional source tarball byte source",
            )
            bootstrap_parser.add_argument(
                "--http-base-url",
                default="",
                help="Optional HTTP base URL byte source",
            )
            bootstrap_parser.add_argument(
                "--max-total-bytes",
                type=int,
                default=256 * 1024 * 1024,
                help="Maximum total materialized bytes",
            )
            bootstrap_parser.add_argument(
                "--recipe",
                default="",
                help="Optional build/test recipe JSON",
            )
            bootstrap_parser.add_argument(
                "--run-recipe",
                action="store_true",
                help="Run the supplied build/test recipe after hash verification",
            )
            bootstrap_parser.add_argument(
                "--recipe-timeout",
                type=int,
                default=120,
                help="Per-command recipe timeout in seconds",
            )
            bootstrap_parser.add_argument(
                "--overwrite",
                action="store_true",
                help="Replace an existing output directory after safety checks",
            )
            continue

        if command == "bootstrap-receipt":
            receipt_parser = subparsers.add_parser(
                "bootstrap-receipt",
                help="Write a local public-agent bootstrap receipt without graph or wallet writes",
            )
            receipt_parser.add_argument(
                "--json-out",
                required=True,
                help="Path to write the local bootstrap receipt JSON",
            )
            receipt_parser.add_argument(
                "--install-surface",
                choices=("github", "clawhub", "openclaw", "private-dev-main", "local"),
                default="local",
                help="Local install surface being attested",
            )
            receipt_parser.add_argument(
                "--repo-root",
                default=".",
                help="Local ILC repository root to inspect",
            )
            receipt_parser.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic tests",
            )
            receipt_parser.add_argument(
                "--identity-state",
                default="",
                help="Optional D2e identity state path; defaults beside --graph-state",
            )
            receipt_parser.add_argument(
                "--ccss-home",
                default="",
                help="Optional CCSS home directory; defaults to ~/.ilc/ccss",
            )
            receipt_parser.add_argument(
                "--verifier-path",
                default="ilc_consensus/target/debug/pq_sign",
                help="ML-DSA verifier binary path, relative to --repo-root unless absolute",
            )
            receipt_parser.add_argument(
                "--skip-signature-verify",
                action="store_true",
                help="Record artifact hashes without invoking the verifier",
            )
            receipt_parser.add_argument(
                "--require-baseline-artifacts",
                action="store_true",
                help="Fail closed unless signed Slice 0 and Slice 1 artifacts verify locally",
            )
            continue

        if command == "bootstrap-census":
            census_parser = subparsers.add_parser(
                "bootstrap-census",
                help="Validate and stage local public-agent bootstrap receipts",
            )
            census_subparsers = census_parser.add_subparsers(
                dest="bootstrap_census_subcommand",
                required=True,
            )
            p_census_intake = census_subparsers.add_parser(
                "intake",
                help="Build a deduplicated local bootstrap census intake JSON",
            )
            p_census_intake.add_argument(
                "--receipt",
                dest="receipt_paths",
                action="append",
                default=[],
                help="Bootstrap receipt JSON file; may be repeated",
            )
            p_census_intake.add_argument(
                "--receipt-dir",
                dest="receipt_dirs",
                action="append",
                default=[],
                help="Directory containing bootstrap receipt JSON files; may be repeated",
            )
            p_census_intake.add_argument(
                "--json-out",
                required=True,
                help="Path to write the local census intake JSON",
            )
            p_census_intake.add_argument(
                "--generated-at-utc",
                default="",
                help="Optional RFC3339 UTC timestamp override for deterministic tests",
            )
            p_census_intake.add_argument(
                "--source-label",
                default="local",
                help="Operator label for this local intake batch",
            )
            p_census_intake.add_argument(
                "--allow-invalid",
                action="store_true",
                help="Record invalid receipts instead of failing closed",
            )
            continue

        if command == "balance":
            balance_parser = subparsers.add_parser(
                "balance",
                help="Report a local per-agent ILC balance or guarded smoke evidence",
            )
            balance_parser.add_argument(
                "--agent-id",
                default="",
                help="Agent identifier to report. Omit for legacy prototype compatibility.",
            )
            balance_parser.add_argument(
                "--state-json",
                dest="balance_state_json",
                default=str(_default_balance_state_path()),
                help="Local balance/evidence JSON file. Defaults to Phase 1561 smoke evidence.",
            )
            continue

        if command == "submit":
            submit_parser = subparsers.add_parser(
                "submit",
                help="Validate a CDL-073 truth primitive submission and return graph-output contract",
            )
            submit_parser.add_argument(
                "--primitive",
                required=True,
                help="Truth primitive name (assert.truth, validate.claim, etc.)",
            )
            submit_group = submit_parser.add_mutually_exclusive_group(required=True)
            submit_group.add_argument(
                "--payload-json",
                dest="payload_json",
                help="Payload as a JSON string",
            )
            submit_group.add_argument(
                "--payload-file",
                dest="payload_file",
                help="Path to a JSON file containing the payload",
            )
            submit_parser.add_argument(
                "--agent-id",
                dest="agent_id",
                required=True,
                help="Submitting agent's canonical agent_id",
            )
            submit_parser.add_argument(
                "--epoch",
                type=int,
                required=True,
                help="Current epoch at submission time (non-negative integer)",
            )
            submit_parser.add_argument(
                "--sig",
                default="UNSIGNED",
                help="COSE Sign1 signature (hex or placeholder). Default: UNSIGNED",
            )
            submit_parser.add_argument(
                "--signing-key",
                dest="signing_key",
                default=None,
                help="Optional file:// Ed25519 hotkey URI for signing the truth primitive payload",
            )
            continue

        if command != "identity":
            subparsers.add_parser(command, help=f"Prototype `{command}` command")
            continue

        identity_parser = subparsers.add_parser("identity", help="Prototype `identity` command")
        identity_subparsers = identity_parser.add_subparsers(dest="identity_subcommand")

        p_init = identity_subparsers.add_parser("init", help="Initialize local identity state")
        p_init.add_argument("--lineage-id", default="lineage-local", help="Lineage identifier")
        p_init.add_argument("--key-ref", default="key-local-0", help="Initial key reference")
        p_init.add_argument(
            "--invite",
            default="",
            help="Local invite batch JSON file for invite-aware identity initialization",
        )
        p_init.add_argument(
            "--enable-invites",
            action="store_true",
            help="Explicitly enable default-off invite CLI plumbing",
        )
        p_init.add_argument(
            "--identity-seed-hex",
            default="",
            help="Hex identity seed for invite redemption and validator candidate linkage",
        )
        p_init.add_argument(
            "--no-validator",
            dest="no_validator",
            action="store_true",
            help="Opt out of default public-RC candidate validator participation",
        )
        p_init.add_argument(
            "--validator-id",
            type=int,
            default=1,
            help="Temporary u32 validator id used until Rust AgentID migration lands",
        )
        p_init.add_argument(
            "--validator-key",
            default="",
            help="96-char lower-hex BLS validator public key for candidate materialization",
        )
        p_init.add_argument(
            "--validator-endpoint",
            default="",
            help="Validator endpoint for candidate materialization, for example host:port",
        )
        p_init.add_argument(
            "--validator-network-id",
            default="public-rc",
            help="Network id for the candidate ValidatorRoleRecord",
        )
        p_init.add_argument(
            "--validator-effective-from-epoch",
            type=int,
            default=1,
            help="Candidate role effective-from epoch; default 1",
        )
        p_init.add_argument(
            "--redeemer-pubkey-cid",
            default="",
            help="CID of the redeemer identity public key material",
        )
        p_init.add_argument(
            "--redemption-epoch",
            type=int,
            default=0,
            help="Epoch recorded in the local InviteRedemptionRecord",
        )

        p_invite = identity_subparsers.add_parser(
            "invite",
            help="Default-off local invite batch plumbing",
        )
        invite_subparsers = p_invite.add_subparsers(
            dest="identity_invite_subcommand",
            required=True,
        )
        p_invite_create = invite_subparsers.add_parser(
            "create",
            help="Create a local InviteBatchRecord and private nonce bundle",
        )
        p_invite_create.add_argument("--count", type=int, required=True, help="Number of invite tokens")
        p_invite_create.add_argument("--output", default="", help="Path to write the local invite batch JSON")
        p_invite_create.add_argument(
            "--enable-invites",
            action="store_true",
            help="Explicitly enable default-off invite CLI plumbing",
        )
        p_invite_create.add_argument(
            "--inviter-cid",
            default="genesis_agent:01",
            help="Inviter CID copied into the InviteBatchRecord",
        )
        p_invite_create.add_argument(
            "--batch-id",
            default="genesis-invite-batch-local",
            help="Unique local batch identifier",
        )
        p_invite_create.add_argument(
            "--created-epoch",
            type=int,
            default=0,
            help="Issuance epoch recorded in the InviteBatchRecord",
        )
        p_invite_create.add_argument(
            "--inviter-sig",
            default="genesis",
            help="Inviter signature placeholder or signature reference",
        )
        p_invite_bundle = invite_subparsers.add_parser(
            "bundle",
            help="Assemble one install-ready invite bundle from a batch JSON",
        )
        p_invite_bundle.add_argument(
            "batch_json_path",
            help="Path to JSON produced by `ilc identity invite create`",
        )
        p_invite_bundle.add_argument(
            "--nonce-index",
            type=int,
            required=True,
            help="Zero-based private nonce index to include in this bundle",
        )
        p_invite_bundle.add_argument(
            "--starmap-path",
            default="",
            help="Optional starmap payload JSON; omitted uses installed public-RC default",
        )
        p_invite_bundle.add_argument(
            "--intended-epoch",
            type=int,
            default=0,
            help="Intended bootstrap epoch for the invite bundle",
        )
        p_invite_bundle.add_argument(
            "--intended-profile",
            default="public_rc_validator_bootstrap",
            help="Expected invite bootstrap profile",
        )
        p_invite_bundle.add_argument(
            "--known-peer-hints-path",
            default="",
            help=(
                "Optional bootstrap_peer_hints.json carrying signed PeerAdvertisement "
                "records plus known_peer_hint_key_bindings"
            ),
        )
        p_invite_bundle.add_argument(
            "--genesis-state-root",
            default="",
            help="Optional Genesis state-root envelope hash to bind into the invite bundle",
        )
        p_invite_bundle.add_argument(
            "--inviter-connectivity-mode",
            default="",
            help="Optional inviter connectivity mode copied into the invite bundle",
        )
        p_invite_bundle.add_argument(
            "--bootstrap-fetch-seed-peer-endpoint",
            default="",
            help="Optional seed peer endpoint for signed distributed bootstrap fetch",
        )
        p_invite_bundle.add_argument(
            "--bootstrap-fetch-bundle-cid",
            default="",
            help="Optional signed bootstrap bundle CID for distributed fetch",
        )
        p_invite_bundle.add_argument(
            "--bootstrap-fetch-genesis-authority-pubkey-hex",
            default="",
            help="Optional trusted Genesis authority ML-DSA pubkey for bootstrap fetch",
        )
        p_invite_bundle.add_argument(
            "--relay-bootstrap-capsule-path",
            default="",
            help=(
                "Optional Genesis-signed relay bootstrap capsule. When present, "
                "ilc install can derive relay URL and DER pin without manual flags."
            ),
        )
        p_invite_bundle.add_argument(
            "--output",
            default="",
            help="Path to write one install-ready invite bundle JSON",
        )
        p_invite_bundle.add_argument(
            "--enable-invites",
            action="store_true",
            help="Explicitly enable default-off invite CLI plumbing",
        )
        p_invite_hint = invite_subparsers.add_parser(
            "hint",
            help="Create a signed bootstrap peer hint file for inclusion in an invite bundle",
        )
        p_invite_hint.add_argument(
            "--relay-url",
            required=True,
            help="Relay HTTPS URL to advertise (e.g. https://host:port)",
        )
        p_invite_hint.add_argument(
            "--output",
            required=True,
            help="Output path for bootstrap_peer_hints.json",
        )
        p_invite_hint.add_argument(
            "--peer-epoch",
            type=int,
            default=0,
            help="Peer advertisement timestamp epoch (default: 0)",
        )
        p_invite_hint.add_argument(
            "--ttl-epochs",
            type=int,
            default=4,
            help="Peer advertisement TTL in epochs (default: 4, max: 4)",
        )
        p_invite_hint.add_argument(
            "--protocol-version",
            default="ilc.v0.4",
            help="Protocol version string (default: ilc.v0.4)",
        )
        p_invite_hint.add_argument(
            "--label",
            default="bootstrap-hint",
            help="Key binding reference prefix (default: bootstrap-hint)",
        )
        p_invite_hint.add_argument(
            "--enable-invites",
            action="store_true",
            help="Explicitly enable default-off invite CLI plumbing",
        )
        p_invite_generate = invite_subparsers.add_parser(
            "generate",
            help="Generate relay-hosted invite-code material with zero required flags",
        )
        p_invite_generate.add_argument(
            "--slots",
            type=int,
            default=1,
            help="Number of invite slots to generate (default: 1; max: 10000)",
        )
        p_invite_generate.add_argument(
            "--ttl",
            default="24h",
            help="Invite-code TTL such as 30m, 24h, or 7d (default: 24h; max: 30d)",
        )
        p_invite_generate.add_argument(
            "--relay-url",
            default="",
            help="Override relay HTTPS URL; otherwise use the bundled relay capsule",
        )
        p_invite_generate.add_argument(
            "--relay-tls-cert-der-sha256",
            default="",
            help="TLS certificate DER SHA-256 pin for --relay-url overrides outside the bundled capsule",
        )
        p_invite_generate.add_argument(
            "--output",
            default="~/.ilc/invite_bundle.json",
            help="Path to write generated bundle material (default: ~/.ilc/invite_bundle.json)",
        )
        p_invite_generate.add_argument(
            "--upload",
            action="store_true",
            help="Upload signed invite bundles to the selected relay and print the invite code",
        )
        p_invite_generate.add_argument(
            "--stdout",
            action="store_true",
            help="Write generated bundle material to stdout JSON",
        )
        p_invite_generate.add_argument(
            "--emit-store-request",
            action="store_true",
            help="Include the signed relay store request in JSON output",
        )
        p_invite_generate.add_argument(
            "--batch-id",
            default="",
            help="Optional deterministic batch id; omitted generates a random id",
        )
        p_invite_generate.add_argument(
            "--intended-profile",
            default="public_rc_invitee_bootstrap",
            help="Invite bundle intended profile",
        )

        identity_subparsers.add_parser("show", help="Show local identity state")

        p_rotate = identity_subparsers.add_parser("rotate", help="Rotate identity key reference")
        p_rotate.add_argument("--new-key-ref", default=None, help="Replacement key reference")

        identity_subparsers.add_parser("export", help="Export sanitized identity snapshot")

    return parser


def _write_json_payload(payload: dict[str, Any], *, stderr: bool = False) -> None:
    print(json.dumps(payload, sort_keys=True), file=sys.stderr if stderr else sys.stdout)


def _simulate_network_error_result(command: str) -> tuple[int, dict[str, Any]]:
    return 3, _error_payload(
        command=command,
        code=3,
        message="simulated network transport failure",
        details={"phase": "264"},
    )


def _run_top_level_command(
    command: str,
    args: argparse.Namespace,
    graph_state_path: Path,
) -> dict[str, Any]:
    stateless_commands = {
        "agent",
        "agent-bootstrap",
        "atlas",
        "bootstrap",
        "bootstrap-census",
        "bootstrap-receipt",
        "bundle",
        "ccss",
        "doctor",
        "install",
        "network-doctor",
        "node",
        "query",
        "relay",
        "sidecar",
        "skills",
        "update",
        "verify",
        "validator",
        "wallet",
    }
    if command not in stateless_commands:
        _ensure_local_graph_state(graph_state_path, command)

    if command == "version":
        return _success_payload(command, _version_data())
    if command == "query":
        query_command, data = _run_query_subcommand(args, graph_state_path)
        return _query_success_payload(query_command, data)
    if command == "verify":
        verify_command, data = _run_verify_subcommand(args, graph_state_path)
        return _verify_success_payload(verify_command, data)
    if command == "bundle":
        bundle_command, data = _run_bundle_subcommand(args, graph_state_path)
        return _bundle_success_payload(bundle_command, data)
    if command == "identity":
        data = _run_identity_subcommand(args, graph_state_path)
        return _success_payload(command, data)
    if command == "agent":
        from ilc_core.cli.d2e_agent_cli import run_agent_command

        data = run_agent_command(args)
        return _success_payload(command, data)
    if command == "agent-bootstrap":
        subcommand = getattr(args, "agent_bootstrap_subcommand", None)
        if subcommand != "plan":
            raise ValueError(f"unknown_agent_bootstrap_subcommand:{subcommand}")
        from ilc_core.rc.agent_bootstrap import (
            AgentBootstrapError,
            build_agent_bootstrap_plan,
            write_agent_bootstrap_plan,
        )

        try:
            data = build_agent_bootstrap_plan(
                census_intake_path=Path(args.census_intake),
                release_manifest_path=Path(args.release_manifest),
                repo_root=Path(args.repo_root),
                generated_at_utc=str(args.generated_at_utc) or None,
                source_label=str(args.source_label),
                require_accepted_receipts=not bool(args.allow_empty),
            )
            plan_path = write_agent_bootstrap_plan(Path(args.json_out), data)
            data = {**data, "plan_path": str(plan_path)}
        except AgentBootstrapError as exc:
            raise ValueError(str(exc)) from exc
        return _success_payload(command, data)
    if command == "install":
        data = _run_install_subcommand(args)
        return _success_payload(command, data)
    if command == "update":
        data = _run_update_subcommand(args)
        return _success_payload(command, data)
    if command == "node":
        if getattr(args, "node_subcommand", None) in {"init", "check", "readiness", "firewall-plan"}:
            data = _run_node_operator_subcommand(args)
            payload_command = (
                f"node {args.node_subcommand}"
                if getattr(args, "node_subcommand", None) in {"readiness", "firewall-plan"}
                else command
            )
            return _success_payload(payload_command, data)
        from ilc_core.cli.d2e_lifecycle_cli import run_node_command

        data = run_node_command(args)
        return _success_payload(command, data)
    if command == "validator":
        data = _run_validator_subcommand(args)
        return _success_payload(command, data)
    if command in {"sidecar", "skills"}:
        from ilc_core.cli.sidecar_cli import run_sidecar_command

        data = run_sidecar_command(args)
        return _success_payload("sidecar" if command == "skills" else command, data)
    if command == "doctor":
        data = _run_doctor_subcommand(args, graph_state_path)
        return _success_payload(command, data)
    if command == "network-doctor":
        from ilc_core.cli.network_doctor import build_network_doctor_payload

        data = build_network_doctor_payload(
            text=bool(getattr(args, "text", False)),
            output_path=str(getattr(args, "out", "") or "") or None,
            enable_upnp=bool(getattr(args, "enable_upnp", False)),
            fetch_peers=bool(getattr(args, "fetch_peers", False)),
            bootstrap_seed_peer=(
                str(getattr(args, "bootstrap_seed_peer", "") or "") or None
            ),
            bootstrap_bundle_cid=(
                str(getattr(args, "bootstrap_bundle_cid", "") or "") or None
            ),
            genesis_authority_pubkey_hex=(
                str(getattr(args, "genesis_authority_pubkey_hex", "") or "") or None
            ),
            probe_epoch=int(getattr(args, "probe_epoch", 0)),
            probe_observers=tuple(getattr(args, "probe_observer", []) or []),
            relay_server_url=str(getattr(args, "relay_url", "") or "") or None,
            relay_admission_material_path=(
                str(getattr(args, "relay_admission_material", "") or "") or None
            ),
        )
        return _success_payload(command, data)
    if command == "relay":
        data = _run_relay_subcommand(args)
        return _success_payload(command, data)
    if command == "ccss":
        from ilc_core.cli.ccss_cli import run_ccss_command

        data = run_ccss_command(args)
        return _success_payload(command, data)
    if command == "atlas":
        try:
            from ilc_core.cli.atlas_lmdb_cli import AtlasLmdbCliError, run_atlas_command
        except ImportError as exc:
            raise ValueError("atlas_lmdb_cli_not_available_public_rc") from exc

        try:
            data = run_atlas_command(args)
        except AtlasLmdbCliError as exc:
            raise ValueError(str(exc)) from exc
        return _success_payload(command, data)
    if command == "wallet":
        from ilc_core.cli.wallet_cli import WalletCliError, run_wallet_command

        try:
            data = run_wallet_command(args)
        except WalletCliError as exc:
            raise ValueError(str(exc)) from exc
        return _success_payload(command, data)
    if command == "bootstrap":
        try:
            from ilc_core.distribution.materialization import (
                MaterializationError,
                bootstrap,
            )
        except ImportError as exc:
            raise ValueError("materialization_not_available_public_rc") from exc

        try:
            data = bootstrap(
                profile_path=Path(args.profile),
                out_dir=Path(args.out),
                receipt_path=Path(args.receipt),
                verify=bool(args.verify),
                repo_root=Path(args.repo_root),
                cache_dir=Path(args.cache_dir) if args.cache_dir else None,
                tarball=Path(args.tarball) if args.tarball else None,
                http_base_url=str(args.http_base_url or ""),
                max_total_bytes=int(args.max_total_bytes),
                recipe_path=Path(args.recipe) if args.recipe else None,
                run_recipe=bool(args.run_recipe),
                recipe_timeout_seconds=int(args.recipe_timeout),
                overwrite=bool(args.overwrite),
            )
        except MaterializationError as exc:
            raise ValueError(str(exc)) from exc
        return _success_payload(command, data)
    if command == "bootstrap-receipt":
        from ilc_core.rc.public_agent_bootstrap_receipt import (
            PublicAgentBootstrapReceiptError,
            build_public_agent_bootstrap_receipt,
            write_public_agent_bootstrap_receipt,
        )

        try:
            data = build_public_agent_bootstrap_receipt(
                repo_root=Path(args.repo_root),
                install_surface=str(args.install_surface),
                generated_at_utc=str(args.generated_at_utc) or None,
                graph_state_path=graph_state_path,
                identity_state_path=Path(args.identity_state) if args.identity_state else None,
                ccss_home=Path(args.ccss_home) if args.ccss_home else None,
                verifier_path=Path(args.verifier_path),
                skip_signature_verify=bool(args.skip_signature_verify),
                require_baseline_artifacts=bool(args.require_baseline_artifacts),
            )
            receipt_path = write_public_agent_bootstrap_receipt(Path(args.json_out), data)
            data = {**data, "receipt_path": str(receipt_path)}
        except PublicAgentBootstrapReceiptError as exc:
            raise ValueError(str(exc)) from exc
        return _success_payload(command, data)
    if command == "bootstrap-census":
        subcommand = getattr(args, "bootstrap_census_subcommand", None)
        if subcommand != "intake":
            raise ValueError(f"unknown_bootstrap_census_subcommand:{subcommand}")
        from ilc_core.rc.bootstrap_census_intake import (
            BootstrapCensusIntakeError,
            build_bootstrap_census_intake,
            write_bootstrap_census_intake,
        )

        try:
            data = build_bootstrap_census_intake(
                receipt_paths=[Path(value) for value in args.receipt_paths],
                receipt_dirs=[Path(value) for value in args.receipt_dirs],
                generated_at_utc=str(args.generated_at_utc) or None,
                source_label=str(args.source_label),
                fail_on_invalid=not bool(args.allow_invalid),
            )
            intake_path = write_bootstrap_census_intake(Path(args.json_out), data)
            data = {**data, "intake_path": str(intake_path)}
        except BootstrapCensusIntakeError as exc:
            raise ValueError(str(exc)) from exc
        return _success_payload(command, data)
    if command == "balance":
        data = _run_balance_command(args)
        return _success_payload(command, data)
    if command == "submit":
        from ilc_core.cli.d2e_submit_cli import handle_submit, SubmitCommandError

        try:
            data = handle_submit(args)
        except SubmitCommandError as exc:
            raise ValueError(exc.message) from exc
        return _success_payload(command, data)

    data = _prototype_data_for_command(command)
    return _success_payload(command, data)


def _run_node_operator_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "node_subcommand", None)
    if subcommand == "firewall-plan":
        firewall_runtime = _load_firewall_plan_runtime_module()
        plan = firewall_runtime.build_and_optionally_write_firewall_plan(
            config_path=Path(args.config),
            provider=str(args.provider),
            source_mode=str(args.source_mode),
            controller_ip=str(args.controller_ip) if args.controller_ip else None,
            validator_ips=str(args.validator_ips) if args.validator_ips else None,
            output_path=Path(args.output) if args.output else None,
        )
        return {"action": "node-firewall-plan", **plan.to_dict()}

    from ilc_core.node.operator_init_runtime import (
        check_node_config,
        generate_node_init_material,
    )
    from ilc_core.node.readiness_runtime import build_readiness_report

    if subcommand == "init":
        result = generate_node_init_material(
            root=Path(args.root),
            network_id=str(args.network_id),
            host=str(args.host),
            grpc_port=int(args.grpc_port),
            quic_port=int(args.quic_port),
            peer_seeds=list(args.peer_seed or []),
            valid_days=int(args.valid_days),
            allow_test_stub_crypto=bool(args.allow_test_stub_crypto),
            genesis_witness=bool(args.genesis_witness),
            asserted_at_epoch=int(args.asserted_at_epoch),
        )
        return {"action": "node-init", **result.to_dict()}
    if subcommand == "check":
        return {"action": "node-check", **check_node_config(Path(args.config))}
    if subcommand == "readiness":
        return {
            "action": "node-readiness",
            **build_readiness_report(
                config_path=Path(args.config),
                network=bool(args.network),
                peer=str(args.peer) if args.peer else None,
            ),
        }
    raise ValueError("node_operator_subcommand_missing")


def _load_firewall_plan_runtime_module() -> Any:
    """Load the firewall planner without importing heavy node package exports.

    `ilc_core.node.__init__` still exports historical protocol modules that may
    require optional crypto packages. The firewall planner is intentionally
    dependency-light so a public install can render operator firewall guidance
    on system Python before optional validator dependencies are installed.
    """

    import importlib.util

    module_name = "_ilc_firewall_plan_runtime"
    if module_name in sys.modules:
        return sys.modules[module_name]
    module_path = Path(__file__).resolve().parents[1] / "node" / "firewall_plan_runtime.py"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ValueError("node_firewall_plan_runtime_import_failed")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _run_relay_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "relay_subcommand", None)
    if subcommand != "serve":
        raise ValueError(f"unknown_relay_subcommand:{subcommand}")
    from ilc_core.network.relay.relay_server import (
        RelayServerConfig,
        RelayServerError,
        run_relay_http_server,
    )

    try:
        config = RelayServerConfig(
            relay_agent_id=str(args.agent_id),
            relay_host=str(args.relay_host),
            network_id=str(args.network_id),
            ttl_epochs=int(args.ttl_epochs),
            max_bytes_per_epoch=int(args.max_bytes_per_epoch),
            max_concurrent_streams=int(args.max_concurrent_streams),
            data_port_range_start=int(args.data_port_range_start),
            data_port_range_end=int(args.data_port_range_end),
            control_port=int(args.control_port),
            ssl_certfile=str(args.ssl_certfile) if args.ssl_certfile else None,
            ssl_keyfile=str(args.ssl_keyfile) if args.ssl_keyfile else None,
        )
        run_relay_http_server(
            config=config,
            bind_host=str(args.bind_host),
            allow_guarded_start=bool(args.allow_guarded_start),
        )
    except RelayServerError as exc:
        raise ValueError(str(exc)) from exc
    return {
        "action": "relay-serve",
        "control_port": config.control_port,
        "data_port_range": {
            "end": config.data_port_range_end,
            "start": config.data_port_range_start,
        },
        "network_id": config.network_id,
        "relay_agent_id": config.relay_agent_id,
        "relay_base_url": config.relay_base_url,
        "relay_host": config.relay_host,
        "status": "stopped",
    }


def _run_validator_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "validator_subcommand", None)
    if subcommand == "status":
        return _validator_status_data(args)
    if subcommand == "rotate-endpoint":
        from ilc_core.validator.endpoint_rotation_runtime import (
            rotate_validator_endpoint_assertion,
        )

        output_path = Path(args.output) if args.output else Path("out/validator_endpoint_rotation/new_assertion.json")
        return {
            "action": "validator-rotate-endpoint",
            **rotate_validator_endpoint_assertion(
                old_assertion_path=Path(args.old_assertion),
                new_endpoint=str(args.new_endpoint),
                network_id=str(args.network_id),
                key_path=Path(args.key),
                output_path=output_path,
                tls_cert_path=Path(args.tls_cert) if args.tls_cert else None,
                asserted_at_epoch=int(args.asserted_at_epoch)
                if args.asserted_at_epoch is not None
                else None,
                now_utc=datetime.now(timezone.utc),
                allow_test_stub_signature=bool(args.allow_test_stub_signature),
            ),
        }
    raise ValueError("validator_subcommand_missing")


def _validator_status_data(args: argparse.Namespace) -> dict[str, Any]:
    from ilc_core import __version__ as ilc_core_version

    home = Path.home()
    root = home.expanduser().resolve() / ".ilc" / "identity"
    agent_id_path = root / "agent_id"
    agent_id: str | None = None
    identity_status = "missing"
    if agent_id_path.is_file():
        try:
            candidate = agent_id_path.read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ValueError("validator_status_identity_unreadable") from exc
        if _AGENT_ID_HEX_RE.fullmatch(candidate) is None:
            raise ValueError("validator_status_agent_id_invalid")
        agent_id = candidate
        identity_status = "present"

    lmdb_path = Path(str(getattr(args, "lmdb_path", "") or home / ".ilc" / "lmdb")).expanduser()
    return {
        "action": "validator-status",
        "agent_id": agent_id,
        "identity_dir": str(root),
        "identity_provisioned": identity_status == "present",
        "identity_status": identity_status,
        "ilc_core_version": ilc_core_version,
        "lmdb_epoch": None,
        "lmdb_path": str(lmdb_path),
        "lmdb_readable": lmdb_path.exists() and os.access(lmdb_path, os.R_OK),
        "validator_participation_enabled": identity_status == "present",
    }


def _run_update_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    from ilc_core.release.update_runtime import (
        artifact_version,
        installed_ilc_core_version,
        is_already_current,
        select_update_artifact,
        verify_download_hash,
    )

    manifest = _load_update_manifest(args)
    artifact = select_update_artifact(manifest, str(args.channel))
    artifact_id = _require_update_artifact_string(artifact, "artifact_id")
    download_url = _require_update_https_url(artifact.get("download_url"), "download_url")
    canonical_hash = _require_update_artifact_string(artifact, "canonical_hash")
    size_bytes = _require_update_positive_int(artifact.get("size_bytes"), "size_bytes")
    version = artifact_version(artifact)
    installed_version = installed_ilc_core_version()
    advisory_current = is_already_current(artifact)

    result: dict[str, Any] = {
        "artifact_id": artifact_id,
        "canonical_hash": canonical_hash,
        "channel": str(args.channel),
        "download_url": download_url,
        "installed_version": installed_version,
        "selected_version": version,
        "status": "dry_run" if bool(args.dry_run) else "pending",
        "subcommand": "software-update",
    }
    if advisory_current:
        result["already_current_advisory"] = True
        result["already_current_token"] = "ilc_update_already_current"

    if bool(args.dry_run):
        result["event_token"] = f"ilc_update_would_install:{artifact_id}"
        return result

    if not bool(args.yes) and sys.stdin.isatty():
        answer = input(f"Install ilc-core from {download_url}? [y/N] ")
        if answer.strip().lower() not in {"y", "yes"}:
            result["status"] = "cancelled"
            result["_exit_code"] = 1
            result["event_token"] = "ilc_update_cancelled"
            return result

    with tempfile.TemporaryDirectory(prefix="ilc-update-") as temp_dir:
        temp_path = Path(temp_dir) / _update_wheel_filename_from_url(download_url)
        _download_update_wheel(download_url, temp_path, size_bytes)
        verify_download_hash(temp_path, canonical_hash)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", str(temp_path)],
            check=True,
            timeout=600,
        )
        post_install = subprocess.run(
            [sys.executable, "-m", "ilc_core.cli.main", "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if post_install.returncode != 0:
            raise ValueError("ilc_update_post_install_check_failed")
        from ilc_core.identity.first_run_provisioning import (
            migrate_identity_schema_if_needed,
        )

        result["identity_migration"] = migrate_identity_schema_if_needed(Path.home())

    result["status"] = "updated"
    result["event_token"] = f"ilc_update_success:{artifact_id}"
    return result


def _update_wheel_filename_from_url(download_url: str) -> str:
    parsed = urlparse(download_url)
    filename = Path(unquote(parsed.path)).name
    if _ILC_CORE_PY3_ANY_WHEEL_RE.fullmatch(filename) is None:
        raise ValueError("ilc_update_wheel_filename_invalid")
    return filename


def _load_update_manifest(args: argparse.Namespace) -> dict[str, Any]:
    manifest_path = str(getattr(args, "manifest_path", "") or "")
    manifest_url = str(getattr(args, "manifest_url", "") or "")
    if manifest_path:
        return _load_update_manifest_from_path(manifest_path)
    return _load_update_manifest_from_url(manifest_url or DEFAULT_UPDATE_MANIFEST_URL)


def _load_update_manifest_from_path(manifest_path: str) -> dict[str, Any]:
    if "://" in manifest_path:
        raise ValueError("ilc_update_manifest_path_must_be_bare_path")
    from ilc_core.release.installable_release_manifest import (
        InstallableReleaseManifestError,
        load_installable_release_manifest,
    )

    try:
        return load_installable_release_manifest(Path(manifest_path).expanduser())
    except InstallableReleaseManifestError as exc:
        raise ValueError(str(exc)) from exc


def _load_update_manifest_from_url(manifest_url: str) -> dict[str, Any]:
    url = _require_update_https_url(manifest_url, "manifest_url")
    request = Request(url, headers={"User-Agent": "ilc-update/GAP-PUBLIC-INSTALL-03"})
    try:
        with urlopen(request, timeout=30) as response:
            status = int(getattr(response, "status", 200))
            if status != 200:
                raise ValueError(f"ilc_update_manifest_fetch_failed:{status}")
            content_length = response.headers.get("Content-Length")
            if content_length:
                try:
                    declared_size = int(content_length)
                except ValueError as exc:
                    raise ValueError("ilc_update_manifest_content_length_invalid") from exc
                if declared_size > UPDATE_MANIFEST_MAX_BYTES:
                    raise ValueError("ilc_update_manifest_too_large")
            body = _read_bounded_http_body(response, UPDATE_MANIFEST_MAX_BYTES)
    except HTTPError as exc:
        raise ValueError(f"ilc_update_manifest_fetch_failed:{exc.code}") from exc
    except URLError as exc:
        raise ValueError("ilc_update_manifest_fetch_failed:network") from exc
    except TimeoutError as exc:
        raise ValueError("ilc_update_manifest_fetch_failed:timeout") from exc

    try:
        manifest = json.loads(
            body.decode("utf-8"),
            parse_constant=_reject_update_non_finite_json_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("ilc_update_manifest_json_invalid") from exc
    if not isinstance(manifest, dict):
        raise ValueError("ilc_update_manifest_not_object")

    from ilc_core.release.installable_release_manifest import (
        InstallableReleaseManifestError,
        validate_installable_release_manifest,
    )

    try:
        validate_installable_release_manifest(manifest)
    except InstallableReleaseManifestError as exc:
        raise ValueError(str(exc)) from exc
    return manifest


def _read_bounded_http_body(response: Any, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = response.read(UPDATE_HTTP_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > max_bytes:
            raise ValueError("ilc_update_manifest_too_large")
        chunks.append(chunk)
    return b"".join(chunks)


def _download_update_wheel(download_url: str, destination: Path, expected_size_bytes: int) -> None:
    from ilc_core.release.update_runtime import enforce_download_size

    url = _require_update_https_url(download_url, "download_url")
    request = Request(url, headers={"User-Agent": "ilc-update/GAP-PUBLIC-INSTALL-03"})
    try:
        with urlopen(request, timeout=120) as response:
            status = int(getattr(response, "status", 200))
            if status != 200:
                raise ValueError(f"ilc_update_download_failed:{status}")
            declared = response.headers.get("Content-Length")
            if declared:
                try:
                    declared_size = int(declared)
                except ValueError as exc:
                    raise ValueError("ilc_update_download_content_length_invalid") from exc
                enforce_download_size(declared_size, expected_size_bytes)
            downloaded = 0
            with destination.open("wb") as handle:
                while True:
                    chunk = response.read(UPDATE_HTTP_CHUNK_BYTES)
                    if not chunk:
                        break
                    downloaded += len(chunk)
                    enforce_download_size(downloaded, expected_size_bytes)
                    handle.write(chunk)
    except HTTPError as exc:
        raise ValueError(f"ilc_update_download_failed:{exc.code}") from exc
    except URLError as exc:
        raise ValueError("ilc_update_download_failed:network") from exc
    except TimeoutError as exc:
        raise ValueError("ilc_update_download_failed:timeout") from exc


def _reject_update_non_finite_json_constant(value: str) -> None:
    raise ValueError(f"ilc_update_manifest_non_finite_json_constant:{value}")


def _require_update_artifact_string(artifact: dict[str, Any], field: str) -> str:
    value = artifact.get(field)
    if not isinstance(value, str) or not value:
        raise ValueError(f"ilc_update_artifact_invalid_string:{field}")
    return value


def _require_update_positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"ilc_update_artifact_invalid_integer:{field}")
    return value


def _require_update_https_url(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"ilc_update_{field}_missing")
    if value.startswith("http://"):
        raise ValueError(f"ilc_update_{field}_not_https")
    if not value.startswith("https://"):
        raise ValueError(f"ilc_update_{field}_not_https")
    return value


def _run_install_subcommand(args: argparse.Namespace) -> dict[str, Any]:
    with _install_process_lock():
        return _run_install_subcommand_locked(args)


def _run_install_subcommand_locked(args: argparse.Namespace) -> dict[str, Any]:
    invite_bundle = _load_install_invite_bundle(str(args.from_invite))
    expected_profile = _install_expected_profile(invite_bundle)
    current_epoch = _install_current_epoch(invite_bundle)
    invite_id = _install_invite_id(invite_bundle)
    from ilc_core.identity.first_run_provisioning import (
        fetch_distributed_release_peers,
        validate_invite_bootstrap_capsule_fields,
    )

    invite_capsule_evidence = validate_invite_bootstrap_capsule_fields(
        invite_bundle,
        current_epoch=current_epoch,
    )

    from ilc_core.genesis.invite_nullifier_lmdb_store import InviteNullifierLmdbRegistry
    from ilc_core.sidecars.openclaw_invite_bootstrap import (
        verify_invite_bootstrap,
    )

    nullifier_registry_path = Path.home() / ".ilc" / "lmdb" / "nullifiers"
    with InviteNullifierLmdbRegistry(nullifier_registry_path) as nullifier_registry:
        decision = verify_invite_bootstrap(
            _invite_bootstrap_payload(invite_bundle),
            expected_profile=expected_profile,
            current_epoch=current_epoch,
            local_nullifier_registry=nullifier_registry,
            persist_nullifier=True,
            register_nullifier=False,
            production_required=False,
        )
        if not decision.bootstrap_allowed:
            raise ValueError(f"invite_verification_failed:{decision.defect_token or 'not_allowed'}")

        witness = _required_mapping(
            invite_bundle.get("atlas_slice_manifest_witness"),
            "invite_bundle_missing_atlas_slice_manifest_witness",
        )
        from ilc_core.bundle.atlas_slice_verifier import (
            AtlasSliceVerifierError,
            verify_portable_manifest_witness,
        )

        try:
            manifest_verification = verify_portable_manifest_witness(witness)
        except AtlasSliceVerifierError as exc:
            raise ValueError(f"manifest_verification_failed:{exc}") from exc
        if manifest_verification.get("verified") is not True:
            token = manifest_verification.get("error") or "not_verified"
            raise ValueError(f"manifest_verification_failed:{token}")
        distributed_fetch_evidence = fetch_distributed_release_peers(
            invite_bundle,
            invite_capsule_evidence,
        )

        materialization_payload = _install_materialization_payload(invite_bundle, witness)
        target_dir = _install_target_dir(args, materialization_payload, witness)
        output_receipt = _install_receipt_path(args, target_dir)

        from ilc_core.sidecars.starmap_installer import (
            StarMapInstallerError,
            build_install_receipt,
            materialize_starmap_manifest,
        )

        receipt_written = False
        receipt_preexisted = output_receipt.exists()
        planned_materialized_paths: tuple[tuple[Path, str], ...] = ()
        try:
            receipt = build_install_receipt(materialization_payload)
            planned_materialized_paths = _install_planned_materialized_paths(target_dir, receipt)
            _reject_existing_materialized_paths(planned_materialized_paths)
            materialization = materialize_starmap_manifest(
                materialization_payload,
                target=target_dir,
                dry_run=False,
            )
        except StarMapInstallerError as exc:
            _rollback_install_side_effects(
                planned_materialized_paths,
                output_receipt=output_receipt,
                receipt_written=False,
                receipt_preexisted=receipt_preexisted,
            )
            raise ValueError(f"install_materialization_failed:{exc}") from exc
        _write_install_receipt_atomic(output_receipt, receipt)
        receipt_written = True
        from ilc_core.identity.first_run_provisioning import (
            IdentityAlreadyExistsError,
            attach_invite_pop_to_onboarding_receipt,
            existing_identity_summary,
            identity_root,
            provision_new_identity,
            record_invite_bootstrap_capsule_evidence,
            record_install_connectivity_receipt,
            write_invitee_install_receipt,
        )

        had_existing_identity = (identity_root(Path.home()) / "signing_key.hex").exists()
        created_fresh_identity = False
        force_reprovision = bool(getattr(args, "force_reprovision", False))
        try:
            identity_provisioning = provision_new_identity(
                Path.home(),
                invite_id=invite_id,
                epoch=current_epoch,
                force_reprovision=force_reprovision,
            )
            created_fresh_identity = not had_existing_identity
        except IdentityAlreadyExistsError:
            print(
                "identity_provisioning_skipped_existing_identity: "
                "use --force-reprovision only after explicit destructive confirmation",
                file=sys.stderr,
            )
            identity_provisioning = existing_identity_summary(Path.home())

        try:
            agent_id = str(identity_provisioning["agent_id"])
            onboarding_receipt = attach_invite_pop_to_onboarding_receipt(
                Path.home(),
                invite_id=invite_id,
                invite_nullifier=str(decision.redemption_nullifier),
                epoch=current_epoch,
                nullifier_persisted=True,
                nullifier_registry="lmdb:~/.ilc/lmdb/nullifiers/",
            )
            redemption_record = _install_invite_redemption_record(
                invite_bundle=invite_bundle,
                agent_id=agent_id,
                invite_id=invite_id,
                redemption_nullifier=str(decision.redemption_nullifier or ""),
                current_epoch=current_epoch,
                redeemer_key_binding={
                    "domain": str(onboarding_receipt["invite_pop_domain"]),
                    "payload_ref": str(onboarding_receipt["invite_pop_payload_ref"]),
                    "signature": str(onboarding_receipt["invite_pop"]),
                },
            )

            from ilc_core.genesis.invite_enforcement import (
                is_enrollment_invite_enforced,
                require_invite_for_enrollment,
            )
            from ilc_core.genesis.invitation_provenance_record import (
                verify_invite_redemption_redeemer_key_binding,
            )

            verify_invite_redemption_redeemer_key_binding(redemption_record)
            require_invite_for_enrollment(
                agent_id,
                redemption_record,
                nullifier_registry=nullifier_registry,
                register_nullifier=True,
            )
            invite_verification = decision.to_dict()
            if not is_enrollment_invite_enforced():
                if not nullifier_registry.register_if_new(str(decision.redemption_nullifier)):
                    raise ValueError("invite_nullifier_already_used_for_enrollment")
            invite_verification["nullifier_status"] = "recorded"
            invite_verification["enrollment_nullifier_status"] = "recorded"
            relay_selection = _install_relay_bootstrap_selection(
                args,
                invite_bundle=invite_bundle,
                current_epoch=current_epoch,
            )
            connectivity_result = record_install_connectivity_receipt(
                Path.home(),
                agent_id=agent_id,
                epoch=current_epoch,
                attempt_router_mapping=bool(getattr(args, "enable_upnp", False)),
                observers=_install_probe_observers(args),
                relay_server_url=(
                    None
                    if relay_selection is None
                    else str(relay_selection["relay_base_url"])
                ),
                relay_admission_material=_install_relay_admission_material(
                    args,
                    relay_selection=relay_selection,
                    agent_id=agent_id,
                    invite_id=invite_id,
                    invite_nullifier=str(decision.redemption_nullifier),
                    invite_pop=str(onboarding_receipt["invite_pop"]),
                    invite_pop_payload_ref_value=str(
                        onboarding_receipt["invite_pop_payload_ref"]
                    ),
                    invite_pop_epoch=current_epoch,
                ),
                internal_port=_install_relay_internal_port(args),
            )
            connectivity_receipt = dict(connectivity_result["connectivity_receipt"])
            onboarding_receipt = dict(connectivity_result["onboarding_receipt"])
            capsule_record = record_invite_bootstrap_capsule_evidence(
                Path.home(),
                agent_id=agent_id,
                current_epoch=current_epoch,
                capsule_evidence=invite_capsule_evidence,
                distributed_fetch_evidence=distributed_fetch_evidence,
            )
            onboarding_receipt = dict(capsule_record["onboarding_receipt"])
            invitee_install_receipt = write_invitee_install_receipt(
                Path.home(),
                agent_id=agent_id,
                invite_id=invite_id,
                invite_nullifier=str(decision.redemption_nullifier),
                install_epoch=current_epoch,
                genesis_state_root=str(invite_capsule_evidence["genesis_state_root"]),
                connectivity_receipt=connectivity_receipt,
                onboarding_receipt=onboarding_receipt,
                installed_release_artifact_id=_install_slice_id(
                    materialization_payload,
                    witness,
                ),
                installed_release_canonical_hash=_install_release_canonical_hash(
                    materialization_payload,
                    witness,
                ),
            )
            receipt.update(_install_connectivity_receipt_fields(connectivity_receipt))
            receipt.update(
                _install_invite_bootstrap_capsule_fields(
                    capsule_record,
                    invitee_install_receipt,
                )
            )
            _write_install_receipt_atomic(output_receipt, receipt)
            return {
                "bootstrap_fetch_peers": capsule_record["bootstrap_fetch_peers"],
                "bootstrap_peer_hints": capsule_record["bootstrap_peer_hints"],
                "connectivity_receipt": connectivity_receipt,
                "connectivity_summary": connectivity_receipt["connectivity_summary"],
                "identity_provisioning": identity_provisioning,
                "invite_bootstrap_capsule_evidence": capsule_record[
                    "invite_bootstrap_capsule_evidence"
                ],
                "invitee_install_receipt": invitee_install_receipt,
                "invite_redemption_record": redemption_record,
                "invite_verification": invite_verification,
                "manifest_verification": manifest_verification,
                "materialization": materialization,
                "onboarding_receipt": onboarding_receipt,
                "receipt_path": str(output_receipt),
                "slice_id": str(
                    materialization.get(
                        "slice_id",
                        _install_slice_id(materialization_payload, witness),
                    )
                ),
                "status": "ok",
                "subcommand": "from-invite",
                "target_dir": str(target_dir),
            }
        except Exception:
            if created_fresh_identity:
                shutil.rmtree(identity_root(Path.home()), ignore_errors=True)
            _rollback_install_side_effects(
                planned_materialized_paths,
                output_receipt=output_receipt,
                receipt_written=receipt_written,
                receipt_preexisted=receipt_preexisted,
            )
            raise


@contextmanager
def _install_process_lock() -> Any:
    lock_dir = Path.home() / ".ilc"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock_path = lock_dir / "install.lock"
    with lock_path.open("a+", encoding="utf-8") as handle:
        try:
            import fcntl
        except ImportError:
            yield
            return
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _load_install_invite_bundle(source: str) -> dict[str, Any]:
    if not source:
        raise ValueError("install_invite_source_missing")
    if source.startswith(("http://", "https://")):
        raise ValueError("install_invite_url_fetch_not_supported")
    if source == "-":
        raw = sys.stdin.buffer.read(INSTALL_INVITE_MAX_BYTES + 1)
    elif source.lstrip().startswith("{"):
        raw = source.encode("utf-8")
    else:
        path = _install_source_path(source)
        raw = _read_install_invite_bundle_file(path)
    if len(raw) > INSTALL_INVITE_MAX_BYTES:
        raise ValueError("install_invite_bundle_too_large")
    try:
        payload = _loads_json_no_constants(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("install_invite_bundle_json_invalid") from exc
    if not isinstance(payload, dict):
        raise ValueError("install_invite_bundle_not_object")
    _reject_float(payload, "install_invite_float_not_allowed")
    if "shortcode_auth" in payload:
        from ilc_core.network.relay.relay_server import verify_shortcode_invite_bundle

        if not verify_shortcode_invite_bundle(payload):
            raise ValueError("install_sh_invite_code_bundle_signature_invalid")
    return payload


def _read_install_invite_bundle_file(path: Path) -> bytes:
    try:
        with path.open("rb") as handle:
            raw = handle.read(INSTALL_INVITE_MAX_BYTES + 1)
    except OSError as exc:
        raise ValueError("install_invite_bundle_unreadable") from exc
    if len(raw) > INSTALL_INVITE_MAX_BYTES:
        raise ValueError("install_invite_bundle_too_large")
    return raw


def _install_source_path(source: str) -> Path:
    if source.startswith("file://"):
        path = Path(source.removeprefix("file://"))
        if not path.is_absolute():
            raise ValueError("install_invite_file_uri_must_be_absolute")
        return path
    return Path(source).expanduser()


def _install_expected_profile(invite_bundle: dict[str, Any]) -> str:
    value = invite_bundle.get("intended_profile")
    if not isinstance(value, str) or not value:
        raise ValueError("install_invite_intended_profile_invalid")
    return value


def _install_invite_id(invite_bundle: dict[str, Any]) -> str:
    value = invite_bundle.get("invite_id")
    if isinstance(value, str) and value:
        return value
    batch = _required_mapping(
        invite_bundle.get("invite_batch_record"),
        "install_invite_batch_record_missing",
    )
    return _required_non_empty_str(batch.get("batch_id"), "install_invite_batch_id_invalid")


def _invite_bootstrap_payload(invite_bundle: dict[str, Any]) -> dict[str, Any]:
    invite_keys = {
        "intended_epoch",
        "intended_profile",
        "invite_batch_record",
        "nonce_membership_proof",
        "private_invite_nonce",
        "redeemer_agent_id",
        "redeemer_pubkey",
        "intended_redeemer_pubkey",
    }
    return {
        key: invite_bundle[key]
        for key in sorted(invite_keys)
        if key in invite_bundle
    }


def _install_current_epoch(invite_bundle: dict[str, Any]) -> int:
    value = invite_bundle.get("intended_epoch")
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("install_invite_intended_epoch_invalid")
    return value


def _install_invite_redemption_record(
    *,
    invite_bundle: dict[str, Any],
    agent_id: str,
    invite_id: str,
    redemption_nullifier: str,
    current_epoch: int,
    redeemer_key_binding: dict[str, str],
) -> dict[str, Any]:
    from ilc_core.genesis.invitation_provenance_record import (
        InviteRedemptionRecord,
        validate_invite_redemption_record,
    )

    batch = _required_mapping(
        invite_bundle.get("invite_batch_record"),
        "install_invite_batch_record_missing",
    )
    proof = _install_redemption_membership_proof(invite_bundle.get("nonce_membership_proof"))
    inviter_cid = _required_non_empty_str(batch.get("inviter_cid"), "install_inviter_cid_invalid")
    batch_id = _required_non_empty_str(batch.get("batch_id"), "install_invite_batch_id_invalid")
    record = InviteRedemptionRecord(
        batch_id=batch_id,
        redemption_nullifier=redemption_nullifier,
        nonce_membership_proof=proof,
        redeemer_pubkey_cid=(
            _optional_non_empty_str(invite_bundle.get("redeemer_pubkey_cid"))
            or f"agent:{agent_id}"
        ),
        redeemer_agent_id=agent_id,
        redemption_epoch=current_epoch,
        inviter_cid=inviter_cid,
        invite_id=invite_id,
        redeemer_key_binding=redeemer_key_binding,
    )
    validate_invite_redemption_record(record)
    return record.to_dict()


def _install_redemption_membership_proof(value: object) -> tuple[dict[str, str], ...]:
    if value in (None, (), []):
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError("install_invite_nonce_membership_proof_invalid")
    steps: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("install_invite_nonce_membership_proof_invalid")
        sibling = item.get("sibling")
        position = item.get("position")
        if not isinstance(sibling, str) or position not in {"left", "right"}:
            raise ValueError("install_invite_nonce_membership_proof_invalid")
        steps.append({"position": str(position), "sibling": sibling})
    return tuple(steps)


def _required_non_empty_str(value: object, token: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(token)
    return value


def _optional_non_empty_str(value: object) -> str | None:
    return value if isinstance(value, str) and value else None


def _required_mapping(value: object, token: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(token)
    _reject_float(value, f"{token}:float_not_allowed")
    return value


def _install_materialization_payload(
    invite_bundle: dict[str, Any],
    witness: dict[str, Any],
) -> dict[str, Any]:
    payload = invite_bundle.get("starmap_manifest_payload")
    if payload is None:
        payload = invite_bundle.get("atlas_slice_manifest_payload", witness)
    return _required_mapping(payload, "invite_bundle_materialization_payload_invalid")


def _install_slice_id(materialization_payload: dict[str, Any], witness: dict[str, Any]) -> str:
    for payload in (materialization_payload, witness):
        value = payload.get("slice_id")
        if isinstance(value, str) and value:
            return value
    return "unknown_slice"


def _install_release_canonical_hash(
    materialization_payload: dict[str, Any],
    witness: dict[str, Any],
) -> str | None:
    for payload in (materialization_payload, witness):
        for key in (
            "canonical_hash",
            "manifest_canonical_hash",
            "content_hash",
            "source_manifest_sha256",
        ):
            value = payload.get(key)
            if isinstance(value, str) and value:
                return value
    return None


def _install_target_dir(
    args: argparse.Namespace,
    materialization_payload: dict[str, Any],
    witness: dict[str, Any],
) -> Path:
    requested = str(getattr(args, "target_dir", "") or "")
    if requested:
        return Path(requested).expanduser().resolve()
    slice_id = _safe_path_segment(_install_slice_id(materialization_payload, witness))
    return (Path("out") / "installed_slices" / slice_id).resolve()


def _install_receipt_path(args: argparse.Namespace, target_dir: Path) -> Path:
    requested = str(getattr(args, "output_receipt", "") or "")
    if requested:
        return Path(requested).expanduser().resolve()
    return target_dir / "install_receipt.json"


def _install_relay_admission_material(
    args: argparse.Namespace,
    *,
    relay_selection: dict[str, Any] | None = None,
    agent_id: str,
    invite_id: str,
    invite_nullifier: str,
    invite_pop: str,
    invite_pop_payload_ref_value: str,
    invite_pop_epoch: int,
) -> dict[str, Any] | None:
    path_value = str(getattr(args, "relay_admission_material", "") or "")
    if path_value:
        if relay_selection is not None and "relay_admission_material" in relay_selection:
            relay_material = relay_selection["relay_admission_material"]
            if not isinstance(relay_material, dict):
                raise ValueError("install_relay_prebuilt_material_invalid")
            return dict(relay_material)
        from ilc_core.cli.network_doctor import _load_relay_admission_material

        return _load_relay_admission_material(path_value)

    relay_base_url = (
        str(getattr(args, "relay_url", "") or "")
        if relay_selection is None
        else str(relay_selection["relay_base_url"])
    )
    if not relay_base_url:
        return None

    tls_cert_der_sha256 = (
        str(getattr(args, "relay_tls_cert_der_sha256", "") or "")
        if relay_selection is None
        else str(relay_selection["tls_cert_der_sha256"])
    )
    if not tls_cert_der_sha256:
        raise ValueError("install_relay_tls_cert_der_sha256_required")

    from ilc_core import __version__ as ilc_core_version
    from ilc_core.identity.bls_backend import sign_relay_admission_digest
    from ilc_core.identity.first_run_provisioning import identity_root
    from ilc_core.network.relay.relay_client import (
        RelayClientError,
        RelayAdmissionRequest,
        relay_admission_payload_ref,
    )

    network_id = str(
        getattr(args, "relay_network_id", "") or INSTALL_RELAY_DEFAULT_NETWORK_ID
    )
    internal_port = _install_relay_internal_port(args)
    try:
        payload_ref = relay_admission_payload_ref(
            agent_id=agent_id,
            invite_id=invite_id,
            invite_nullifier=invite_nullifier,
            invite_pop_payload_ref_value=invite_pop_payload_ref_value,
            admission_epoch=invite_pop_epoch,
            network_id=network_id,
            relay_base_url=relay_base_url,
            requested_internal_port=internal_port,
            requested_protocol="quic",
            software_version=ilc_core_version,
        )
    except RelayClientError as exc:
        raise ValueError(str(exc)) from exc

    signing_key_path = identity_root(Path.home()) / "signing_key.hex"
    try:
        secret_key_hex = signing_key_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError("install_relay_signing_key_unreadable") from exc
    relay_admission_signature = sign_relay_admission_digest(secret_key_hex, payload_ref)
    material = {
        "admission_epoch": invite_pop_epoch,
        "agent_id": agent_id,
        "invite_id": invite_id,
        "invite_nullifier": invite_nullifier,
        "invite_pop": invite_pop,
        "invite_pop_epoch": invite_pop_epoch,
        "network_id": network_id,
        "relay_admission_payload_ref": payload_ref,
        "relay_admission_signature": relay_admission_signature,
        "relay_base_url": relay_base_url,
        "requested_internal_port": internal_port,
        "requested_protocol": "quic",
        "software_version": ilc_core_version,
        "tls_cert_der_sha256": tls_cert_der_sha256,
    }
    try:
        request_material = {
            key: value
            for key, value in material.items()
            if key != "tls_cert_der_sha256"
        }
        RelayAdmissionRequest(**request_material)
    except RelayClientError as exc:
        raise ValueError(str(exc)) from exc
    return material


def _install_relay_bootstrap_selection(
    args: argparse.Namespace,
    *,
    invite_bundle: dict[str, Any],
    current_epoch: int,
) -> dict[str, Any] | None:
    explicit_relay_url = str(getattr(args, "relay_url", "") or "")
    explicit_tls_pin = str(getattr(args, "relay_tls_cert_der_sha256", "") or "")
    prebuilt_material_path = str(getattr(args, "relay_admission_material", "") or "")
    network_id = str(
        getattr(args, "relay_network_id", "") or INSTALL_RELAY_DEFAULT_NETWORK_ID
    )
    capsule = invite_bundle.get("relay_bootstrap_capsule")
    verified_records = _install_verified_relay_bootstrap_records(
        capsule,
        expected_network_id=network_id,
        current_epoch=current_epoch,
    )
    if capsule is not None and not verified_records:
        raise ValueError("install_relay_bootstrap_capsule_no_verified_records")

    if prebuilt_material_path:
        return _install_prebuilt_relay_bootstrap_selection(
            args,
            verified_records=verified_records,
        )

    if explicit_relay_url:
        if verified_records:
            matches = [
                record
                for record in verified_records
                if record.get("control_url") == explicit_relay_url
            ]
            if not matches:
                raise ValueError("install_relay_bootstrap_control_url_mismatch")
            selected = matches[0]
            selected_tls_pin = _install_relay_record_tls_pin(selected)
            if explicit_tls_pin and explicit_tls_pin != selected_tls_pin:
                raise ValueError("install_relay_bootstrap_tls_pin_mismatch")
            return {
                "relay_base_url": explicit_relay_url,
                "tls_cert_der_sha256": selected_tls_pin,
            }
        if not explicit_tls_pin:
            raise ValueError("install_relay_tls_cert_der_sha256_required")
        return {
            "relay_base_url": explicit_relay_url,
            "tls_cert_der_sha256": explicit_tls_pin,
        }

    if not verified_records:
        return None
    selected = sorted(
        verified_records,
        key=lambda record: (
            str(record.get("control_url")),
            str(record.get("relay_agent_id")),
        ),
    )[0]
    return {
        "relay_base_url": str(selected["control_url"]),
        "tls_cert_der_sha256": _install_relay_record_tls_pin(selected),
    }


def _install_prebuilt_relay_bootstrap_selection(
    args: argparse.Namespace,
    *,
    verified_records: tuple[dict[str, Any], ...],
) -> dict[str, Any]:
    from ilc_core.cli.network_doctor import _load_relay_admission_material

    path_value = str(getattr(args, "relay_admission_material", "") or "")
    explicit_relay_url = str(getattr(args, "relay_url", "") or "")
    explicit_tls_pin = str(getattr(args, "relay_tls_cert_der_sha256", "") or "")
    material = _load_relay_admission_material(path_value)
    material_relay_url = _required_non_empty_str(
        material.get("relay_base_url"),
        "install_relay_prebuilt_base_url_invalid",
    )
    material_tls_pin = _install_relay_tls_pin(
        material.get("tls_cert_der_sha256"),
        "install_relay_prebuilt_tls_pin_invalid",
    )
    if explicit_relay_url and explicit_relay_url != material_relay_url:
        raise ValueError("install_relay_prebuilt_base_url_mismatch")
    if explicit_tls_pin and explicit_tls_pin != material_tls_pin:
        raise ValueError("install_relay_prebuilt_tls_pin_mismatch")
    if verified_records:
        matches = [
            record
            for record in verified_records
            if record.get("control_url") == material_relay_url
        ]
        if not matches:
            raise ValueError("install_relay_bootstrap_control_url_mismatch")
        if material_tls_pin != _install_relay_record_tls_pin(matches[0]):
            raise ValueError("install_relay_bootstrap_tls_pin_mismatch")
    return {
        "relay_base_url": material_relay_url,
        "relay_admission_material": dict(material),
        "tls_cert_der_sha256": material_tls_pin,
    }


def _install_verified_relay_bootstrap_records(
    capsule: object,
    *,
    expected_network_id: str,
    current_epoch: int,
) -> tuple[dict[str, Any], ...]:
    if capsule is None:
        return ()
    if not isinstance(capsule, dict):
        raise ValueError("install_relay_bootstrap_capsule_invalid")

    from ilc_core.epoch.genesis_settlement_destination import (
        GENESIS_CAPSULE_SIGNING_PK_HEX,
    )
    from ilc_core.network.relay.relay_server import parse_relay_bootstrap_capsule

    records = parse_relay_bootstrap_capsule(
        capsule,
        genesis_capsule_pk_hex=GENESIS_CAPSULE_SIGNING_PK_HEX,
        expected_network_id=expected_network_id,
        current_epoch=current_epoch,
    )
    if len(records) > INSTALL_RELAY_BOOTSTRAP_RECORD_MAX_COUNT:
        raise ValueError("install_relay_bootstrap_capsule_too_many_records")
    return tuple(dict(record) for record in records)


def _install_relay_record_tls_pin(record: dict[str, Any]) -> str:
    return _install_relay_tls_pin(
        record.get("tls_cert_der_sha256"),
        "install_relay_bootstrap_tls_pin_invalid",
    )


def _install_relay_tls_pin(value: object, token: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(token)
    if any(char not in "0123456789abcdef" for char in value):
        raise ValueError(token)
    return value


def _install_relay_internal_port(args: argparse.Namespace) -> int:
    value = getattr(args, "relay_internal_port", INSTALL_RELAY_DEFAULT_INTERNAL_PORT)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("install_relay_internal_port_invalid")
    if value < 1 or value > 65535:
        raise ValueError("install_relay_internal_port_invalid")
    return value



def _install_probe_observers(args: argparse.Namespace) -> tuple[str, ...]:
    values = tuple(getattr(args, "probe_observer", []) or ())
    if len(values) > INSTALL_PROBE_OBSERVER_MAX_COUNT:
        raise ValueError("install_probe_observer_count_exceeded")
    return values


def _install_connectivity_receipt_fields(
    connectivity_receipt: dict[str, Any],
) -> dict[str, Any]:
    return {
        "connectivity_evidence_status": connectivity_receipt["connectivity_evidence_status"],
        "connectivity_mode": connectivity_receipt["connectivity_mode"],
        "connectivity_receipt_path": connectivity_receipt["connectivity_receipt_path"],
        "connectivity_receipt_sha384": connectivity_receipt["connectivity_receipt_sha384"],
        "connectivity_summary": connectivity_receipt["connectivity_summary"],
        "firewall_mutation_attempted": connectivity_receipt["firewall_mutation_attempted"],
        "firewall_mutation_status": connectivity_receipt["firewall_mutation_status"],
        "observed_endpoint": connectivity_receipt["observed_endpoint"],
        "relay_endpoint": connectivity_receipt["relay_endpoint"],
    }


def _install_invite_bootstrap_capsule_fields(
    capsule_record: dict[str, Any],
    invitee_install_receipt: dict[str, Any],
) -> dict[str, Any]:
    evidence = capsule_record.get("invite_bootstrap_capsule_evidence")
    if not isinstance(evidence, dict):
        raise ValueError("install_invite_bootstrap_capsule_evidence_invalid")
    invitee_install_receipt_path = (
        Path.home() / ".ilc" / "identity" / "invitee_install_receipt.json"
    )
    return {
        "bootstrap_peer_hints_count": evidence["bootstrap_peer_hints_count"],
        "bootstrap_peer_hints_path": evidence["bootstrap_peer_hints_path"],
        "bootstrap_peer_hints_sha384": evidence["bootstrap_peer_hints_sha384"],
        "bootstrap_peer_hints_written": evidence["bootstrap_peer_hints_written"],
        "bootstrap_fetch_bundle_cid": evidence["bootstrap_fetch_bundle_cid"],
        "bootstrap_fetch_genesis_authority_pubkey_hex": evidence[
            "bootstrap_fetch_genesis_authority_pubkey_hex"
        ],
        "bootstrap_fetch_peer_endpoints": evidence["bootstrap_fetch_peer_endpoints"],
        "bootstrap_fetch_peers_count": evidence["bootstrap_fetch_peers_count"],
        "bootstrap_fetch_peers_path": evidence["bootstrap_fetch_peers_path"],
        "bootstrap_fetch_peers_sha384": evidence["bootstrap_fetch_peers_sha384"],
        "bootstrap_fetch_peers_written": evidence["bootstrap_fetch_peers_written"],
        "bootstrap_fetch_seed_peer_endpoint": evidence["bootstrap_fetch_seed_peer_endpoint"],
        "bootstrap_fetch_status": evidence["bootstrap_fetch_status"],
        "genesis_state_root": evidence["genesis_state_root"],
        "genesis_state_root_status": evidence["genesis_state_root_status"],
        "invite_bootstrap_capsule_schema_version": evidence[
            "invite_bootstrap_capsule_schema_version"
        ],
        "invitee_install_receipt_path": str(invitee_install_receipt_path),
        "invitee_install_receipt_sha384": hashlib.sha384(
            json.dumps(
                invitee_install_receipt,
                sort_keys=True,
                separators=(",", ":"),
                allow_nan=False,
            ).encode("utf-8")
        ).hexdigest(),
        "inviter_connectivity_mode": evidence["inviter_connectivity_mode"],
        "known_peer_hints_dropped_expired": evidence["known_peer_hints_dropped_expired"],
        "known_peer_hints_dropped_invalid": evidence["known_peer_hints_dropped_invalid"],
        "known_peer_hints_dropped_unverifiable": evidence[
            "known_peer_hints_dropped_unverifiable"
        ],
        "known_peer_hints_offered": evidence["known_peer_hints_offered"],
        "known_peer_hints_verified": evidence["known_peer_hints_verified"],
    }


def _write_install_receipt_atomic(path: Path, receipt: dict[str, Any]) -> Path:
    _reject_float(receipt, "install_receipt_float_not_allowed")
    payload = json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        os.chmod(temp_name, 0o644)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = -1
            handle.write(payload)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except BaseException:
        if fd != -1:
            os.close(fd)
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            _temp_file_already_removed = True
        raise
    return path


def _install_planned_materialized_paths(
    target_dir: Path,
    receipt: dict[str, Any],
) -> tuple[tuple[Path, str], ...]:
    content_hashes = receipt.get("content_hashes")
    if not isinstance(content_hashes, dict):
        raise ValueError("install_receipt_content_hashes_invalid")
    planned: list[tuple[Path, str]] = []
    for relative, expected_sha256 in content_hashes.items():
        if not isinstance(relative, str) or not relative:
            raise ValueError("install_materialization_relative_path_invalid")
        if not isinstance(expected_sha256, str) or len(expected_sha256) != 64:
            raise ValueError("install_materialization_expected_hash_invalid")
        if any(char not in "0123456789abcdef" for char in expected_sha256):
            raise ValueError("install_materialization_expected_hash_invalid")
        relative_path = Path(relative)
        if relative_path.is_absolute() or any(part in {"", ".", ".."} for part in relative_path.parts):
            raise ValueError("install_materialization_relative_path_invalid")
        planned.append((target_dir / relative_path, expected_sha256))
    return tuple(planned)


def _reject_existing_materialized_paths(planned_paths: tuple[tuple[Path, str], ...]) -> None:
    for path, _expected_sha256 in planned_paths:
        if path.exists():
            raise ValueError(f"install_materialization_target_path_exists:{path}")


def _rollback_install_side_effects(
    planned_paths: tuple[tuple[Path, str], ...],
    *,
    output_receipt: Path,
    receipt_written: bool,
    receipt_preexisted: bool,
) -> None:
    for path, expected_sha256 in planned_paths:
        try:
            if path.is_file() and _sha256_file(path) == expected_sha256:
                path.unlink()
        except OSError as exc:
            _rollback_cleanup_error = exc
    if receipt_written and not receipt_preexisted:
        try:
            output_receipt.unlink()
        except FileNotFoundError:
            _receipt_already_removed = True


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(UPDATE_HTTP_CHUNK_BYTES), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_path_segment(value: str) -> str:
    safe = "".join(char if char.isalnum() or char in {"-", "_", "."} else "_" for char in value)
    return safe.strip("._") or "unknown_slice"


def _reject_float(value: object, token: str) -> None:
    if isinstance(value, float):
        raise ValueError(token)
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_float(key, token)
            _reject_float(item, token)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_float(item, token)


def _query_error_result(
    args: argparse.Namespace,
    exc: QueryCommandError,
) -> tuple[int, dict[str, Any]]:
    return 1, _query_error_payload(
        command_token=_query_command_token(args),
        code=exc.code,
        message=exc.message,
    )


def _verify_error_result(
    args: argparse.Namespace,
    exc: VerifyCommandError,
) -> tuple[int, dict[str, Any]]:
    return 1, _verify_error_payload(
        command_token=_verify_command_token(args),
        code=exc.code,
        message=exc.message,
    )


def _bundle_error_result(
    args: argparse.Namespace,
    exc: BundleCommandError,
) -> tuple[int, dict[str, Any]]:
    return 1, _bundle_error_payload(
        command_token=_bundle_command_token(args),
        code=exc.code,
        message=exc.message,
    )


def _value_error_result(command: str, exc: ValueError) -> tuple[int, dict[str, Any]]:
    return 1, _error_payload(
        command=command,
        code=1,
        message=str(exc),
        details={"phase": "264"},
    )


def main() -> int:
    # Short-circuit sidecar passthrough commands before argparse so that
    # sidecar-specific flags (e.g. --open, --summary) are not consumed by
    # the top-level parser.  Pattern: ilc sidecar <name> [args...]
    #
    # Convention: every external sidecar package exposes a Python module
    # named ilc_sidecar_<snake_name> with a main(argv) entry point.
    # The CLI name is <kebab-name>, e.g.:
    #   ilc sidecar graph-viz --open   →  ilc_sidecar_graph_viz.main(["--open"])
    #   ilc sidecar ccss-monitor ...   →  ilc_sidecar_ccss_monitor.main([...])
    #
    # Built-in sidecars (graph-viz) are registered here explicitly.
    _SIDECAR_PASSTHROUGH: dict[str, str] = {
        "graph-viz": "ilc_graph_viz.__main__",
        "genesis-atlas": "ilc_genesis_atlas.__main__",
    }
    argv = sys.argv[1:]
    if len(argv) >= 2 and argv[0] == "sidecar" and argv[1] in _SIDECAR_PASSTHROUGH:
        sidecar_name = argv[1]
        module_path = _SIDECAR_PASSTHROUGH[sidecar_name]
        sidecar_argv = argv[2:]
        try:
            import importlib
            mod = importlib.import_module(module_path)
            raise SystemExit(mod.main(sidecar_argv))
        except ModuleNotFoundError:
            _write_json_payload(
                {
                    "ok": False,
                    "error": True,
                    "code": "sidecar_not_installed",
                    "message": (
                        f"sidecar '{sidecar_name}' is not installed. "
                        f"Run install.sh from the ilc-graphics-sidecar repo."
                    ),
                },
                stderr=True,
            )
            return 1

    parser = _build_parser()
    args = parser.parse_args()

    if args.command is None:
        _write_json_payload(
            {
                "help": "run 'ilc --help' for full command reference",
                "hint": "ILC — Intelligent Labor Coin CLI",
                "ok": True,
                "quick_start": [
                    "ilc identity init   # initialize local agent identity",
                    "ilc doctor          # check configuration health",
                    "ilc sidecar list    # list installed sidecars",
                    "ilc ccss status     # check CCSS inbox",
                    "ilc version         # show version",
                ],
            }
        )
        return 0

    command = str(args.command)

    if command == "skills" and getattr(args, "sidecar_subcommand", "") == "install":
        _write_json_payload(
            {
                "error": "sidecar_install_requires_clawhub_post_fix2g",
                "note": "ClawHub-backed sidecar install is planned for Phase 1575b-Fix2g after public RC.",
                "ok": False,
            },
            stderr=True,
        )
        return 1

    if args.simulate_network_error:
        code, payload = _simulate_network_error_result(command)
        _write_json_payload(payload, stderr=True)
        return code

    graph_state_path = Path(args.graph_state)

    try:
        payload = _run_top_level_command(command, args, graph_state_path)
        data = payload.get("data") or {}
        exit_code = int(data.pop("_exit_code", 0))
        if command == "doctor" and bool(getattr(args, "pretty", False)):
            print(_format_doctor_pretty(data))
            return exit_code
        # Machine-readable raw output — print bare value, no JSON wrapper.
        # Used by: ilc ccss inbox --count
        raw_val = data.get("_raw")
        if raw_val is not None:
            print(raw_val)
            return 0
        _write_json_payload(payload)
        # Surface any warnings as human-readable stderr lines so they are
        # visible to interactive users without breaking JSON stdout for scripts.
        for w in data.get("warnings", []):
            print(f"[ilc warning] {w}", file=sys.stderr)
        # Safety warning for decrypted messages flagged by the content inspector.
        # Printed to stderr so JSON stdout stays machine-readable.
        if data.get("subcommand") == "read" and not data.get("safe", True):
            flags_str = json.dumps(sorted(data.get("flags", [])))
            print(
                f"[ccss] SAFETY WARNING: message flagged safe=false flags={flags_str}",
                file=sys.stderr,
            )
        # ilc ccss status exits 1 when messages are waiting (shell-condition friendly).
        if data.get("subcommand") == "status" and data.get("has_messages"):
            return 1
        return exit_code
    except QueryCommandError as exc:
        code, payload = _query_error_result(args, exc)
    except VerifyCommandError as exc:
        code, payload = _verify_error_result(args, exc)
    except BundleCommandError as exc:
        code, payload = _bundle_error_result(args, exc)
    except ValueError as exc:
        code, payload = _value_error_result(command, exc)

    _write_json_payload(payload, stderr=True)
    return code


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    raise SystemExit(main())
