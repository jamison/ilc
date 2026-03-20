"""Phase 436 runtime-tranche benchmark harness and completion tests."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import types
from hashlib import sha256
from pathlib import Path

HANDOFF_PATH = Path("docs/specs/ilc_runtime_tranche_benchmark_handoff_436_v0.1.md")
TOOL_PATH = Path("tools/runtime_baseline.py")
RELEASE_TRACK_TOOL_PATH = Path("../ILC_release_track/tools/runtime_baseline.py")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
PHASE_435_RUNTIME_PATHS = {
    "ilc_core/network/peer.py",
    "ilc_core/cli/main.py",
    "ilc_core/node/node_dissemination_runtime_362.py",
}
FROZEN_HANDOFF_SHA = "4e16ccb979d555329158753499b9dbbf38180460dd5db969a987999fc08a3113"
FROZEN_TOOL_SHA = "dcffef7fb20e10d1ca4f649c752b9bb92875738133b0863881f7a52157ec29db"
PHASE_436_COMMIT_SUBJECT = "runtime(g8): phase 436 benchmark harness and runtime tranche completion"


_module_cache: dict[str, object] = {}


def _read_file_at_ref(ref: str, path: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{ref}:{path}"],
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        raise AssertionError(f"unable_to_read_file_at_ref:{ref}:{path}:{result.stderr.strip()}")
    return result.stdout


def _load_runtime_baseline_module_at_ref(ref: str):
    if ref not in _module_cache:
        source_text = _read_file_at_ref(ref, str(TOOL_PATH))
        module = types.ModuleType(f"phase_436_runtime_baseline_{ref[:8]}")
        module.__file__ = str(TOOL_PATH.resolve())
        exec(compile(source_text, module.__file__, "exec"), module.__dict__)
        _module_cache[ref] = module
    return _module_cache[ref]


def _sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _sha256_text(text: str) -> str:
    return sha256(text.encode("utf-8")).hexdigest()


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_436_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    required_paths = {
        str(TOOL_PATH),
        "tests/test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py",
        str(HANDOFF_PATH),
    }
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_436_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if changed_paths == required_paths:
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_436_commit_subject_present_but_no_qualifying_runtime_commit")
    raise AssertionError("phase_436_commit_not_present_in_local_history")


def _assert_phase_436_runtime_scope(commit_ref: str) -> None:
    changed_paths = _changed_paths_for_commit(commit_ref)
    required_paths = {
        str(TOOL_PATH),
        "tests/test_phase_436_runtime_tranche_benchmark_harness_and_tranche_completion.py",
        str(HANDOFF_PATH),
    }
    assert changed_paths == required_paths, f"phase_436_runtime_scope_mismatch:{sorted(changed_paths)}"
    assert str(DECISION_LOG_PATH) not in changed_paths, "phase_436_runtime_commit_unlawfully_touched_cdl"
    assert PHASE_435_RUNTIME_PATHS.isdisjoint(changed_paths), "phase_436_runtime_commit_unlawfully_touched_phase_435_runtime"
    assert all(not path.startswith("out/public_export/") for path in changed_paths)
    assert all(not path.startswith("docs/antigravity_tasks/") for path in changed_paths)


def test_runtime_baseline_source_matches_frozen_release_track() -> None:
    historical_text = _read_file_at_ref(_resolve_phase_436_commit_ref(), str(TOOL_PATH))
    assert RELEASE_TRACK_TOOL_PATH.exists()
    assert _sha256_text(historical_text) == FROZEN_TOOL_SHA
    assert _sha256(RELEASE_TRACK_TOOL_PATH) == FROZEN_TOOL_SHA
    assert historical_text == RELEASE_TRACK_TOOL_PATH.read_text(encoding="utf-8")


def test_runtime_baseline_report_shape_and_locked_budget_keys() -> None:
    # The Phase-436 runtime_baseline snapshot is a historical runtime-tranche reference.
    module = _load_runtime_baseline_module_at_ref(_resolve_phase_436_commit_ref())
    report = module.build_runtime_baseline_report(1, 1)
    assert set(report) == {"tool", "iterations", "fanout_peers", "budgets", "measurements"}
    assert report["tool"] == "runtime_baseline.py"
    assert set(module.DEFAULT_BUDGETS_MS) == {
        "protocol_claim_ingest_ms",
        "peer_fanout_ms",
        "epoch_snapshot_roundtrip_ms",
        "event_export_ms",
    }
    assert set(report["budgets"]) == set(module.DEFAULT_BUDGETS_MS)


def test_runtime_baseline_cli_defaults_are_locked(monkeypatch) -> None:
    module = _load_runtime_baseline_module_at_ref(_resolve_phase_436_commit_ref())
    monkeypatch.setattr(sys, "argv", ["runtime_baseline.py"])
    args = module._parse_args()
    assert args.iterations == 5
    assert args.fanout_peers == 3
    assert args.report_path == "out/runtime_baseline/report.json"
    assert args.enforce_budgets is False

 
def test_runtime_baseline_cli_writes_report_and_stdout(monkeypatch, tmp_path, capsys) -> None:
    module = _load_runtime_baseline_module_at_ref(_resolve_phase_436_commit_ref())
    report_path = tmp_path / "report.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "runtime_baseline.py",
            "--iterations",
            "1",
            "--fanout-peers",
            "1",
            "--report-path",
            str(report_path),
        ],
    )
    assert module.main() == 0
    assert report_path.exists()
    file_payload = json.loads(report_path.read_text(encoding="utf-8"))
    stdout_payload = json.loads(capsys.readouterr().out)
    assert set(file_payload) == {"tool", "iterations", "fanout_peers", "budgets", "measurements"}
    assert stdout_payload == file_payload
    assert stdout_payload["tool"] == "runtime_baseline.py"


def test_runtime_baseline_enforce_budgets_exits_nonzero_when_breached(monkeypatch, tmp_path, capsys) -> None:
    module = _load_runtime_baseline_module_at_ref(_resolve_phase_436_commit_ref())
    monkeypatch.setitem(module.DEFAULT_BUDGETS_MS, "protocol_claim_ingest_ms", 0.0)
    monkeypatch.setitem(module.DEFAULT_BUDGETS_MS, "peer_fanout_ms", 0.0)
    monkeypatch.setitem(module.DEFAULT_BUDGETS_MS, "epoch_snapshot_roundtrip_ms", 0.0)
    monkeypatch.setitem(module.DEFAULT_BUDGETS_MS, "event_export_ms", 0.0)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "runtime_baseline.py",
            "--iterations",
            "1",
            "--fanout-peers",
            "1",
            "--report-path",
            str(tmp_path / "report.json"),
            "--enforce-budgets",
        ],
    )
    assert module.main() == 1
    payload = json.loads(capsys.readouterr().out)
    assert any(not item["within_budget"] for item in payload["budgets"].values())


def test_runtime_completion_handoff_exists_with_required_tokens() -> None:
    text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Phase 436 runtime scope summary",
        "## 2. Imported runtime surface",
        "## 3. Runtime baseline harness contract",
        "## 4. Preserved runtime and constitutional invariants",
        "## 5. Test evidence and tranche completion state",
        "## 6. Non-goals and Phase 437 pointer",
    ):
        assert heading in text
    for token in (
        "Phase 436 imported only the remaining Phase-434-authorized runtime-tranche file: tools/runtime_baseline.py.",
        "Release-track source anchor: ../ILC_release_track/docs/handoffs/main_track_handoff_window_434_runtime_tranche_v0.1.md",
        f"Release-track source handoff sha256: {FROZEN_HANDOFF_SHA}",
        f"Release-track source tool sha256: {FROZEN_TOOL_SHA}",
        "Runtime baseline harness import was byte-aligned to the frozen release-track source.",
        "Window 434+ must cherry-pick the release-track runtime tranche before any public repo packaging commits are merged.",
        "Runtime tranche imports landed on main with identifiable runtime commit messages and not as a bulk packaging merge.",
        "Phase 436 did not mutate ilc_core/network/peer.py, ilc_core/cli/main.py, or ilc_core/node/node_dissemination_runtime_362.py.",
        "CDL-050 remains unopened and unaffected by Phase 436.",
        "No decision-log mutation occurred in Phase 436.",
        "Public packaging/bootstrap work remained outside the numbered window.",
        "The numbered runtime tranche authorized by Phase 434 is complete after Phase 436.",
        "Phase 437 is the next authorized non-sensitive findings and regression-hardening phase.",
    ):
        assert token in text


def test_phase_436_commit_did_not_mutate_decision_log() -> None:
    commit_ref = _resolve_phase_436_commit_ref()
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert str(DECISION_LOG_PATH) not in changed_paths


def test_phase_436_runtime_scope_is_exact() -> None:
    commit_ref = _resolve_phase_436_commit_ref()
    _assert_phase_436_runtime_scope(commit_ref)
