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


def test_signed_atlas_slice_manifest_forward_plan_has_four_axis_separation() -> None:
    """Verify the four axes are each present and not collapsed into each other."""
    text = PLAN.read_text(encoding="utf-8")

    # Each axis must be named as a distinct row in the separation table
    assert "| Identity |" in text
    assert "| Integrity |" in text
    assert "| Availability |" in text
    assert "| Authorization |" in text
    # Must not be collapsed
    assert "Must not be collapsed into" in text


def test_signed_atlas_slice_manifest_forward_plan_names_signer_authority_classes() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "genesis" in text
    assert "sidecar_maintainer" in text
    assert "collaborator_group" in text
    assert "private_capability_holder" in text


def test_signed_atlas_slice_manifest_forward_plan_has_dependency_chain() -> None:
    """Section 8 must record which lanes depend on which — not just a flat table."""
    text = PLAN.read_text(encoding="utf-8")

    assert "Depends on" in text
    assert "Dependency chain" in text
    assert "1576-slice-schema" in text
    assert "1576-slice-verifier" in text
    assert "1576-slice-materializer" in text


def test_signed_atlas_slice_manifest_forward_plan_names_pre_rc_foundation() -> None:
    """The Window 1576+ lanes must anchor to the pre-RC phases that lay their foundation."""
    text = PLAN.read_text(encoding="utf-8")

    assert "1573ao" in text
    assert "1573ap" in text
    # Pre-RC foundation section must be explicit
    assert "Pre-RC foundation" in text


def test_signed_atlas_slice_manifest_forward_plan_names_canonical_serialization() -> None:
    """Canonical serialization rules must be named — determinism is not assumed."""
    text = PLAN.read_text(encoding="utf-8")

    assert "canonical" in text.lower()
    assert "serialization" in text.lower()
    # Must be a commitment in the manifest, not a deferred afterthought
    assert "canonical serialization" in text.lower()


def test_signed_atlas_slice_manifest_forward_plan_covers_all_slice_modes() -> None:
    text = PLAN.read_text(encoding="utf-8")

    assert "Public Slice" in text
    assert "Private Slice" in text
    assert "Mixed Slice" in text
    # Private slices must gate on capability
    assert "capability" in text.lower()


def test_signed_atlas_slice_manifest_forward_plan_has_entry_criteria() -> None:
    """Window 1576 entry point must be specified — not left implicit."""
    text = PLAN.read_text(encoding="utf-8")

    assert "Entry criteria" in text
    assert "Phase 1575" in text
