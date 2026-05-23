# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


MANIFEST_PATH = Path("docs/specs/ilc_phase_commit_manifest_296_v0.1.json")


def load_phase_commit_manifest() -> dict[str, Any]:
    if not MANIFEST_PATH.exists():
        raise AssertionError(f"phase_commit_manifest_missing:{MANIFEST_PATH}")
    payload = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("phase_commit_manifest_invalid_payload")
    if payload.get("version") != "v0.1":
        raise AssertionError("phase_commit_manifest_invalid_version")
    phases = payload.get("phases")
    if not isinstance(phases, dict):
        raise AssertionError("phase_commit_manifest_missing_phases")
    return payload


def _git_commit_exists(commit_ref: str) -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", f"{commit_ref}^{{commit}}"],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _skip(reason: str) -> None:
    import pytest

    pytest.skip(reason)


def resolve_phase_commit_ref_or_skip(phase_id: str) -> str:
    payload = load_phase_commit_manifest()
    phases = payload["phases"]
    if phase_id not in phases:
        raise AssertionError(f"phase_commit_manifest_missing_phase:{phase_id}")

    entry = phases[phase_id]
    if not isinstance(entry, dict):
        raise AssertionError(f"phase_commit_manifest_invalid_entry:{phase_id}")

    commit_ref = entry.get("commit")
    status = entry.get("status")

    if not commit_ref:
        note = entry.get("note", "commit_unavailable")
        _skip(f"{phase_id}_commit_unavailable:{status}:{note}")

    if not isinstance(commit_ref, str):
        raise AssertionError(f"phase_commit_manifest_invalid_commit_type:{phase_id}")

    if not _git_commit_exists(commit_ref):
        _skip(f"{phase_id}_commit_not_present_in_local_history:{commit_ref}")

    return commit_ref
