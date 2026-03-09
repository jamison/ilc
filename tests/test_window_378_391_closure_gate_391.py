"""Phase 391 closure gate contract tests for window 378-391."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from ilc_core.identity.sybil_resistance_runtime import CDL_V2_DEPENDENCY
from ilc_core.reputation.temporal_decay_runtime import CDL_V1_DEPENDENCY


GATE_PATH = Path("tools/check_window_378_391_closure_gate_phase_391.sh")
GATE_CMD = ["bash", str(GATE_PATH)]
HANDOFF_PATH = Path("docs/specs/ilc_window_378_391_handoff_391_v0.1.md")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
RATIFICATION_PATH = Path(
    "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md"
)
COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_390_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.3.md")
GOSSIP_PATH = Path("ilc_core/network/d2d/gossip.py")
PHASE_391_COMMIT_SUBJECT = "docs(g8): phase 391 window 378-391 closure gate and 392-plus handoff"


def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(GATE_CMD + args, capture_output=True, text=True, env=env, check=False)


def _clean_full_run_env() -> dict[str, str]:
    blocked = {
        "ILC_PHASE_391_SNAPSHOT_PATH",
        "ILC_PHASE_316_SNAPSHOT_PATH",
        "ILC_PHASE_316_FORCE_VERDICT",
        "ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE",
        "ILC_PHASE_391_GATE_SELFTEST",
        "ILC_PHASE_377_GATE_SELFTEST",
        "ILC_PHASE_367_GATE_SELFTEST",
        "ILC_PHASE_357_GATE_SELFTEST",
        "ILC_PHASE_347_GATE_SELFTEST",
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _snapshot_override_env(tmp_path: Path, verdict: str) -> tuple[dict[str, str], bytes, int, str]:
    payload = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    severity = payload.get("severity_summary")
    assert isinstance(severity, dict), "snapshot_missing_severity_summary"
    for key in ("s2_indicators", "s3_indicators", "verdict"):
        assert key in severity, f"snapshot_missing_severity_key:{key}"
    severity["verdict"] = verdict

    snapshot_copy = tmp_path / f"snapshot_{verdict}.json"
    snapshot_copy.write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

    env = _clean_full_run_env()
    env["ILC_PHASE_391_SNAPSHOT_PATH"] = str(snapshot_copy)
    canonical_bytes = SNAPSHOT_PATH.read_bytes()
    canonical_mtime = SNAPSHOT_PATH.stat().st_mtime_ns
    canonical_sha = hashlib.sha256(canonical_bytes).hexdigest()
    return env, canonical_bytes, canonical_mtime, canonical_sha


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_391_commit_ref() -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matching_commits: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject.strip() == PHASE_391_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(GATE_PATH),
        "tests/test_window_378_391_closure_gate_391.py",
        str(HANDOFF_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_391_commit_subject_present_but_no_qualifying_closure_commit")
    raise AssertionError("phase_391_commit_not_present_in_local_history")


def _extract_calibration_section(text: str) -> str:
    lines = text.splitlines()
    start_index = None
    for idx, line in enumerate(lines):
        if line.startswith("## ") and "calibration" in line.lower():
            start_index = idx + 1
            break
    assert start_index is not None, "phase_391_missing_calibration_heading"

    collected: list[str] = []
    for line in lines[start_index:]:
        if line.startswith("## "):
            break
        collected.append(line)
    return "\n".join(collected)


def test_gate_script_exists() -> None:
    assert GATE_PATH.exists()


def test_gate_cli_contract_dry_run_help_alias_unknown_arg_and_exact_lines() -> None:
    help_result = _run_gate(["--help"])
    assert help_result.returncode == 0
    assert "Usage:" in help_result.stdout

    help_alias = _run_gate(["-h"])
    assert help_alias.returncode == 0
    assert "Usage:" in help_alias.stdout

    dry_run = _run_gate(["--dry-run"])
    assert dry_run.returncode == 0
    lines = [line.strip() for line in dry_run.stdout.splitlines() if line.strip()]
    assert lines == [
        "[1/6] prompt_contract_validation",
        "python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_391_g8_constitution_cluster_a_window_378_391_closure_verification_gate_and_392_plus_handoff.md",
        "[2/6] lane_contract_tests",
        "python3 -m pytest tests/test_phase_378_sequence_lock.py tests/test_cdl_039_ratification_379.py tests/test_d2d_abstract_interface_runtime_380.py tests/test_d2d_peering_runtime_381.py tests/test_d2d_gossip_runtime_382.py tests/test_cdl_040_open_and_admission_control_identity_envelope_prelock_383.py tests/test_cdl_041_open_and_shard_lifecycle_prelock_384.py tests/test_cdl_043_open_and_storage_economics_prelock_385.py tests/test_phase_386_sim_006_007_commissioning.py tests/test_phase_387_v_series_implementation_authorization_lock.py tests/test_cdl_v1_temporal_decay_runtime_388.py tests/test_cdl_v2_sybil_resistance_runtime_389.py tests/test_phase_390_coherence_and_capsule_v1_3.py -q",
        "[3/6] cross_phase_regression",
        "python3 -m pytest tests/test_phase_commit_manifest_296.py tests/test_d2_schema_baseline_runtime_310.py tests/test_genesis_state_bundle_runtime_312.py tests/test_epoch_snapshot_runtime_314.py tests/test_infrastructure_economic_risk_monitoring_update_315.py tests/test_infrastructure_composed_preflight_316.py tests/test_wire_transport_runtime_323.py tests/test_window_368_377_closure_gate_377.py tests/test_window_358_367_closure_gate_367.py tests/test_window_348_357_closure_gate_357.py tests/test_window_338_347_closure_gate_347.py tests/test_window_328_337_closure_gate_337.py -q",
        "[4/6] mutation_canary",
        "python3 tools/run_mutation_canary_phase_297.py",
        "[5/6] closure_gate_cli_contract",
        "python3 -m pytest tests/test_window_378_391_closure_gate_391.py -q",
        "[6/6] walkthrough_hygiene",
        "python3 -m pytest tests/test_no_ellipses_in_walkthroughs.py -q",
    ]

    unknown = _run_gate(["--unknown-arg"])
    assert unknown.returncode == 2


def test_gate_full_run_exits_zero_on_pass_snapshot_and_preserves_canonical_snapshot() -> None:
    if os.environ.get("ILC_PHASE_391_GATE_SELFTEST") == "1":
        pytest.skip("phase_391_selftest_context_skip_full_gate")
    canonical_before = SNAPSHOT_PATH.read_bytes()
    canonical_mtime_before = SNAPSHOT_PATH.stat().st_mtime_ns
    canonical_sha_before = hashlib.sha256(canonical_before).hexdigest()
    env = _clean_full_run_env()
    env["ILC_PHASE_316_FORCE_VERDICT"] = "conditional"
    result = _run_gate([], env=env)
    assert result.returncode == 0
    assert "phase_391_snapshot_gate=passed" in result.stdout
    assert "phase_391_verdict=pass" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical_before
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime_before
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha_before


def test_gate_full_run_enforces_conditional_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_391_GATE_SELFTEST") == "1":
        pytest.skip("phase_391_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "conditional")
    result = _run_gate([], env=env)
    assert result.returncode == 3
    assert "phase_391_override_required=human" in result.stdout
    assert "phase_391_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_full_run_enforces_blocked_exit_and_snapshot_isolation(tmp_path: Path) -> None:
    if os.environ.get("ILC_PHASE_391_GATE_SELFTEST") == "1":
        pytest.skip("phase_391_selftest_context_skip_verdict_simulation")
    env, canonical, canonical_mtime, canonical_sha = _snapshot_override_env(tmp_path, "blocked")
    result = _run_gate([], env=env)
    assert result.returncode == 1
    assert "phase_391_snapshot_gate=failed" in result.stdout
    assert SNAPSHOT_PATH.read_bytes() == canonical
    assert SNAPSHOT_PATH.stat().st_mtime_ns == canonical_mtime
    assert hashlib.sha256(SNAPSHOT_PATH.read_bytes()).hexdigest() == canonical_sha


def test_gate_assertions_and_handoff_contract_tokens() -> None:
    assert RATIFICATION_PATH.exists()
    ratification_text = RATIFICATION_PATH.read_text(encoding="utf-8")
    assert (
        "CDL-039 ratification removes creator_agent_id from the CDL-036 Transport Envelope candidate header field set;"
        in ratification_text
    )
    calibration_section = _extract_calibration_section(ratification_text)
    assert "bounded_range" not in calibration_section

    assert "no creator_agent_id in transport headers, opaque channel routing field, and cluster membership non-inferrability." in GOSSIP_PATH.read_text(
        encoding="utf-8"
    )

    assert CDL_V1_DEPENDENCY == "cdl_v1_temporal_decay_388.v0.1"
    assert CDL_V2_DEPENDENCY == "cdl_v2_sybil_resistance_389.v0.1"

    coherence_text = COHERENCE_PATH.read_text(encoding="utf-8")
    assert (
        "CDL-039 ratification created a named forward obligation: retention_epochs operational value requires a subsequent CDL amendment before deployment. This amendment must be opened as the first constitutional action of Window 392+."
        in coherence_text
    )
    assert (
        "Wallet-agnostic signing carry-forward remains active: ILC protocol signing is wallet-agnostic, signer-lineage lifecycle is protocol-layer, and signing-provider key custody remains an operator concern."
        in coherence_text
    )

    capsule_text = CAPSULE_PATH.read_text(encoding="utf-8")
    assert (
        "Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern."
        in capsule_text
    )

    decision_log_text = Path(DECISION_LOG_PATH).read_text(encoding="utf-8")
    row_match = re.search(r"^\| CDL-039 \|.*$", decision_log_text, flags=re.MULTILINE)
    assert row_match is not None, "phase_391_cdl_039_row_missing"
    row = row_match.group(0)
    assert "| ratified |" in row
    for token in ("ratified_phase:", "ratified_date:", "evidence_document:"):
        assert token in row

    assert HANDOFF_PATH.exists()
    handoff_text = HANDOFF_PATH.read_text(encoding="utf-8")
    for heading in (
        "## 1. Window summary (378-391 completion state)",
        "## 2. Deliverable matrix for phases 378-390",
        "## 3. Closure-gate category evidence",
        "## 4. Constitutional and runtime closure summary",
        "## 5. Window-392+ start boundary",
        "## 6. Monitoring snapshot isolation controls",
        "## 7. Carry-forward risks and controls",
        "## 8. Canonical anchors and next-window pointer",
    ):
        assert heading in handoff_text

    for token in (
        "CDL-039 is ratified as of Phase 379 with calibration constants locked.",
        "CDL-040, CDL-041, CDL-043 prelocks are complete and non-ratifying.",
        "D2d wire protocol enforcement is active in ilc_core/network/d2d/.",
        "CDL-V1 temporal decay and CDL-V2 sybil resistance are implemented.",
        "CDL-039 ratification created a named forward obligation: retention_epochs operational value requires a subsequent CDL amendment before deployment. This amendment must be opened as the first constitutional action of Window 392+.",
        "Wallet-agnostic signing carry-forward remains active across coherence and capsule handoff artifacts.",
        "No decision-log mutation occurred in Phase 391.",
        "No new ilc_core runtime feature implementation occurred in Phase 391.",
        "Window 392+ begins with CDL-040/041/043 ratification planning, CDL-042 opening, and CDL-V3/V7 governance resolution.",
        "docs/specs/ilc_phase_378_391_sequence_lock_v0.1.md",
        "docs/specs/ilc_cdl_039_p2p_transport_and_topology_privacy_ratification_evidence_379_v0.1.md",
        "docs/specs/ilc_integration_coherence_report_390_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.3.md",
        "git restore out/monitoring/infrastructure_risk_snapshot_phase_316.json",
    ):
        assert token in handoff_text


def test_no_decision_log_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_391_GATE_SELFTEST") == "1":
        pytest.skip("phase_391_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_391_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_ilc_core_runtime_feature_mutation_in_phase_commit() -> None:
    if os.environ.get("ILC_PHASE_391_GATE_SELFTEST") == "1":
        pytest.skip("phase_391_selftest_context_skip_commit_guardrails")
    commit_ref = _resolve_phase_391_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_391_runtime_feature_mutations:{forbidden}"
