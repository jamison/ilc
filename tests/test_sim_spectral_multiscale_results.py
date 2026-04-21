"""Gate test for H-006b Parts 1-2 simulation checkpoints."""

from __future__ import annotations

import os
import re


SELFTEST_ENV = "ILC_SIM_SPECTRAL_MULTISCALE_SELFTEST"
SCRIPT_PATH = "tools/sim/sim_spectral_multiscale_01.py"
RESULTS_PATH = "docs/research/ilc_sim_spectral_multiscale_results_v0.1.md"
PART1_TOKEN = "sim_spectral_embedding_01_clusters_viable=true"
PART2_TOKEN = "sim_local_lambda2_viable=true"


def _read_results() -> str:
    with open(RESULTS_PATH, encoding="utf-8") as handle:
        return handle.read()


def test_selftest_guard() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return


def test_part1_script_exists() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    assert os.path.isfile(SCRIPT_PATH), f"missing Part 1 simulator: {SCRIPT_PATH}"


def test_results_document_exists() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    assert os.path.isfile(RESULTS_PATH), f"missing Part 1 results doc: {RESULTS_PATH}"


def test_part1_token_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert PART1_TOKEN in text, f"expected Part 1 viability token {PART1_TOKEN!r}"


def test_part2_token_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert PART2_TOKEN in text, f"expected Part 2 viability token {PART2_TOKEN!r}"


def test_shape_contract_markers_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for marker in [
        "N = 500",
        "80` large panels",
        "120` binary edges",
        "application/math-panel",
        "application/biology-panel",
        "application/governance-panel",
        "application/systems-panel",
    ]:
        assert marker in text, f"missing shape marker {marker!r}"


def test_cluster_separation_metric_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    match = re.search(r"silhouette_score = ([0-9.]+)", text)
    assert match is not None, "missing silhouette_score marker"
    assert float(match.group(1)) >= 0.50


def test_bridge_boundary_metrics_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert "15th percentile" in text

    recall_match = re.search(r"bridge_boundary_band_recall = ([0-9.]+)", text)
    median_match = re.search(r"bridge_median_percentile_rank = ([0-9.]+)", text)
    mean_match = re.search(r"bridge_mean_percentile_rank = ([0-9.]+)", text)

    assert recall_match is not None, "missing bridge recall marker"
    assert median_match is not None, "missing bridge median percentile marker"
    assert mean_match is not None, "missing bridge mean percentile marker"

    assert float(recall_match.group(1)) >= 0.75
    assert float(median_match.group(1)) <= 15.0
    assert float(mean_match.group(1)) <= 15.0


def test_cross_domain_metric_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    match = re.search(r"cross_domain_centroid_distance_ratio = ([0-9.]+)", text)
    assert match is not None, "missing cross-domain centroid ratio marker"
    assert float(match.group(1)) >= 1.10


def test_part2_induced_subgraph_contract_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for marker in [
        "partial-membership hyperedges are excluded",
        "delta_generation_contract = +20 intra-cluster binary edges per epoch step",
        "5` new intra-cluster edges per `content_type` at epoch 2",
    ]:
        assert marker in text, f"missing Part 2 contract marker {marker!r}"


def test_part2_local_lambda2_table_and_classifications_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    for marker in [
        "`mature_domain`",
        "`emerging_domain`",
        "`sparse_but_healthy`",
        "theta_floor_ratio",
        "application/math-panel",
        "application/biology-panel",
        "application/governance-panel",
        "application/systems-panel",
    ]:
        assert marker in text, f"missing Part 2 baseline marker {marker!r}"


def test_part2_distinguishable_spread_and_monotonic_markers_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    spread_match = re.search(r"distinguishable_local_lambda2_spread = ([0-9.]+)", text)
    monotonic_match = re.search(r"monotonic_local_lambda2_clusters = ([^\n]+)", text)
    assert spread_match is not None, "missing distinguishable spread marker"
    assert monotonic_match is not None, "missing monotonic cluster marker"
    assert float(spread_match.group(1)) >= 0.02
    monotonic_clusters = [item.strip() for item in monotonic_match.group(1).split(",")]
    assert len(monotonic_clusters) >= 1


def test_part2_sparse_but_healthy_note_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert "emerging_domain / sparse_but_healthy" in text
    assert "none of the induced subgraphs are near-partition" in text


def test_raw_eigenvalue_markers_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    lambda2_match = re.search(r"lambda2 = ([0-9.]+)", text)
    lambda3_match = re.search(r"lambda3 = ([0-9.]+)", text)
    lambda4_match = re.search(r"lambda4 = ([0-9.]+)", text)
    assert lambda2_match is not None, "missing lambda2 marker"
    assert lambda3_match is not None, "missing lambda3 marker"
    assert lambda4_match is not None, "missing lambda4 marker"

    lambda2 = float(lambda2_match.group(1))
    lambda3 = float(lambda3_match.group(1))
    lambda4 = float(lambda4_match.group(1))
    assert 0.0 < lambda2 < lambda3 < lambda4


def test_part1_does_not_claim_later_phase_tokens() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    assert "run_h006b_multiscale_spectral_verdict=" not in text


def test_manual_bridge_node_count_present() -> None:
    if os.environ.get(SELFTEST_ENV) == "1":
        return
    text = _read_results()
    match = re.search(r"Manual bridge set: the first `(\d+)` designated", text)
    assert match is not None, "expected explicit manual bridge count marker"
    assert int(match.group(1)) == 8
