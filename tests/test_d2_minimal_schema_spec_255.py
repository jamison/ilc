from __future__ import annotations

from pathlib import Path


SPEC_PATH = Path("docs/specs/ilc_d2_minimal_schema_specification_255_v0.1.md")

REQUIRED_SECTIONS = [
    "## 1. Purpose and scope",
    "## 2. Node schema specification (D2-01)",
    "## 3. Edge schema specification (D2-02)",
    "## 4. Epoch Record schema specification (D2-08)",
    "## 5. Canonical encoding rules",
    "## 6. Deferred schemas",
    "## 7. Non-goal boundaries",
]

NODE_FIELDS = [
    "`node_id`",
    "`payload`",
    "`primitive_type`",
    "`creator_agent_id`",
    "`epoch_created`",
    "`parent_edges`",
    "`signature`",
]

EDGE_FIELDS = [
    "`edge_id`",
    "`source_node_id`",
    "`target_node_id`",
    "`edge_type`",
    "`weight`",
    "`epoch_created`",
    "`creator_agent_id`",
]

EPOCH_FIELDS = [
    "`epoch_id`",
    "`participating_agents`",
    "`scoring_results`",
    "`reward_distribution`",
    "`finalization_hash`",
    "`previous_epoch_hash`",
    "`timestamp`",
]

DEFERRED_SCHEMAS = [
    "Shard",
    "Agent Profile",
    "Star Map Entry",
    "Subscription",
    "Inter-Agent Contract",
    "CapProof Bundle",
    "Governance Proposal",
    "Quorum Record",
]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_255_schema_spec_exists() -> None:
    assert SPEC_PATH.exists()


def test_phase_255_required_sections_present() -> None:
    text = _read(SPEC_PATH)
    for section in REQUIRED_SECTIONS:
        assert section in text


def test_phase_255_node_edge_epoch_required_fields_present() -> None:
    text = _read(SPEC_PATH)
    for token in NODE_FIELDS + EDGE_FIELDS + EPOCH_FIELDS:
        assert token in text


def test_phase_255_canonical_encoding_rules_include_ndjson_log_only_statement() -> None:
    text = _read(SPEC_PATH)
    assert "NDJSON is for logs only" in text


def test_phase_255_deferred_schema_list_is_explicit() -> None:
    text = _read(SPEC_PATH)
    for schema in DEFERRED_SCHEMAS:
        assert schema in text


def test_phase_255_no_ratification_language() -> None:
    text = _read(SPEC_PATH).lower()
    forbidden = [
        "is hereby ratified",
        "ratified in this phase",
        "this phase ratifies",
        "status changed to ratified",
    ]
    for token in forbidden:
        assert token not in text
