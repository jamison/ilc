"""Phase 1431 rehearsal identity ceremony tests.

Ceremony complete. These tests verify:
- FINDING-9 disposition: no unratified change to CDL-069/CDL-090 v2 derivation
- Manifest has exactly 7 entries with correct structure
- Manifest authority scope is private rehearsal only
- Public identity activation is false
- Future public RC re-init is required
- No private key material or mnemonic/seed material in the manifest
- Phase tokens present
- v2 known-vector guard (CDL-069/CDL-090 ratified formula)
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

import ilc_core.identity.agent_id_runtime as agent_id_runtime
from ilc_core.identity.agent_id_runtime import derive_agent_id, derive_agent_id_v2

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs/specs/ilc_rehearsal_agent_identity_manifest_1431_v0.1.md"
AGENT_ID_RUNTIME_PATH = ROOT / "ilc_core/identity/agent_id_runtime.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# FINDING-9 disposition — CDL-069/CDL-090 known-vector guard
# ---------------------------------------------------------------------------

def test_finding_9_v2_domain_separator_unchanged() -> None:
    """_AGENT_ID_DOMAIN_V2 must remain the CDL-069 ratified value."""
    assert agent_id_runtime._AGENT_ID_DOMAIN_V2 == b"ilc-agent-id-v1:"  # noqa: SLF001


def test_finding_9_v2_known_vector() -> None:
    """derive_agent_id_v2 must match CDL-069/CDL-090 ratified formula."""
    seed = b"\x00" * 32
    expected = hashlib.sha384(b"ilc-agent-id-v1:" + seed).hexdigest()
    assert derive_agent_id_v2(seed) == expected


def test_finding_9_no_unratified_derivation_change() -> None:
    """Only the ratified domain constant may appear in the runtime source."""
    source = AGENT_ID_RUNTIME_PATH.read_text()
    # Match only constant declaration lines, not use-sites
    domain_lines = [
        line.strip() for line in source.splitlines()
        if "_AGENT_ID_DOMAIN" in line and ": bytes =" in line
    ]
    for line in domain_lines:
        assert 'b"ilc-agent-id-v1:"' in line, (
            f"Unexpected domain constant declaration: {line!r}. "
            "Any new domain requires explicit CDL/ADR authority."
        )


def test_legacy_and_v2_identity_paths_remain_unambiguous() -> None:
    same_32_bytes = bytes(range(32))
    legacy_id = derive_agent_id(same_32_bytes)
    v2_id = derive_agent_id_v2(same_32_bytes)
    assert legacy_id != v2_id
    assert legacy_id.startswith("agent-")
    assert len(legacy_id) == 70
    assert not v2_id.startswith("agent-")
    assert len(v2_id) == 96
    assert all(c in "0123456789abcdef" for c in v2_id)


# ---------------------------------------------------------------------------
# Manifest existence and structure
# ---------------------------------------------------------------------------

def test_manifest_exists() -> None:
    assert MANIFEST.exists(), f"Manifest not found: {MANIFEST}"


def test_manifest_has_exactly_seven_agents() -> None:
    text = _read(MANIFEST)
    entries = re.findall(r"^### Agent \d+", text, re.MULTILINE)
    assert len(entries) == 7, f"Expected 7 agent entries, found {len(entries)}"


def test_manifest_seven_agent_ids_present_and_unique() -> None:
    text = _read(MANIFEST)
    agent_ids = re.findall(r"agent_id:\s+([0-9a-f]{96})", text)
    assert len(agent_ids) == 7, (
        f"Expected 7 agent_id values (96-char hex), found {len(agent_ids)}"
    )
    assert len(agent_ids) == len(set(agent_ids)), "All 7 agent_ids must be unique"


def test_manifest_machine_assignments_cover_all_three_machines() -> None:
    text = _read(MANIFEST)
    assert "machine:                  M1" in text
    assert "machine:                  M2" in text
    assert "machine:                  M3" in text


# ---------------------------------------------------------------------------
# Authority scope assertions
# ---------------------------------------------------------------------------

def test_manifest_authority_scope_private_rehearsal_only() -> None:
    text = _read(MANIFEST)
    assert "artifact_authority_scope=private_soft_rc_rehearsal_only" in text


def test_manifest_public_identity_activation_false() -> None:
    text = _read(MANIFEST)
    assert "public_identity_activation_authorized=false" in text


def test_manifest_future_rc_reinit_required() -> None:
    text = _read(MANIFEST)
    assert "future_rc_reinit_required=true" in text


def test_manifest_private_key_material_absent_declaration() -> None:
    text = _read(MANIFEST)
    assert "private_key_material_present=false" in text


def test_manifest_no_secret_material() -> None:
    """No mnemonic, seed phrase, or private key material in manifest."""
    text = _read(MANIFEST).lower()
    # These patterns would only appear if actual secret material were present,
    # not in a disclaimer sentence that enumerates what is absent.
    forbidden = [
        "plate 1]",   # pq_keygen output section header
        "plate 2]",
        "plate 3]",
        "private_key:",
        "mldsa_sk",
        "sphincs_sk",
        "sk_hex",
    ]
    for term in forbidden:
        assert term not in text, (
            f"Forbidden term '{term}' found in manifest — "
            "no private key or mnemonic material may be present."
        )


# ---------------------------------------------------------------------------
# Phase tokens
# ---------------------------------------------------------------------------

def test_phase_tokens_present() -> None:
    text = _read(MANIFEST)
    required_tokens = [
        "rehearsal_identity_ceremony_complete_phase_1431",
        "finding_9_domain_separator_fixed_phase_1431",
        "finding_9_domain_separator_disposition_phase_1431",
        "finding_9_no_unratified_cdl_069_derivation_change_phase_1431",
        "seven_agent_keypairs_generated_phase_1431",
        "seven_agent_keypairs_generated_off_machine_phase_1431",
        "keypairs_not_in_repo_phase_1431",
        "identity_ceremony_public_manifest_only_phase_1431",
        "rehearsal_identity_artifacts_private_scope_phase_1431",
        "q1_identity_continuity_preserved_keys_off_machine_phase_1431",
        "no_live_ecu_phase_1431",
        "no_graph_writes_phase_1431",
        "no_public_serving_phase_1431",
        "rehearsal_identity_ceremony_not_production_rc_phase_1431",
    ]
    for token in required_tokens:
        assert token in text, f"Required phase token missing: {token}"


# ---------------------------------------------------------------------------
# Pre-epoch blockers
# ---------------------------------------------------------------------------

def test_pre_epoch_blocker_tokens_present() -> None:
    text = _read(MANIFEST)
    assert "pre_epoch_blocker_gap_genesis_validator_provenance_binding_00_phase_1431" in text
    assert "pre_epoch_blocker_gap_genesis_invite_issuer_00_phase_1431" in text


def test_pre_epoch_blocker_gap_names_in_table() -> None:
    text = _read(MANIFEST)
    assert "GAP-GENESIS-VALIDATOR-PROVENANCE-BINDING-00" in text
    assert "GAP-GENESIS-INVITE-ISSUER-00" in text
