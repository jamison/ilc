from pathlib import Path

from ilc_core.bundle.type_registry import ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED


ROOT = Path(__file__).resolve().parents[1]
SPEC_ROOT = ROOT / "docs" / "specs"
STATUS = ROOT / "docs" / "phases" / "STATUS.md"

SPEC_PATH = SPEC_ROOT / "ilc_cdl_100_jury_type_dispute_procedure_v0.1.md"
EVIDENCE_PATH = (
    SPEC_ROOT
    / "ilc_cdl_100_jury_type_dispute_procedure_ratification_evidence_1573c_v0.1.md"
)
CDL_REGISTER = SPEC_ROOT / "ilc_constitutional_decision_log_v0.1.md"

DECISION_TOKENS = (
    "cdl_100_type_level_jury_size_global_tier_high_stakes_auto",
    "cdl_100_type_level_bond_petition_cdl095_high_stakes_plus_scope_multiplier",
    "cdl_100_type_level_verdict_authorizes_cdl_opening_not_automatic_ratification",
    "cdl_100_in_flight_snapshot_semantics_no_retroactive_redefinition",
    "cdl_100_instance_level_statute_cdl046_orphan_timeout_payout_irreversible",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_cdl100_procedure_spec_exists_and_contains_both_paths() -> None:
    text = _read(SPEC_PATH)

    assert "Path A - Type-Level Constitutional Claims" in text
    assert "Path B - Instance-Level Epistemic Claims" in text
    assert "CDL amendment process only" in text
    assert "standard Popperian refutation node" in text
    assert "ADR-0035 S9 Closure Declaration" in text


def test_cdl100_all_five_decisions_are_locked_in_evidence() -> None:
    evidence = _read(EVIDENCE_PATH)

    for token in DECISION_TOKENS:
        assert token in evidence

    assert "CDL-044 ratifies `retention_epochs = 1 issuance_epoch`" in evidence
    assert "live orphan timeout is ratified by CDL-046" in evidence


def test_cdl100_register_row_is_ratified_and_cdl099_dependency_is_preserved() -> None:
    register = _read(CDL_REGISTER)

    assert "| CDL-100 |" in register
    assert "| ratified | phase_1573c | cdl_100_ratified |" in register
    assert "jury_type_dispute_procedure_s9_ratified" in register
    assert "depends_on: CDL-099_ratified" in register
    assert "type_registry_activation_status: not_authorized" in register


def test_cdl100_status_tokens_are_recorded() -> None:
    status = _read(STATUS)

    for token in (
        "cdl_100_opened",
        "cdl_100_ratified",
        "jury_type_dispute_procedure_s9_ratified",
        "public_path_remains_blocked_phase_1573c",
    ):
        assert token in status


def test_cdl100_keeps_adr0035_type_registry_default_off() -> None:
    assert ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED is True

    spec = _read(SPEC_PATH)
    evidence = _read(EVIDENCE_PATH)
    assert "does not activate the ADR-0035 type registry" in spec
    assert "clear `ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED`" in evidence


def test_cdl100_does_not_reclassify_type_level_claims_as_popperian() -> None:
    spec = _read(SPEC_PATH)

    path_a = spec.split("## 3. Path A - Type-Level Constitutional Claims", 1)[1]
    path_a = path_a.split("## 4. Path B - Instance-Level Epistemic Claims", 1)[0]
    assert "CDL amendment process only" in path_a
    assert "standard Popperian" not in path_a

    path_b = spec.split("## 4. Path B - Instance-Level Epistemic Claims", 1)[1]
    assert "standard Popperian refutation node" in path_b
