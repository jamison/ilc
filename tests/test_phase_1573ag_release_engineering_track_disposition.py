from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = ROOT / "docs/specs/ilc_release_engineering_track_disposition_1573ag_v0.1.md"
PHASE_1574_PROMPT = (
    ROOT
    / "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)


def _git_changed_files() -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "main...release-engineering-track"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def _disposition_rows() -> dict[str, str]:
    text = DISPOSITION.read_text(encoding="utf-8")
    rows: dict[str, str] = {}
    for line in text.splitlines():
        if not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        path = cells[0].strip("`")
        classification = cells[2].strip("`")
        rows[path] = classification
    return rows


def test_disposition_document_exists_and_lists_all_branch_files() -> None:
    assert DISPOSITION.exists()
    rows = _disposition_rows()
    missing = sorted(set(_git_changed_files()) - set(rows))
    assert missing == []


def test_disposition_classifications_are_closed_enum() -> None:
    allowed = {"superseded", "salvage_candidate", "reject"}
    rows = _disposition_rows()
    assert rows
    assert set(rows.values()) <= allowed


def test_required_superseded_public_export_artifacts() -> None:
    rows = _disposition_rows()
    assert rows["tools/public_export_sync.py"] == "superseded"
    assert rows["config/public_surface_manifest_v0.1.json"] == "superseded"


def test_disposition_keeps_release_engineering_track_quarantined() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    required = [
        "release-engineering-track` remains quarantined",
        "No wholesale merge is authorized",
        "No cherry-pick from the branch is authorized",
        "No runtime change from the branch is accepted",
        "does not merge `release-engineering-track`",
        "push to GitHub",
    ]
    for phrase in required:
        assert phrase in text


def test_phase_1574_requires_release_engineering_disposition_token() -> None:
    text = PHASE_1574_PROMPT.read_text(encoding="utf-8")
    token = "release_engineering_track_disposition_audit_committed_phase_1573ag"
    assert re.search(re.escape(token), text)

