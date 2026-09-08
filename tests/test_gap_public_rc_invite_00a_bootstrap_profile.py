from __future__ import annotations

import ast
import json
import re
from pathlib import Path

from ilc_core.genesis import invite_enforcement
from ilc_core.genesis.invitation_provenance_record import InviteBatchRecord
from ilc_core.network.relay.invite_code import validate_code


ROOT = Path(__file__).resolve().parents[1]
SPEC = (
    ROOT
    / "docs/specs/ilc_public_rc_invite_bootstrap_profile_GAP_PUBLIC_RC_INVITE_00a_v0.1.md"
)
MAIN = ROOT / "ilc_core/cli/main.py"
STATUS = ROOT / "docs/phases/STATUS.md"
CAPSULE = ROOT / "ilc_core/data/relay_bootstrap_capsule.json"
DELEGATION = (
    ROOT
    / "docs/specs/ilc_genesis_invite_issuer_delegation_record_GAP_GENESIS_INVITE_ISSUER_00_v0.1.json"
)


def _spec_text() -> str:
    return SPEC.read_text(encoding="utf-8")


def _invite_bootstrap_payload_keys() -> set[str]:
    tree = ast.parse(MAIN.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_invite_bootstrap_payload":
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name) and target.id == "invite_keys":
                            assert isinstance(child.value, ast.Set)
                            return {
                                item.value
                                for item in child.value.elts
                                if isinstance(item, ast.Constant)
                                and isinstance(item.value, str)
                            }
    raise AssertionError("_invite_bootstrap_payload invite_keys set not found")


def test_spec_doc_exists() -> None:
    assert SPEC.is_file()
    text = _spec_text()
    for section in range(1, 8):
        assert f"## \u00a7{section}" in text


def test_invite_bundle_fields_match_cli_implementation() -> None:
    text = _spec_text()
    keys = _invite_bootstrap_payload_keys()
    assert keys == {
        "intended_epoch",
        "intended_profile",
        "invite_batch_record",
        "nonce_membership_proof",
        "private_invite_nonce",
        "redeemer_agent_id",
        "redeemer_pubkey",
        "intended_redeemer_pubkey",
    }
    for key in keys:
        assert f"`{key}`" in text


def test_spec_distinguishes_openclaw_subset_from_install_materialization_fields() -> None:
    text = _spec_text()
    for field in (
        "atlas_slice_manifest_witness",
        "starmap_manifest_payload",
        "known_peer_hints",
        "known_peer_hint_key_bindings",
        "relay_bootstrap_capsule",
        "shortcode_auth",
    ):
        assert f"`{field}`" in text
    assert "outside that OpenClaw subset" not in text
    assert "OpenClaw subset" in text


def test_invite_enforcement_profile_records_pre_activation_state() -> None:
    text = _spec_text()
    assert "`INVITE_ENFORCEMENT_ENABLED` still false" in text
    assert isinstance(invite_enforcement.INVITE_ENFORCEMENT_ENABLED, bool)


def test_genesis_agent_exempt_from_enforcement() -> None:
    source = (ROOT / "ilc_core/genesis/invite_enforcement.py").read_text(
        encoding="utf-8"
    )
    assert "GENESIS_AGENT1_AGENT_ID" in source
    assert "agent_id == GENESIS_AGENT1_AGENT_ID" in source


def test_invite_batch_record_required_fields() -> None:
    record = InviteBatchRecord(
        inviter_cid="genesis_agent:01",
        batch_id="public-rc-test",
        count=1,
        nonce_merkle_root="00" * 32,
        created_epoch=0,
        inviter_sig="structural-non-empty",
    )
    text = _spec_text()
    assert set(record.to_dict()) == {
        "batch_id",
        "count",
        "created_epoch",
        "inviter_cid",
        "inviter_sig",
        "nonce_merkle_root",
    }
    for key in record.to_dict():
        assert f"`{key}`" in text


def test_bootstrap_env_vars_in_node_startup_are_documented_as_legacy_authority() -> None:
    source = (ROOT / "ilc_core/node/node_startup_runtime.py").read_text(
        encoding="utf-8"
    )
    text = _spec_text()
    for token in ("ILC_BOOTSTRAP_SEED_PEER", "ILC_BOOTSTRAP_BUNDLE_CID"):
        assert token in source
        assert token in text
    assert "historical authority" in text or "legacy/fallback" in text


def test_bundled_relay_capsule_live_public_rc_endpoints_are_documented() -> None:
    capsule = json.loads(CAPSULE.read_text(encoding="utf-8"))
    text = _spec_text()
    assert capsule["network_id"] == "public-rc"
    assert len(capsule["relay_records"]) == 3
    for record in capsule["relay_records"]:
        assert record["control_url"] in text
        assert record["tls_mode"] == "pinned_der_sha256"


def test_shortcode_path_and_checksum_are_documented() -> None:
    text = _spec_text()
    assert "`tools/install.sh --invite-code ILC-XXXX-XXXX`" in text
    assert validate_code("ILC-H7K2-X9P4") is True
    assert "ILC-XXXX-XXXX" in text
    assert "relay shortcode" in text.lower()


def test_delegated_invite_issuer_record_is_referenced_without_private_key_claim() -> None:
    delegation = json.loads(DELEGATION.read_text(encoding="utf-8"))
    text = _spec_text()
    assert re.fullmatch(r"[0-9a-f]{96}", delegation["invite_issuer_pk_hex"])
    assert delegation["invite_issuer_pk_hex"] in text
    assert "secret" not in delegation
    assert "validator hot keys" in text
    assert "capsule signing key" in text


def test_legacy_inviter_sig_not_overclaimed_as_crypto_verification() -> None:
    text = _spec_text()
    assert "non-empty string" in text
    assert "not a cryptographic authority boundary" in text
    assert "shortcode_auth" in text
    assert "ILC_RELAY_INVITE_BUNDLE_V1_BLS12381G2_XMD:SHA-256_SSWU_RO_" in text


def test_status_contains_current_prerequisite_tokens() -> None:
    status = STATUS.read_text(encoding="utf-8")
    for token in (
        "public_rc_published_GAP_PUBLIC_RC_PUBLISH_EXEC_00",
        "invite_enforcement_fix1_durable_nullifier_wiring_committed_GAP_PUBLIC_RC_INVITE_ENFORCEMENT_FIX1_00",
        "invite_shortcode_deploy_guard_cleared_GAP_INVITE_SHORTCODE_DEPLOY_00",
        "relay_bootstrap_capsule_signed_bundled_GAP_RELAY_BOOTSTRAP_CAPSULE_SIGN_00",
        "genesis_invite_issuer_delegation_complete_GAP_GENESIS_INVITE_ISSUER_00",
    ):
        assert token in status
