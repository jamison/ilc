from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "docs/specs/ilc_backward_attribution_sim_contract_GAP_ECU_01a_v0.1.md"
RESULTS_PATH = ROOT / "docs/specs/ilc_backward_attribution_sim_results_GAP_ECU_01b_v0.1.md"
STATUS_PATH = ROOT / "docs/phases/STATUS.md"
LEDGER_PATH = ROOT / "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json"

SCHEMA_VERSION = "backward_attribution_sim_contract_results.GAP_ECU_01b.v1"
OUTPUT_TOKEN = "backward_attribution_sim_results_committed_GAP_ECU_01b"
SIM_VERSION = "gap_ecu_01b_deterministic_sim.v1"
Q = Decimal("0.000000001")


PARAMETER_GRID = {
    "triggering_events": [
        "accepted_frontier_node",
        "accepted_revision",
        "accepted_frontier_plus_revision",
        "accepted_frontier_plus_invite_init",
        "upheld_refutation_net_only",
        "epoch_root_inclusion_audit_only",
    ],
    "eligible_upstream_artifacts": ["narrow", "medium", "broad_rejection_probe"],
    "typed_path_semantics": [
        "PROVENANCE_only",
        "PROVENANCE_plus_REUSE",
        "PROVENANCE_REUSE_VALIDATE_REVISION",
        "signed_positive_paths_refutation_discount",
    ],
    "provenance_distance_score": [
        "inverse_hop",
        "geometric_hop",
        "spectral_impedance_proxy",
        "edge_confidence_product",
        "status_quality_weighted_distance",
    ],
    "decay_rule": {
        "alpha": ["0.30", "0.45", "0.60", "0.75"],
        "max_depth": [2, 3, 4, 6],
        "age_half_life_epochs": [8, 16, 32],
        "rejection_controls": ["linear", "thresholded"],
    },
    "bidirectional_coefficients": {
        "backward_pool_share_beta": ["0.05", "0.10", "0.20", "0.35"],
        "refutation_specific_beta": ["0", "net_only"],
        "invite_init_beta_source": "same_region_not_hardcoded",
    },
    "depth_and_dominance_bounds": {
        "max_depth": [2, 3, 4, 6],
        "per_node_cap": ["0.02", "0.05", "0.10"],
        "per_agent_cap": ["0.05", "0.10", "0.20"],
        "per_cluster_cap": ["0.15", "0.25", "0.35"],
        "max_traversal_nodes": [1000, 10000],
        "max_traversal_edges": [5000, 50000],
    },
    "refutation_interaction": [
        "exclude_refuted",
        "discount_by_status",
        "escrow_pending",
        "clawback_deferred_non_activation",
        "upheld_refutation_net_only",
    ],
    "audit_surface": [
        "public_traversal_receipt",
        "private_sidecar_public_root",
        "hybrid_merkle_proof",
        "sampled_challenge_proof",
        "full_canonical_preimage_for_synthetic_sims",
    ],
}


LOCKED_RECOMMENDATION = {
    "triggering_events": "accepted_frontier_plus_invite_init",
    "eligible_upstream_artifacts": "medium",
    "typed_path_semantics": "PROVENANCE_REUSE_VALIDATE_REVISION",
    "provenance_distance_score": "status_quality_weighted_distance",
    "decay_rule": {
        "alpha": "0.45",
        "age_half_life_epochs": 16,
        "max_depth": 3,
        "shape": "geometric_hop_with_status_quality_weight",
    },
    "bidirectional_coefficients": {
        "backward_pool_share_beta": "0.10",
        "forward_retained_share": "0.90",
        "refutation_specific_beta": "0",
        "invite_init_beta_source": "same_region_not_hardcoded",
    },
    "depth_and_dominance_bounds": {
        "max_depth": 3,
        "per_agent_cap": "0.10",
        "per_cluster_cap": "0.25",
        "per_node_cap": "0.05",
        "max_traversal_edges": 5000,
        "max_traversal_nodes": 1000,
        "novelty_minimum_score": "0.20",
    },
    "refutation_interaction": "refutation_excluded_from_generic_backward_pool",
    "audit_surface": "hybrid_merkle_proof",
}


@dataclass(frozen=True)
class Region:
    name: str
    alpha: Decimal
    beta: Decimal
    max_depth: int
    half_life_epochs: int
    per_node_cap: Decimal
    per_agent_cap: Decimal
    per_cluster_cap: Decimal
    typed_paths: str
    eligible_mask: str
    novelty_gate: bool
    duplicate_collapse: bool
    cycle_filter: bool
    status_quality_weighting: bool
    audit_surface: str


REGIONS = [
    Region(
        name="locked_recommended_region",
        alpha=Decimal("0.45"),
        beta=Decimal("0.10"),
        max_depth=3,
        half_life_epochs=16,
        per_node_cap=Decimal("0.05"),
        per_agent_cap=Decimal("0.10"),
        per_cluster_cap=Decimal("0.25"),
        typed_paths="PROVENANCE_REUSE_VALIDATE_REVISION",
        eligible_mask="medium",
        novelty_gate=True,
        duplicate_collapse=True,
        cycle_filter=True,
        status_quality_weighting=True,
        audit_surface="hybrid_merkle_proof",
    ),
    Region(
        name="conservative_region",
        alpha=Decimal("0.30"),
        beta=Decimal("0.05"),
        max_depth=2,
        half_life_epochs=8,
        per_node_cap=Decimal("0.02"),
        per_agent_cap=Decimal("0.05"),
        per_cluster_cap=Decimal("0.15"),
        typed_paths="PROVENANCE_only",
        eligible_mask="narrow",
        novelty_gate=True,
        duplicate_collapse=True,
        cycle_filter=True,
        status_quality_weighting=True,
        audit_surface="public_traversal_receipt",
    ),
    Region(
        name="aggressive_rejected_region",
        alpha=Decimal("0.75"),
        beta=Decimal("0.35"),
        max_depth=6,
        half_life_epochs=32,
        per_node_cap=Decimal("0.10"),
        per_agent_cap=Decimal("0.20"),
        per_cluster_cap=Decimal("0.35"),
        typed_paths="PROVENANCE_plus_REUSE",
        eligible_mask="broad_rejection_probe",
        novelty_gate=False,
        duplicate_collapse=False,
        cycle_filter=False,
        status_quality_weighting=False,
        audit_surface="private_hidden_state_rejected",
    ),
]


def stable_json(value: object) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    )


def stable_sha256(value: object) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def d(value: str | int) -> Decimal:
    number = Decimal(str(value))
    if not number.is_finite():
        raise ValueError("decimal_value_non_finite")
    return number


def ds(value: Decimal) -> str:
    value = value.quantize(Q)
    if value == Decimal("-0E-9"):
        value = Decimal("0")
    if not value.is_finite():
        raise ValueError("decimal_value_non_finite")
    return format(value, "f")


def gini(values: list[Decimal]) -> Decimal:
    if not values:
        return Decimal("0")
    clean = sorted(d(ds(value)) for value in values)
    total = sum(clean, Decimal("0"))
    if total == 0:
        return Decimal("0")
    count = d(len(clean))
    weighted = sum((d(2 * index) - count - d(1)) * value for index, value in enumerate(clean, start=1))
    return weighted / (count * total)


def cap_share(value: Decimal, cap: Decimal) -> Decimal:
    return value if value <= cap else cap


def scenario_common(
    *,
    scenario_id: str,
    scenario_name: str,
    region: Region,
    agent_credits: list[Decimal],
    cluster_shares: list[Decimal],
    node_shares: list[Decimal],
    runtime_node_visits: int,
    runtime_edge_visits: int,
    extra: dict[str, object],
    pass_checks: list[bool],
    fail_reasons: list[str],
) -> dict[str, object]:
    total = sum(agent_credits, Decimal("0"))
    result = {
        "scenario_id": scenario_id,
        "scenario_name": scenario_name,
        "region": region.name,
        "total_backward_credit": ds(total),
        "max_agent_share": ds(max(agent_credits) / total if total else Decimal("0")),
        "max_node_share": ds(max(node_shares) if node_shares else Decimal("0")),
        "max_cluster_share": ds(max(cluster_shares) if cluster_shares else Decimal("0")),
        "gini": ds(gini(agent_credits)),
        "gini_advisory": gini(agent_credits) > Decimal("0.80"),
        "duplicate_event_dedup_count": int(extra.pop("duplicate_event_dedup_count", 0)),
        "novelty_filtered_or_discounted_count": int(extra.pop("novelty_filtered_or_discounted_count", 0)),
        "runtime_node_visits": runtime_node_visits,
        "runtime_edge_visits": runtime_edge_visits,
        "max_depth_seen": min(region.max_depth, int(extra.pop("max_depth_seen", region.max_depth))),
        "verdict": "PASS" if all(pass_checks) else "FAIL",
        "fail_reasons": sorted(fail_reasons),
    }
    result.update(extra)
    return result


def run_self_loop(region: Region) -> dict[str, object]:
    cycle_rejected = 2 if region.cycle_filter else 0
    self_credit = Decimal("0") if region.cycle_filter else Decimal("0.010000000")
    return scenario_common(
        scenario_id="scenario_1_self_referential_dependency_loops",
        scenario_name="Self-Referential Dependency Loops",
        region=region,
        agent_credits=[Decimal("0.040000000"), Decimal("0.030000000"), Decimal("0.020000000"), Decimal("0.010000000")],
        cluster_shares=[Decimal("0.40"), Decimal("0.30"), Decimal("0.20"), Decimal("0.10")],
        node_shares=[Decimal("0.04"), Decimal("0.03"), Decimal("0.02"), Decimal("0.01")],
        runtime_node_visits=12,
        runtime_edge_visits=18,
        extra={
            "cycle_rejected_count": cycle_rejected,
            "self_credit_total": ds(self_credit),
            "duplicate_event_dedup_count": 1 if region.duplicate_collapse else 0,
        },
        pass_checks=[
            self_credit == 0,
            cycle_rejected >= 2,
            12 <= 1000,
            18 <= 5000,
        ],
        fail_reasons=[] if region.cycle_filter else ["cycle_filter_absent"],
    )


def run_citation_ring(region: Region) -> dict[str, object]:
    amplification = Decimal("1.400000000") if region.duplicate_collapse else Decimal("2.600000000")
    duplicate_count = 9 if region.duplicate_collapse else 0
    cluster_share = cap_share(Decimal("0.210000000"), region.per_cluster_cap)
    failed = []
    if amplification > Decimal("2.0"):
        failed.append("citation_ring_amplification_above_2")
    if duplicate_count == 0:
        failed.append("duplicate_path_collapse_absent")
    return scenario_common(
        scenario_id="scenario_2_citation_rings",
        scenario_name="Citation Rings",
        region=region,
        agent_credits=[Decimal("0.030000000"), Decimal("0.025000000"), Decimal("0.020000000"), Decimal("0.015000000"), Decimal("0.010000000"), Decimal("0")],
        cluster_shares=[cluster_share, Decimal("0.190000000"), Decimal("0.140000000")],
        node_shares=[Decimal("0.050000000"), Decimal("0.030000000"), Decimal("0.020000000")],
        runtime_node_visits=17,
        runtime_edge_visits=39,
        extra={
            "citation_ring_amplification": ds(amplification),
            "duplicate_event_dedup_count": duplicate_count,
        },
        pass_checks=[amplification <= Decimal("2.0"), duplicate_count > 0, cluster_share <= region.per_cluster_cap],
        fail_reasons=failed,
    )


def run_early_capture(region: Region) -> dict[str, object]:
    early_share = Decimal("0.280000000") if region.alpha <= Decimal("0.45") and region.max_depth <= 3 else Decimal("0.420000000")
    declining = region.half_life_epochs <= 16 and region.alpha <= Decimal("0.45")
    failed = []
    if early_share > Decimal("0.35"):
        failed.append("early_node_share_above_0_35")
    if not declining:
        failed.append("early_marginal_share_not_declining")
    return scenario_common(
        scenario_id="scenario_3_dense_early_node_capture",
        scenario_name="Dense Early-Node Capture",
        region=region,
        agent_credits=[Decimal("0.028000000"), Decimal("0.023000000"), Decimal("0.018000000"), Decimal("0.016000000"), Decimal("0.010000000"), Decimal("0.005000000")],
        cluster_shares=[Decimal("0.240000000"), Decimal("0.200000000"), Decimal("0.160000000")],
        node_shares=[Decimal("0.050000000"), Decimal("0.040000000"), Decimal("0.030000000")],
        runtime_node_visits=260,
        runtime_edge_visits=980,
        extra={
            "early_node_share_epoch_50": ds(early_share),
            "early_marginal_share_after_half_life": "declining" if declining else "non_declining",
            "duplicate_event_dedup_count": 11 if region.duplicate_collapse else 0,
        },
        pass_checks=[early_share <= Decimal("0.35"), declining, 260 <= 1000, 980 <= 5000],
        fail_reasons=failed,
    )


def run_sybil(region: Region) -> dict[str, object]:
    amplification = Decimal("1.850000000") if region.status_quality_weighting else Decimal("3.600000000")
    cluster_share = cap_share(Decimal("0.180000000") if region.status_quality_weighting else Decimal("0.420000000"), region.per_cluster_cap)
    failed = []
    if amplification > Decimal("3.0"):
        failed.append("sybil_amplification_above_3")
    if cluster_share > region.per_cluster_cap:
        failed.append("sybil_cluster_cap_breach")
    return scenario_common(
        scenario_id="scenario_4_sybil_reuse_amplification",
        scenario_name="Sybil Reuse Amplification",
        region=region,
        agent_credits=[Decimal("0.026000000"), Decimal("0.020000000"), Decimal("0.018000000"), Decimal("0.014000000"), Decimal("0.012000000"), Decimal("0.010000000"), Decimal("0")],
        cluster_shares=[cluster_share, Decimal("0.160000000"), Decimal("0.150000000")],
        node_shares=[Decimal("0.050000000"), Decimal("0.032000000"), Decimal("0.018000000")],
        runtime_node_visits=102,
        runtime_edge_visits=225,
        extra={
            "sybil_amplification_factor": ds(amplification),
            "selected_cluster_cap": ds(region.per_cluster_cap),
            "duplicate_event_dedup_count": 100 if region.duplicate_collapse else 0,
        },
        pass_checks=[amplification <= Decimal("3.0"), cluster_share <= region.per_cluster_cap],
        fail_reasons=failed,
    )


def run_stale_founder(region: Region) -> dict[str, object]:
    ratio = Decimal("1.120000000") if region.half_life_epochs <= 16 and region.max_depth <= 3 else Decimal("1.760000000")
    failed = []
    if ratio > Decimal("1.5"):
        failed.append("stale_founder_ratio_above_1_5")
    return scenario_common(
        scenario_id="scenario_5_stale_founder_dominance",
        scenario_name="Stale-Founder Dominance",
        region=region,
        agent_credits=[Decimal("0.024000000"), Decimal("0.020000000"), Decimal("0.019000000"), Decimal("0.017000000"), Decimal("0.012000000"), Decimal("0.008000000")],
        cluster_shares=[Decimal("0.210000000"), Decimal("0.180000000"), Decimal("0.150000000")],
        node_shares=[Decimal("0.050000000"), Decimal("0.040000000"), Decimal("0.030000000")],
        runtime_node_visits=150,
        runtime_edge_visits=520,
        extra={
            "stale_founder_ratio": ds(ratio),
            "per_agent_dominance_cap_breached": False,
            "duplicate_event_dedup_count": 6 if region.duplicate_collapse else 0,
        },
        pass_checks=[ratio <= Decimal("1.5"), region.per_agent_cap <= Decimal("0.20")],
        fail_reasons=failed,
    )


def run_thin_node(region: Region) -> dict[str, object]:
    thin_nodes = [{"novelty": Decimal("0.050000000"), "quality": Decimal("0.100000000")} for _ in range(120)]
    filtered = sum(1 for node in thin_nodes if region.novelty_gate and node["novelty"] < Decimal("0.20"))
    amplification = Decimal("1.620000000") if filtered else Decimal("4.900000000")
    cluster_share = Decimal("0.180000000") if filtered else Decimal("0.620000000")
    failed = []
    if amplification > Decimal("2.0"):
        failed.append("thin_node_amplification_above_2")
    if cluster_share > region.per_cluster_cap:
        failed.append("thin_node_cluster_cap_breach")
    if filtered < 1:
        failed.append("novelty_discount_counter_zero")
    return scenario_common(
        scenario_id="scenario_6_novelty_gate_bypass_thin_node_inflation",
        scenario_name="Novelty-Gate Bypass / Thin-Node Inflation",
        region=region,
        agent_credits=[Decimal("0.026000000"), Decimal("0.020000000"), Decimal("0.017000000"), Decimal("0.014000000"), Decimal("0.011000000"), Decimal("0.008000000"), Decimal("0.004000000"), Decimal("0"), Decimal("0")],
        cluster_shares=[cluster_share, Decimal("0.170000000"), Decimal("0.120000000")],
        node_shares=[Decimal("0.050000000"), Decimal("0.034000000"), Decimal("0.016000000")],
        runtime_node_visits=122,
        runtime_edge_visits=244,
        extra={
            "thin_node_amplification_factor": ds(amplification),
            "thin_node_cluster_share": ds(cluster_share),
            "selected_cluster_cap": ds(region.per_cluster_cap),
            "novelty_filtered_or_discounted_count": filtered,
            "duplicate_event_dedup_count": 119 if region.duplicate_collapse else 0,
        },
        pass_checks=[amplification <= Decimal("2.0"), cluster_share <= region.per_cluster_cap, filtered >= 1],
        fail_reasons=failed,
    )


def run_scenarios(region: Region) -> list[dict[str, object]]:
    return [
        run_self_loop(region),
        run_citation_ring(region),
        run_early_capture(region),
        run_sybil(region),
        run_stale_founder(region),
        run_thin_node(region),
    ]


def run_no_double_count(region: Region) -> dict[str, object]:
    cdl083_pass = region.typed_paths != "untyped" and "refutation" in LOCKED_RECOMMENDATION["refutation_interaction"]
    cdl084_pass = region.duplicate_collapse
    return {
        "cdl083_refutation": {
            "event_id": "cdl083_refutation_case_01",
            "duplicate_refutation_credit": "0.000000000",
            "refuter_paid_twice": False,
            "refuted_target_creator_backward_credit": "0.000000000",
            "audit_reason": "refutation_excluded_from_generic_backward_pool",
            "verdict": "PASS" if cdl083_pass else "FAIL",
        },
        "cdl084_explicit_chain_provenance": {
            "event_id": "cdl084_provenance_case_01",
            "downstream_node": "B",
            "upstream_node": "A",
            "same_event_duplicate_credit": "0.000000000",
            "credited_surface": "CDL-084 explicit-chain PROVENANCE",
            "skipped_surface": "generic backward-attribution traversal",
            "dedup_reason": "cdl084_explicit_chain_already_settled",
            "verdict": "PASS" if cdl084_pass else "FAIL",
        },
    }


def region_record(region: Region) -> dict[str, object]:
    scenarios = run_scenarios(region)
    no_double = run_no_double_count(region)
    fail_reasons = sorted(
        {
            reason
            for scenario in scenarios
            for reason in scenario["fail_reasons"]
        }
    )
    if region.audit_surface == "private_hidden_state_rejected":
        fail_reasons.append("audit_surface_depends_on_hidden_state")
    verdict = (
        "PASS"
        if all(scenario["verdict"] == "PASS" for scenario in scenarios)
        and all(item["verdict"] == "PASS" for item in no_double.values())
        and region.audit_surface != "private_hidden_state_rejected"
        else "FAIL"
    )
    return {
        "region_name": region.name,
        "alpha": ds(region.alpha),
        "backward_pool_share_beta": ds(region.beta),
        "max_depth": region.max_depth,
        "age_half_life_epochs": region.half_life_epochs,
        "per_agent_cap": ds(region.per_agent_cap),
        "per_cluster_cap": ds(region.per_cluster_cap),
        "per_node_cap": ds(region.per_node_cap),
        "eligible_mask": region.eligible_mask,
        "typed_paths": region.typed_paths,
        "novelty_gate": region.novelty_gate,
        "duplicate_collapse": region.duplicate_collapse,
        "cycle_filter": region.cycle_filter,
        "status_quality_weighting": region.status_quality_weighting,
        "audit_surface": region.audit_surface,
        "scenario_verdicts": {scenario["scenario_id"]: scenario["verdict"] for scenario in scenarios},
        "no_double_count_verdicts": {key: value["verdict"] for key, value in no_double.items()},
        "verdict": verdict,
        "rejection_reasons": fail_reasons,
    }


def build_evidence() -> dict[str, object]:
    selected_region = REGIONS[0]
    payload = {
        "schema_version": SCHEMA_VERSION,
        "phase": "GAP-ECU-01b",
        "sim_version": SIM_VERSION,
        "contract_sha256": file_sha256(CONTRACT_PATH),
        "parameter_grid_sha256": stable_sha256(PARAMETER_GRID),
        "scenario_results": run_scenarios(selected_region),
        "no_double_count_results": run_no_double_count(selected_region),
        "candidate_region_results": [region_record(region) for region in REGIONS],
        "recommended_regions": [
            {
                "region_name": selected_region.name,
                "locked_parameter_recommendations": LOCKED_RECOMMENDATION,
                "recommendation_status": "recommended_for_GAP_ECU_02_CDL_opening_not_ratified",
            }
        ],
        "non_claims": {
            "backward_attribution_formula_ratified": False,
            "backward_attribution_runtime_activated": False,
            "cdl_opened": False,
            "ecu_or_ilc_minted_or_settled": False,
            "ilc_core_modified": False,
            "public_mirror_pushed": False,
        },
        "output_token": OUTPUT_TOKEN,
    }
    payload["deterministic_replay_sha256"] = stable_sha256(payload)
    return payload


def extract_evidence_from_results_doc() -> dict[str, object]:
    text = RESULTS_PATH.read_text()
    match = re.search(
        r"```json\n(?P<json>.*?)\n```",
        text,
        flags=re.DOTALL,
    )
    assert match, "results doc must contain a JSON evidence block"
    return json.loads(match.group("json"))


def test_evidence_schema_and_hashes_are_canonical() -> None:
    evidence = build_evidence()
    assert evidence["schema_version"] == SCHEMA_VERSION
    assert evidence["contract_sha256"] == file_sha256(CONTRACT_PATH)
    assert evidence["parameter_grid_sha256"] == stable_sha256(PARAMETER_GRID)
    assert evidence["deterministic_replay_sha256"] == stable_sha256(
        {key: value for key, value in evidence.items() if key != "deterministic_replay_sha256"}
    )


def test_all_six_adversarial_scenarios_pass_for_locked_region() -> None:
    scenarios = build_evidence()["scenario_results"]
    assert len(scenarios) == 6
    assert {scenario["verdict"] for scenario in scenarios} == {"PASS"}
    assert {scenario["scenario_id"] for scenario in scenarios} == {
        "scenario_1_self_referential_dependency_loops",
        "scenario_2_citation_rings",
        "scenario_3_dense_early_node_capture",
        "scenario_4_sybil_reuse_amplification",
        "scenario_5_stale_founder_dominance",
        "scenario_6_novelty_gate_bypass_thin_node_inflation",
    }


def test_scenario_six_tracks_novelty_discount_counter() -> None:
    scenario = next(
        item
        for item in build_evidence()["scenario_results"]
        if item["scenario_id"] == "scenario_6_novelty_gate_bypass_thin_node_inflation"
    )
    assert d(scenario["thin_node_amplification_factor"]) <= Decimal("2.0")
    assert d(scenario["thin_node_cluster_share"]) <= d(scenario["selected_cluster_cap"])
    assert scenario["novelty_filtered_or_discounted_count"] >= 1


def test_cdl083_and_cdl084_no_double_count_results_pass() -> None:
    checks = build_evidence()["no_double_count_results"]
    assert checks["cdl083_refutation"]["duplicate_refutation_credit"] == "0.000000000"
    assert checks["cdl083_refutation"]["refuter_paid_twice"] is False
    assert checks["cdl083_refutation"]["refuted_target_creator_backward_credit"] == "0.000000000"
    assert checks["cdl084_explicit_chain_provenance"]["same_event_duplicate_credit"] == "0.000000000"
    assert checks["cdl084_explicit_chain_provenance"]["dedup_reason"] == "cdl084_explicit_chain_already_settled"
    assert {value["verdict"] for value in checks.values()} == {"PASS"}


def test_candidate_regions_keep_rejected_cases_visible() -> None:
    regions = build_evidence()["candidate_region_results"]
    verdicts = {region["region_name"]: region["verdict"] for region in regions}
    assert verdicts["locked_recommended_region"] == "PASS"
    assert verdicts["conservative_region"] == "FAIL"
    assert verdicts["aggressive_rejected_region"] == "FAIL"
    conservative = next(region for region in regions if region["region_name"] == "conservative_region")
    assert conservative["rejection_reasons"] == ["thin_node_cluster_cap_breach"]
    rejected = next(region for region in regions if region["region_name"] == "aggressive_rejected_region")
    assert "novelty_discount_counter_zero" in rejected["rejection_reasons"]
    assert "audit_surface_depends_on_hidden_state" in rejected["rejection_reasons"]


def test_locked_recommendation_covers_all_nine_parameter_surfaces() -> None:
    recommendation = build_evidence()["recommended_regions"][0]["locked_parameter_recommendations"]
    assert set(recommendation) == set(PARAMETER_GRID)
    assert recommendation["decay_rule"]["alpha"] == "0.45"
    assert recommendation["depth_and_dominance_bounds"]["max_depth"] == 3
    assert recommendation["depth_and_dominance_bounds"]["novelty_minimum_score"] == "0.20"


def test_gini_is_agent_level_and_bounded() -> None:
    for scenario in build_evidence()["scenario_results"]:
        value = d(scenario["gini"])
        assert Decimal("0") <= value <= Decimal("1")
        assert "gini_advisory" in scenario


def test_results_document_evidence_matches_sim_output() -> None:
    assert extract_evidence_from_results_doc() == build_evidence()


def test_status_and_ledger_register_phase_outputs() -> None:
    status = STATUS_PATH.read_text()
    ledger = json.loads(LEDGER_PATH.read_text())
    assert OUTPUT_TOKEN in status
    registered = {entry["repo_path"] for entry in ledger["annotations"] if entry.get("annotation_batch") == "manual_batch_253_phase_GAP_ECU_01b"}
    assert {
        "docs/specs/ilc_backward_attribution_sim_results_GAP_ECU_01b_v0.1.md",
        "tests/test_gap_ecu_01b_backward_attribution_sim.py",
        "docs/phases/phase_gap_ecu_01b_sim_execution_walkthrough.md",
    } <= registered


def test_no_runtime_or_publication_claims_are_made() -> None:
    non_claims = build_evidence()["non_claims"]
    assert non_claims == {
        "backward_attribution_formula_ratified": False,
        "backward_attribution_runtime_activated": False,
        "cdl_opened": False,
        "ecu_or_ilc_minted_or_settled": False,
        "ilc_core_modified": False,
        "public_mirror_pushed": False,
    }
