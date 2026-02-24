from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v0.5.md")
REPORT_PATH = Path("docs/specs/ilc_integration_coherence_report_258_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _phase_commit_hash() -> str:
    result = subprocess.run(
        [
            "git",
            "log",
            "--format=%H",
            "--fixed-strings",
            "--grep",
            "docs(g8): phase 258 integration coherence and capsule v0.5",
            "-n",
            "1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    commit_hash = result.stdout.strip()
    if not commit_hash:
        pytest.skip("phase_258_commit_subject_not_found: commit-scoped assertion skipped")
    return commit_hash


def test_capsule_exists_and_supersedes_v0_4() -> None:
    text = _read(CAPSULE_PATH)
    assert CAPSULE_PATH.exists()
    assert "# ILC Antigravity Context Capsule v0.5" in text
    assert "Supersedes: `ilc_antigravity_context_capsule_v0.4.md`" in text


def test_capsule_contains_wallet_agnostic_signing_note() -> None:
    text = _read(CAPSULE_PATH)
    assert "Wallet-agnostic signing principle adopted." in text
    assert "pre-D2e-07 planning dependency" in text


def test_coherence_report_exists_with_all_required_sections() -> None:
    text = _read(REPORT_PATH)
    assert REPORT_PATH.exists()
    required = [
        "## 1. Scope",
        "## 2. Capsule alignment check (v0.5 versus 250-258 artifacts)",
        "## 3. Roadmap alignment check",
        "## 4. CDL log alignment check",
        "## 5. Cross-reference integrity",
        "## 6. Non-goal boundaries",
    ]
    for section in required:
        assert section in text


def test_coherence_report_confirms_ratified_security_cdls() -> None:
    text = _read(REPORT_PATH)
    assert "CDL-001 status = `ratified`" in text
    assert "CDL-002 status = `ratified`" in text
    assert "CDL-007 status = `ratified`" in text


def test_coherence_report_confirms_cdl_032_ratified() -> None:
    text = _read(REPORT_PATH)
    assert "CDL-032 status = `ratified`" in text


def test_coherence_report_confirms_cdl_019_open_unconditionally() -> None:
    text = _read(REPORT_PATH)
    assert "CDL-019 status = `open`" in text


def test_no_ilc_core_files_touched_in_phase_258_commit() -> None:
    commit_hash = _phase_commit_hash()
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=format:", commit_hash],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    touched_files = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    ilc_core_touches = [path for path in touched_files if path.startswith("ilc_core/")]
    assert ilc_core_touches == []
