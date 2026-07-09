# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "docs/specs/ilc_signed_atlas_slice_manifest_executable_map_forward_plan_v0.1.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"


def test_signed_atlas_slice_manifest_forward_plan_records_executable_map_architecture() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "AtlasSliceManifest is the signed executable map" in text
    assert "Node and content blobs are separate material" in text
    assert "Identity" in text
    assert "Integrity" in text
    assert "Availability" in text
    assert "Authorization" in text
    assert "verify the manifest before fetching content" in text
    assert "3 VPS + 7-agent install rehearsal" in text


def test_signed_atlas_slice_manifest_forward_plan_is_routed_from_planning_index() -> None:
    text = PLANNING_INDEX.read_text(encoding="utf-8")

    assert "ilc_signed_atlas_slice_manifest_executable_map_forward_plan_v0.1.md" in text
    assert "1576-slice-schema" in text
    assert "1576-agent-bootstrap" in text
