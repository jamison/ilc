# SPDX-License-Identifier: AGPL-3.0-only
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MEMO_PATH = (
    REPO_ROOT
    / "docs/research/ilc_market_commissioning_recipes_GAP_HARNESS_SIDECAR_09_v0.1.md"
)
CLI_MATRIX_PATH = (
    REPO_ROOT / "docs/specs/ilc_cli_json_conformance_matrix_GAP_HARNESS_SIDECAR_01_v0.1.md"
)
ROOT_SKILLS_PATH = (
    REPO_ROOT / "docs/specs/ilc_root_skills_pack_spec_GAP_HARNESS_SIDECAR_07_v0.1.md"
)
RECEIPT_SCHEMA_PATH = (
    REPO_ROOT / "docs/specs/ilc_sidecar_execution_receipt_schema_GAP_HARNESS_SIDECAR_05_v0.1.md"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_memo_exists_and_advisory_banner_present() -> None:
    text = _read(MEMO_PATH)
    assert "ADVISORY INPUT TO A FUTURE CDL OR RUNTIME LANE" in text
    assert "NOT GOVERNING RECIPE AUTHORITY" in text
    assert "market_commissioning_recipes_committed_GAP_HARNESS_SIDECAR_09" in text


def test_required_sections_present() -> None:
    text = _read(MEMO_PATH)
    for section in [
        "## 2. Scope and Non-Goals",
        "## 4. Task Discovery Recipe",
        "## 5. Commission Offer Recipe",
        "## 6. Bid and Accept Pattern",
        "## 7. Result Delivery and Receipt",
        "## 8. Payment Trigger Sketch",
        "## 10. Open Questions",
        "## 12. Non-Claims",
    ]:
        assert section in text


def test_open_questions_section_is_non_empty_and_specific() -> None:
    text = _read(MEMO_PATH)
    assert "## 10. Open Questions" in text
    for question in [
        "Should `task:` labels remain informal labels",
        "Which actor may create a commission offer",
        "Does an offer require preauthorization of funds",
    ]:
        assert question in text
    assert text.count("?") >= 10


def test_payment_trigger_section_requires_cdl_before_automation() -> None:
    text = _read(MEMO_PATH)
    section = text.split("## 8. Payment Trigger Sketch", 1)[1].split("## 9.", 1)[0]
    assert "CDL" in section
    assert "automated payment triggers require a future CDL before implementation" in section
    assert "This memo does not implement or authorize any of those automated triggers." in section


def test_task_namespace_is_sketch_only_not_ratified() -> None:
    text = _read(MEMO_PATH)
    assert "`task:` namespace is a sketch/proposal only" in text
    assert "not a ratified node type" in text
    assert "not a governing Atlas taxonomy" in text


def test_cli_commands_cited_map_to_sidecar_01_matrix() -> None:
    text = _read(MEMO_PATH)
    matrix = _read(CLI_MATRIX_PATH)
    for command in [
        "ilc query node",
        "ilc query receipt",
        "ilc submit --primitive",
    ]:
        assert command in text
    assert "ilc query node" in matrix
    assert "ilc submit --primitive" in matrix
    assert "ilc query receipt" in _read(ROOT_SKILLS_PATH)


def test_referenced_tool_and_module_surfaces_exist() -> None:
    text = _read(MEMO_PATH)
    for relative_path in [
        "ilc_core/graph/sidecar_query_runtime.py",
        "ilc_core/value_action/ilc_transfer_intent.py",
        "ilc_core/ecu/ecu_fast_path_intent.py",
        "tools/testbed/ilc_transfer_submit.py",
        "tools/testbed/ecu_transfer_submit.py",
        "docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md",
        "docs/specs/ilc_bounded_ecu_exchange_model_622_v0.1.md",
    ]:
        assert relative_path in text
        assert (REPO_ROOT / relative_path).exists()


def test_receipt_schema_and_root_skills_inputs_are_linked() -> None:
    text = _read(MEMO_PATH)
    root_skills = _read(ROOT_SKILLS_PATH)
    receipt_schema = _read(RECEIPT_SCHEMA_PATH)
    assert "SidecarExecutionReceipt" in text
    assert "SidecarExecutionReceipt" in receipt_schema
    assert "transfer.ilc" in text
    assert "transfer.ecu" in text
    assert "transfer.ilc" in root_skills
    assert "transfer.ecu" in root_skills


def test_non_claims_reject_runtime_and_authority_overclaim() -> None:
    text = _read(MEMO_PATH)
    for phrase in [
        "a ratified task market",
        "a ratified `task:` namespace",
        "public graph write authority",
        "automated payment trigger",
        "generalized ECU money transfer",
        "public RC, mainnet, or epoch transition",
    ]:
        assert phrase in text
    for forbidden in [
        "This memo implements",
        "automated payment trigger is active",
        "task market is ratified",
    ]:
        assert forbidden not in text
