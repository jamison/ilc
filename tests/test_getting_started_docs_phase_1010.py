from __future__ import annotations

from pathlib import Path


def test_getting_started_exists_and_has_required_runtime_sections() -> None:
    doc_path = Path("docs/GETTING_STARTED.md")
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")

    assert "# ILC Getting Started" in text
    assert "## 3) First local run (quick path)" in text
    assert "python3 tools/genesis_boot.py" in text
    assert "python3 run_node.py" in text
    assert "python3 tools/demo_walkthrough.py" in text


def test_getting_started_lists_protocol_surface_and_replay_gate_examples() -> None:
    text = Path("docs/GETTING_STARTED.md").read_text(encoding="utf-8")

    assert "POST /v1/protocol/claim" in text
    assert "POST /v1/protocol/refute" in text
    assert "POST /v1/protocol/task_outcome" in text
    assert "ilc-canon-cluster-a-replay-proof ci-gate --profile release-v0.1 --pretty" in text
    assert "bash tools/check_cluster_a_replay_proof_release_gate.sh" in text


def test_root_readme_links_to_getting_started() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    assert "`docs/GETTING_STARTED.md`" in readme
