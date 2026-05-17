from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1371_g8_identity_bootstrap_cdl_opening.md"
)
REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
OPENING = ROOT / "docs/specs/ilc_cdl_090_identity_bootstrap_opening_1371_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1371_identity_bootstrap_cdl_opening_walkthrough.md"

REQUIRED_TOKENS = (
    "cdl_090_identity_bootstrap_opened_phase_1371",
    "cdl_090_not_ratified_phase_1371",
    "cdl_090_non_custodial_seed_path_candidate_scope_phase_1371",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1371_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_cdl_090_register_row_is_open_only_and_cdl_088_absent() -> None:
    register = read(REGISTER)

    rows = [line for line in register.splitlines() if line.startswith("| CDL-090 |")]
    assert len(rows) == 1
    row = rows[0]

    assert "| open |" in row
    assert "docs/specs/ilc_cdl_090_identity_bootstrap_opening_1371_v0.1.md" in row
    assert "prelock_status: deferred_to_phase_1372" in row
    assert "ratification_status: not_ratified_phase_1371" in row
    assert "cdl_088_status: unopened_reserved_for_phase_1374" in row
    for token in REQUIRED_TOKENS:
        assert token in row

    assert "| CDL-089 |" in register
    assert "blocking_authority_ratified_phase_1364.v0.1" in register
    assert not any(line.startswith("| CDL-088 |") for line in register.splitlines())


def test_opening_document_carries_candidate_scope_and_non_claims() -> None:
    text = read(OPENING)

    for token in REQUIRED_TOKENS:
        assert token in text

    required_phrases = (
        "**Status:** OPEN",
        "not prelocked and not ratified",
        "Non-custodial identity-seed path",
        "interactive",
        "agent-mode",
        "No-stdout-fallback rule",
        "Private-graph entropy exclusion",
        "ADR-0038",
        "ADR-0037",
        "CDL-042",
        "CDL-069",
        "CDL-048",
        "CDL-088",
        "Phase 1386",
    )
    for phrase in required_phrases:
        assert phrase in text

    forbidden_claims = (
        "CDL-090 ratification",
        "CDL-090 prelock",
        "CDL-088 opening",
        "Identity artifact creation",
        "Secret generation or secret-store write authorization",
        "Public identity activation",
        "Public claimability activation",
    )
    for claim in forbidden_claims:
        assert claim in text


def test_phase_1371_support_docs_record_completion_next_phase_and_no_runtime() -> None:
    for path in (STATUS, PLANNING_INDEX, WALKTHROUGH):
        text = read(path)
        for token in REQUIRED_TOKENS:
            assert token in text
        assert "Phase 1372" in text
        assert "CDL-090" in text

    status = read(STATUS)
    assert "580bf148" in status
    assert "CDL-090 open; Phase 1372 deliberation/prelock next (SENSITIVE)" in status

    walkthrough = read(WALKTHROUGH)
    assert "cdl_088_not_opened_phase_1371" in walkthrough
    assert "identity_artifact_creation_not_authorized_phase_1371" in walkthrough
    assert "runtime_not_modified_phase_1371" in walkthrough
    assert "graph_delta=load_bearing_artifact_changed" in walkthrough
