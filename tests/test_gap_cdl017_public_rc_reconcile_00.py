# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SPEC = REPO / "docs/specs/ilc_cdl017_public_rc_reconciliation_GAP_CDL017_PUBLIC_RC_RECONCILE_00_v0.1.md"


def _read(path: str | Path) -> str:
    return (REPO / path if isinstance(path, str) else path).read_text(encoding="utf-8")


def _python_source_contains(root: Path, needle: str) -> bool:
    return any(needle in path.read_text(encoding="utf-8") for path in root.rglob("*.py"))


def test_reconciliation_spec_records_required_tokens() -> None:
    text = _read(SPEC)
    assert "cdl017_public_rc_reconciliation_complete_GAP_CDL017_PUBLIC_RC_RECONCILE_00" in text
    assert "cdl017_no_duplicate_open_ratify_required_GAP_CDL017_PUBLIC_RC_RECONCILE_00" in text
    assert "cdl017_public_rc_impl_delta_required_GAP_CDL017_PUBLIC_RC_RECONCILE_00" in text


def test_cdl017_is_ratified_not_open() -> None:
    text = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    rows = [line for line in text.splitlines() if line.startswith("| CDL-017 |")]
    assert len(rows) == 1
    assert "| ratified |" in rows[0]
    assert "ratified_phase: 765" in rows[0]


def test_existing_python_validator_role_runtime_is_present() -> None:
    from ilc_core.validator.admission_ejection_runtime import (  # noqa: PLC0415
        CDL_017_DEPENDENCY,
        FIRST_NON_GENESIS_VALIDATOR_DEPLOYMENT_HUMAN_GATE_TOKEN,
        PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN,
        ValidatorRoleRecord,
        build_validator_role_record,
    )

    assert "ratified_phase_765" in CDL_017_DEPENDENCY
    assert PRODUCTION_VALIDATOR_ADMISSION_NOT_ACTIVATED_TOKEN
    assert FIRST_NON_GENESIS_VALIDATOR_DEPLOYMENT_HUMAN_GATE_TOKEN
    assert ValidatorRoleRecord.__name__ == "ValidatorRoleRecord"
    assert callable(build_validator_role_record)


def test_existing_eligibility_certificate_runtime_is_present() -> None:
    from ilc_core.validator.validator_eligibility_certificate import (  # noqa: PLC0415
        GENESIS_BOOTSTRAP_AUTHORITY_TOKEN,
        GenesisBootstrapAuthorityCertificate,
        ValidatorEligibilityCertificate,
    )

    assert GENESIS_BOOTSTRAP_AUTHORITY_TOKEN
    assert GenesisBootstrapAuthorityCertificate.__name__ == "GenesisBootstrapAuthorityCertificate"
    assert ValidatorEligibilityCertificate.__name__ == "ValidatorEligibilityCertificate"


def test_rust_admit_eject_hooks_are_live_not_placeholders() -> None:
    text = _read("ilc_consensus/src/validator.rs")
    admit_start = text.index("pub fn admit_validator(")
    eject_start = text.index("pub fn eject_validator(")
    hook_region = text[admit_start : eject_start + 900]
    assert "pub fn admit_validator(" in hook_region
    assert "pub fn eject_validator(" in hook_region
    assert "unimplemented!" not in hook_region
    assert "ValidatorSet::rebuild_with" in hook_region


def test_public_rc_default_candidate_field_gap_recorded_or_implemented() -> None:
    spec_text = _read(SPEC)
    assert "validator_participation_enabled" in spec_text
    assert (
        "validator_participation_enabled" in _read("ilc_core/validator/admission_ejection_runtime.py")
        or "not implemented" in spec_text
    )


def test_no_validator_cli_opt_out_gap_recorded_or_implemented() -> None:
    spec_text = _read(SPEC)
    cli_text = _read("ilc_core/cli/main.py")
    assert "--invite" in cli_text
    assert "--no-validator" in cli_text or "no `--no-validator`" in spec_text


def test_first_class_validator_registration_model_is_not_implemented_yet() -> None:
    assert not _python_source_contains(REPO / "ilc_core/validator", "class ValidatorRegistration")
    assert "pub struct ValidatorRegistration" not in _read("ilc_consensus/src/validator.rs")


def test_forward_plan_records_reconciliation_row_and_delta() -> None:
    text = _read("docs/specs/ilc_comprehensive_forward_plan_post_1575c_v0.1.md")
    assert "GAP-CDL017-PUBLIC-RC-RECONCILE-00" in text
    assert "COMPLETE" in text
    assert "GAP-CDL017-IMPL-DELTA-00" in text
    assert "cdl017_public_rc_impl_delta_required_GAP_CDL017_PUBLIC_RC_RECONCILE_00" in text
