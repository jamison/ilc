from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from ilc_core.protocol import (
    HARNESS_INTERFACES_VERSION,
    StorageHarness,
    TransportHarness,
)
from ilc_core.rc.package_boundary_inventory import (
    DEFAULT_IMPORT_BOUNDARY_SPECS,
    IMPORT_BOUNDARY_INVENTORY_VERSION,
    ImportBoundarySpec,
    build_default_import_boundary_inventory,
    build_import_boundary_inventory,
    export_import_boundary_inventory_json,
    validate_import_boundary,
)


HARNESS_INTERFACE_PATH = Path("ilc_core/protocol/harness_interfaces.py")


class _MemoryTransport:
    def __init__(self) -> None:
        self.payloads: dict[str, bytes] = {}

    def publish_payload(
        self,
        *,
        channel: str,
        payload: bytes,
        epoch: int,
        metadata: dict[str, str] | None = None,
    ) -> str:
        address = f"{channel}:{epoch}:{len(self.payloads)}"
        self.payloads[address] = payload
        return address

    def fetch_payload(
        self,
        *,
        address: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        payload = self.payloads[address]
        return payload[:max_bytes]


class _MemoryStorage:
    def __init__(self) -> None:
        self.payloads: dict[str, bytes] = {}

    def put_payload(
        self,
        *,
        key: str,
        payload: bytes,
        epoch: int,
        metadata: dict[str, str] | None = None,
    ) -> str:
        self.payloads[key] = payload
        return key

    def get_payload(
        self,
        *,
        key: str,
        max_bytes: int,
        epoch: int,
    ) -> bytes:
        return self.payloads[key][:max_bytes]

    def has_payload(
        self,
        *,
        key: str,
        epoch: int,
    ) -> bool:
        return key in self.payloads


def test_phase_1244_harness_interfaces_are_structural_protocols() -> None:
    transport = _MemoryTransport()
    storage = _MemoryStorage()

    assert HARNESS_INTERFACES_VERSION == "harness_interfaces_1244.v0.1"
    assert isinstance(transport, TransportHarness)
    assert isinstance(storage, StorageHarness)

    address = transport.publish_payload(
        channel="claims",
        payload=b"payload",
        epoch=7,
        metadata={"source": "test"},
    )
    assert transport.fetch_payload(address=address, max_bytes=4, epoch=7) == b"payl"

    key = storage.put_payload(key="artifact", payload=b"artifact-bytes", epoch=7)
    assert key == "artifact"
    assert storage.has_payload(key="artifact", epoch=7) is True
    assert storage.get_payload(key="artifact", max_bytes=8, epoch=7) == b"artifact"


def test_phase_1244_harness_interface_module_has_no_runtime_io_imports() -> None:
    tree = ast.parse(HARNESS_INTERFACE_PATH.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    assert imports <= {"__future__", "collections", "typing"}
    assert "http" not in imports
    assert "lmdb" not in imports
    assert "socket" not in imports
    assert "urllib" not in imports


def test_phase_1244_import_boundary_detects_internal_runtime_prefix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "candidate"
    root.mkdir()
    (root / "logic.py").write_text(
        "from ilc_core.node.runtime import start_node\n",
        encoding="utf-8",
    )
    spec = ImportBoundarySpec(
        surface_id="tmp_logic",
        root_paths=("candidate",),
        forbidden_module_prefixes=("ilc_core.node",),
    )
    inventory = build_import_boundary_inventory(spec)

    assert inventory["status"] == "violations_present"
    assert inventory["violations"] == [
        {
            "file": "candidate/logic.py",
            "import_root": "ilc_core",
            "matched_rule": "ilc_core.node",
            "module": "ilc_core.node.runtime",
            "violation_type": "forbidden_module_prefix",
        }
    ]
    with pytest.raises(ValueError, match="package_boundary_inventory_forbidden_imports_present"):
        validate_import_boundary(spec)


def test_phase_1244_import_boundary_detects_relative_internal_runtime_prefix(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "ilc_core" / "protocol"
    root.mkdir(parents=True)
    (root / "logic.py").write_text(
        "from ..node.runtime import start_node\n",
        encoding="utf-8",
    )
    spec = ImportBoundarySpec(
        surface_id="tmp_logic",
        root_paths=("ilc_core/protocol",),
        forbidden_module_prefixes=("ilc_core.node",),
    )

    inventory = build_import_boundary_inventory(spec)
    assert inventory["violations"] == [
        {
            "file": "ilc_core/protocol/logic.py",
            "import_root": "ilc_core",
            "matched_rule": "ilc_core.node",
            "module": "ilc_core.node.runtime",
            "violation_type": "forbidden_module_prefix",
        }
    ]


def test_phase_1244_import_boundary_detects_dynamic_forbidden_import(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    root = tmp_path / "candidate"
    root.mkdir()
    (root / "logic.py").write_text(
        "import importlib\n"
        "from importlib import import_module\n"
        "importlib.import_module('lmdb')\n"
        "__import__('urllib.parse')\n"
        "import_module('requests')\n",
        encoding="utf-8",
    )
    spec = ImportBoundarySpec(
        surface_id="tmp_logic",
        root_paths=("candidate",),
        forbidden_import_roots=("lmdb", "requests", "urllib"),
    )

    inventory = build_import_boundary_inventory(spec)
    assert inventory["status"] == "violations_present"
    assert [violation["module"] for violation in inventory["violations"]] == [
        "lmdb",
        "requests",
        "urllib.parse",
    ]


def test_phase_1244_default_inventory_is_repo_root_anchored(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    inventory = build_default_import_boundary_inventory()
    logic = inventory["surfaces"]["ilc_logic"]
    assert logic["file_count"] > 0
    assert logic["status"] == "violations_present"


def test_phase_1244_default_ilc_logic_boundary_records_migration_debt() -> None:
    spec = DEFAULT_IMPORT_BOUNDARY_SPECS["ilc_logic"]
    assert "ilc_core.node" in spec.forbidden_module_prefixes
    assert "ilc_core.storage" in spec.forbidden_module_prefixes
    assert "argparse" in spec.forbidden_import_roots
    assert "lmdb" in spec.forbidden_import_roots

    inventory = build_import_boundary_inventory(spec)
    assert inventory["status"] == "violations_present"
    assert inventory["violations"] == [
        {
            "file": "ilc_core/epistemic/truth_primitive_graph_store.py",
            "import_root": "ilc_core",
            "matched_rule": "ilc_core.storage",
            "module": "ilc_core.storage.lmdb_public_runtime",
            "violation_type": "forbidden_module_prefix",
        },
        {
            "file": "ilc_core/epistemic/truth_primitive_submission_runtime.py",
            "import_root": "ilc_core",
            "matched_rule": "ilc_core.node",
            "module": "ilc_core.node.node_schema_core_runtime_360",
            "violation_type": "forbidden_module_prefix",
        },
        {
            "file": "ilc_core/protocol/public_init_admission_runtime.py",
            "import_root": "ilc_core",
            "matched_rule": "ilc_core.storage",
            "module": "ilc_core.storage.lmdb_public_runtime",
            "violation_type": "forbidden_module_prefix",
        },
        {
            "file": "ilc_core/protocol/public_receipt_runtime.py",
            "import_root": "ilc_core",
            "matched_rule": "ilc_core.storage",
            "module": "ilc_core.storage.lmdb_public_runtime",
            "violation_type": "forbidden_module_prefix",
        },
        {
            "file": "ilc_core/protocol/public_wallet_runtime.py",
            "import_root": "ilc_core",
            "matched_rule": "ilc_core.storage",
            "module": "ilc_core.storage.lmdb_public_runtime",
            "violation_type": "forbidden_module_prefix",
        },
    ]
    with pytest.raises(ValueError, match="package_boundary_inventory_forbidden_imports_present"):
        validate_import_boundary(spec)


def test_phase_1244_default_inventory_records_module_prefix_rules() -> None:
    inventory = build_default_import_boundary_inventory()
    logic = inventory["surfaces"]["ilc_logic"]
    assert logic["forbidden_module_prefixes"] == sorted(
        DEFAULT_IMPORT_BOUNDARY_SPECS["ilc_logic"].forbidden_module_prefixes
    )
    assert "ilc_core.network" in logic["forbidden_module_prefixes"]
    assert "ilc_core.cli" in logic["forbidden_module_prefixes"]


def test_phase_1244_inventory_export_remains_canonical_with_prefix_rules() -> None:
    payload = export_import_boundary_inventory_json()
    parsed = json.loads(payload)
    assert parsed["version"] == "package_boundary_inventory_1244.v0.1"
    assert IMPORT_BOUNDARY_INVENTORY_VERSION == "package_boundary_inventory_1244.v0.1"
    assert "forbidden_module_prefixes" in parsed["surfaces"]["ilc_logic"]
    assert payload == json.dumps(
        parsed,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    )
