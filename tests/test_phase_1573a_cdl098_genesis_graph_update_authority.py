from __future__ import annotations

import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CDL_REGISTER = REPO_ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
EVIDENCE = (
    REPO_ROOT
    / "docs/specs/ilc_cdl_098_genesis_graph_update_authority_ratification_evidence_1573a_v0.1.md"
)
STATUS = REPO_ROOT / "docs/phases/STATUS.md"
TYPE_REGISTRY = REPO_ROOT / "ilc_core/bundle/type_registry.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_row(cdl_id: str) -> str:
    return next(line for line in _read(CDL_REGISTER).splitlines() if line.startswith(f"| {cdl_id} |"))


def test_cdl098_ratification_evidence_exists_and_contains_required_sections() -> None:
    text = _read(EVIDENCE)

    for required in (
        "## 2a. Authorized Scope",
        "## 2b. Prohibited Scope",
        "## 2c. Mechanism",
        "## 2d. Per-Node Provenance Metadata Schema",
        "## 2e. Sunset Condition",
        "## 2f. Relationship To Prior Governance",
        "## 2g. Section Architecture Object Types Authorized Under CDL-098",
        "## 3. Reconciliation Note",
        "## 4. Non-Claims Of CDL-098",
    ):
        assert required in text

    assert "cdl_098_ratified_phase_1573a" in text
    assert "CDL-017 bootstrap transition criteria" in text
    assert "homoiconic test registry is live" in text
    assert '"annotation_method"' in text
    assert '"update_authority_cdl": "cdl_098"' in text
    assert "theta_hard = 0.05" in text
    assert "epoch-60 outer ceiling" in text
    assert "not a standalone graph-update sunset trigger" in text


def test_cdl_register_contains_first_class_cdl098_ratified_row() -> None:
    row = _cdl_row("CDL-098")

    assert "| CDL-098 |" in row
    assert "Genesis Graph Update Authority" in row
    assert "| ratified | phase_1573a | cdl_098_ratified_phase_1573a |" in row
    assert "opened_phase: 1573a" in row
    assert "ratified_phase: 1573a" in row
    assert "genesis_graph_update_authority_ratified_phase_1573a" in row
    assert "per_node_provenance_metadata_schema_ratified_phase_1573a" in row
    assert "cdl_098_section_architecture_types_ratified_phase_1573a" in row
    assert "genesis_base_graph_signing_authority_unlocked_phase_1573a" in row
    assert "runtime_activation_status: not_authorized" in row
    assert "graph_update_execution_status: not_executed" in row
    assert "public_path_status: blocked" in row


def test_phase1573a_status_tokens_and_no_signing_claim() -> None:
    text = _read(STATUS)

    for token in (
        "cdl_098_opened_phase_1573a",
        "cdl_098_ratified_phase_1573a",
        "genesis_graph_update_authority_ratified_phase_1573a",
        "per_node_provenance_metadata_schema_ratified_phase_1573a",
        "cdl_098_sunset_condition_defined_phase_1573a",
        "genesis_base_graph_signing_authority_unlocked_phase_1573a",
        "cdl_098_section_architecture_types_ratified_phase_1573a",
        "public_path_remains_blocked_phase_1573a",
    ):
        assert token in text

    assert "genesis_base_graph_v0.4_signed" not in text
    assert "genesis_base_graph_v04_signed_phase_1573" not in text


def test_cdl098_section_architecture_types_authorized() -> None:
    text = _read(EVIDENCE)

    assert "## 2g. Section Architecture Object Types Authorized Under CDL-098" in text
    assert "GraphSection" in text
    assert "CROSS_SECTION_REF" in text
    assert "AtlasSliceManifest" in text
    assert "NOT ADR-0035 type definition nodes" in text
    assert "NOT CDL-099 definition-node instances" in text
    assert "graph curation/export schemas" in text


def test_cdl098_private_section_manifests_excluded() -> None:
    text = _read(EVIDENCE)

    assert "excluded_private_material" in text
    assert "owner-signed" in text
    assert "Genesis may not:" in text
    assert "Sign `AtlasSliceManifest` records for public sections" in text
    assert "Sign `AtlasSliceManifest` records for `excluded_private_material` sections" in text
    assert "docs/specs/ilc_private_layer_policy_v0.1.md" in text


def test_cdl098_section_architecture_no_adr0035_activation() -> None:
    evidence = _read(EVIDENCE)
    type_registry = _read(TYPE_REGISTRY)

    assert "does NOT activate the ADR-0035 type registry" in evidence
    assert "ADR_0035_TYPE_REGISTRY_NOT_ACTIVATED = True" in type_registry
    assert "CDL-099 definition-node instances" in evidence


def test_phase1573a_does_not_modify_ilc_core_runtime_files() -> None:
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    modified = {line.strip() for line in result.stdout.splitlines() if line.strip()}
    assert not [path for path in modified if path.startswith("ilc_core/")]
