from __future__ import annotations

from pathlib import Path

from ilc_core.network.d2d import spectral_sigma_policy


REPO_ROOT = Path(__file__).resolve().parents[1]
RESULTS_DOC = REPO_ROOT / "docs/specs/ilc_sim_fix2w_sigma_adversary_model_results_v0.1.md"
OBL_REGISTER = REPO_ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
CDL_SIGMA_DOC = (
    REPO_ROOT
    / "docs/specs/ilc_cdl_sigma_01_spectral_sigma_adversary_model_authority_v0.1.md"
)


def test_fix2w_sim_results_document_present() -> None:
    text = RESULTS_DOC.read_text(encoding="utf-8")

    assert "# ILC SIM Fix2w: Sigma Adversary-Model Calibration Results" in text
    assert "## 1. Adversary Model" in text
    assert "## 2. Sweep Parameters" in text
    assert "## 3. Verdict" in text
    assert "## 4. Curve Table" in text
    assert "## 5. Closure Disposition" in text
    assert "p_correct = 0.992" in text


def test_fix2w_verdict_token_present() -> None:
    text = RESULTS_DOC.read_text(encoding="utf-8")

    assert "phase_1568_fix2w_obl_046_verdict_not_validated" in text
    assert "phase_1568_fix2w_obl_046_verdict_validated" not in text


def test_fix2w_sigma_policy_consistent_with_verdict() -> None:
    text = RESULTS_DOC.read_text(encoding="utf-8")

    assert "Verdict: `not_validated`" in text
    assert spectral_sigma_policy.SIGMA_DP_CALIBRATION_VALIDATED is False
    assert spectral_sigma_policy.SIM_BEACON_01_ADVERSARY_MODEL_REVISION_REQUIRED is True
    assert (
        spectral_sigma_policy.SIGMA_POLICY_STATUS_PRE_CDL_SIGMA_01
        == "specified_floor_testnet_candidate_obl_046_open"
    )
    assert (
        spectral_sigma_policy.SIGMA_POLICY_STATUS
        == "sigma_local_simulation_only_cdl_sigma_01_ratified"
    )
    assert CDL_SIGMA_DOC.exists()


def test_fix2w_obl_046_closed() -> None:
    text = OBL_REGISTER.read_text(encoding="utf-8")
    obl_row = next(line for line in text.splitlines() if line.startswith("| OBL-046 |"))

    assert "closed_routed_to_cdl_sigma_01" in obl_row
    assert "open - pre-public-RC blocker" not in obl_row
    assert "phase_1568_fix2w_obl_046_closed" in obl_row


def test_fix2w_no_float_in_policy_for_validated_sigma() -> None:
    assert not hasattr(spectral_sigma_policy, "SIM_FIX2W_VALIDATED_SIGMA")


def test_fix2w_no_public_rc_activated() -> None:
    text = RESULTS_DOC.read_text(encoding="utf-8")

    assert spectral_sigma_policy.SIGMA_PRE_PUBLIC_RC_BLOCKER is True
    assert "phase_1568_fix2w_no_public_rc_activated" in text
    assert "public_path_remains_blocked_phase_1568_fix2w" in text
