import json
from pathlib import Path

from ilc_core.network.d2d import spectral_route_token as srt


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs/specs/ilc_cdl_sigma_01_adversary_model_ratification_evidence_1573i_v0.1.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
SIM_RESULTS = ROOT / "out/sim_ccss_spectral_01_adversary_model_results.json"
FIX38_LEDGER = ROOT / "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_evidence_document_contains_required_tokens_and_non_claims() -> None:
    text = _text(EVIDENCE)
    assert "cdl_sigma_01_adversary_model_ratified_phase_1573i" in text
    assert "ccss_spectral_01_indistinguishability_target_locked_phase_1573i" in text
    assert "ccss_spectral_01_relay_adversary_model_ratified_phase_1573i" in text
    assert "ccss_spectral_01_activation_precondition_recorded_phase_1573i" in text
    assert "public_path_remains_blocked_phase_1573i" in text
    assert "formal cryptographic proof" in text
    assert "differential privacy" in text
    assert "anonymity" in text
    assert "guard clearance" in text


def test_relay_adversary_model_records_visible_and_hidden_surfaces() -> None:
    text = _text(EVIDENCE)
    for visible in (
        "`epoch`",
        "`route_token`",
        "`sender_ephemeral_pubkey`",
        "`kem_ciphertext`",
        "`hiding_commitment`",
        "`capability_context_commitment`",
        "`size_class`",
        "`message_nonce`",
    ):
        assert visible in text
    for hidden in (
        "`lambda_local`",
        "quantized lambda values",
        "`commitment_salt`",
        "raw contact capability identifier",
        "`sk_recipient_capability`",
        "hybrid shared secret `ss`",
    ):
        assert hidden in text


def test_indistinguishability_target_is_design_target_not_proof() -> None:
    text = _text(EVIDENCE)
    assert (
        "I(lambda_local; Token_1, ..., Token_T) <= "
        "T * (epsilon_PRF + epsilon_hiding) ~= negl(lambda)"
    ) in text
    assert "This is a design target and governance constraint, not a formal proof" in text


def test_sim_results_are_pass_and_recorded_as_analytic_no_signal_bound() -> None:
    sim = json.loads(SIM_RESULTS.read_text(encoding="utf-8"))
    assert sim["verdict"] == "pass"
    assert sim["kem_algorithm"] == "hybrid_x25519_ml_kem_768_fips203"
    assert sim["non_claim"] == "SIM pass does not constitute a formal cryptographic proof"
    assert len(sim["results"]) == 18
    assert max(row["linking_probability"] for row in sim["results"]) == 0.01
    assert all(row["linking_probability"] <= row["threshold"] for row in sim["results"])
    assert all(row["pass"] is True for row in sim["results"])
    assert all(row["slope"] == 0.0 for row in sim["t_obs_correlation_by_n"])
    text = _text(EVIDENCE)
    assert "linking_probability = 1/N" in text
    assert "analytic no-signal bound" in text
    assert "not an empirical 200-trial estimate" in text


def test_side_channel_constraints_are_precisely_recorded() -> None:
    text = _text(EVIDENCE)
    assert "hmac.compare_digest()" in text
    for purpose in ("`bootstrap`", "`direct-message`", "`query`", "`relay`"):
        assert purpose in text
    assert srt.CCSS_SPECTRAL_SIZE_CLASS_VALUES == frozenset()
    assert "CCSS_SPECTRAL_SIZE_CLASS_VALUES` remains empty" in text
    assert "no dedicated size-class validator exists" in text
    assert "Cover traffic and batching: not addressed" in text
    assert "Relay-path metadata: not addressed" in text


def test_runtime_activation_guard_remains_closed() -> None:
    assert srt.CCSS_SPECTRAL_01_NOT_ACTIVATED is True
    assert srt.CCSS_SPECTRAL_01_KEM_ALGORITHM == "hybrid_x25519_ml_kem_768_fips203"
    text = _text(EVIDENCE)
    assert "does not clear `CCSS_SPECTRAL_01_NOT_ACTIVATED`" in text
    assert "does not activate route-token runtime emission" in text


def test_cdl_register_contains_inline_1573i_amendment() -> None:
    text = _text(CDL_REGISTER)
    row = next(line for line in text.splitlines() if line.startswith("| CDL-SIGMA-01 |"))
    assert "ratified | phase_1573e | cdl_sigma_01_ratified_phase_1573e" in row
    assert "amendment_phase: 1573i" in row
    assert "amendment_date: 2026-07-07" in row
    assert "amendment_token: cdl_sigma_01_adversary_model_ratified_phase_1573i" in row
    assert "no formal proof, no DP/anonymity claim, no guard clearance" in row


def test_status_records_phase_1573i_tokens_once() -> None:
    text = _text(STATUS)
    section = text.split("## Phase 1573i", 1)[1]
    required = (
        "cdl_sigma_01_adversary_model_ratified_phase_1573i",
        "ccss_spectral_01_indistinguishability_target_locked_phase_1573i",
        "ccss_spectral_01_relay_adversary_model_ratified_phase_1573i",
        "ccss_spectral_01_activation_precondition_recorded_phase_1573i",
        "public_path_remains_blocked_phase_1573i",
    )
    for token in required:
        assert section.count(token) == 1
    assert "ccss_spectral_01_sim_adversary_model_fail_phase_1573h" not in text


def test_fix38_annotation_ledger_records_phase_1573i() -> None:
    ledger = json.loads(FIX38_LEDGER.read_text(encoding="utf-8"))
    annotations = ledger["annotations"]
    matches = [
        row for row in annotations if row.get("annotation_batch") == "manual_batch_078_phase_1573i"
    ]
    assert len(matches) == 1
    row = matches[0]
    assert row["repo_path"] == str(EVIDENCE.relative_to(ROOT))
    assert "ccss_spectral_01_sim_adversary_model_pass_phase_1573h" in json.dumps(
        row, sort_keys=True
    )
    assert "invariant:ccss_spectral_01_no_formal_privacy_proof_claim_phase_1573i" in json.dumps(
        row, sort_keys=True
    )
