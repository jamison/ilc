import hashlib
import json
from collections import defaultdict, deque
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "docs" / "phases" / "STATUS.md"
BASE = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix48.json"
FIX50 = ROOT / "out" / "atlas_research" / "genesis_atlas_enriched_candidate_fix50.json"
LEDGER = ROOT / "docs" / "specs" / "ilc_fix50_authority_edge_repair_ledger_v0.1.json"


NODE0 = "artifact:genesis_intent_attestation_init_authority_map"
FORBIDDEN_GOVERNS_TARGET_PREFIXES = ("repo:file:", "test:", "phase:", "sim:", "target:")
AUTHORITY_PREFIXES = ("adr:", "cdl:")
RULE_PREFIXES = ("policy:", "invariant:")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _new_edges() -> list[dict]:
    return [
        edge
        for edge in _load(FIX50)["edges"]
        if edge.get("annotation_phase") == "phase_1545p_fix50"
    ]


def _classifications() -> dict[str, str]:
    ledger = _load(LEDGER)
    return {
        node_id: entry["classification_tier"]
        for node_id, entry in ledger["authority_classifications"].items()
    }


def test_fix50_status_token_present() -> None:
    status = STATUS.read_text(encoding="utf-8")
    assert "fix50_complete" in status
    assert "public_path_remains_blocked_phase_1545p_fix50" in status


def test_fix50_candidate_exists_and_adds_edges_without_adding_nodes() -> None:
    base = _load(BASE)
    fix50 = _load(FIX50)
    assert len(fix50["nodes"]) == len(base["nodes"])
    assert len(fix50["edges"]) > len(base["edges"])
    assert fix50["fix50_generation_report"]["new_edge_count"] == len(_new_edges())
    assert fix50["fix50_generation_report"]["cdl_098_unconsumed_candidate_gap"] is True


def test_fix50_new_edges_have_deterministic_ids_and_candidate_metadata() -> None:
    for edge in _new_edges():
        expected = "edge:" + hashlib.sha256(
            f"{edge['source']}|{edge['edge_type']}|{edge['target']}".encode("utf-8")
        ).hexdigest()[:16]
        assert edge["edge_id"] == expected
        assert edge["candidate_status"] == "fix50_support_only_not_canonical"
        assert edge["annotation_method"].startswith("fix50_")
        assert edge["review_status"] == "candidate_only_not_authority_promotion"
        assert edge["signature_status"] == "unsigned_candidate_preimage"
        assert edge.get("rationale")


def test_fix50_governs_edges_respect_authority_scope() -> None:
    classifications = _classifications()
    for edge in _new_edges():
        if edge["edge_type"] != "GOVERNS":
            continue

        source = edge["source"]
        target = edge["target"]
        assert not target.startswith(FORBIDDEN_GOVERNS_TARGET_PREFIXES)

        if source == NODE0:
            assert target.startswith(AUTHORITY_PREFIXES)
            assert classifications[target].startswith("canonical_")
            continue

        assert source.startswith(AUTHORITY_PREFIXES)
        assert classifications[source].startswith("canonical_")
        assert target.startswith(AUTHORITY_PREFIXES + RULE_PREFIXES)
        if target.startswith(AUTHORITY_PREFIXES):
            assert classifications[target].startswith("canonical_")
        else:
            assert target.startswith(RULE_PREFIXES)


def test_fix50_governs_does_not_target_lifecycle_or_open_nodes() -> None:
    classifications = _classifications()
    blocked = {"lifecycle_snapshot", "proposed_open", "source_derived_duplicate"}
    for edge in _new_edges():
        if edge["edge_type"] == "GOVERNS" and edge["target"] in classifications:
            assert classifications[edge["target"]] not in blocked


def test_fix50_does_not_recreate_fix38_source_tree_hub_edges() -> None:
    hub = "artifact:genesis_source_tree_manifest_candidate_1545p_fix38"
    for edge in _new_edges():
        assert not (
            edge["edge_type"] == "SOURCE_TREE_MEMBER"
            and (edge["source"] == hub or edge["target"] == hub)
        )


def test_fix50_new_governs_edges_are_acyclic() -> None:
    graph: dict[str, set[str]] = defaultdict(set)
    for edge in _new_edges():
        if edge["edge_type"] == "GOVERNS":
            graph[edge["source"]].add(edge["target"])

    for start in graph:
        queue = deque(graph[start])
        seen: set[str] = set()
        while queue:
            node = queue.popleft()
            assert node != start
            if node in seen:
                continue
            seen.add(node)
            queue.extend(graph.get(node, ()))
