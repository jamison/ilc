import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADR_0020 = ROOT / "docs/adr/ADR_0020_Knowledge_Node_First_Design_Principle.md"
REVIEW = ROOT / "docs/sims/sim_spectral_04/adr_0020_acceptance_review_1157_v0.1.md"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.2_candidate.json"


def test_adr_0020_status_is_accepted() -> None:
    text = ADR_0020.read_text(encoding="utf-8")
    assert "**Status:** Accepted" in text
    assert "adr_0020_accepted_phase_1157" in text


def test_adr_0020_review_records_scope_boundary() -> None:
    text = REVIEW.read_text(encoding="utf-8")
    assert "ADR-0020 is accepted" in text
    assert "does not immediately" in text
    assert "migrate all governance constants" in text
    assert "adr_0020_acceptance_review_priority_before_tier3_embedding_linkage" in text


def test_adr_0020_present_in_unsigned_v02_candidate() -> None:
    data = json.loads(STAR_MAP.read_text(encoding="utf-8"))
    node_ids = {node["candidate_id"] for node in data["nodes"]}
    assert "adr:0020_knowledge_node_first_design_principle" in node_ids
    assert len(node_ids) == 41
