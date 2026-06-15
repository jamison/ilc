import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "out/sim_atlas_candidate_reducer_v04_v05_1545p_fix31.json"
VARIANTS = ROOT / "out/atlas_research/genesis_atlas_v04_v05_candidate_variants_1545p_fix31.json"
BATCH_PLAN = ROOT / "out/atlas_research/genesis_atlas_public_private_batch_plan_1545p_fix31.json"
REPORT = ROOT / "docs/sims/sim_atlas_candidate_reducer_v04_v05_1545p_fix31_v0.1.md"
PACKET = ROOT / "docs/specs/ilc_genesis_atlas_v04_v05_candidate_decision_packet_1545p_fix31_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix31_candidate_reducer_v04_v05_walkthrough.md"


REQUIRED_TOKENS = {
    "atlas_candidate_reducer_v04_v05_packet_committed_phase_1545p_fix31",
    "atlas_v04_core_plus_support_variant_recorded_phase_1545p_fix31",
    "atlas_v05_full_repo_optimized_variant_recorded_phase_1545p_fix31",
    "atlas_public_private_signing_batch_plan_recorded_phase_1545p_fix31",
    "phase1573_signing_input_requires_human_scope_selection_phase_1545p_fix31",
    "public_path_remains_blocked_phase_1545p_fix31",
}


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_fix31_summary_and_tokens():
    payload = _json(SUMMARY)
    combined = REPORT.read_text(encoding="utf-8") + WALKTHROUGH.read_text(encoding="utf-8")

    assert payload["status"] == "pass"
    assert payload["phase"] == "1545p-Fix31"
    assert payload["sim_id"] == "SIM-ATLAS-CANDIDATE-REDUCER-01"
    assert REQUIRED_TOKENS.issubset(set(payload["output_tokens"]))
    for token in REQUIRED_TOKENS:
        assert token in combined


def test_fix31_variants_preserve_phase1573_scope_boundary():
    payload = _json(VARIANTS)
    variants = {variant["variant_id"]: variant for variant in payload["variants"]}

    assert set(variants) == {
        "v04_core_only_fix18_preserved",
        "v04_core_plus_full_repo_support",
        "v05_full_repo_optimized_candidate",
        "maximal_research_not_for_signing",
    }
    assert variants["v04_core_only_fix18_preserved"]["node_count"] == 57
    assert variants["v04_core_only_fix18_preserved"]["edge_count"] == 80
    assert (
        variants["v04_core_only_fix18_preserved"]["signing_compatibility_verdict"]
        == "phase1573_current_guidance_compatible_with_fix18_only"
    )
    assert (
        variants["v04_core_plus_full_repo_support"]["signing_compatibility_verdict"]
        == "phase1573_requires_guidance_patch_for_v04_core_plus_support"
    )
    assert (
        variants["v05_full_repo_optimized_candidate"]["signing_compatibility_verdict"]
        == "phase1573_requires_new_scope_or_later_v05_for_full_repo_optimized"
    )


def test_fix31_proof_classes_and_batch_records():
    variants = {variant["variant_id"]: variant for variant in _json(VARIANTS)["variants"]}
    batch = _json(BATCH_PLAN)
    records = batch["signing_batches"]["genesis_core_fix18"]["records"]

    assert len(records) == 57
    assert all(record["signing_batch_classification"] == "genesis_core" for record in records)
    assert all(
        record["proof_class"] == "merkle_plus_typed_authority_eligibility_path"
        for record in records
    )
    assert any(
        record["genesis_rootedness_proof"] == "axiomatic_exception_declared"
        for record in records
    )
    assert variants["v05_full_repo_optimized_candidate"]["hashed_repo_material_only_count"] > 0
    assert variants["v05_full_repo_optimized_candidate"][
        "directed_view_not_yet_contractualized_count"
    ] > 0


def test_fix31_decision_packet_non_claims_and_human_gate():
    payload = _json(VARIANTS)
    decision = payload["signing_scope_decision"]
    combined = REPORT.read_text(encoding="utf-8") + PACKET.read_text(encoding="utf-8")

    assert decision["v04_signing_input"] == "fix18_core_only"
    assert decision["v05_signing_input"] == "deferred"
    assert decision["scope_decision_requires_human_authorization"] is True
    assert "This packet is the decision packet, not the signing decision." in combined
    assert "No Genesis v0.4 signing" in combined
    assert "No Genesis v0.5 signing" in combined
    assert "not a semantically rooted Atlas node" in combined


def test_fix31_docs_have_no_placeholder_ellipses():
    combined = REPORT.read_text(encoding="utf-8") + PACKET.read_text(encoding="utf-8") + WALKTHROUGH.read_text(encoding="utf-8")

    assert "..." not in combined
    assert "…" not in combined
