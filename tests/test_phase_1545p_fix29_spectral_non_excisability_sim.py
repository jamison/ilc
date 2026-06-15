import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/evaluators/sim_atlas_spectral_non_excisability_1545p_fix29.py"
SUMMARY = ROOT / "out/sim_atlas_spectral_non_excisability_1545p_fix29.json"
REPORT = ROOT / "docs/sims/sim_atlas_spectral_non_excisability_1545p_fix29_v0.1.md"
REVIEW = ROOT / "docs/specs/ilc_atlas_spectral_non_excisability_review_1545p_fix29_v0.1.md"
WALKTHROUGH = ROOT / "docs/phases/phase_1545p_fix29_spectral_non_excisability_sim_walkthrough.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PLANNING = ROOT / "docs/PLANNING_INDEX.md"


REQUIRED_TOKENS = {
    "atlas_spectral_non_excisability_sim_committed_phase_1545p_fix29",
    "atlas_laplacian_diagnostics_recorded_phase_1545p_fix29",
    "atlas_non_excisability_probes_recorded_phase_1545p_fix29",
    "atlas_authority_cut_checks_recorded_phase_1545p_fix29",
    "atlas_structural_negative_controls_passed_phase_1545p_fix29",
    "public_path_remains_blocked_phase_1545p_fix29",
}


def _ensure_outputs() -> None:
    if SUMMARY.exists() and REPORT.exists() and REVIEW.exists():
        return
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)


def _summary() -> dict:
    _ensure_outputs()
    return json.loads(SUMMARY.read_text(encoding="utf-8"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_fix29_tokens_and_research_only_outputs_present():
    payload = _summary()
    surfaces = [_read(REPORT), _read(REVIEW), _read(WALKTHROUGH), _read(STATUS), _read(PLANNING)]

    assert payload["phase"] == "1545p-Fix29"
    assert payload["status"] == "pass"
    assert set(payload["output_tokens"]) == REQUIRED_TOKENS
    for token in REQUIRED_TOKENS:
        assert any(token in surface for surface in surfaces)


def test_fix29_laplacian_methods_and_fiedler_records_are_explicit():
    payload = _summary()
    clique = payload["spectral_diagnostics"]["clique_incidence_projection"]
    star = payload["spectral_diagnostics"]["star_projection"]

    assert clique["lambda2_method"] == "eigsh_SM_k2_scipy_sparse"
    assert clique["lambda2"] > 0
    assert clique["component_count"] == 1
    assert clique["fiedler_vector_export_scope"] == "top_120_by_absolute_coordinate"
    assert clique["fiedler_top_coordinates"]
    assert star["lambda2_method"] == "cheeger_lb_fallback"
    assert star["spectral_failure"] == "star_projection_exceeds_fix29_spectral_budget"
    assert payload["projection_sensitivity"]["use_for_fix30_fix31"] in {"star", "clique_incidence"}


def test_fix29_authority_semantics_firewall_prevents_overclaim():
    payload = _summary()
    firewall = payload["spectral_authority_semantics_firewall"]

    assert firewall["lambda2_proves"] == "structural_connectedness_only"
    assert "authority" in firewall["lambda2_does_not_prove"]
    assert firewall["non_excisability_proves"] == "structural_criticality_only"
    assert firewall["authority_proof_requires"] == (
        "typed_directed_trace_per_fix24_genesis_rootedness_standard"
    )
    combined = _read(REPORT) + _read(REVIEW)
    assert "not authority proof" in combined
    assert "does not establish Genesis-rootedness under a typed authority view" in combined


def test_fix29_non_excisability_families_and_negative_controls():
    payload = _summary()
    probes = {record["family"]: record for record in payload["non_excisability_probes"]}

    assert {
        "genesis_root_or_axiomatic_root_exception",
        "accepted_adr_nodes",
        "ratified_cdl_nodes",
        "runtime_source_nodes",
        "public_release_candidate_material",
        "private_excluded_material",
        "generated_evidence_material",
        "high_degree_support_hubs",
        "low_degree_support_leaves",
    } <= set(probes)
    assert probes["accepted_adr_nodes"]["nodes_removed"] > 0
    assert probes["ratified_cdl_nodes"]["nodes_removed"] > 0
    assert probes["genesis_root_or_axiomatic_root_exception"]["verdict"] == "non_excisable"
    assert probes["low_degree_support_leaves"]["verdict"] == "safe_to_defer"
    assert payload["negative_controls"]["support_only_low_value_control"]["verdict"] == "pass"
    assert payload["negative_controls"]["forbidden_authority_removal_control"]["verdict"] == (
        "warns_as_expected"
    )
    assert payload["structural_negative_controls_passed"] is True


def test_fix29_reports_no_placeholders_or_activation_claims():
    combined = "\n".join([_read(REPORT), _read(REVIEW), _read(WALKTHROUGH)])

    assert "No Genesis signing occurred." in combined
    assert "No public RC activation occurred." in combined
    assert "No canonical Genesis graph mutation occurred." in combined
    assert "No ADR or CDL mutation occurred." in combined
    assert "..." not in combined
    assert "…" not in combined
