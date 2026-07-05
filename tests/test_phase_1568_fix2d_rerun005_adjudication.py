from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_phase_1568_fix2d_rerun005_adjudication_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1568_fix2d_rerun005_adjudication_walkthrough.md"
OBL_REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
RERUN = ROOT / "out/block6_rehearsal/block6_rehearsal_2026_06_27_v0_1/fix2d_rerun_005"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> dict:
    return json.loads(_read(path))


def test_rerun005_artifacts_are_quote_only_partial_pass_evidence() -> None:
    operator_status = _json(RERUN / "operator_run_status.json")
    scenario_manifest = _json(RERUN / "scenario_manifest.json")
    economics = _json(RERUN / "rehearsal_economics_record.json")

    assert operator_status["exit_code"] == 1
    assert operator_status["scenario_exit_code"] == 0
    assert operator_status["settlement_verification_exit_code"] == 1

    assert scenario_manifest["submission_count"] == 7
    assert scenario_manifest["panel_passed"] is True
    assert scenario_manifest["rehearsal_cdl048_per_agent_lot_count"] == 7
    assert scenario_manifest["rehearsal_cdl048_four_epoch_quote_coverage_verified"] is True
    assert scenario_manifest["rehearsal_cdl048_wallet_write_authorized"] is False

    assert economics["quote_only"] is True
    assert economics["activation_requested"] is False
    assert economics["cdl048_wallet_write_authorized"] is False


def test_local_and_remote_settlement_verifiers_match_without_write_authority() -> None:
    expected_root = "81b60919cd1a21473b454020c64d11a533811c0f38e50bd08ecf2955190d239a"
    verifier_files = (
        "local_settlement_verify.json",
        "remote_settlement_verify_ilc-node-2.json",
        "remote_settlement_verify_ilc-node-3.json",
        "remote_settlement_verify_ilc-node-6.json",
    )

    for filename in verifier_files:
        verifier = _json(RERUN / filename)
        assert verifier["settlement_root_verified"] is True
        assert verifier["settlement_root_hex"] == expected_root
        assert verifier["cdl048_wallet_write_authorized"] is False
        assert verifier["treasury_write_authorized"] is False


def test_adjudication_spec_records_verdict_and_non_claims() -> None:
    text = _read(SPEC)

    assert "fix2d_rerun005_classified_as_quote_only_partial_pass" in text
    assert "fix2d_rerun006_required_for_full_obl_040_043_closure` is not emitted" in text
    assert "partially_closed_quote_read_model_evidence_accepted_live_execution_deferred" in text
    assert "closed_narrowed_non_claim_quote_read_model_only" in text
    assert "It does not prove live value-write settlement" in text
    assert "does not run a rehearsal" in text
    assert "write wallets" in text
    assert "activate public RC" in text


def test_obligation_register_dispositions_are_precise() -> None:
    text = _read(OBL_REGISTER)

    assert "OBL-040" in text
    assert "partially-closed - schema/verifier and Rerun 005 quote/read-model evidence accepted" in text
    assert "live distributed value execution deferred" in text
    assert "full production closure still requires deterministic eligible-lot derivation" in text

    assert "OBL-043" in text
    assert "closed - narrowed non-claim; lineage/read-model adapter and Rerun 005 quote evidence accepted" in text
    assert "live value-write settlement is not claimed" in text


def test_status_records_exactly_one_verdict_token_for_adjudication() -> None:
    text = _read(STATUS)

    required = (
        "phase_1568_fix2d_adj_rerun005_adjudication_complete",
        "phase_1568_fix2d_adj_rerun005_evidence_classified",
        "fix2d_rerun005_classified_as_quote_only_partial_pass",
        "phase_1568_fix2d_adj_no_runtime_activation",
        "public_path_remains_blocked_phase_1568_fix2d_adj",
    )
    for token in required:
        assert token in text

    assert "fix2d_rerun006_required_for_full_obl_040_043_closure" not in text


def test_walkthrough_has_no_ellipsis_and_repeats_non_activation_boundary() -> None:
    text = _read(WALKTHROUGH)

    assert "..." not in text
    assert "No ellipses in walkthrough." in text
    assert "No new rehearsal was run" in text
    assert "No Rerun 006 artifacts were created" in text
    assert "No wallet write" in text
    assert "public RC activation" in text
