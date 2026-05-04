import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BATCH_REVIEW = ROOT / "docs/sims/sim_spectral_04/adr_batch_acceptance_review_1158_v0.1.md"
STAR_MAP = ROOT / "out/genesis_core_star_map_v0.2_candidate.json"

ADR_STATUS_FILES = {
    "adr_0012_accepted_phase_1158": ROOT
    / "docs/adr/ADR_0012_ECU_ILC_Graph_Coupling_and_Anti_Reflexivity.md",
    "adr_0022_accepted_phase_1158": ROOT
    / "docs/adr/ADR_0022_Local_First_Private_Use_and_Publication_Bound_Economics.md",
    "adr_0023_accepted_phase_1158_scoped_quality_signal_architecture": ROOT
    / "docs/adr/ADR_0023_Multi_Layer_Quality_Signal_Architecture.md",
    "adr_0008_accepted_phase_1158": ROOT
    / "docs/adr/ADR_0008_Node_Usefulness_vs_Governance_Weight_and_Genesis_Dilution.md",
}

EXPECTED_NODES = {
    "adr:0012_ecu_ilc_graph_coupling_anti_reflexivity",
    "adr:0022_local_first_private_publication_bound_economics",
    "adr:0023_multi_layer_quality_signal_architecture",
    "adr:0008_node_usefulness_governance_weight_genesis_dilution",
}


def test_phase_1158_adr_statuses_and_tokens() -> None:
    for token, path in ADR_STATUS_FILES.items():
        text = path.read_text(encoding="utf-8")
        assert "Status: Accepted" in text or "**Status:** Accepted" in text
        assert token in text


def test_phase_1158_batch_review_records_all_verdicts() -> None:
    text = BATCH_REVIEW.read_text(encoding="utf-8")
    for token in ADR_STATUS_FILES:
        assert token in text
    assert "ADR-0023" in text
    assert "ACCEPTED SCOPED" in text
    assert "No ADR in this batch accepts final runtime retuning" in text


def test_phase_1158_nodes_present_in_unsigned_v02_candidate() -> None:
    data = json.loads(STAR_MAP.read_text(encoding="utf-8"))
    node_ids = {node["candidate_id"] for node in data["nodes"]}
    assert EXPECTED_NODES.issubset(node_ids)
    assert len(node_ids) == 41
    assert len(data["edges"]) == 73
