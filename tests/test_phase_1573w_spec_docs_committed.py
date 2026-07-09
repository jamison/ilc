from __future__ import annotations

from pathlib import Path


PIPELINE_SPEC = Path("docs/specs/ilc_atlas_slice_manifest_build_pipeline_v0.1.md")
NAMING_POLICY = Path("docs/specs/ilc_graph_projection_naming_policy_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")


def test_phase_1573w_spec_files_exist_and_contain_required_sections() -> None:
    pipeline = PIPELINE_SPEC.read_text(encoding="utf-8")
    policy = NAMING_POLICY.read_text(encoding="utf-8")

    assert "ILC AtlasSliceManifest Build Pipeline v0.1" in pipeline
    assert "## 4. CLI Pipeline Contract" in pipeline
    assert "## 5. Layered Download Architecture" in pipeline
    assert "ILC Graph Projection Naming Policy v0.1" in policy
    assert "## 2. Canonical Top-Level Buckets" in policy
    assert "## 3. ProjectionPolicyNode" in policy


def test_layered_download_tier_table_is_present() -> None:
    pipeline = PIPELINE_SPEC.read_text(encoding="utf-8")

    assert "| User tier | Projection set | Intended user | Contents | Authority boundary |" in pipeline
    assert "Tier 0" in pipeline
    assert "`genesis_core_star_map`" in pipeline
    assert "Tier 1" in pipeline
    assert "`public_protocol_graph` plus `support_candidate_graph`" in pipeline
    assert "Tier 2" in pipeline
    assert "`excluded_private_material`" in pipeline
    assert "not LMDB `tier`" in pipeline


def test_projection_policy_node_definition_is_present() -> None:
    policy = NAMING_POLICY.read_text(encoding="utf-8")

    assert "`ProjectionPolicyNode` is an ADR-0020-style public knowledge node" in policy
    assert '"node_type": "ProjectionPolicyNode"' in policy
    assert '"authority": "cdl:CDL-098"' in policy
    assert "The policy node is expected to carry a `GOVERNS` edge" in policy


def test_private_layer_policy_is_referenced() -> None:
    pipeline = PIPELINE_SPEC.read_text(encoding="utf-8")
    policy = NAMING_POLICY.read_text(encoding="utf-8")

    assert "docs/specs/ilc_private_layer_policy_v0.1.md" in pipeline
    assert "Not public-signable by Genesis; owner/local only" in policy
    assert "A sub-label cannot upgrade private or review-required material" in policy


def test_phase_1573w_status_tokens_present() -> None:
    status = STATUS.read_text(encoding="utf-8")

    assert "atlas_slice_manifest_build_pipeline_spec_committed_phase_1573w" in status
    assert "graph_projection_naming_policy_spec_committed_phase_1573w" in status
    assert "public_path_remains_blocked_phase_1573w" in status
