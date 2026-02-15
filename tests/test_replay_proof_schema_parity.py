import json
from pathlib import Path
from importlib import resources


REPLAY_PROOF_SCHEMA_NAMES = [
    "ilc_cluster_a_replay_proof_batch_report_v0.1.json",
    "ilc_cluster_a_replay_proof_ci_gate_report_v0.1.json",
    "ilc_cluster_a_replay_proof_batch_compare_v0.1.json",
    "ilc_cluster_a_replay_proof_batch_ops_contract_v0.1.json",
]


def _load_docs_schema(name: str) -> dict[str, object]:
    path = Path("docs/specs") / name
    return json.loads(path.read_text(encoding="utf-8"))


def _load_packaged_schema(name: str) -> dict[str, object]:
    text = resources.files("ilc_core.protocol.schemas").joinpath(name).read_text(encoding="utf-8")
    return json.loads(text)


def test_replay_proof_schema_parity() -> None:
    for name in REPLAY_PROOF_SCHEMA_NAMES:
        docs_schema = _load_docs_schema(name)
        packaged_schema = _load_packaged_schema(name)
        assert docs_schema == packaged_schema, f"replay_proof_schema_drift:{name}"
