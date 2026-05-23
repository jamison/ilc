from __future__ import annotations

import ast
from pathlib import Path

from ilc_core.rc import cla_governance_status


ROOT = Path(__file__).resolve().parents[1]
CLA_PATH = ROOT / "docs/specs/ilc_cla_text_v1.md"
MODULE_PATH = ROOT / "ilc_core/rc/cla_governance_status.py"

EXPECTED_TOKENS = (
    "cla_text_finalized_phase_1444",
    "cla_governance_policy_committed_phase_1444",
    "cla_not_external_legal_opinion_phase_1444",
    "gap_7_cla_milestone_complete_phase_1444",
    "gap_7_provisional_patent_deferred_external_action_phase_1444",
    "gap_7_trademark_deferred_external_action_phase_1444",
    "gap_7_not_fully_closed_external_actions_pending_phase_1444",
)


def test_cla_text_exists_and_records_required_governance_scope() -> None:
    assert CLA_PATH.exists()
    text = CLA_PATH.read_text(encoding="utf-8")
    assert text.strip()

    lowered = text.lower()
    assert "Genesis-authority" in text
    assert "not external legal opinion" in lowered
    assert "AGPL-3.0-or-later" in text
    assert "patent" in lowered
    assert "public-source allowlist" in lowered
    assert "gap 7" in lowered
    assert "does not fully" in lowered


def test_phase_1444_governance_tokens_are_first_class_constants() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert source.startswith("# SPDX-License-Identifier: AGPL-3.0-or-later")

    for token in EXPECTED_TOKENS:
        assert token in source
        assert token in cla_governance_status.PHASE_1444_CLA_GOVERNANCE_TOKENS

    assert (
        cla_governance_status.CLA_NOT_EXTERNAL_LEGAL_OPINION_PHASE_1444_TOKEN
        == "cla_not_external_legal_opinion_phase_1444"
    )
    assert (
        cla_governance_status.GAP_7_NOT_FULLY_CLOSED_PHASE_1444_TOKEN
        == "gap_7_not_fully_closed_external_actions_pending_phase_1444"
    )
    assert (
        cla_governance_status.GAP_7_PROVISIONAL_PATENT_DEFERRED_PHASE_1444_TOKEN
        == "gap_7_provisional_patent_deferred_external_action_phase_1444"
    )
    assert (
        cla_governance_status.GAP_7_TRADEMARK_DEFERRED_PHASE_1444_TOKEN
        == "gap_7_trademark_deferred_external_action_phase_1444"
    )
    assert cla_governance_status.PHASE_1444_CLA_GOVERNANCE_TOKENS == EXPECTED_TOKENS


def test_phase_1444_governance_module_has_no_runtime_taboo_patterns() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert "import random" not in source
    assert "from random import" not in source
    assert not any(isinstance(node, ast.Assert) for node in ast.walk(tree))
    assert not any(
        isinstance(node, ast.Constant) and isinstance(node.value, float)
        for node in ast.walk(tree)
    )
