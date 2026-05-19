from pathlib import Path


REPO = Path(__file__).resolve().parents[1]

CLEARANCE = REPO / "docs/specs/ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md"
PROMPT_1388 = (
    REPO
    / "docs/antigravity_tasks/antigravity_prompt__phase_1388_g8_cdl_048_activation_counsel_clearance.md"
)
PROMPT_1388A = (
    REPO / "docs/antigravity_tasks/antigravity_prompt__phase_1388a_g8_cdl_048_self_counsel_clearance.md"
)
LICENSING = REPO / "LICENSING.md"
CDL_086 = REPO / "docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md"
PHASE_1300 = REPO / "docs/specs/ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md"
RUNTIME = REPO / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
WALKTHROUGH = REPO / "docs/phases/phase_1388a_cdl_048_self_counsel_clearance_walkthrough.md"
STATUS = REPO / "docs/phases/STATUS.md"
PLANNING_INDEX = REPO / "docs/PLANNING_INDEX.md"
SEQUENCE_LOCK = REPO / "docs/specs/ilc_phase_1369_1390_sequence_lock_v0.1.md"
WINDOW_GROUPING = REPO / "docs/specs/ilc_window_1369_1390_candidate_phase_grouping_v0.1.md"

REQUIRED_TOKENS = {
    "counsel_clearance_cdl_048_activation_phase_1388a",
    "self_counsel_decision_not_external_legal_opinion_phase_1388a",
}

PHASE_1388_SUCCESS_TOKENS = {
    "cdl_048" + "_activated_phase_1388",
    "counsel_clearance_public_verifier_api" + "_phase_1388",
    "first_live_value_path" + "_activation_phase_1388",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_clearance_artifact_records_required_tokens() -> None:
    text = _read(CLEARANCE)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_forward_external_legal_advice_obligation_token_absent() -> None:
    combined = "\n".join(
        _read(path)
        for path in (
            CLEARANCE,
            PROMPT_1388A,
            LICENSING,
            CDL_086,
            WALKTHROUGH,
            STATUS,
            PLANNING_INDEX,
            SEQUENCE_LOCK,
            WINDOW_GROUPING,
        )
    )
    forbidden_token = (
        "forward_obligation_qualified_legal"
        "_advice_before_mainnet_phase_1388a"
    )
    forbidden_phrase = "qualified legal" + " advice"
    assert forbidden_token not in combined
    assert forbidden_phrase not in combined


def test_clearance_artifact_is_narrow_and_not_external_legal_opinion() -> None:
    text = _read(CLEARANCE)
    assert "pre-production/testnet" in text
    assert "not external legal advice" in text
    assert "not attorney sign-off" in text
    assert "not a licensed-practitioner opinion" in text
    assert "mainnet launch" in text
    assert "public ECU-to-ILC conversions with real-world economic value" in text


def test_clearance_artifact_does_not_activate_phase_1388_success_tokens() -> None:
    text = _read(CLEARANCE) + "\n" + _read(WALKTHROUGH)
    for token in PHASE_1388_SUCCESS_TOKENS:
        assert token not in text


def test_runtime_preserves_phase_1380_token_and_records_phase_1388_activation() -> None:
    text = _read(RUNTIME)
    assert "CDL048_NOT_ACTIVATED_PHASE_1380_TOKEN" in text
    for token in PHASE_1388_SUCCESS_TOKENS:
        assert token in text


def test_licensing_records_scoped_phase_1388a_note_without_claiming_external_opinion() -> None:
    text = _read(LICENSING)
    assert "Phase 1388a CDL-048 Pre-Production Activation Scope" in text
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "not an external legal opinion" in text
    assert "mainnet launch" in text
    assert "public token distribution/offering/listing surfaces" in text


def test_cdl_086_records_scoped_phase_1388a_addendum() -> None:
    text = _read(CDL_086)
    assert "Phase 1388a Scoped Self-Counsel Addendum" in text
    for token in REQUIRED_TOKENS:
        assert token in text
    assert "no longer provisional" in text
    assert "pre-production/testnet activation" in text
    assert "does not convert the Phase 1220 counsel disposition into an" in text
    assert "external counsel opinion" in text


def test_phase_1300_publication_inventory_remains_inventory_only() -> None:
    text = _read(PHASE_1300)
    assert "counsel_ip_publication_verdict_phase_1300=inventory_only_no_publication" in text


def test_phase_1388_prompt_uses_phase_1388a_self_counsel_prerequisite() -> None:
    text = _read(PROMPT_1388)
    assert "ilc_pre_activation_hardening_gate_report_1387_rerun_v0.2.md" in text
    assert "ilc_counsel_clearance_cdl_048_activation_1388a_v0.1.md" in text
    assert "Genesis-authority self-counsel decision" in text
    assert "Formal sign-off from counsel" not in text
    assert "ilc_counsel_clearance_1388_v0.1.md" not in text


def test_phase_1388a_prompt_exists_and_declares_non_sensitive_scope() -> None:
    text = _read(PROMPT_1388A)
    assert "# Phase 1388a-G8" in text
    assert "NON-SENSITIVE" in text
    assert "no runtime activation" in text
    for token in REQUIRED_TOKENS:
        assert token in text


def test_planning_surfaces_record_phase_1388a_without_public_claimability_activation() -> None:
    for path in (STATUS, PLANNING_INDEX, SEQUENCE_LOCK, WINDOW_GROUPING):
        text = _read(path)
        for token in REQUIRED_TOKENS:
            assert token in text, path
        assert "Phase 1389" in text, path
        assert "GO Phase 1389" in text, path
