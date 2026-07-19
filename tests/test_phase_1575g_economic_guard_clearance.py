from __future__ import annotations

from pathlib import Path

from ilc_core.economics.productive_ecu_expansion_bounty_runtime import (
    PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED,
)
from ilc_core.epoch.cdl057_witness_gate_adapter import (
    EpochWitnessGateAdapter,
    is_batch_eligible_for_public_rc_certification,
)
from ilc_core.epoch.ejected_stake_distribution_production_path import (
    EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED,
)
from ilc_core.epoch.epoch_boundary_witness_runtime import record_epoch_boundary_witness
from ilc_core.epoch.epoch_emission_production_path import PRODUCTION_EMISSION_NOT_ACTIVATED
from ilc_core.epoch.treasury_validator_reward_production_path import (
    TREASURY_DISTRIBUTION_NOT_ACTIVATED,
)
from ilc_core.ledger.conversion_candidate_runtime import (
    CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED,
)
from ilc_core.ledger.distributed_conversion_schema import (
    CDL057_WITNESS_ABSENT_TOKEN,
    GENESIS_TRANCHE_EXPLICITLY_DEFERRED,
    ConversionCandidate,
    attach_cdl057_witness_ref,
    build_conversion_resolution,
)
from ilc_core.rc.source_allowlist_export_rehearsal import (
    build_source_allowlist_export_rehearsal,
)
from ilc_core.validator.validator_admission_ejection_production_path import (
    VALIDATOR_ADMISSION_NOT_ACTIVATED,
)


ROOT = Path(__file__).resolve().parents[1]
ECONOMIC_MODULES = (
    "ilc_core/epoch/epoch_emission_production_path.py",
    "ilc_core/ledger/conversion_candidate_runtime.py",
    "ilc_core/validator/validator_admission_ejection_production_path.py",
    "ilc_core/epoch/treasury_validator_reward_production_path.py",
    "ilc_core/epoch/ejected_stake_distribution_production_path.py",
    "ilc_core/economics/productive_ecu_expansion_bounty_runtime.py",
)


def _candidate() -> ConversionCandidate:
    return ConversionCandidate(
        lot_id="phase-1575g-lot-001",
        agent_id="agent-" + "e" * 64,
        amount_ecu="100",
        issue_epoch=0,
        deadline_epoch=1,
        conversion_epoch=1,
        genesis_tranche_treatment=GENESIS_TRANCHE_EXPLICITLY_DEFERRED,
        cdl057_witness_ref=CDL057_WITNESS_ABSENT_TOKEN,
        candidate_source="phase_1575g_test",
    )


def test_phase_1575g_two_single_lock_guards_cleared_four_double_locks_retained() -> None:
    # Guard cleared by Phase 1575g.
    assert PRODUCTION_EMISSION_NOT_ACTIVATED is False
    # Guard cleared by Phase 1575g.
    assert CONVERSION_CANDIDATE_RUNTIME_NOT_ACTIVATED is False

    assert VALIDATOR_ADMISSION_NOT_ACTIVATED is True
    assert TREASURY_DISTRIBUTION_NOT_ACTIVATED is True
    assert EJECTED_STAKE_DISTRIBUTION_PRODUCTION_NOT_ACTIVATED is True
    assert PRODUCTIVE_ECU_EXPANSION_NOT_ACTIVATED is True


def test_phase_1575g_economic_modules_are_marker_free() -> None:
    for rel_path in ECONOMIC_MODULES:
        header = "\n".join((ROOT / rel_path).read_text(encoding="utf-8").splitlines()[:8])
        assert "PUBLIC_RC_EXCLUDE" not in header


def test_phase_1575g_source_export_required_inclusion_passes_for_six_modules() -> None:
    manifest = build_source_allowlist_export_rehearsal(
        repo_root=ROOT,
        include_roots=ECONOMIC_MODULES,
        excluded_roots=(),
        required_included_paths=ECONOMIC_MODULES,
    )

    assert manifest["marker_scan"]["result"] == "pass"
    assert manifest["required_included_paths"]["result"] == "pass"
    assert manifest["required_included_paths"]["checked_count"] == len(ECONOMIC_MODULES)
    assert [record["path"] for record in manifest["required_included_paths"]["present"]] == sorted(
        ECONOMIC_MODULES
    )


def test_phase_1575g_cdl057_witness_gate_fails_closed_without_runtime_and_passes_live() -> None:
    adapter = EpochWitnessGateAdapter()
    adapter.add_witness_record(
        record_epoch_boundary_witness("validator-phase-1575g-001", 1, "phase-1575g-lot-001")
    )
    live_resolution = build_conversion_resolution(
        attach_cdl057_witness_ref(_candidate(), adapter),
        resolution_epoch=1,
        resolution_status="resolved",
    )

    assert is_batch_eligible_for_public_rc_certification(live_resolution, None) is False
    assert is_batch_eligible_for_public_rc_certification(live_resolution, adapter) is True

