import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SIM_JSON = ROOT / "out/sim_atlas_axiomatic_extraction_replay_1545p_fix26.json"
ATOM_QUEUE = ROOT / "out/atlas_research/genesis_atlas_atom_candidates_1545p_fix26.jsonl"
GRAPH = ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
REPORT = ROOT / "docs/sims/sim_atlas_axiomatic_extraction_replay_1545p_fix26_v0.1.md"
REVIEW = ROOT / "docs/specs/ilc_atlas_axiomatic_extraction_replay_review_1545p_fix26_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix26_axiomatic_extraction_replay_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


REQUIRED_TOKENS = {
    "whole_graph_axiomatic_extraction_replay_committed_phase_1545p_fix26",
    "truth_primitive_recipe_replay_full_repo_phase_1545p_fix26",
    "atlas_atom_candidate_queue_generated_phase_1545p_fix26",
    "atlas_axiomatic_negative_controls_retained_phase_1545p_fix26",
    "atlas_atoms_not_promoted_phase_1545p_fix26",
    "public_path_remains_blocked_phase_1545p_fix26",
}

REQUIRED_RECORD_KEYS = {
    "analysis_method",
    "atom_candidate_id",
    "authority_class",
    "confidence_class",
    "evidence_authority_refs",
    "evidence_span_hint",
    "evidence_text_hash",
    "nonclaim_boundary",
    "privacy_class",
    "queue_class",
    "recipe_id",
    "rejection_reason",
    "source_node_id",
    "source_path",
    "traversal_direction",
    "truth_primitive_recipe",
    "typed_trace_edge_role",
    "typed_trace_terminal_node_id",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _payload() -> dict:
    return json.loads(_read(SIM_JSON))


def _queue_rows() -> list[dict]:
    return [json.loads(line) for line in _read(ATOM_QUEUE).splitlines() if line.strip()]


def _authority_forward_terminals() -> set[str]:
    graph = json.loads(_read(GRAPH))
    adjacency: dict[str, set[str]] = {}
    node0 = "artifact:genesis_intent_attestation_init_authority_map"
    for edge in graph["edges"]:
        if edge["edge_type"] in {"GOVERNS", "ATTESTATION"}:
            adjacency.setdefault(edge["source"], set()).add(edge["target"])
    seen = {node0}
    queue = [node0]
    while queue:
        current = queue.pop(0)
        for target in sorted(adjacency.get(current, set())):
            if target not in seen:
                seen.add(target)
                queue.append(target)
    return seen


def test_fix26_outputs_and_tokens_present():
    payload = _payload()
    surfaces = [_read(REPORT), _read(REVIEW), _read(WALKTHROUGH), _read(STATUS), _read(PLANNING)]

    assert payload["status"] == "committed_research_only_axiomatic_replay"
    for token in REQUIRED_TOKENS:
        assert token in payload["tokens"]
        assert any(token in surface for surface in surfaces)


def test_atom_candidate_queue_has_required_schema_and_non_promotional_classes():
    payload = _payload()
    rows = _queue_rows()

    assert len(rows) == payload["atom_candidate_record_count"] == 20440
    assert payload["queue_counts"]["accepted_atom_candidates_for_review"] == 5482
    assert payload["queue_counts"]["deferred_low_confidence"] == 14958
    assert payload["queue_counts"]["rejected_overclaim_or_noisy"] == 0
    assert "CLASSIFIED_BY" not in payload["trace_role_counts"]

    for row in rows[:250]:
        assert set(row) == REQUIRED_RECORD_KEYS
        assert row["atom_candidate_id"].startswith("atlas-atom:")
        assert row["queue_class"] in {
            "accepted_atom_candidates_for_review",
            "deferred_low_confidence",
            "rejected_overclaim_or_noisy",
        }
        assert row["typed_trace_edge_role"] != "connected"
        assert row["nonclaim_boundary"] == "candidate_atom_for_review_only_no_promotion_no_authority_claim"

    for row in rows:
        if row["typed_trace_edge_role"] == "undeclared":
            assert row["queue_class"] == "deferred_low_confidence"
            assert row["typed_trace_terminal_node_id"] == "undeclared"


def test_calibration_gates_and_confusion_matrix_remain_clean():
    payload = _payload()
    matrix = payload["extraction_confusion_matrix"]
    gates = payload["calibration_gates"]

    assert matrix["TP"] == 64
    assert matrix["FP"] == 0
    assert matrix["FN"] == 0
    assert matrix["Uncertain"] == payload["queue_counts"]["deferred_low_confidence"]
    assert gates["fix19_golden_replay"]["missing_atom_count"] == 0
    assert gates["fix20_negative_controls"]["failed_count"] == 0
    assert gates["fix20_manual_spot_checks"]["failed_count"] == 0
    assert "held-out validation" in gates["held_out_validation_non_claim"]


def test_accepted_candidates_target_authority_forward_terminals_only():
    rows = _queue_rows()
    authority_terminals = _authority_forward_terminals()
    material_roots = {
        "artifact:full_repo_genesis_atlas_candidate_root_1545p_fix22",
        "artifact:generated_evidence_material_root_1545p_fix22",
        "artifact:genesis_private_local_material_root_1545p_fix22",
        "artifact:public_release_candidate_material_root_1545p_fix22",
    }

    accepted = [row for row in rows if row["queue_class"] == "accepted_atom_candidates_for_review"]
    assert accepted
    for row in accepted:
        terminal = row["typed_trace_terminal_node_id"]
        assert terminal in authority_terminals
        assert terminal not in material_roots


def test_denominator_lock_trace_orientation_and_python_ast_are_recorded():
    payload = _payload()

    assert payload["authority_bearing_denominator_lock"] == {
        "fix25_authority_bearing_node_count": 104,
        "phase26_denominator_action": "unchanged_no_node_metadata_reclassification",
    }
    assert payload["typed_trace_contract"]["candidate_edge_orientation"] == (
        "source_node_to_authority_or_classification_terminal"
    )
    assert payload["analysis_method_counts"]["python_ast_symbols_docstrings_comments"] == 2790
    assert payload["analysis_method_counts"]["direct_text"] == 17650
    assert payload["deferred_carry_forward"] == [
        "semantic_authority_bearing_node_count deferred to Fix29/Fix31.",
        "authority_document_file_node_count deferred to Fix29/Fix31.",
        "Support-edge backtrace orientation remains source_node_to_authority_terminal; support edges were not reversed.",
    ]


def test_docs_preserve_non_claims_and_no_placeholder_ellipses():
    combined = "\n".join([_read(REPORT), _read(REVIEW), _read(WALKTHROUGH)])
    normalized = " ".join(combined.split())

    assert "Accepted candidates are accepted for review only, not promoted." in combined
    assert "No canonical Genesis graph mutation occurred." in combined
    assert "No public RC activation occurred." in combined
    assert "No ADR or CDL mutation occurred." in combined
    assert "source to terminal" in normalized
    assert "..." not in combined
    assert "…" not in combined
