from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TAXONOMY = ROOT / "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
LEDGER = ROOT / "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json"
AGENTS = ROOT / "AGENTS.md"
CLAUDE = ROOT / "CLAUDE.md"


RECENT_BATCHES = {
    "manual_batch_079_phase_1573e_1573i_retroactive",
    "manual_batch_080_phase_1573j_current",
}

RECENT_TEST_FILES = {
    "tests/test_h013_spectral_sigma_policy.py",
    "tests/test_phase_1568_fix2w_sigma_adversary_model.py",
    "tests/test_phase_1573e_cdl_sigma_01_ratification.py",
    "tests/test_phase_1573f_ccss_spectral_01_crypto_primitives.py",
    "tests/test_phase_1573g_ccss_spectral_01_beacon_emission.py",
    "tests/test_phase_1573h_ccss_spectral_01_full_test_suite.py",
    "tests/test_phase_1573i_cdl_sigma_01_adversary_model.py",
    "tests/test_phase_1573j_conversion_candidate_runtime.py",
    "tests/test_phase_1573k_obl040_rerun006.py",
    "tests/test_phase_1573l_obl039_obl040_closure.py",
    "tests/test_phase_1573m_full_suite_test_hardening.py",
    "tests/test_phase_1573n_preflight_history_wide_public_mirror_filter.py",
    "tests/test_phase_1573n_public_mirror_preparation.py",
    "tests/test_phase_1573o_ccss_privacy_claim_boundary.py",
    "tests/test_phase_1573p_ccss_metadata_leakage_audit.py",
    "tests/test_phase_1573q_ccss_side_channel_sim.py",
    "tests/test_phase_1573r_ccss_cover_batching_design.py",
    "tests/test_phase_1573s_contact_gate_policy_spec.py",
    "tests/test_phase_1573t_contact_gate_local_evaluator.py",
}

RUNTIME_FILES = {
    "ilc_core/network/d2d/spectral_beacon.py",
    "ilc_core/network/d2d/spectral_route_token.py",
    "ilc_core/network/d2d/spectral_sigma_policy.py",
    "ilc_core/ccss/contact_gate.py",
    "ilc_core/ccss/__init__.py",
}


def _annotations() -> list[dict[str, object]]:
    return json.loads(LEDGER.read_text())["annotations"]


def test_taxonomy_documents_live_legacy_references_edge() -> None:
    taxonomy = TAXONOMY.read_text()
    assert "### REFERENCES" in taxonomy
    assert "Legacy generic reference edge" in taxonomy
    assert "Prefer" in taxonomy and "REFERENCES_AUTHORITY" in taxonomy


def test_taxonomy_batch_numbering_matches_post_1573u_state() -> None:
    taxonomy = TAXONOMY.read_text()
    assert "Current last batch (as of Phase 1573ag prompt hardening)" in taxonomy
    assert "manual_batch_086_phase_1573ag_release_engineering_disposition_prompt" in taxonomy
    assert "manual_batch_087_<slug>" in taxonomy


def test_recent_fix38_batches_use_repo_path_not_candidate_id() -> None:
    recent = [
        annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch") in RECENT_BATCHES
    ]
    assert len(recent) == 64
    assert all("repo_path" in annotation for annotation in recent)
    assert all("candidate_id" not in annotation for annotation in recent)
    assert all("proposed_edges" not in annotation for annotation in recent)


def test_taxonomy_hardening_batch_registers_new_phase_files() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch")
        == "manual_batch_081_phase_1573u_fix1_taxonomy_hardening"
    }
    assert set(by_path) == {
        "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md",
        "tests/test_phase_1573u_node_classification_taxonomy.py",
        "docs/phases/phase_1573u_fix1_node_classification_taxonomy_hardening_walkthrough.md",
    }
    assert all("candidate_id" not in annotation for annotation in by_path.values())
    assert by_path[
        "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md"
    ]["recommended_graph_action"] == "load_bearing_artifact_added"
    assert by_path[
        "tests/test_phase_1573u_node_classification_taxonomy.py"
    ]["recommended_graph_action"] == "support_only"


def test_semantic_edge_enrichment_batch_registers_fix2_walkthrough() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch")
        == "manual_batch_082_phase_1573u_fix2_semantic_edge_enrichment"
    }
    assert set(by_path) == {
        "docs/phases/phase_1573u_fix2_fix38_semantic_edge_enrichment_walkthrough.md",
        "docs/specs/ilc_atlas_ledger_backlog_v0.1.md",
    }
    annotation = by_path[
        "docs/phases/phase_1573u_fix2_fix38_semantic_edge_enrichment_walkthrough.md"
    ]
    assert "candidate_id" not in annotation
    assert annotation["recommended_graph_action"] == "support_only"
    assert {
        "edge_type": "ATTESTATION",
        "target": "phase:phase_1573u_fix2_batch079080_semantic_edges_enriched",
    } in annotation["proposed_semantic_edges"]
    backlog = by_path["docs/specs/ilc_atlas_ledger_backlog_v0.1.md"]
    assert backlog["recommended_graph_action"] == "load_bearing_artifact_added"
    assert "catch-up batch namespace" in backlog["manual_read_summary"]


def test_batch_079_080_test_files_have_tests_edges_and_read_summaries() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch") in RECENT_BATCHES
    }
    assert RECENT_TEST_FILES <= set(by_path)
    for repo_path in RECENT_TEST_FILES:
        annotation = by_path[repo_path]
        targets = {
            edge["target"]
            for edge in annotation["proposed_semantic_edges"]
            if edge["edge_type"] == "TESTS"
        }
        assert targets, repo_path
        assert not annotation["manual_read_summary"].startswith("Registers ")


def test_batch_079_080_runtime_modules_have_implements_edges() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch") in RECENT_BATCHES
    }
    for repo_path in RUNTIME_FILES:
        annotation = by_path[repo_path]
        targets = {
            edge["target"]
            for edge in annotation["proposed_semantic_edges"]
            if edge["edge_type"] == "IMPLEMENTS"
        }
        assert targets, repo_path
        assert annotation["recommended_graph_action"] == "load_bearing_artifact_added"


def test_batch_079_080_authority_edges_use_canonical_targets_not_phase_tokens() -> None:
    forbidden_targets = {
        "ccss_spectral_01_full_test_suite_pass_phase_1573h",
        "ccss_spectral_01_route_token_spec_1573f",
        "cdl_sigma_01_ratified_phase_1573e",
        "public_mirror_pipeline_rehearsed_phase_1573n",
        "cdl_098_ratified_phase_1573a",
        "ccss_contact_gate_local_evaluator_committed_phase_1573t",
    }
    for annotation in _annotations():
        if annotation.get("annotation_batch") not in RECENT_BATCHES:
            continue
        for edge in annotation.get("proposed_authority_trace_edges", []):
            assert edge["target"] not in forbidden_targets


def test_batch_079_080_evidence_and_attestation_edges_are_present() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch") in RECENT_BATCHES
    }
    evidence = by_path[
        "docs/specs/ilc_cdl_sigma_01_ratification_evidence_1573e_v0.1.md"
    ]["proposed_semantic_edges"]
    assert {"edge_type": "EVIDENCES", "target": "cdl:CDL-SIGMA-01"} in evidence

    closure = by_path[
        "docs/specs/ilc_obl039_obl040_pre_rc_closure_record_1573l_v0.1.md"
    ]["proposed_semantic_edges"]
    assert {"edge_type": "EVIDENCES", "target": "obl:OBL-039"} in closure
    assert {"edge_type": "EVIDENCES", "target": "obl:OBL-040"} in closure

    walkthrough = by_path[
        "docs/phases/phase_1573t_ccss_contact_gate_local_rehearsal_walkthrough.md"
    ]["proposed_semantic_edges"]
    assert {
        "edge_type": "ATTESTATION",
        "target": "phase:ccss_contact_gate_local_evaluator_committed_phase_1573t",
    } in walkthrough


def test_guidance_distinguishes_new_schema_from_legacy_keys() -> None:
    taxonomy = TAXONOMY.read_text()
    agents = AGENTS.read_text()
    claude = CLAUDE.read_text()
    assert "legacy records may retain it" in taxonomy
    assert "do not use legacy `candidate_id` for new records" in agents
    claude_flat = " ".join(claude.split())
    assert "Historical ledger records may still contain legacy keys" in claude_flat
    assert "Do not copy those keys into new records" in claude_flat


def test_contact_gate_unverifiable_peer_hardening_batch_is_semantically_wired() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch")
        == "manual_batch_084_phase_1573u_fix4_contact_gate_unverifiable_peer_hardening"
    }
    assert set(by_path) == {
        "ilc_core/ccss/contact_gate.py",
        "ilc_core/network/d2d/http_gossip_transport_runtime.py",
        "tests/test_phase_1573t_contact_gate_local_evaluator.py",
        "tests/test_phase_1572_receiver_mldsa_verification.py",
        "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md",
        "tests/test_phase_1573u_node_classification_taxonomy.py",
        "docs/phases/phase_1573u_fix4_contact_gate_unverifiable_peer_hardening_walkthrough.md",
    }
    assert {
        "edge_type": "IMPLEMENTS",
        "target": "spec:CCSS-ContactGate",
    } in by_path["ilc_core/ccss/contact_gate.py"]["proposed_semantic_edges"]
    assert {
        "edge_type": "IMPLEMENTS",
        "target": "cdl:CDL-101",
    } in by_path[
        "ilc_core/network/d2d/http_gossip_transport_runtime.py"
    ]["proposed_semantic_edges"]
    assert {
        "edge_type": "TESTS",
        "target": "ilc_core/ccss/contact_gate.py",
    } in by_path[
        "tests/test_phase_1573t_contact_gate_local_evaluator.py"
    ]["proposed_semantic_edges"]
    assert {
        "edge_type": "TESTS",
        "target": "ilc_core/network/d2d/http_gossip_transport_runtime.py",
    } in by_path[
        "tests/test_phase_1572_receiver_mldsa_verification.py"
    ]["proposed_semantic_edges"]
    assert {
        "edge_type": "ATTESTATION",
        "target": "phase:phase_1573u_fix4_contact_gate_contacts_only_constant_time_scan",
    } in by_path[
        "docs/phases/phase_1573u_fix4_contact_gate_unverifiable_peer_hardening_walkthrough.md"
    ]["proposed_semantic_edges"]


def test_public_mirror_policy_batch_is_semantically_wired() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch")
        == "manual_batch_085_phase_1573u_fix5_public_mirror_policy"
    }
    assert set(by_path) == {
        "AGENTS.md",
        "CLAUDE.md",
        "docs/antigravity_tasks/README.md",
        "tools/validate_phase_prompt.py",
        "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1575_g10_block6_public_rc_gate_001.md",
        "tests/test_phase_1573u_fix5_public_mirror_policy.py",
        "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md",
        "tests/test_phase_1573u_node_classification_taxonomy.py",
        "docs/phases/phase_1573u_fix5_public_mirror_policy_walkthrough.md",
    }
    assert {
        "edge_type": "GOVERNS_CLASSIFICATION",
        "target": "policy:sanitized_public_mirror_derived_artifact",
    } in by_path["AGENTS.md"]["proposed_semantic_edges"]
    assert {
        "edge_type": "GOVERNS_CLASSIFICATION",
        "target": "policy:sanitized_public_mirror_derived_artifact",
    } in by_path["docs/antigravity_tasks/README.md"]["proposed_semantic_edges"]
    assert {
        "edge_type": "IMPLEMENTS",
        "target": "policy:phase_prompt_public_mirror_maintenance_required",
    } in by_path["tools/validate_phase_prompt.py"]["proposed_semantic_edges"]
    assert {
        "edge_type": "TESTS",
        "target": "tools/validate_phase_prompt.py",
    } in by_path["tests/test_phase_1573u_fix5_public_mirror_policy.py"][
        "proposed_semantic_edges"
    ]
    assert {
        "edge_type": "ATTESTATION",
        "target": "phase:phase_1573u_fix5_public_mirror_policy_committed",
    } in by_path[
        "docs/phases/phase_1573u_fix5_public_mirror_policy_walkthrough.md"
    ]["proposed_semantic_edges"]


def test_release_engineering_disposition_prompt_batch_is_semantically_wired() -> None:
    by_path = {
        annotation["repo_path"]: annotation
        for annotation in _annotations()
        if annotation.get("annotation_batch")
        == "manual_batch_086_phase_1573ag_release_engineering_disposition_prompt"
    }
    assert set(by_path) == {
        "docs/antigravity_tasks/antigravity_prompt__phase_1573ag_g8_release_engineering_track_disposition_audit.md",
        "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md",
        "tests/test_phase_1573ag_release_engineering_prompt.py",
        "docs/specs/ilc_atlas_graph_node_classification_and_edge_type_taxonomy_v0.1.md",
        "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json",
    }
    assert {
        "edge_type": "NEGATIVE_ASSERTS",
        "target": "nonclaim:no_release_engineering_track_merge",
    } in by_path[
        "docs/antigravity_tasks/antigravity_prompt__phase_1573ag_g8_release_engineering_track_disposition_audit.md"
    ]["proposed_semantic_edges"]
    assert {
        "edge_type": "REFERENCES_AUTHORITY",
        "target": "phase:release_engineering_track_disposition_audit_committed_phase_1573ag",
    } in by_path[
        "docs/antigravity_tasks/antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
    ]["proposed_semantic_edges"]
    assert {
        "edge_type": "TESTS",
        "target": "docs/antigravity_tasks/antigravity_prompt__phase_1573ag_g8_release_engineering_track_disposition_audit.md",
    } in by_path["tests/test_phase_1573ag_release_engineering_prompt.py"][
        "proposed_semantic_edges"
    ]
