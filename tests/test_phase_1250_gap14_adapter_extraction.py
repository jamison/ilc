from __future__ import annotations

import ast
from pathlib import Path

from ilc_core.protocol import (
    ALLOWED_PRIMITIVE_TYPES,
    GAP14_ADAPTER_EXTRACTION_VERSION,
    PRIMITIVE_TYPE_REGISTRY_VERSION,
    PUBLIC_RUNTIME_STORE_INTERFACES_VERSION,
    SYSTEM_PRIMITIVE_TYPES,
    AdmissionReceiptStore,
    PublicReceiptStore,
    PublicWalletStore,
    TruthPrimitiveGraphPersistence,
)
from ilc_core.rc.package_boundary_inventory import (
    DEFAULT_IMPORT_BOUNDARY_SPECS,
    GAP14_ADAPTER_EXTRACTION_VERSION as INVENTORY_GAP14_VERSION,
    IMPORT_BOUNDARY_INVENTORY_VERSION,
    ILC_LOGIC_IMPORT_BOUNDARY_REDUCTION_TOKEN,
    PHASE_1250_GAP14_ADAPTER_EXTRACTION_COMPLETE_TOKEN,
    build_import_boundary_inventory,
    validate_import_boundary,
)
from ilc_core.storage.truth_primitive_graph_lmdb_adapter import (
    TRUTH_PRIMITIVE_GRAPH_LMDB_ADAPTER_VERSION,
    TruthPrimitiveGraphStore,
)


PURE_LOGIC_FILES = (
    Path("ilc_core/epistemic/truth_primitive_graph_store.py"),
    Path("ilc_core/epistemic/truth_primitive_submission_runtime.py"),
    Path("ilc_core/protocol/public_init_admission_runtime.py"),
    Path("ilc_core/protocol/public_receipt_runtime.py"),
    Path("ilc_core/protocol/public_wallet_runtime.py"),
)


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.as_posix())
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_phase_1250_required_tokens_are_exported() -> None:
    assert IMPORT_BOUNDARY_INVENTORY_VERSION == "package_boundary_inventory_1250.v0.1"
    assert GAP14_ADAPTER_EXTRACTION_VERSION == "gap14_adapter_extraction_phase_1250.v0.1"
    assert INVENTORY_GAP14_VERSION == "gap14_adapter_extraction_phase_1250.v0.1"
    assert ILC_LOGIC_IMPORT_BOUNDARY_REDUCTION_TOKEN == (
        "ilc_logic_import_boundary_migration_debt_reduced_phase_1250"
    )
    assert PHASE_1250_GAP14_ADAPTER_EXTRACTION_COMPLETE_TOKEN == (
        "phase_1250_gap14_adapter_extraction_complete"
    )


def test_phase_1250_ilc_logic_boundary_has_zero_forbidden_imports() -> None:
    inventory = build_import_boundary_inventory(DEFAULT_IMPORT_BOUNDARY_SPECS["ilc_logic"])

    assert inventory["status"] == "pass"
    assert inventory["violations"] == []
    assert validate_import_boundary(DEFAULT_IMPORT_BOUNDARY_SPECS["ilc_logic"])["status"] == "pass"


def test_phase_1250_pure_logic_files_do_not_import_storage_or_node_runtime() -> None:
    for path in PURE_LOGIC_FILES:
        imports = _imported_modules(path)
        assert not any(module == "ilc_core.storage" or module.startswith("ilc_core.storage.") for module in imports)
        assert not any(module == "ilc_core.node" or module.startswith("ilc_core.node.") for module in imports)


def test_phase_1250_public_store_interfaces_are_structural() -> None:
    assert PUBLIC_RUNTIME_STORE_INTERFACES_VERSION == "public_runtime_store_interfaces_1250.v0.1"
    assert AdmissionReceiptStore
    assert PublicReceiptStore
    assert PublicWalletStore
    assert TruthPrimitiveGraphPersistence


def test_phase_1250_primitive_registry_preserves_node_runtime_values() -> None:
    from ilc_core.node.node_schema_core_runtime_360 import (
        ALLOWED_PRIMITIVE_TYPES as NODE_ALLOWED_PRIMITIVE_TYPES,
        SYSTEM_PRIMITIVE_TYPES as NODE_SYSTEM_PRIMITIVE_TYPES,
    )

    assert PRIMITIVE_TYPE_REGISTRY_VERSION == "primitive_type_registry_1250.v0.1"
    assert ALLOWED_PRIMITIVE_TYPES == NODE_ALLOWED_PRIMITIVE_TYPES
    assert SYSTEM_PRIMITIVE_TYPES == NODE_SYSTEM_PRIMITIVE_TYPES
    assert "knowledge_claim" in ALLOWED_PRIMITIVE_TYPES
    assert "genesis_authority_assertion" in SYSTEM_PRIMITIVE_TYPES


def test_phase_1250_truth_primitive_lmdb_adapter_preserves_store_behavior(tmp_path: Path) -> None:
    store = TruthPrimitiveGraphStore(tmp_path / "truth-store")
    try:
        assert TRUTH_PRIMITIVE_GRAPH_LMDB_ADAPTER_VERSION == (
            "truth_primitive_graph_lmdb_adapter_1250.v0.1"
        )
        assert isinstance(store, TruthPrimitiveGraphPersistence)

        assert store.put_node_if_absent("node-1", {"primitive": "assert.truth"}) is True
        assert store.put_node_if_absent("node-1", {"primitive": "assert.truth"}) is False
        assert store.get_node("node-1") == {"primitive": "assert.truth"}

        edge = {"source": "node-1", "edge_type": "asserted_by", "target": "agent-1"}
        assert store.put_edge_if_absent("node-1:asserted_by:agent-1", edge) is True
        assert store.put_edge_if_absent("node-1:asserted_by:agent-1", edge) is False
        assert store.get_edge("node-1:asserted_by:agent-1") == edge
    finally:
        store.close()
