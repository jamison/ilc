# SPDX-License-Identifier: AGPL-3.0-only
"""First-run AgentID provisioning for public-RC onboarding.

This module creates the local identity store used by ``ilc install
--from-invite`` and, after GAP-AGENT-ONBOARDING-00d, can bind the generated
AgentID key to the invite redemption transcript with a BLS proof-of-possession.
"""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import json
import os
import re
import secrets  # OS CSPRNG; no private graph entropy.
import shlex
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

from ilc_core import __version__ as ILC_CORE_VERSION
from ilc_core.crypto.pq_signature_verify import (
    _MLDSA_PK_HEX_LENGTH,
    verify_mldsa65_signature,
)
from ilc_core.identity.bls_backend import (
    keypair_from_ikm_hex,
    sign_invitee_install_receipt_digest,
    sign_invite_pop_digest,
    verify_invitee_install_receipt_digest,
    verify_invite_pop_digest,
)
from ilc_core.validator.validator_key_derivation import (
    build_validator_key_derivation_record,
    derive_validator_key_ikm,
)

FIRST_RUN_PROVISIONING_VERSION = "gap_agent_onboarding_00c.v0.1"
INSTALL_CONNECTIVITY_RECEIPT_VERSION = (
    "install_connectivity_receipt_GAP_INSTALL_CONNECTIVITY_RECEIPT_00.v0.1"
)
INSTALL_CONNECTIVITY_NAT_PROBE_SCHEMA_VERSION = (
    "nat_probe_engine_GAP_AUTO_NAT_TRAVERSAL_IMPL_00.v0.1"
)
INVITE_BOOTSTRAP_CAPSULE_SCHEMA_VERSION = (
    "invite_bootstrap_capsule_GAP_INVITE_BOOTSTRAP_CAPSULE_IMPL_00.v0.1"
)
BOOTSTRAP_PEER_HINTS_SCHEMA_VERSION = "bootstrap_peer_hints.v0.1"
BOOTSTRAP_FETCH_PEERS_SCHEMA_VERSION = (
    "distributed_release_fetch_GAP_DISTRIBUTED_RELEASE_FETCH_00.v0.1"
)
INVITEE_INSTALL_RECEIPT_SCHEMA_VERSION = "invitee_install_receipt.v0.1"
INVITEE_INSTALL_RECEIPT_SIGNATURE_DOMAIN = "ILC_INVITEE_INSTALL_RECEIPT_V1"
MAX_KNOWN_PEER_HINTS = 8
MIN_KNOWN_PEERS = 3
MAX_BOOTSTRAP_FETCH_PEERS = 16
POP_DOMAIN = "ilc-invite-pop-v1"
KEY_STORE_PROFILE_FILE_0600 = "file_0600_unencrypted"
ONBOARDING_SOFTWARE_VERSION = ILC_CORE_VERSION
GENESIS_ROOT_ENVELOPE_HASH = (
    "sha256:ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c"
)
ONBOARDING_BLS_KEYGEN_COMMAND_ENV = "ILC_ONBOARDING_BLS_KEYGEN_COMMAND"
ONBOARDING_BLS_POP_COMMAND_ENV = "ILC_ONBOARDING_BLS_POP_COMMAND"
BOOTSTRAP_FETCH_TRUSTED_GENESIS_PUBKEY_ENV = (
    "ILC_BOOTSTRAP_FETCH_TRUSTED_GENESIS_AUTHORITY_PUBKEY_HEX"
)

_AGENT_ID_RE = re.compile(r"^[0-9a-f]{96}$")
_PRIVATE_KEY_RE = re.compile(rb"^[0-9a-f]{64}\n?$")
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_SHA384_RE = re.compile(r"^[0-9a-f]{96}$")
_BLS_SIGNATURE_RE = re.compile(r"^[0-9a-f]{192}$")
_LOWER_HEX_RE = re.compile(r"^[0-9a-f]+$")


class IdentityAlreadyExistsError(ValueError):
    """Raised when provisioning would overwrite an existing local identity."""


def identity_root(install_dir: Path | str) -> Path:
    """Return the identity directory rooted under ``install_dir/.ilc``."""

    return Path(install_dir).expanduser().resolve() / ".ilc" / "identity"


def provision_new_identity(
    install_dir: Path,
    *,
    invite_id: str | None = None,
    epoch: int = 0,
    force_reprovision: bool = False,
    keygen_command: list[str] | None = None,
    emit_warning: bool = True,
) -> dict[str, str]:
    """Create a new local BLS-backed AgentID identity store.

    Returns only public-safe metadata. The 32-byte identity seed is never
    written to disk or returned. The derived BLS signing key is written to
    the local key file via same-directory temp file and ``os.replace``.
    """

    if isinstance(epoch, bool) or not isinstance(epoch, int) or epoch < 0:
        raise ValueError("onboarding_epoch_invalid")

    root = identity_root(install_dir)
    signing_key_path = root / "signing_key.hex"
    if signing_key_path.exists() and not force_reprovision:
        raise IdentityAlreadyExistsError("identity_signing_key_already_exists")

    root.mkdir(parents=True, exist_ok=True)
    os.chmod(root.parent, 0o700)
    os.chmod(root, 0o700)

    identity_seed_buf = bytearray(secrets.token_bytes(32))  # OS CSPRNG
    validator_ikm_buf: bytearray | None = None
    try:
        identity_seed = bytes(identity_seed_buf)
        derivation_record = build_validator_key_derivation_record(identity_seed)
        # Python cannot zero immutable hex strings after subprocess handoff; keep
        # the IKM lifetime bounded to this function and zero bytearray copies.
        validator_ikm = derive_validator_key_ikm(identity_seed)
        validator_ikm_buf = bytearray(validator_ikm)
        agent_id = _write_private_key_from_ikm(
            root,
            validator_ikm.hex(),
            signing_key_path,
            keygen_command=keygen_command,
        )
    finally:
        _zero_bytearray(identity_seed_buf)
        if validator_ikm_buf is not None:
            _zero_bytearray(validator_ikm_buf)

    if force_reprovision:
        _remove_stale_identity_metadata(root)

    _atomic_write_text(root / "agent_id", f"{agent_id}\n", mode=0o644)
    recovery_policy = _build_recovery_policy()
    birth_attestation = _build_birth_attestation(
        agent_id,
        identity_seed_commitment=derivation_record["identity_seed_commitment"],
    )
    _atomic_write_json(root / "recovery_policy.json", recovery_policy, mode=0o644)
    _atomic_write_json(root / "birth_attestation.json", birth_attestation, mode=0o644)

    receipt = _build_onboarding_receipt(
        agent_id,
        invite_id=invite_id,
        epoch=epoch,
        birth_attestation=birth_attestation,
        recovery_policy=recovery_policy,
    )
    _atomic_write_json(root / "onboarding_receipt.json", receipt, mode=0o644)

    if emit_warning:
        print(
            "key_store_profile=file_0600_unencrypted: signing key is in plaintext. "
            "Upgrade key store post-RC for production use.",
            file=sys.stderr,
        )

    return {
        "agent_id": agent_id,
        "identity_dir": str(root),
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "status": "provisioned",
    }


def existing_identity_summary(install_dir: Path | str) -> dict[str, str]:
    """Return public-safe metadata for an already-provisioned identity."""

    root = identity_root(install_dir)
    agent_id = _read_agent_id(root / "agent_id")
    return {
        "agent_id": agent_id,
        "identity_dir": str(root),
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "status": "existing_identity_reused",
    }


def record_install_connectivity_receipt(
    install_dir: Path | str,
    *,
    agent_id: str,
    epoch: int,
    attempt_router_mapping: bool = False,
    observers: tuple[str, ...] = (),
    relay_server_url: str | None = None,
    relay_admission_material: Mapping[str, Any] | None = None,
    internal_port: int = 50151,
) -> dict[str, Any]:
    """Probe local reachability and attach a connectivity receipt to onboarding state.

    Probe failures are deliberately non-fatal: installation should still finish
    with a local receipt that makes the reduced claim explicit.
    """

    _require_agent_id(agent_id)
    _require_epoch(epoch, "connectivity_probe_epoch_invalid")
    if not isinstance(attempt_router_mapping, bool):
        raise ValueError("connectivity_probe_attempt_router_mapping_invalid")

    root = identity_root(install_dir)
    if not root.exists():
        raise ValueError("connectivity_receipt_identity_root_missing")

    try:
        from ilc_core.network.nat_probe import NatProbeEngine

        report = NatProbeEngine(
            observers=tuple(observers),
            relay_server_url=relay_server_url,
            relay_admission_material=relay_admission_material,
            agent_id=agent_id,
            internal_port=internal_port,
        ).run_probe(
            attempt_router_mapping=attempt_router_mapping,
            probe_epoch=epoch,
        )
        report_payload = report.to_dict()
        connectivity_receipt = _require_connectivity_report_payload(report_payload)
        firewall_mutation_attempted = report_payload.get(
            "firewall_mutation_attempted",
            False,
        )
        if not isinstance(firewall_mutation_attempted, bool):
            raise ValueError("connectivity_probe_report_firewall_mutation_invalid")
    except Exception as exc:
        report_payload = _fallback_connectivity_report_payload(
            agent_id=agent_id,
            epoch=epoch,
            attempt_router_mapping=attempt_router_mapping,
            error_type=type(exc).__name__,
        )
        connectivity_receipt = _require_connectivity_report_payload(report_payload)
        firewall_mutation_attempted = False

    connectivity_evidence_status = report_payload.get(
        "connectivity_evidence_status",
        "probe_succeeded",
    )
    if not isinstance(connectivity_evidence_status, str) or not connectivity_evidence_status:
        raise ValueError("connectivity_probe_report_evidence_status_invalid")
    firewall_mutation_status = report_payload.get("firewall_mutation_status")
    if firewall_mutation_status is None:
        firewall_mutation_status = (
            "confirmed_mutated"
            if firewall_mutation_attempted
            else "confirmed_not_mutated"
        )
    if not isinstance(firewall_mutation_status, str) or not firewall_mutation_status:
        raise ValueError("connectivity_probe_report_firewall_mutation_status_invalid")

    connectivity_receipt_path = root / "connectivity_receipt.json"
    payload = {
        "agent_id": agent_id,
        "attempt_router_mapping": attempt_router_mapping,
        "connectivity_evidence_status": connectivity_evidence_status,
        "connectivity_mode": connectivity_receipt["mode"],
        "connectivity_receipt_path": str(connectivity_receipt_path),
        "connectivity_summary": _format_connectivity_summary(connectivity_receipt),
        "firewall_mutation_attempted": firewall_mutation_attempted,
        "firewall_mutation_status": firewall_mutation_status,
        "nat_probe_report": report_payload,
        "observed_endpoint": connectivity_receipt.get("observed_endpoint"),
        "probe_epoch": epoch,
        "relay_endpoint": connectivity_receipt.get("relay_endpoint"),
        "schema_version": INSTALL_CONNECTIVITY_RECEIPT_VERSION,
    }
    receipt_sha384 = _canonical_sha384(payload)
    payload["connectivity_receipt_sha384"] = receipt_sha384
    _atomic_write_json(connectivity_receipt_path, payload, mode=0o644)

    onboarding_receipt_path = root / "onboarding_receipt.json"
    onboarding_receipt = _read_json_object(
        onboarding_receipt_path,
        "onboarding_receipt_invalid",
    )
    if onboarding_receipt.get("agent_id") != agent_id:
        raise ValueError("onboarding_receipt_agent_id_mismatch")
    onboarding_receipt.update(
        {
            "connectivity_evidence_status": payload["connectivity_evidence_status"],
            "connectivity_mode": payload["connectivity_mode"],
            "connectivity_receipt_path": payload["connectivity_receipt_path"],
            "connectivity_receipt_sha384": receipt_sha384,
            "connectivity_summary": payload["connectivity_summary"],
            "firewall_mutation_attempted": payload["firewall_mutation_attempted"],
            "firewall_mutation_status": payload["firewall_mutation_status"],
            "observed_endpoint": payload["observed_endpoint"],
            "relay_endpoint": payload["relay_endpoint"],
        }
    )
    _atomic_write_json(onboarding_receipt_path, onboarding_receipt, mode=0o644)
    return {
        "connectivity_receipt": payload,
        "onboarding_receipt": onboarding_receipt,
    }


def validate_invite_bootstrap_capsule_fields(
    invite_bundle: Mapping[str, Any],
    *,
    current_epoch: int,
) -> dict[str, Any]:
    """Validate optional invite bootstrap capsule fields without local side effects."""

    if not isinstance(invite_bundle, Mapping):
        raise ValueError("invite_bootstrap_capsule_bundle_invalid")
    _require_epoch(current_epoch, "invite_bootstrap_current_epoch_invalid")

    genesis_state_root = invite_bundle.get("genesis_state_root")
    genesis_state_root_status = "absent_using_package_root"
    if genesis_state_root is not None:
        if not isinstance(genesis_state_root, str) or not genesis_state_root:
            raise ValueError("invite_bootstrap_genesis_state_root_invalid")
        if genesis_state_root != GENESIS_ROOT_ENVELOPE_HASH:
            raise ValueError("invite_bootstrap_genesis_state_root_mismatch")
        genesis_state_root_status = "matched_package_root"

    inviter_connectivity_mode = invite_bundle.get("inviter_connectivity_mode")
    if inviter_connectivity_mode is not None:
        if not isinstance(inviter_connectivity_mode, str):
            raise ValueError("invite_bootstrap_inviter_connectivity_mode_invalid")
        try:
            from ilc_core.network.connectivity_mode import ConnectivityMode

            inviter_connectivity_mode = ConnectivityMode(inviter_connectivity_mode).value
        except Exception as exc:
            raise ValueError("invite_bootstrap_inviter_connectivity_mode_invalid") from exc

    peer_hints = invite_bundle.get("known_peer_hints", [])
    if peer_hints is None:
        peer_hints = []
    if not isinstance(peer_hints, list):
        raise ValueError("invite_bootstrap_known_peer_hints_invalid")
    if len(peer_hints) > MAX_KNOWN_PEER_HINTS:
        raise ValueError("invite_bootstrap_known_peer_hints_too_many")

    key_bindings = invite_bundle.get("known_peer_hint_key_bindings", {})
    if key_bindings is None:
        key_bindings = {}
    if not isinstance(key_bindings, Mapping):
        raise ValueError("invite_bootstrap_known_peer_hint_key_bindings_invalid")
    normalized_key_bindings = {
        _require_key_binding_ref(key): _require_mldsa_pubkey_hex(value)
        for key, value in key_bindings.items()
    }

    from ilc_core.network.d2d.peer_advertisement import PeerAdvertisement

    verified_hints: list[dict[str, Any]] = []
    verified_bindings: dict[str, str] = {}
    seen: set[tuple[str, str]] = set()
    dropped_invalid = 0
    dropped_expired = 0
    dropped_unverifiable = 0
    for raw_hint in peer_hints:
        try:
            ad = PeerAdvertisement.from_dict(raw_hint)
        except Exception:
            dropped_invalid += 1
            continue
        if ad.is_expired(current_epoch) or ad.peer_timestamp_epoch > current_epoch + 1:
            dropped_expired += 1
            continue
        pubkey_hex = normalized_key_bindings.get(ad.key_binding_ref)
        if pubkey_hex is None or not ad.verify(
            verify_mldsa65_signature,
            pubkey_hex=pubkey_hex,
        ):
            dropped_unverifiable += 1
            continue
        dedupe_key = (ad.agent_id, ad.endpoint_url)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        verified_hints.append(ad.to_dict())
        verified_bindings[ad.key_binding_ref] = pubkey_hex

    return {
        "bootstrap_capsule_schema_version": INVITE_BOOTSTRAP_CAPSULE_SCHEMA_VERSION,
        "genesis_state_root": genesis_state_root or GENESIS_ROOT_ENVELOPE_HASH,
        "genesis_state_root_status": genesis_state_root_status,
        "inviter_connectivity_mode": inviter_connectivity_mode,
        "known_peer_hints_dropped_expired": dropped_expired,
        "known_peer_hints_dropped_invalid": dropped_invalid,
        "known_peer_hints_dropped_unverifiable": dropped_unverifiable,
        "known_peer_hints_offered": len(peer_hints),
        "known_peer_hints_verified": len(verified_hints),
        "verified_peer_hint_key_bindings": verified_bindings,
        "verified_peer_hints": verified_hints,
    }


def record_invite_bootstrap_capsule_evidence(
    install_dir: Path | str,
    *,
    agent_id: str,
    current_epoch: int,
    capsule_evidence: Mapping[str, Any],
    distributed_fetch_evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Persist verified invite capsule evidence and update onboarding receipt."""

    _require_agent_id(agent_id)
    _require_epoch(current_epoch, "invite_bootstrap_current_epoch_invalid")
    if not isinstance(capsule_evidence, Mapping):
        raise ValueError("invite_bootstrap_capsule_evidence_invalid")
    root = identity_root(install_dir)
    onboarding_receipt_path = root / "onboarding_receipt.json"
    onboarding_receipt = _read_json_object(
        onboarding_receipt_path,
        "onboarding_receipt_invalid",
    )
    if onboarding_receipt.get("agent_id") != agent_id:
        raise ValueError("onboarding_receipt_agent_id_mismatch")

    verified_hints = _require_peer_hint_list(capsule_evidence.get("verified_peer_hints", []))
    verified_bindings = _require_peer_hint_key_bindings(
        capsule_evidence.get("verified_peer_hint_key_bindings", {})
    )
    fetch_evidence = _normalize_distributed_fetch_evidence(distributed_fetch_evidence)
    pending_path = root / "invite_bootstrap_capsule_evidence.pending.json"
    _atomic_write_json(
        pending_path,
        {
            "agent_id": agent_id,
            "current_epoch": current_epoch,
            "schema_version": "invite_bootstrap_capsule_evidence_pending.v0.1",
        },
        mode=0o644,
    )
    hints_path = root / "bootstrap_peer_hints.json"
    hints_payload: dict[str, Any] | None = None
    hints_sha384: str | None = None
    if verified_hints:
        hints_payload = {
            "current_epoch": current_epoch,
            "known_peer_hint_key_bindings": verified_bindings,
            "known_peer_hints": verified_hints,
            "schema_version": BOOTSTRAP_PEER_HINTS_SCHEMA_VERSION,
        }
        hints_sha384 = _canonical_sha384(hints_payload)
        hints_payload["bootstrap_peer_hints_sha384"] = hints_sha384
        _atomic_write_json(hints_path, hints_payload, mode=0o644)

    fetch_payload: dict[str, Any] | None = None
    fetch_sha384: str | None = None
    fetch_peers_path = root / "bootstrap_fetch_peers.json"
    if fetch_evidence["bootstrap_fetch_status"] == "fetched":
        fetch_payload = {
            "bootstrap_fetch_bundle_cid": fetch_evidence["bootstrap_fetch_bundle_cid"],
            "genesis_authority_pubkey_hex": fetch_evidence[
                "bootstrap_fetch_genesis_authority_pubkey_hex"
            ],
            "peer_count": fetch_evidence["bootstrap_fetch_peers_count"],
            "peer_endpoints": fetch_evidence["bootstrap_fetch_peer_endpoints"],
            "schema_version": BOOTSTRAP_FETCH_PEERS_SCHEMA_VERSION,
            "seed_peer_endpoint": fetch_evidence["bootstrap_fetch_seed_peer_endpoint"],
            "verified_bootstrap_bundle": fetch_evidence["verified_bootstrap_bundle"],
        }
        fetch_sha384 = _canonical_sha384(fetch_payload)
        fetch_payload["bootstrap_fetch_peers_sha384"] = fetch_sha384
        _atomic_write_json(fetch_peers_path, fetch_payload, mode=0o644)

    evidence_fields = {
        "bootstrap_peer_hints_count": len(verified_hints),
        "bootstrap_peer_hints_path": str(hints_path) if verified_hints else None,
        "bootstrap_peer_hints_sha384": hints_sha384,
        "bootstrap_peer_hints_written": bool(verified_hints),
        "bootstrap_fetch_bundle_cid": fetch_evidence["bootstrap_fetch_bundle_cid"],
        "bootstrap_fetch_genesis_authority_pubkey_hex": fetch_evidence[
            "bootstrap_fetch_genesis_authority_pubkey_hex"
        ],
        "bootstrap_fetch_peer_endpoints": fetch_evidence["bootstrap_fetch_peer_endpoints"],
        "bootstrap_fetch_peers_count": fetch_evidence["bootstrap_fetch_peers_count"],
        "bootstrap_fetch_peers_path": str(fetch_peers_path) if fetch_payload else None,
        "bootstrap_fetch_peers_sha384": fetch_sha384,
        "bootstrap_fetch_peers_written": bool(fetch_payload),
        "bootstrap_fetch_seed_peer_endpoint": fetch_evidence[
            "bootstrap_fetch_seed_peer_endpoint"
        ],
        "bootstrap_fetch_status": fetch_evidence["bootstrap_fetch_status"],
        "genesis_state_root": _require_non_empty_string(
            capsule_evidence.get("genesis_state_root"),
            "invite_bootstrap_genesis_state_root_invalid",
        ),
        "genesis_state_root_status": _require_non_empty_string(
            capsule_evidence.get("genesis_state_root_status"),
            "invite_bootstrap_genesis_state_root_status_invalid",
        ),
        "inviter_connectivity_mode": capsule_evidence.get("inviter_connectivity_mode"),
        "known_peer_hints_dropped_expired": _require_count(
            capsule_evidence.get("known_peer_hints_dropped_expired"),
            "invite_bootstrap_known_peer_hints_dropped_expired_invalid",
        ),
        "known_peer_hints_dropped_invalid": _require_count(
            capsule_evidence.get("known_peer_hints_dropped_invalid"),
            "invite_bootstrap_known_peer_hints_dropped_invalid_invalid",
        ),
        "known_peer_hints_dropped_unverifiable": _require_count(
            capsule_evidence.get("known_peer_hints_dropped_unverifiable"),
            "invite_bootstrap_known_peer_hints_dropped_unverifiable_invalid",
        ),
        "known_peer_hints_offered": _require_count(
            capsule_evidence.get("known_peer_hints_offered"),
            "invite_bootstrap_known_peer_hints_offered_invalid",
        ),
        "known_peer_hints_verified": len(verified_hints),
        "invite_bootstrap_capsule_schema_version": INVITE_BOOTSTRAP_CAPSULE_SCHEMA_VERSION,
    }
    onboarding_receipt.update(evidence_fields)
    _atomic_write_json(onboarding_receipt_path, onboarding_receipt, mode=0o644)
    try:
        pending_path.unlink()
    except FileNotFoundError:
        pass
    return {
        "bootstrap_fetch_peers": fetch_payload,
        "bootstrap_peer_hints": hints_payload,
        "invite_bootstrap_capsule_evidence": evidence_fields,
        "onboarding_receipt": onboarding_receipt,
    }


def fetch_distributed_release_peers(
    invite_bundle: Mapping[str, Any],
    capsule_evidence: Mapping[str, Any],
    *,
    trusted_genesis_authority_pubkey_hex: str | None = None,
) -> dict[str, Any]:
    """Fetch signed bootstrap peers when invite-carried hints are insufficient."""

    if not isinstance(invite_bundle, Mapping):
        raise ValueError("bootstrap_fetch_invite_bundle_invalid")
    if not isinstance(capsule_evidence, Mapping):
        raise ValueError("bootstrap_fetch_capsule_evidence_invalid")
    known_peer_count = _require_count(
        capsule_evidence.get("known_peer_hints_verified"),
        "bootstrap_fetch_known_peer_count_invalid",
    )
    if known_peer_count >= MIN_KNOWN_PEERS:
        return _distributed_fetch_skipped("skipped_known_peers_sufficient")

    material = _bootstrap_fetch_material(invite_bundle)
    if material is None:
        return _distributed_fetch_skipped("skipped_not_configured")
    seed_peer_endpoint, bundle_cid, genesis_authority_pubkey_hex = material
    trusted_pubkey_hex = _trusted_bootstrap_fetch_genesis_pubkey_hex(
        trusted_genesis_authority_pubkey_hex
    )
    if trusted_pubkey_hex != genesis_authority_pubkey_hex:
        raise ValueError("bootstrap_fetch_trust_root_mismatch")

    from ilc_core.network.d2d.bootstrap_fetch_runtime import (
        BootstrapBundleError,
        FetchTransportError,
        extract_peer_endpoints,
        fetch_bootstrap_bundle,
        verify_bootstrap_bundle_signature,
    )

    try:
        bundle = fetch_bootstrap_bundle(seed_peer_endpoint, bundle_cid)
    except (BootstrapBundleError, FetchTransportError) as exc:
        raise ValueError("bootstrap_fetch_bundle_fetch_failed") from exc
    if bundle is None:
        raise ValueError("bootstrap_fetch_bundle_not_found")
    _reject_float(bundle, "bootstrap_fetch_bundle_float_not_allowed")
    if not verify_bootstrap_bundle_signature(bundle, genesis_authority_pubkey_hex):
        raise ValueError("bootstrap_fetch_bundle_signature_invalid")
    peer_endpoints = extract_peer_endpoints(bundle)
    if not peer_endpoints:
        raise ValueError("bootstrap_fetch_no_valid_peers")
    if len(peer_endpoints) > MAX_BOOTSTRAP_FETCH_PEERS:
        raise ValueError("bootstrap_fetch_peer_endpoints_too_many")
    return {
        "bootstrap_fetch_bundle_cid": bundle_cid,
        "bootstrap_fetch_genesis_authority_pubkey_hex": genesis_authority_pubkey_hex,
        "bootstrap_fetch_peer_endpoints": peer_endpoints,
        "bootstrap_fetch_peers_count": len(peer_endpoints),
        "bootstrap_fetch_seed_peer_endpoint": seed_peer_endpoint,
        "bootstrap_fetch_status": "fetched",
        "verified_bootstrap_bundle": dict(bundle),
    }


def write_invitee_install_receipt(
    install_dir: Path | str,
    *,
    agent_id: str,
    invite_id: str,
    invite_nullifier: str,
    install_epoch: int,
    genesis_state_root: str,
    connectivity_receipt: Mapping[str, Any],
    onboarding_receipt: Mapping[str, Any],
    installed_release_artifact_id: str | None = None,
    installed_release_canonical_hash: str | None = None,
) -> dict[str, Any]:
    """Write the invitee-signed bilateral install receipt."""

    _require_agent_id(agent_id)
    _require_non_empty_string(invite_id, "invitee_install_receipt_invite_id_invalid")
    _require_sha256_hex(invite_nullifier, "invitee_install_receipt_nullifier_invalid")
    _require_epoch(install_epoch, "invitee_install_receipt_epoch_invalid")
    if genesis_state_root != GENESIS_ROOT_ENVELOPE_HASH:
        raise ValueError("invitee_install_receipt_genesis_state_root_mismatch")
    if not isinstance(connectivity_receipt, Mapping) or not isinstance(onboarding_receipt, Mapping):
        raise ValueError("invitee_install_receipt_source_receipts_invalid")
    if onboarding_receipt.get("agent_id") != agent_id:
        raise ValueError("invitee_install_receipt_agent_id_mismatch")
    if installed_release_artifact_id is not None:
        installed_release_artifact_id = _require_non_empty_string(
            installed_release_artifact_id,
            "invitee_install_receipt_artifact_id_invalid",
        )
    if installed_release_canonical_hash is not None:
        installed_release_canonical_hash = _require_non_empty_string(
            installed_release_canonical_hash,
            "invitee_install_receipt_canonical_hash_invalid",
        )

    root = identity_root(install_dir)
    signing_key_path = root / "signing_key.hex"
    try:
        secret_key_hex = signing_key_path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError("onboarding_bls_private_key_unreadable") from exc
    body = {
        "agent_id": agent_id,
        "connectivity_mode": _require_non_empty_string(
            connectivity_receipt.get("connectivity_mode"),
            "invitee_install_receipt_connectivity_mode_invalid",
        ),
        "connectivity_receipt_sha384": _require_sha384_hex(
            connectivity_receipt.get("connectivity_receipt_sha384"),
            "invitee_install_receipt_connectivity_sha384_invalid",
        ),
        "genesis_state_root": genesis_state_root,
        "install_epoch": install_epoch,
        "installed_release_artifact_id": installed_release_artifact_id,
        "installed_release_canonical_hash": installed_release_canonical_hash,
        "invite_id": invite_id,
        "invite_nullifier": invite_nullifier,
        "onboarding_receipt_sha384": _canonical_sha384(dict(onboarding_receipt)),
        "schema_version": INVITEE_INSTALL_RECEIPT_SCHEMA_VERSION,
        "signature_domain": INVITEE_INSTALL_RECEIPT_SIGNATURE_DOMAIN,
        "software_version": ONBOARDING_SOFTWARE_VERSION,
    }
    digest_hex = hashlib.sha384(_canonical_json_bytes(body)).hexdigest()
    signature_hex = _require_bls_signature_hex(
        sign_invitee_install_receipt_digest(secret_key_hex, digest_hex),
        "invitee_install_receipt_signature_invalid",
    )
    if not verify_invitee_install_receipt_digest(
        public_key_hex=agent_id,
        digest_hex=digest_hex,
        signature_hex=signature_hex,
    ):
        raise ValueError("invitee_install_receipt_signature_self_verify_failed")
    receipt = {
        **body,
        "created_at_unix": int(time.time()),
        "signature": signature_hex,
        "signature_payload_ref": digest_hex,
    }
    _atomic_write_json(root / "invitee_install_receipt.json", receipt, mode=0o644)
    return receipt


def migrate_identity_schema_if_needed(install_dir: Path | str) -> dict[str, Any]:
    """Apply the 00b D5 update migration contract to an existing identity dir."""

    root = identity_root(install_dir)
    if not root.exists():
        return {"migration_status": "not_needed_identity_dir_absent"}

    agent_id = _read_agent_id(root / "agent_id")
    recovery_path = root / "recovery_policy.json"
    if not recovery_path.is_file():
        raise ValueError("identity_migration_recovery_policy_missing")

    birth_path = root / "birth_attestation.json"
    if not birth_path.is_file():
        raise ValueError("identity_migration_birth_attestation_missing")

    birth = _read_json_object(birth_path, "identity_migration_birth_attestation_invalid")
    if birth.get("agent_id") != agent_id:
        raise ValueError("identity_migration_agent_id_mismatch")

    changed = False
    if birth.get("key_store_profile") is None:
        birth["key_store_profile"] = KEY_STORE_PROFILE_FILE_0600
        _atomic_write_json(birth_path, birth, mode=0o644)
        changed = True

    receipt = {
        "agent_id": agent_id,
        "migration_changed": changed,
        "migration_status": "updated" if changed else "not_needed",
        "migration_version": "gap_agent_onboarding_00c_update_migration.v0.1",
    }
    _atomic_write_json(root / "migration_receipt.json", receipt, mode=0o644)
    return receipt


def build_invite_pop_transcript(
    *,
    agent_id_hex: str,
    invite_nullifier: str,
    invite_id: str,
    epoch: int,
) -> bytes:
    """Return canonical JSON bytes for an invite redemption PoP transcript."""

    _require_agent_id(agent_id_hex)
    _require_sha256_hex(invite_nullifier, "invite_pop_nullifier_invalid")
    _require_non_empty_string(invite_id, "invite_pop_invite_id_invalid")
    _require_epoch(epoch, "invite_pop_epoch_invalid")
    return _canonical_json_bytes(
        {
            "agent_id_hex": agent_id_hex,
            "domain": POP_DOMAIN,
            "epoch": epoch,
            "invite_id": invite_id,
            "invite_nullifier": invite_nullifier,
        }
    )


def invite_pop_payload_ref(
    *,
    agent_id_hex: str,
    invite_nullifier: str,
    invite_id: str,
    epoch: int,
) -> str:
    transcript = build_invite_pop_transcript(
        agent_id_hex=agent_id_hex,
        invite_nullifier=invite_nullifier,
        invite_id=invite_id,
        epoch=epoch,
    )
    return hashlib.sha384(transcript).hexdigest()


def generate_invite_pop(
    agent_id_hex: str,
    invite_nullifier: str,
    signing_key_path: Path,
    *,
    invite_id: str,
    epoch: int,
    pop_command: list[str] | None = None,
) -> str:
    """Sign the SHA-384 invite transcript digest with the AgentID BLS key."""

    digest_hex = invite_pop_payload_ref(
        agent_id_hex=agent_id_hex,
        invite_nullifier=invite_nullifier,
        invite_id=invite_id,
        epoch=epoch,
    )
    signature_hex = _run_invite_pop_command(
        ["sign", "--secret-key", str(signing_key_path)],
        digest_hex,
        pop_command=pop_command,
        failure_token="invite_pop_signing_failed",
    )
    return _require_bls_signature_hex(signature_hex, "invite_pop_signature_invalid")


def verify_invite_pop(
    *,
    agent_id_hex: str,
    invite_nullifier: str,
    invite_id: str,
    epoch: int,
    invite_pop: str,
    pop_command: list[str] | None = None,
) -> bool:
    """Verify an invite PoP signature against its AgentID public key."""

    digest_hex = invite_pop_payload_ref(
        agent_id_hex=agent_id_hex,
        invite_nullifier=invite_nullifier,
        invite_id=invite_id,
        epoch=epoch,
    )
    signature_hex = _require_bls_signature_hex(invite_pop, "invite_pop_signature_invalid")
    try:
        _run_invite_pop_command(
            [
                "verify",
                "--public-key-hex",
                agent_id_hex,
                "--signature-hex",
                signature_hex,
            ],
            digest_hex,
            pop_command=pop_command,
            failure_token="invite_pop_verification_failed",
        )
    except ValueError:
        return False
    return True


def attach_invite_pop_to_onboarding_receipt(
    install_dir: Path | str,
    *,
    invite_id: str,
    invite_nullifier: str,
    epoch: int,
    nullifier_persisted: bool,
    nullifier_registry: str,
    pop_command: list[str] | None = None,
) -> dict[str, Any]:
    """Attach public invite PoP fields to the local onboarding receipt."""

    root = identity_root(install_dir)
    agent_id = _read_agent_id(root / "agent_id")
    invite_pop = generate_invite_pop(
        agent_id,
        invite_nullifier,
        root / "signing_key.hex",
        invite_id=invite_id,
        epoch=epoch,
        pop_command=pop_command,
    )
    receipt_path = root / "onboarding_receipt.json"
    receipt = _read_json_object(receipt_path, "onboarding_receipt_invalid")
    if receipt.get("agent_id") != agent_id:
        raise ValueError("onboarding_receipt_agent_id_mismatch")
    existing_invite_id = receipt.get("invite_id")
    existing_nullifier = receipt.get("invite_nullifier")
    if existing_invite_id not in (None, "not_recorded", invite_id):
        raise ValueError("onboarding_receipt_invite_binding_mismatch")
    if existing_nullifier not in (None, "not_yet_bound_00d", invite_nullifier):
        raise ValueError("onboarding_receipt_invite_binding_mismatch")
    receipt.update(
        {
            "invite_id": invite_id,
            "invite_nullifier": invite_nullifier,
            "invite_pop": invite_pop,
            "invite_pop_domain": POP_DOMAIN,
            "invite_pop_payload_ref": invite_pop_payload_ref(
                agent_id_hex=agent_id,
                invite_nullifier=invite_nullifier,
                invite_id=invite_id,
                epoch=epoch,
            ),
            "nullifier_persisted": bool(nullifier_persisted),
            "nullifier_registry": nullifier_registry,
            "nullifier_status": "recorded" if nullifier_persisted else "not_persisted",
        }
    )
    _atomic_write_json(receipt_path, receipt, mode=0o644)
    return receipt


def _build_birth_attestation(
    agent_id: str,
    *,
    identity_seed_commitment: str,
) -> dict[str, str]:
    _require_agent_id(agent_id)
    return {
        "agent_id": agent_id,
        "agent_id_derivation_ref": "cdl-017-bls-g1-pubkey",
        "attestation_signature_ref": "not_yet_implemented_cdl_090_pending",
        "attestation_version": "ilc-birth-attestation-v1",
        "ceremony_mode": "agent_mode",
        "custody_statement": "non_custodial_default_adr_0038",
        "entropy_source_statement": "getrandom_os_csprng_no_private_graph_content",
        "genesis_lineage_anchor": GENESIS_ROOT_ENVELOPE_HASH,
        "identity_seed_commitment_ref": identity_seed_commitment,
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "lineage_proof_ref": "adr-0037",
        "recovery_policy_ref": "~/.ilc/identity/recovery_policy.json",
        "seed_output_target_ref": "~/.ilc/identity/signing_key.hex",
    }


def _build_recovery_policy() -> dict[str, Any]:
    return {
        "cdl_authority": "cdl-002-section-0a",
        "credentials": [],
        "policy_version": "ilc-recovery-policy-v1",
        "precommitted_at_epoch": None,
        "statement": "no_recovery_path_precommitted_lost_key_equals_lost_agent_id",
        "type": "none",
    }


def _build_onboarding_receipt(
    agent_id: str,
    *,
    invite_id: str | None,
    epoch: int,
    birth_attestation: dict[str, Any],
    recovery_policy: dict[str, Any],
) -> dict[str, Any]:
    transcript = {
        "agent_id": agent_id,
        "birth_attestation_sha384": _canonical_sha384(birth_attestation),
        "recovery_policy_sha384": _canonical_sha384(recovery_policy),
        "software_version": ONBOARDING_SOFTWARE_VERSION,
    }
    return {
        "agent_id": agent_id,
        "birth_attestation_path": "~/.ilc/identity/birth_attestation.json",
        "invite_id": invite_id or "not_recorded",
        "invite_nullifier": "not_yet_bound_00d",
        "key_store_profile": KEY_STORE_PROFILE_FILE_0600,
        "key_store_warning": "signing_key_is_in_plaintext_0600_file_upgrade_key_store_post_rc",
        "onboarded_at_epoch": epoch,
        "receipt_version": "ilc-onboarding-receipt-v1",
        "recovery_policy_path": "~/.ilc/identity/recovery_policy.json",
        "restart_verification_token": hashlib.sha384(
            _canonical_json_bytes(transcript)
        ).hexdigest(),
        "software_version": ONBOARDING_SOFTWARE_VERSION,
    }


def _write_private_key_from_ikm(
    identity_dir: Path,
    ikm_hex: str,
    final_path: Path,
    *,
    keygen_command: list[str] | None,
) -> str:
    command = list(keygen_command or _configured_keygen_command() or [])
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{final_path.name}.", suffix=".tmp", dir=identity_dir
    )
    os.close(fd)
    temp_path = Path(temp_name)
    temp_path.unlink()
    try:
        if command:
            agent_id = _run_keygen_command(command, ikm_hex, temp_path)
        else:
            private_key_hex, agent_id = keypair_from_ikm_hex(ikm_hex)
            _atomic_write_text(temp_path, f"{private_key_hex}\n", mode=0o600)
        try:
            private_payload = temp_path.read_bytes()
        except OSError as exc:
            raise ValueError("onboarding_bls_private_key_unreadable") from exc
        if _PRIVATE_KEY_RE.fullmatch(private_payload) is None:
            raise ValueError("onboarding_bls_private_key_invalid")
        os.chmod(temp_path, 0o600)
        os.replace(temp_path, final_path)
        os.chmod(final_path, 0o600)
        return agent_id
    except BaseException:
        try:
            temp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _run_keygen_command(command: list[str], ikm_hex: str, temp_path: Path) -> str:
    try:
        result = subprocess.run(
            [
                *command,
                "--keypair-from-ikm-hex-stdin",
                "--out",
                str(temp_path),
            ],
            input=f"{ikm_hex}\n",
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError as exc:
        raise ValueError("onboarding_bls_keygen_unavailable") from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError("onboarding_bls_keygen_timed_out") from exc
    if result.returncode != 0:
        raise ValueError("onboarding_bls_keygen_failed")
    return _require_agent_id(result.stdout.strip())


def _configured_keygen_command() -> list[str] | None:
    env_command = os.environ.get(ONBOARDING_BLS_KEYGEN_COMMAND_ENV)
    if env_command:
        return shlex.split(env_command)
    return None


def _run_invite_pop_command(
    args: list[str],
    digest_hex: str,
    *,
    pop_command: list[str] | None,
    failure_token: str,
) -> str:
    command = list(pop_command or _configured_invite_pop_command() or [])
    if not command:
        return _run_invite_pop_python(args, digest_hex, failure_token=failure_token)
    try:
        result = subprocess.run(
            [*command, *args],
            input=f"{digest_hex}\n",
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except FileNotFoundError as exc:
        raise ValueError("invite_pop_bls_backend_unavailable") from exc
    except subprocess.TimeoutExpired as exc:
        raise ValueError("invite_pop_bls_backend_timed_out") from exc
    if result.returncode != 0:
        raise ValueError(failure_token)
    return result.stdout.strip()


def _run_invite_pop_python(
    args: list[str],
    digest_hex: str,
    *,
    failure_token: str,
) -> str:
    if not args:
        raise ValueError(failure_token)
    command = args[0]
    if command == "sign":
        parsed = _parse_exact_cli_args(args[1:], ("--secret-key",))
        key_path = parsed["--secret-key"]
        try:
            secret_key_hex = Path(key_path).read_text(encoding="utf-8").strip()
        except OSError as exc:
            raise ValueError("onboarding_bls_private_key_unreadable") from exc
        return sign_invite_pop_digest(secret_key_hex, digest_hex)
    if command == "verify":
        parsed = _parse_exact_cli_args(args[1:], ("--public-key-hex", "--signature-hex"))
        public_key_hex = parsed["--public-key-hex"]
        signature_hex = parsed["--signature-hex"]
        if verify_invite_pop_digest(
            public_key_hex=public_key_hex,
            digest_hex=digest_hex,
            signature_hex=signature_hex,
        ):
            return "invite_pop_bls_valid"
        raise ValueError(failure_token)
    raise ValueError(failure_token)


def _parse_exact_cli_args(args: list[str], names: tuple[str, ...]) -> dict[str, str]:
    if len(args) != 2 * len(names):
        raise ValueError("invite_pop_bls_args_invalid")
    parsed: dict[str, str] = {}
    for index in range(0, len(args), 2):
        name = args[index]
        value = args[index + 1]
        if name not in names or name in parsed or value.startswith("--"):
            raise ValueError("invite_pop_bls_args_invalid")
        parsed[name] = value
    if set(parsed) != set(names):
        raise ValueError("invite_pop_bls_args_invalid")
    return parsed


def _configured_invite_pop_command() -> list[str] | None:
    env_command = os.environ.get(ONBOARDING_BLS_POP_COMMAND_ENV)
    if env_command:
        return shlex.split(env_command)
    return None


def _remove_stale_identity_metadata(root: Path) -> None:
    for name in (
        "migration_receipt.json",
    ):
        try:
            (root / name).unlink()
        except FileNotFoundError:
            pass


def _fallback_connectivity_report_payload(
    *,
    agent_id: str,
    epoch: int,
    attempt_router_mapping: bool,
    error_type: str,
) -> dict[str, Any]:
    from ilc_core.network.connectivity_mode import (
        CONNECTIVITY_MODE_RUNTIME_VERSION,
        ConnectivityMode,
        ConnectivityReceipt,
        ProbeResult,
    )

    fallback_mode = "local_only"
    receipt = ConnectivityReceipt(
        mode=ConnectivityMode(fallback_mode),
        observed_endpoint=None,
        relay_endpoint=None,
        probe_observer_agent_id=None,
        probe_epoch=epoch,
    )
    return {
        "attempt_receipts": [],
        "connectivity_evidence_status": "probe_failed_connectivity_unverified",
        "connectivity_receipt": receipt.to_dict(),
        "firewall_mutation_attempted": False,
        "firewall_mutation_status": (
            "unknown_after_opt_in_probe_failure"
            if attempt_router_mapping
            else "confirmed_not_mutated"
        ),
        "nat_probe_failure": {
            "agent_id": agent_id,
            "error_type": error_type,
            "fallback_mode": fallback_mode,
            "schema_version": CONNECTIVITY_MODE_RUNTIME_VERSION,
        },
        "observer_endpoint_url": None,
        "probe_result": {
            **ProbeResult(
                has_public_ip=False,
                observed_ip=None,
                observed_port=None,
                relay_available=False,
                validator_participation_enabled=False,
                has_outbound_connectivity=False,
            ).__dict__,
        },
        "router_mapping": None,
        "schema_version": INSTALL_CONNECTIVITY_NAT_PROBE_SCHEMA_VERSION,
        "warnings": [f"connectivity_probe_failed:{error_type}"],
    }


def _require_connectivity_report_payload(report_payload: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report_payload, dict):
        raise ValueError("connectivity_probe_report_invalid")
    receipt = report_payload.get("connectivity_receipt")
    if not isinstance(receipt, dict):
        raise ValueError("connectivity_probe_report_receipt_missing")
    from ilc_core.network.connectivity_mode import ConnectivityReceipt

    try:
        validated = ConnectivityReceipt(
            mode=receipt.get("mode"),
            observed_endpoint=receipt.get("observed_endpoint"),
            relay_endpoint=receipt.get("relay_endpoint"),
            probe_observer_agent_id=receipt.get("probe_observer_agent_id"),
            probe_epoch=receipt.get("probe_epoch"),
        )
    except Exception as exc:
        raise ValueError("connectivity_probe_report_receipt_invalid") from exc
    return validated.to_dict()


def _format_connectivity_summary(connectivity_receipt: dict[str, Any]) -> str:
    mode = str(connectivity_receipt["mode"])
    relay_endpoint = connectivity_receipt.get("relay_endpoint")
    observed_endpoint = connectivity_receipt.get("observed_endpoint")
    if relay_endpoint:
        return f"Detected mode: {mode} via {relay_endpoint}"
    if observed_endpoint:
        return f"Detected mode: {mode} at {observed_endpoint}"
    return f"Detected mode: {mode}"


def _read_agent_id(path: Path) -> str:
    try:
        value = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError("identity_agent_id_unreadable") from exc
    return _require_agent_id(value)


def _require_agent_id(value: str) -> str:
    if not isinstance(value, str) or _AGENT_ID_RE.fullmatch(value) is None:
        raise ValueError("identity_agent_id_invalid")
    return value


def _require_sha256_hex(value: str, token: str) -> str:
    if not isinstance(value, str) or _SHA256_RE.fullmatch(value) is None:
        raise ValueError(token)
    return value


def _require_sha384_hex(value: Any, token: str) -> str:
    if not isinstance(value, str) or _SHA384_RE.fullmatch(value) is None:
        raise ValueError(token)
    return value


def _require_count(value: Any, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _require_key_binding_ref(value: Any) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError("invite_bootstrap_peer_key_binding_ref_invalid")
    if len(value) > 256 or any(char.isspace() for char in value):
        raise ValueError("invite_bootstrap_peer_key_binding_ref_invalid")
    return value


def _require_mldsa_pubkey_hex(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _MLDSA_PK_HEX_LENGTH
        or _LOWER_HEX_RE.fullmatch(value) is None
    ):
        raise ValueError("invite_bootstrap_peer_mldsa_pubkey_hex_invalid")
    return value


def _require_bls_signature_hex(value: str, token: str) -> str:
    if not isinstance(value, str) or _BLS_SIGNATURE_RE.fullmatch(value) is None:
        raise ValueError(token)
    return value


def _require_non_empty_string(value: str, token: str) -> str:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(token)
    return value


def _require_epoch(value: int, token: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(token)
    return value


def _bootstrap_fetch_material(invite_bundle: Mapping[str, Any]) -> tuple[str, str, str] | None:
    fields = {
        "bootstrap_fetch_bundle_cid": invite_bundle.get("bootstrap_fetch_bundle_cid"),
        "bootstrap_fetch_genesis_authority_pubkey_hex": invite_bundle.get(
            "bootstrap_fetch_genesis_authority_pubkey_hex"
        ),
        "bootstrap_fetch_seed_peer_endpoint": invite_bundle.get(
            "bootstrap_fetch_seed_peer_endpoint"
        ),
    }
    present = {key for key, value in fields.items() if value is not None}
    if not present:
        return None
    if present != set(fields):
        raise ValueError("bootstrap_fetch_material_incomplete")
    seed_peer_endpoint = _require_non_empty_string(
        fields["bootstrap_fetch_seed_peer_endpoint"],
        "bootstrap_fetch_seed_peer_endpoint_invalid",
    )
    from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint

    try:
        seed_peer_endpoint = validate_peer_endpoint(seed_peer_endpoint)
    except Exception as exc:
        raise ValueError("bootstrap_fetch_seed_peer_endpoint_invalid") from exc
    return (
        seed_peer_endpoint,
        _require_non_empty_string(
            fields["bootstrap_fetch_bundle_cid"],
            "bootstrap_fetch_bundle_cid_invalid",
        ),
        _require_genesis_authority_pubkey_hex(
            fields["bootstrap_fetch_genesis_authority_pubkey_hex"]
        ),
    )


def _trusted_bootstrap_fetch_genesis_pubkey_hex(explicit_value: str | None) -> str:
    value = explicit_value
    if value is None:
        value = os.environ.get(BOOTSTRAP_FETCH_TRUSTED_GENESIS_PUBKEY_ENV)
    if value is None:
        raise ValueError("bootstrap_fetch_trust_root_not_configured")
    try:
        return _require_genesis_authority_pubkey_hex(value)
    except ValueError as exc:
        raise ValueError("bootstrap_fetch_trust_root_invalid") from exc


def _require_genesis_authority_pubkey_hex(value: Any) -> str:
    if (
        not isinstance(value, str)
        or len(value) != _MLDSA_PK_HEX_LENGTH
        or _LOWER_HEX_RE.fullmatch(value) is None
    ):
        raise ValueError("bootstrap_fetch_genesis_authority_pubkey_hex_invalid")
    return value


def _distributed_fetch_skipped(status: str) -> dict[str, Any]:
    if status not in {"skipped_known_peers_sufficient", "skipped_not_configured"}:
        raise ValueError("bootstrap_fetch_status_invalid")
    return {
        "bootstrap_fetch_bundle_cid": None,
        "bootstrap_fetch_genesis_authority_pubkey_hex": None,
        "bootstrap_fetch_peer_endpoints": [],
        "bootstrap_fetch_peers_count": 0,
        "bootstrap_fetch_seed_peer_endpoint": None,
        "bootstrap_fetch_status": status,
        "verified_bootstrap_bundle": None,
    }


def _normalize_distributed_fetch_evidence(
    value: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if value is None:
        return _distributed_fetch_skipped("skipped_not_configured")
    if not isinstance(value, Mapping):
        raise ValueError("bootstrap_fetch_evidence_invalid")
    status = value.get("bootstrap_fetch_status")
    if status in {"skipped_known_peers_sufficient", "skipped_not_configured"}:
        return _distributed_fetch_skipped(status)
    if status != "fetched":
        raise ValueError("bootstrap_fetch_status_invalid")
    bundle = value.get("verified_bootstrap_bundle")
    if not isinstance(bundle, Mapping):
        raise ValueError("bootstrap_fetch_verified_bundle_invalid")
    bundle_dict = dict(bundle)
    _reject_float(bundle_dict, "bootstrap_fetch_bundle_float_not_allowed")
    endpoints = value.get("bootstrap_fetch_peer_endpoints")
    if not isinstance(endpoints, list) or not endpoints:
        raise ValueError("bootstrap_fetch_peer_endpoints_invalid")
    if len(endpoints) > MAX_BOOTSTRAP_FETCH_PEERS:
        raise ValueError("bootstrap_fetch_peer_endpoints_too_many")
    from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint

    normalized_endpoints = []
    for endpoint in endpoints:
        try:
            normalized_endpoints.append(
                validate_peer_endpoint(
                    _require_non_empty_string(
                        endpoint,
                        "bootstrap_fetch_peer_endpoint_invalid",
                    )
                )
            )
        except Exception as exc:
            raise ValueError("bootstrap_fetch_peer_endpoint_invalid") from exc
    count = _require_count(
        value.get("bootstrap_fetch_peers_count"),
        "bootstrap_fetch_peers_count_invalid",
    )
    if count != len(normalized_endpoints):
        raise ValueError("bootstrap_fetch_peers_count_mismatch")
    return {
        "bootstrap_fetch_bundle_cid": _require_non_empty_string(
            value.get("bootstrap_fetch_bundle_cid"),
            "bootstrap_fetch_bundle_cid_invalid",
        ),
        "bootstrap_fetch_genesis_authority_pubkey_hex": _require_genesis_authority_pubkey_hex(
            value.get("bootstrap_fetch_genesis_authority_pubkey_hex")
        ),
        "bootstrap_fetch_peer_endpoints": normalized_endpoints,
        "bootstrap_fetch_peers_count": count,
        "bootstrap_fetch_seed_peer_endpoint": _require_non_empty_string(
            value.get("bootstrap_fetch_seed_peer_endpoint"),
            "bootstrap_fetch_seed_peer_endpoint_invalid",
        ),
        "bootstrap_fetch_status": "fetched",
        "verified_bootstrap_bundle": bundle_dict,
    }


def _reject_float(value: object, token: str) -> None:
    if isinstance(value, float):
        raise ValueError(token)
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_float(key, token)
            _reject_float(item, token)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _reject_float(item, token)


def _read_json_object(path: Path, token: str) -> dict[str, Any]:
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=lambda _constant: (_ for _ in ()).throw(ValueError(token)),
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(token) from exc
    if not isinstance(payload, dict):
        raise ValueError(token)
    _reject_float(payload, token)
    return payload


def _require_peer_hint_list(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > MAX_KNOWN_PEER_HINTS:
        raise ValueError("invite_bootstrap_verified_peer_hints_invalid")
    hints: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("invite_bootstrap_verified_peer_hint_invalid")
        hints.append(dict(item))
    return hints


def _require_peer_hint_key_bindings(value: Any) -> dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError("invite_bootstrap_verified_peer_hint_key_bindings_invalid")
    return {
        _require_key_binding_ref(key): _require_mldsa_pubkey_hex(binding)
        for key, binding in value.items()
    }


def _atomic_write_json(path: Path, payload: dict[str, Any], *, mode: int) -> None:
    _atomic_write_text(
        path,
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        + "\n",
        mode=mode,
    )


def _atomic_write_text(path: Path, payload: str, *, mode: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        os.chmod(temp_name, mode)
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = -1
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
        os.chmod(path, mode)
    except BaseException:
        if fd != -1:
            os.close(fd)
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def _canonical_json_bytes(payload: dict[str, Any]) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def _canonical_sha384(payload: dict[str, Any]) -> str:
    return hashlib.sha384(_canonical_json_bytes(payload)).hexdigest()


def _zero_bytearray(value: bytearray) -> None:
    for index in range(len(value)):
        value[index] = 0


__all__ = [
    "FIRST_RUN_PROVISIONING_VERSION",
    "BOOTSTRAP_FETCH_PEERS_SCHEMA_VERSION",
    "BOOTSTRAP_PEER_HINTS_SCHEMA_VERSION",
    "IdentityAlreadyExistsError",
    "GENESIS_ROOT_ENVELOPE_HASH",
    "INVITEE_INSTALL_RECEIPT_SCHEMA_VERSION",
    "INVITEE_INSTALL_RECEIPT_SIGNATURE_DOMAIN",
    "INVITE_BOOTSTRAP_CAPSULE_SCHEMA_VERSION",
    "INSTALL_CONNECTIVITY_RECEIPT_VERSION",
    "INSTALL_CONNECTIVITY_NAT_PROBE_SCHEMA_VERSION",
    "BOOTSTRAP_FETCH_TRUSTED_GENESIS_PUBKEY_ENV",
    "MAX_BOOTSTRAP_FETCH_PEERS",
    "MAX_KNOWN_PEER_HINTS",
    "MIN_KNOWN_PEERS",
    "POP_DOMAIN",
    "attach_invite_pop_to_onboarding_receipt",
    "build_invite_pop_transcript",
    "existing_identity_summary",
    "fetch_distributed_release_peers",
    "generate_invite_pop",
    "identity_root",
    "invite_pop_payload_ref",
    "migrate_identity_schema_if_needed",
    "provision_new_identity",
    "record_install_connectivity_receipt",
    "record_invite_bootstrap_capsule_evidence",
    "validate_invite_bootstrap_capsule_fields",
    "verify_invite_pop",
    "write_invitee_install_receipt",
]
