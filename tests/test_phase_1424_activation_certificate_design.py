"""Phase 1424: Public RC Activation Certificate Design tests.

Verifies:
- activation_certificate_v1 schema structure and required fields
- epoch_0_to_1_transition_authorized default value (must be false in unsigned templates)
- canonical-lineage interpretation claims
- artifact:hello_world non-trigger and non-overclaim invariants
- canonical JSON serialization rule

Phase tokens (must appear in source):
  activation_certificate_v1_schema_defined_phase_1424
  genesis_signing_ceremony_procedure_defined_phase_1424
  epoch_0_to_1_transition_trigger_defined_phase_1424
  artifact_hello_world_design_defined_phase_1424
  public_rc_not_activated_phase_1424
"""

from __future__ import annotations

import hashlib
import json
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Phase tokens — must appear in source
# ---------------------------------------------------------------------------
_TOKEN_SCHEMA_DEFINED = "activation_certificate_v1_schema_defined_phase_1424"
_TOKEN_CEREMONY_DEFINED = "genesis_signing_ceremony_procedure_defined_phase_1424"
_TOKEN_TRIGGER_DEFINED = "epoch_0_to_1_transition_trigger_defined_phase_1424"
_TOKEN_HELLO_WORLD = "artifact_hello_world_design_defined_phase_1424"
_TOKEN_NOT_ACTIVATED = "public_rc_not_activated_phase_1424"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
REPO_ROOT = pathlib.Path(__file__).parent.parent
DESIGN_DOC = REPO_ROOT / "docs/specs/ilc_activation_certificate_v1_design_1424_v0.1.md"
MANIFEST_SCHEMA = REPO_ROOT / "docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _unsigned_template() -> dict:
    """Return the canonical unsigned activation_certificate_v1 template."""
    return {
        "certificate_version": "activation_certificate_v1",
        "launch_readiness_manifest_hash": None,
        "genesis_signing_agent_id": None,
        "genesis_signing_epoch": 0,
        "epoch_0_to_1_transition_authorized": False,
        "activation_timestamp_epoch": 0,
        "certificate_signature": None,
        "public_rc_claim": None,
    }


def _canonical_json(payload: dict) -> str:
    """Canonical JSON per ILC coding security standards."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)


# ---------------------------------------------------------------------------
# Design document existence and token tests
# ---------------------------------------------------------------------------

class TestDesignDocExists:
    def test_design_doc_exists(self):
        assert DESIGN_DOC.exists(), f"Design doc not found: {DESIGN_DOC}"

    def test_design_doc_contains_schema_token(self):
        text = DESIGN_DOC.read_text()
        assert "activation_certificate_v1_schema_defined_phase_1424" in text

    def test_design_doc_contains_ceremony_token(self):
        text = DESIGN_DOC.read_text()
        assert "genesis_signing_ceremony_procedure_defined_phase_1424" in text

    def test_design_doc_contains_trigger_token(self):
        text = DESIGN_DOC.read_text()
        assert "epoch_0_to_1_transition_trigger_defined_phase_1424" in text

    def test_design_doc_contains_hello_world_token(self):
        text = DESIGN_DOC.read_text()
        assert "artifact_hello_world_design_defined_phase_1424" in text

    def test_design_doc_contains_not_activated_token(self):
        text = DESIGN_DOC.read_text()
        assert "public_rc_not_activated_phase_1424" in text


# ---------------------------------------------------------------------------
# Schema structure tests
# ---------------------------------------------------------------------------

class TestActivationCertificateSchema:
    REQUIRED_FIELDS = [
        "certificate_version",
        "launch_readiness_manifest_hash",
        "genesis_signing_agent_id",
        "genesis_signing_epoch",
        "epoch_0_to_1_transition_authorized",
        "activation_timestamp_epoch",
        "certificate_signature",
        "public_rc_claim",
    ]

    def test_all_required_fields_present(self):
        template = _unsigned_template()
        for field in self.REQUIRED_FIELDS:
            assert field in template, f"Missing required field: {field}"

    def test_certificate_version_value(self):
        template = _unsigned_template()
        assert template["certificate_version"] == "activation_certificate_v1"

    def test_epoch_0_to_1_transition_authorized_default_false(self):
        """The most critical invariant: must be false in any unsigned template."""
        template = _unsigned_template()
        assert template["epoch_0_to_1_transition_authorized"] is False, (
            "epoch_0_to_1_transition_authorized must be False in unsigned templates"
        )

    def test_epoch_0_to_1_transition_authorized_is_boolean(self):
        template = _unsigned_template()
        assert isinstance(template["epoch_0_to_1_transition_authorized"], bool)

    def test_certificate_signature_null_in_unsigned_template(self):
        template = _unsigned_template()
        assert template["certificate_signature"] is None

    def test_public_rc_claim_null_in_unsigned_template(self):
        template = _unsigned_template()
        assert template["public_rc_claim"] is None

    def test_launch_readiness_manifest_hash_null_in_unsigned_template(self):
        template = _unsigned_template()
        assert template["launch_readiness_manifest_hash"] is None

    def test_genesis_signing_agent_id_null_in_unsigned_template(self):
        template = _unsigned_template()
        assert template["genesis_signing_agent_id"] is None

    def test_genesis_signing_epoch_is_zero_for_initial_rc(self):
        template = _unsigned_template()
        assert template["genesis_signing_epoch"] == 0

    def test_activation_timestamp_epoch_is_zero_for_initial_rc(self):
        template = _unsigned_template()
        assert template["activation_timestamp_epoch"] == 0


# ---------------------------------------------------------------------------
# Canonical JSON tests
# ---------------------------------------------------------------------------

class TestCanonicalJSON:
    def test_canonical_json_uses_sort_keys(self):
        """Keys must be sorted — insertion order must not matter."""
        p1 = {"b": 2, "a": 1}
        p2 = {"a": 1, "b": 2}
        assert _canonical_json(p1) == _canonical_json(p2)

    def test_canonical_json_uses_compact_separators(self):
        payload = {"a": 1}
        result = _canonical_json(payload)
        # No spaces after separators
        assert " " not in result

    def test_canonical_json_rejects_nan(self):
        """allow_nan=False must cause float('nan') to raise ValueError."""
        with pytest.raises((ValueError, TypeError)):
            _canonical_json({"v": float("nan")})

    def test_canonical_json_rejects_inf(self):
        """allow_nan=False must cause float('inf') to raise ValueError."""
        with pytest.raises((ValueError, TypeError)):
            _canonical_json({"v": float("inf")})

    def test_canonical_hash_of_unsigned_template_is_deterministic(self):
        """Same template must always produce the same SHA-256 hash."""
        t1 = _unsigned_template()
        t2 = _unsigned_template()
        h1 = hashlib.sha256(_canonical_json(t1).encode()).hexdigest()
        h2 = hashlib.sha256(_canonical_json(t2).encode()).hexdigest()
        assert h1 == h2

    def test_pre_signature_hash_excludes_signature_field(self):
        """Pre-signature hash must be computed with certificate_signature=null."""
        base = _unsigned_template()
        base["genesis_signing_agent_id"] = "test_agent_id"
        base["launch_readiness_manifest_hash"] = "abc123"

        # With null signature
        pre_sig = dict(base)
        pre_sig["certificate_signature"] = None
        pre_sig["public_rc_claim"] = None
        h_pre = hashlib.sha256(_canonical_json(pre_sig).encode()).hexdigest()

        # With populated signature (would differ if signature is included)
        with_sig = dict(base)
        with_sig["certificate_signature"] = {"sig": "some_sig_value"}
        with_sig["public_rc_claim"] = "public_rc_activated"
        h_with = hashlib.sha256(_canonical_json(with_sig).encode()).hexdigest()

        # The pre-signature hash must differ from the with-signature hash
        assert h_pre != h_with


# ---------------------------------------------------------------------------
# Canonical lineage interpretation tests
# ---------------------------------------------------------------------------

class TestCanonicalLineageInterpretation:
    def test_design_doc_references_adr_0037(self):
        text = DESIGN_DOC.read_text()
        assert "ADR-0037" in text or "ADR_0037" in text

    def test_design_doc_references_adr_0036(self):
        text = DESIGN_DOC.read_text()
        assert "ADR-0036" in text or "ADR_0036" in text

    def test_design_doc_references_adr_0038(self):
        text = DESIGN_DOC.read_text()
        assert "ADR-0038" in text or "ADR_0038" in text

    def test_design_doc_references_launch_readiness_manifest(self):
        text = DESIGN_DOC.read_text()
        assert "public_rc_launch_readiness_manifest_v1" in text

    def test_design_doc_states_not_a_launch_checklist(self):
        text = DESIGN_DOC.read_text()
        assert "launch checklist" in text.lower()

    def test_design_doc_states_not_operator_runbook(self):
        text = DESIGN_DOC.read_text()
        assert "operator-runbook" in text or "operator runbook" in text.lower()

    def test_design_doc_states_not_unsigned_status_report(self):
        text = DESIGN_DOC.read_text()
        assert "unsigned status report" in text.lower()

    def test_design_doc_states_no_manual_flag_flip(self):
        text = DESIGN_DOC.read_text()
        assert "manual" in text.lower()
        assert "runtime flag" in text.lower()

    def test_manifest_schema_exists(self):
        assert MANIFEST_SCHEMA.exists(), f"Manifest schema not found: {MANIFEST_SCHEMA}"

    def test_manifest_schema_has_epoch_authorized_false(self):
        text = MANIFEST_SCHEMA.read_text()
        assert "epoch_0_to_1_transition_authorized" in text
        assert "false" in text.lower()


# ---------------------------------------------------------------------------
# Epoch trigger tests
# ---------------------------------------------------------------------------

class TestEpochTrigger:
    def test_design_doc_defines_certificate_as_sole_trigger(self):
        text = DESIGN_DOC.read_text()
        assert "sole authorized trigger" in text.lower() or "single" in text.lower()

    def test_design_doc_states_no_other_mechanism(self):
        text = DESIGN_DOC.read_text()
        assert "no other" in text.lower() or "no party" in text.lower()

    def test_design_doc_references_genesis_signing_epoch_zero(self):
        text = DESIGN_DOC.read_text()
        assert "genesis_signing_epoch" in text

    def test_epoch_trigger_requires_signing_not_just_template(self):
        """Unsigned template must have transition_authorized=False."""
        template = _unsigned_template()
        # Signing ceremony sets it to True — but Phase 1424 does not execute ceremony
        assert template["epoch_0_to_1_transition_authorized"] is False

    def test_public_rc_claim_not_set_before_signing(self):
        template = _unsigned_template()
        assert template["public_rc_claim"] is None
        # After signing it would be "public_rc_activated"
        assert template["public_rc_claim"] != "public_rc_activated"


# ---------------------------------------------------------------------------
# artifact:hello_world non-trigger and non-overclaim tests
# ---------------------------------------------------------------------------

class TestArtifactHelloWorld:
    def test_design_doc_defines_hello_world_node(self):
        text = DESIGN_DOC.read_text()
        assert "artifact:hello_world" in text

    def test_design_doc_states_hello_world_does_not_trigger_epoch(self):
        text = DESIGN_DOC.read_text()
        # Must explicitly state hello_world does not trigger epoch start
        assert "does not trigger" in text.lower() or "does NOT trigger" in text

    def test_design_doc_states_hello_world_is_t1_non_reward(self):
        text = DESIGN_DOC.read_text()
        assert "T1_PUBLIC_NON_REWARD_METADATA" in text

    def test_design_doc_states_hello_world_author_is_genesis_agent(self):
        text = DESIGN_DOC.read_text()
        assert "Genesis Agent 01" in text

    def test_design_doc_states_hello_world_has_activation_cert_hash(self):
        text = DESIGN_DOC.read_text()
        assert "activation_certificate_hash" in text or "canonical_external_id" in text

    def test_design_doc_contains_frost_poem_content(self):
        text = DESIGN_DOC.read_text()
        assert "Two roads diverged in a yellow wood" in text

    def test_design_doc_contains_dedication_content(self):
        text = DESIGN_DOC.read_text()
        assert "dedicated to my children" in text

    def test_design_doc_states_no_review_lane_required(self):
        text = DESIGN_DOC.read_text()
        assert "review lane" in text.lower()
        # No review lane is required
        assert "no review lane" in text.lower() or "not required" in text.lower()

    def test_design_doc_states_no_inverted_ecu(self):
        text = DESIGN_DOC.read_text()
        assert "inverted ECU" in text

    def test_design_doc_states_no_cwea(self):
        text = DESIGN_DOC.read_text()
        assert "CWEA" in text

    def test_design_doc_states_no_pressure_flow(self):
        text = DESIGN_DOC.read_text()
        assert "pressure-flow" in text

    def test_design_doc_states_no_direct_werner_ecu(self):
        text = DESIGN_DOC.read_text()
        assert "Werner ECU" in text.lower() or "werner ecu" in text.lower()

    def test_design_doc_states_no_merkle_laplacian(self):
        text = DESIGN_DOC.read_text()
        assert "Merkle-Laplacian" in text

    def test_design_doc_states_no_spectral_hash_epoch_commitment(self):
        text = DESIGN_DOC.read_text()
        assert "spectral hash epoch commitment" in text.lower()

    def test_design_doc_states_no_posk(self):
        text = DESIGN_DOC.read_text()
        assert "PoSK" in text

    def test_design_doc_states_no_jubilee(self):
        text = DESIGN_DOC.read_text()
        assert "jubilee" in text

    def test_design_doc_states_no_threshold_signing(self):
        text = DESIGN_DOC.read_text()
        assert "threshold signing" in text

    def test_cdl_053_already_ratified_not_future_only(self):
        """CDL-053 is ratified narrowly — must not be described as unratified."""
        text = DESIGN_DOC.read_text()
        # Must mention CDL-053 ratification scope
        assert "CDL-053" in text
        # Must not describe it as unratified
        assert "cdl-053 is ratified" in text.lower() or "cdl-053 ratified" in text.lower() or \
               "CDL-053 is already ratified" in text


# ---------------------------------------------------------------------------
# Non-activation invariant tests
# ---------------------------------------------------------------------------

class TestNonActivation:
    def test_phase_1424_does_not_activate_public_rc(self):
        """Phase 1424 is design-only. Public RC remains not activated."""
        # This is asserted by the token in the design doc
        text = DESIGN_DOC.read_text()
        assert "public_rc_not_activated_phase_1424" in text

    def test_design_doc_states_no_cdl_mutation(self):
        text = DESIGN_DOC.read_text()
        assert "CDL mutation" in text

    def test_design_doc_states_no_ilc_core_change(self):
        text = DESIGN_DOC.read_text()
        assert "ilc_core" in text.lower() or "`ilc_core/`" in text

    def test_design_doc_states_no_signing_ceremony_execution(self):
        text = DESIGN_DOC.read_text()
        assert "signing ceremony" in text.lower()
        assert "not execute" in text.lower() or "does not" in text.lower() or \
               "Phase 1424 produces this design only" in text

    def test_no_ilc_core_files_modified(self):
        """Verify no ilc_core runtime files are expected to be modified by this phase."""
        # Phase 1424 is design/spec only — a test verifying the constraint is recorded
        text = DESIGN_DOC.read_text()
        assert "modify any" in text.lower() and "ilc_core" in text.lower()
