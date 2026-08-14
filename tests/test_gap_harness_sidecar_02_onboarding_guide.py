# SPDX-License-Identifier: AGPL-3.0-only
"""Artifact tests for GAP-HARNESS-SIDECAR-02."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/specs/ilc_agent_onboarding_guide_GAP_HARNESS_SIDECAR_02_v0.1.md"
AUDIT = ROOT / "docs/specs/ilc_private_harness_cli_audit_GAP_HARNESS_SIDECAR_02_v0.1.md"
PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_gap_harness_sidecar_02_g10_agent_onboarding_guide.md"
)
STATUS = ROOT / "docs/phases/STATUS.md"
MAIN = ROOT / "ilc_core/cli/main.py"
HARNESS_DIR = ROOT / "ilc_core/harness"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_prompt_uses_actual_keygen_token_not_stale_hotkey_token() -> None:
    prompt = _read(PROMPT)
    assert "agent_keygen_cli_committed_GAP_AGENT_KEYGEN_00" in prompt
    assert "agent_hotkey_cli_committed_GAP_AGENT_KEYGEN_00" not in prompt


def test_guide_has_required_onboarding_sections() -> None:
    guide = _read(GUIDE)
    for section in (
        "Prerequisites",
        "Identity Initialization",
        "Hotkey Generation",
        "Identity State Check",
        "Balance Check",
        "First Truth Submission",
        "Receipt Verification",
        "Limitations And Blockers",
    ):
        assert f"## " in guide and section in guide


def test_guide_uses_real_cli_surface_names() -> None:
    guide = _read(GUIDE)
    main = _read(MAIN)
    for command in ("identity", "agent", "balance", "submit", "verify"):
        assert f'if command == "{command}"' in main
    assert "ilc agent keygen" in guide
    assert "ilc --graph-state ./.ilc-local/state/graph.json identity init" in guide
    assert "ilc --graph-state ./.ilc-local/state/graph.json submit" in guide
    assert "ilc value-action" not in guide
    assert "ilc hotkey generate" not in guide


def test_guide_flags_prototype_and_gated_surfaces() -> None:
    guide = _read(GUIDE)
    assert 'report_mode: "prototype_compat"' in guide
    assert "NOT YET AVAILABLE FOR AGENT USE" in guide
    assert "Does not by itself prove the hotkey is authorized for an AgentID" in guide
    assert "`ILC_TRUTH_GRAPH_STORE_PATH` is not configured" in guide
    assert "`ilc_core/harness/` modules | Private `PUBLIC_RC_EXCLUDE` scaffolds" in guide


def test_private_harness_audit_covers_every_python_harness_file() -> None:
    audit = _read(AUDIT)
    harness_files = sorted(
        path.relative_to(ROOT).as_posix()
        for path in HARNESS_DIR.glob("*.py")
        if path.name != "__pycache__"
    )
    assert harness_files
    for repo_path in harness_files:
        assert f"`{repo_path}`" in audit


def test_private_harness_audit_preserves_no_promotion_boundary() -> None:
    audit = _read(AUDIT)
    assert "not a promotion decision" in audit
    assert "`PUBLIC_RC_EXCLUDE` infrastructure" in audit
    assert "cannot be cited as public RC runtime capability" in audit
    assert "LOCAL_IMMUTABLE_STORE_NOT_PRODUCTION = True" in audit
    assert "IDLE_CAPACITY_SCHEDULER_NOT_ACTIVATED = True" in audit
    assert "MAINTENANCE_TASK_EXECUTOR_NOT_ACTIVATED = True" in audit


def test_no_fictional_value_action_command_in_phase_artifacts() -> None:
    combined = "\n".join([_read(GUIDE), _read(AUDIT)])
    forbidden_patterns = (
        r"\bilc value-action\b",
        r"\bilc hotkey generate\b",
        r"\bpython -m ilc_core\s+(identity|agent|balance|submit|verify)\b",
    )
    for pattern in forbidden_patterns:
        assert re.search(pattern, combined) is None


def test_status_token_is_recorded() -> None:
    assert "agent_onboarding_guide_committed_GAP_HARNESS_SIDECAR_02" in _read(STATUS)
