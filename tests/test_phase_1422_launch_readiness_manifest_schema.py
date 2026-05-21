"""Phase 1422 launch readiness manifest schema tests."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "docs/specs/ilc_launch_readiness_manifest_schema_1422_v0.1.md"


def _spec_text() -> str:
    assert SPEC.exists()
    return SPEC.read_text(encoding="utf-8")


def _template() -> dict[str, object]:
    text = _spec_text()
    match = re.search(r"```json\n(.*?)\n```", text, flags=re.DOTALL)
    assert match, "schema spec must include unsigned JSON template"
    return json.loads(match.group(1))


def test_required_phase_tokens_present() -> None:
    text = _spec_text()

    for token in (
        "launch_readiness_manifest_schema_defined_phase_1422",
        "public_rc_launch_readiness_manifest_v1",
        "launch_readiness_manifest_not_signed_phase_1422",
        "public_rc_not_activated_phase_1422",
    ):
        assert token in text


def test_template_has_required_schema_fields() -> None:
    template = _template()

    assert set(template) == {
        "manifest_version",
        "phase_1387_hardening_gate_verdict",
        "phase_1389_claimability_gate_verdict",
        "j008_jury_activation_gate_verdict",
        "soft_rc_eligible",
        "genesis_signing_authority",
        "epoch_0_to_1_transition_authorized",
        "activation_timestamp_epoch",
        "manifest_content_hash",
        "manifest_signature",
    }


def test_unsigned_template_is_not_signed_or_activated() -> None:
    template = _template()

    assert template["manifest_version"] == "public_rc_launch_readiness_manifest_v1"
    assert template["epoch_0_to_1_transition_authorized"] is False
    assert template["manifest_content_hash"] is None
    assert template["manifest_signature"] is None


def test_gate_inputs_reference_expected_phase_artifacts() -> None:
    template = _template()

    hardening = template["phase_1387_hardening_gate_verdict"]
    claimability = template["phase_1389_claimability_gate_verdict"]
    j008 = template["j008_jury_activation_gate_verdict"]
    soft_rc = template["soft_rc_eligible"]

    assert isinstance(hardening, dict)
    assert hardening["token"] == "pre_activation_hardening_gate_pass_phase_1387"
    assert isinstance(claimability, dict)
    assert claimability["token"] == "result=public_claimability_activated"
    assert isinstance(j008, dict)
    assert j008["status"] == "pending_phase_1427_rerun"
    assert isinstance(soft_rc, dict)
    assert soft_rc["status"] == "pending_phase_1426_rerun"


def test_canonical_json_rule_is_explicit() -> None:
    text = _spec_text()

    assert "sort_keys=True" in text
    assert 'separators=(",", ":")' in text
    assert "allow_nan=False" in text


def test_non_authorization_language_present() -> None:
    text = _spec_text()

    assert "does not sign the manifest" in text
    assert "public_rc_not_activated_phase_1422" in text
    assert "authorize epoch 0->1 transition" in text
    assert "patch `jury_activation_gate.py`" in text
