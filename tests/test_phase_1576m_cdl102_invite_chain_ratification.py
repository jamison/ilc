from __future__ import annotations

from pathlib import Path


RATIFICATION = Path(
    "docs/specs/ilc_cdl_102_inviter_chaining_economics_ratification_1576m_v0.1.md"
)
REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")
PROMPT = Path(
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1576m_g10_cdl102_invite_chain_ratification.md"
)


def _cdl_102_row() -> str:
    return next(
        line
        for line in REGISTER.read_text(encoding="utf-8").splitlines()
        if line.startswith("| CDL-102 |")
    )


def test_cdl_102_ratification_doc_locks_organic_cdl108_model() -> None:
    text = RATIFICATION.read_text(encoding="utf-8")

    assert "**Status:** RATIFIED" in text
    assert "cdl_102_ratified_phase_1576m" in text
    assert "No hardcoded fraction is ratified" in text
    assert "CDL-108" in text
    assert "no CDL-084 explicit inviter chain" in text
    assert 'alpha = Decimal("0.45")' in text
    assert "max_depth = 3" in text
    assert "backward pool share" in text
    assert 'Decimal("0.10")' in text


def test_cdl_102_ratification_doc_rejects_referral_fee_language() -> None:
    text = RATIFICATION.read_text(encoding="utf-8")

    assert "no referral fee" in text
    assert "no percentage of the invitee's future earnings" in text
    assert "no direct transfer" in text
    assert "top-down payment" in text
    assert "no separate invite-only expiry period" in text.lower()


def test_cdl_102_ratification_preserves_non_activation_boundaries() -> None:
    text = RATIFICATION.read_text(encoding="utf-8")

    required = (
        "does not activate invite\n"
        "enforcement, invite nullifier gossip, invite provenance edge writing",
        "does not by itself activate any runtime path",
        "mint ECU",
        "settle ILC",
        "authorize public RC",
    )
    for phrase in required:
        assert phrase in text


def test_cdl_102_ratification_resolves_q1_through_q6() -> None:
    text = RATIFICATION.read_text(encoding="utf-8")

    for section in (
        "## 3. Q1 Resolution",
        "## 4. Q2 Resolution",
        "## 5. Q3 Resolution",
        "## 6. Q4 Resolution",
        "## 7. Q5 Resolution",
        "## 8. Q6 Resolution",
    ):
        assert section in text
    assert "TBD" not in text
    assert "to be determined" not in text.lower()


def test_cdl_102_register_row_is_ratified_and_cites_evidence() -> None:
    row = _cdl_102_row()

    assert " | ratified | " in row
    assert "ratified_phase: 1576m" in row
    assert "ratification_token: cdl_102_ratified_phase_1576m" in row
    assert (
        "evidence_document: "
        "docs/specs/ilc_cdl_102_inviter_chaining_economics_ratification_1576m_v0.1.md"
    ) in row
    assert "invite_credit_model: organic_cdl_108_backward_attribution" in row
    assert "fixed_fraction_status: rejected" in row
    assert "runtime_activation_status: not_authorized" in row


def test_status_records_cdl_102_ratification_token() -> None:
    text = STATUS.read_text(encoding="utf-8")

    assert "cdl_102_ratified_phase_1576m" in text
    assert "backward_attribution_cdl_ratified_GAP_ECU_03" in text
    assert "backward_attribution_runtime_wired_GAP_ECU_04b" in text
    assert "backward_attribution_soak_complete_GAP_ECU_06" in text


def test_phase_1576m_prompt_hardened_to_current_go_and_cdl108_inputs() -> None:
    text = PROMPT.read_text(encoding="utf-8")

    assert "GO Phase 1576m CDL-102-RATIFY" in text
    assert "phase_1575h_canonical_soak_complete" not in text
    assert "backward_attribution_cdl_ratified_GAP_ECU_03" in text
    assert "backward_attribution_runtime_wired_GAP_ECU_04b" in text
    assert "backward_attribution_soak_complete_GAP_ECU_06" in text
    assert "no hardcoded" in text
    assert "no CDL-084 explicit inviter chain" in text


def test_cdl_091_and_cdl_029_are_explicitly_unmodified() -> None:
    text = RATIFICATION.read_text(encoding="utf-8")
    row = _cdl_102_row()

    assert "CDL-091 remains Jury Incentive Economics" in text
    assert "CDL-029 remains the 80/15/5 allocation split" in text
    assert "cdl_091_status: unchanged" in row
    assert "cdl_029_status: unchanged" in row
