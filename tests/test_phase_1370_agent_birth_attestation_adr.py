from __future__ import annotations

from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

ADR = ROOT / "docs/adr/ADR_0038_Agent_Birth_Attestation.md"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1370_g8_agent_birth_attestation_adr.md"
)
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1370_agent_birth_attestation_adr_walkthrough.md"

REQUIRED_TOKENS = (
    "agent_birth_attestation_adr_0038_committed_phase_1370",
    "adr_0038_agent_birth_attestation_genesis_rooted",
    "adr_0038_non_custodial_default_required",
    "adr_0038_no_private_graph_content_as_entropy",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1370_prompt_remains_schema_valid() -> None:
    assert validate(PROMPT) == []


def test_adr_0038_carries_required_tokens_and_core_requirements() -> None:
    text = read(ADR)

    for token in REQUIRED_TOKENS:
        assert token in text

    required_phrases = (
        "Genesis-rooted identity-origin proof",
        "signed Genesis/Atlas lineage anchor",
        "ADR-0037",
        "CDL-042",
        "CDL-069",
        "CDL-090",
        "non-custodial",
        "Private graph content must not become identity seed entropy",
        "interactive",
        "agent_mode",
        "designated secure output target",
        "Stdout",
        "not itself create an identity artifact",
    )
    for phrase in required_phrases:
        assert phrase in text


def test_adr_0038_forbids_seed_material_in_public_or_log_outputs() -> None:
    text = read(ADR)

    for forbidden_output in (
        "stdout",
        "logs",
        "walkthroughs",
        "STATUS entries",
        "docs",
        "chat transcripts",
        "terminal scrollback",
        "environment dumps",
    ):
        assert forbidden_output in text

    assert "The record must contain no secret seed" in text
    assert "identity-seed or recovery material from private graph content is not" in text


def test_phase_1370_frontier_docs_record_completion_and_next_phase() -> None:
    for path in (PLANNING_INDEX, STATUS, WALKTHROUGH):
        text = read(path)
        for token in REQUIRED_TOKENS:
            assert token in text
        assert "Phase 1371" in text
        assert "CDL-090" in text

    walkthrough = read(WALKTHROUGH)
    assert "identity_artifact_creation_not_authorized_phase_1370" in walkthrough
    assert "production_activation_not_authorized_phase_1370" in walkthrough
    assert "graph_delta=support_only" in walkthrough
