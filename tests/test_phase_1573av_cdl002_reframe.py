from __future__ import annotations

from pathlib import Path

from ilc_core.security import key_compromise_runtime


ROOT = Path(__file__).resolve().parents[1]
CDL_LOG = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
CDL_002_SPEC = ROOT / "docs/specs/ilc_cdl_002_key_compromise_response_contract_v0.1.md"

CANONICAL_PRINCIPLE = (
    "Root identity keys are not revocable. They may only be forward-superseded "
    "through a recovery or succession policy that was explicitly committed on-graph "
    "before the supersession event and whose activation rules are verifiable from "
    "on-graph evidence. Bad behavior from a root key is handled organically by "
    "juries, reputation, routing refusal, pruning, and temporal validity, not by "
    "cancellation."
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_002_row() -> str:
    for line in _read(CDL_LOG).splitlines():
        if line.startswith("| CDL-002 |"):
            return line
    raise AssertionError("CDL-002 row not found")


def test_cdl_002_spec_doc_contains_canonical_language() -> None:
    assert CANONICAL_PRINCIPLE in _read(CDL_002_SPEC)


def test_cdl_002_spec_doc_names_credential_supersession() -> None:
    text = _read(CDL_002_SPEC)

    assert "# ILC CDL-002: Credential Supersession and Compromise Signaling" in text
    assert "Phase 1573av constitutional reframe applied" in text


def test_cdl_002_spec_doc_has_key_class_table() -> None:
    text = _read(CDL_002_SPEC)

    for term in (
        "`root_identity_key`",
        "`delegated_signer`",
        "`compromise_claim`",
        "`coercion_signal`",
        "`bad_root_key_behavior`",
    ):
        assert term in text


def test_cdl_002_spec_doc_no_administrative_root_revocation_language() -> None:
    text = _read(CDL_002_SPEC).lower()

    forbidden_phrases = (
        "genesis revokes",
        "admin deletes",
        "admin revokes",
        "centralized revocation",
        "third-party root identity revocation",
        "signed before compromise",
    )
    for phrase in forbidden_phrases:
        assert phrase not in text


def test_cdl_log_cdl002_row_renamed_and_amended() -> None:
    row = _cdl_002_row()

    assert "Credential Supersession and Compromise Signaling" in row
    assert "amendment_phase: 1573av" in row
    assert "cdl_002_credential_supersession_reframe_complete_phase_1573av" in row
    assert "root identity keys are not revocable" in row


def test_runtime_scope_constant_present() -> None:
    assert key_compromise_runtime.CDL_002_SCOPE == "delegated_signer_only"


def test_runtime_scope_phase_recorded() -> None:
    assert key_compromise_runtime.CDL_002_SCOPE_RATIFIED_PHASE == "1573av"


def test_later_governance_cannot_invent_recovery_stated() -> None:
    text = _read(CDL_002_SPEC)

    assert "It may not invent a recovery path for an agent that did not precommit one." in text


def test_delegated_runtime_trigger_behavior_preserved() -> None:
    assert (
        key_compromise_runtime.STATE_BY_TRIGGER[key_compromise_runtime.TRIGGER_COERCION_SIGNAL]
        == key_compromise_runtime.COMPROMISE_CONFIRMED
    )
    assert (
        key_compromise_runtime.STATE_BY_TRIGGER[key_compromise_runtime.TRIGGER_CUSTODY_LOSS]
        == key_compromise_runtime.COMPROMISE_CONFIRMED
    )
    assert (
        key_compromise_runtime.STATE_BY_TRIGGER[key_compromise_runtime.TRIGGER_CRYPTO_COMPROMISE]
        == key_compromise_runtime.COMPROMISE_CONFIRMED
    )
