# SPDX-License-Identifier: AGPL-3.0-only
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs/specs/ilc_root_skills_pack_spec_GAP_HARNESS_SIDECAR_07_v0.1.md"
CLI_MATRIX_PATH = (
    REPO_ROOT / "docs/specs/ilc_cli_json_conformance_matrix_GAP_HARNESS_SIDECAR_01_v0.1.md"
)
MAIN_CLI_PATH = REPO_ROOT / "ilc_core/cli/main.py"
ILC_TRANSFER_INTENT_PATH = REPO_ROOT / "ilc_core/value_action/ilc_transfer_intent.py"
ECU_FAST_PATH_INTENT_PATH = REPO_ROOT / "ilc_core/ecu/ecu_fast_path_intent.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_spec_exists_and_contains_advisory_banner() -> None:
    text = _read(SPEC_PATH)
    assert "ADVISORY INPUT TO A FUTURE CDL OR RUNTIME LANE" in text
    assert "NOT GOVERNING RECIPE AUTHORITY" in text
    assert "root_skills_pack_spec_committed_GAP_HARNESS_SIDECAR_07" in text


def test_required_sections_present() -> None:
    text = _read(SPEC_PATH)
    for section in [
        "## 1. Advisory Status",
        "## 3. Tier 1 Root Skills",
        "## 4. Tier 2 Optional Skills",
        "## 5. Install Surface Disposition",
        "## 6. Invocation Interface Sketch",
        "## 7. Activation Guard Requirements",
        "## 8. Non-Claims",
    ]:
        assert section in text


def test_tier_1_skills_map_to_sidcar_01_cli_matrix_commands() -> None:
    spec = _read(SPEC_PATH)
    matrix = _read(CLI_MATRIX_PATH)
    for skill_id, command in {
        "graph.query": "ilc query node",
        "identity.show": "ilc identity show",
        "balance.check": "ilc balance",
        "epoch.status": "ilc epoch",
    }.items():
        assert skill_id in spec
        assert command in spec
        assert command in matrix
    assert "PROTOTYPE" in spec
    assert "PROTOTYPE" in matrix


def test_tier_2_skills_reference_existing_surfaces() -> None:
    spec = _read(SPEC_PATH)
    for skill_id in [
        "graph.submit",
        "attribution.readback",
        "transfer.ilc",
        "transfer.ecu",
    ]:
        assert skill_id in spec
    for relative_path in [
        "ilc_core/cli/d2e_submit_cli.py",
        "ilc_core/epistemic/truth_primitive_sig_verifier.py",
        "ilc_core/consensus/attribution_audit_lmdb.py",
        "ilc_core/value_action/ilc_transfer_intent.py",
        "ilc_core/value_action/ilc_transfer_ledger.py",
        "ilc_core/ecu/ecu_fast_path_intent.py",
        "ilc_core/ecu/ecu_transfer_adapter.py",
        "tools/testbed/attribution_readback.py",
        "tools/testbed/ilc_transfer_submit.py",
        "tools/testbed/ecu_transfer_submit.py",
    ]:
        assert relative_path in spec
        assert (REPO_ROOT / relative_path).exists()


def test_activation_gated_skills_record_current_guard_values() -> None:
    spec = _read(SPEC_PATH)
    ilc_source = _read(ILC_TRANSFER_INTENT_PATH)
    ecu_source = _read(ECU_FAST_PATH_INTENT_PATH)
    assert "ILC_TRANSFER_ENABLED = True" in ilc_source
    assert "ECU_FAST_PATH_TRANSFER_ENABLED = True" in ecu_source
    assert "`ILC_TRANSFER_ENABLED = True`" in spec
    assert "`ECU_FAST_PATH_TRANSFER_ENABLED = True`" in spec


def test_install_surface_does_not_claim_live_sidecar_install() -> None:
    spec = _read(SPEC_PATH)
    main_cli = _read(MAIN_CLI_PATH)
    assert "There is no active `ilc sidecar install` parser path." in spec
    assert "sidecar_install_requires_clawhub_post_fix2g" in spec
    assert "sidecar_install_requires_clawhub_post_fix2g" in main_cli
    assert 'add_parser("install"' not in main_cli


def test_spec_records_graph_query_helper_functions() -> None:
    spec = _read(SPEC_PATH)
    query_source = _read(REPO_ROOT / "ilc_core/graph/sidecar_query_runtime.py")
    for function_name in [
        "compute_local_novelty_score",
        "rank_nodes_by_reuse_centrality",
        "lookup_submission_receipt",
    ]:
        assert function_name in spec
        assert f"def {function_name}" in query_source


def test_non_claims_include_required_boundaries() -> None:
    text = _read(SPEC_PATH)
    for phrase in [
        "skill dispatch runtime",
        "skill authentication",
        "multi-agent skill delegation",
        "ClawHub listing",
        "OpenClaw integration",
        "public sidecar serving",
        "public graph write admission",
        "generalized ECU money transfer",
    ]:
        assert phrase in text


def test_no_runtime_authority_language_is_claimed() -> None:
    text = _read(SPEC_PATH)
    forbidden_claims = [
        "This spec governs",
        "ratifies a skill dispatch table",
        "clears an activation guard",
        "available `ilc sidecar install`",
        "working `ilc sidecar install`",
        "live `ilc sidecar install` runtime",
    ]
    for phrase in forbidden_claims:
        assert phrase not in text
