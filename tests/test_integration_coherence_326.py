from __future__ import annotations

import hashlib
import os
import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_326_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v0.7.md")
SEQUENCING_PATH = Path("docs/specs/ilc_cdl_v_ratification_sequencing_326_v0.1.md")
GATE_PATH = Path("tools/check_window_308_317_closure_gate_phase_317.sh")
SNAPSHOT_PATH = Path("out/monitoring/infrastructure_risk_snapshot_phase_316.json")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_326_COMMIT_SUBJECT = "docs(g8): phase 326 coherence, capsule v0.7, and v-series sequencing"



def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")



def _run_gate(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(GATE_PATH)] + args, capture_output=True, text=True, env=env, check=False)


def _clean_phase_317_gate_env() -> dict[str, str]:
    blocked = {
        "ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE",
        "ILC_PHASE_316_SNAPSHOT_PATH",
        "ILC_PHASE_317_SNAPSHOT_PATH",
        "ILC_PHASE_317_GATE_SELFTEST",
        "ILC_PHASE_327_GATE_SELFTEST",
        "ILC_PHASE_327_SNAPSHOT_PATH",
    }
    return {key: value for key, value in os.environ.items() if key not in blocked}


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}



def _resolve_phase_326_commit_ref() -> str:
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
        if subject.strip() == PHASE_326_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(COHERENCE_PATH),
        str(CAPSULE_PATH),
        str(SEQUENCING_PATH),
        "tests/test_integration_coherence_326.py",
        str(GATE_PATH),
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_326_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_326_commit_not_present_in_local_history")



def test_coherence_artifact_exists_and_has_required_rules() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)

    for heading in (
        "## 1. Scope",
        "## 2. Window 318-325 completion alignment",
        "## 3. Snapshot isolation remediation",
        "## 4. Evidence-authority rule",
        "## 5. V-series ratification implications",
        "## 6. Non-goals and explicit boundaries",
    ):
        assert heading in text

    for token in (
        "future CDL-V ratification prompts must treat Section 3 of the corresponding evidence-prelock artifact as authoritative",
        "the CDL row `required_artifacts` field is shorthand and does not override more specific Section-3 evidence obligations",
        "Phase-327 is closure only and is not the place to repair closure-gate mechanics",
        "`CDL-020` is `ratified`",
        "`CDL-024` remains `open`",
        "`CDL-V1` through `CDL-V7` are `open`",
        "no additional constitutional mutations occurred in Phase 326",
    ):
        assert token in text



def test_capsule_v0_7_supersedes_v0_6_and_contains_required_sections() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)

    for token in (
        "Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.6.md`",
        "## 4. Window 318-325 Constitutional State",
        "## 5. CDL-V Ratification Authority Rule",
        "## 6. CDL-V Ratification Sequencing",
        "## 7. Phase-317 Snapshot Isolation Remediation",
        "`CDL-020`, `CDL-022`, and `CDL-023` are ratified",
        "`CDL-024` remains open",
        "`CDL-V1` through `CDL-V7` are open",
        "future CDL-V ratification prompts must treat Section 3 of the corresponding evidence-prelock artifact as authoritative",
    ):
        assert token in text



def test_v_series_sequencing_artifact_contains_exact_directional_and_boundary_tokens() -> None:
    assert SEQUENCING_PATH.exists()
    text = _read(SEQUENCING_PATH)

    for heading in (
        "## 1. Scope",
        "## 2. Ordering constraints",
        "## 3. Boundary-coupling rules",
        "## 4. Explicit non-dependencies",
        "## 5. Carry-forward ratification requirements",
        "## 6. Non-goals",
    ):
        assert heading in text

    for token in (
        "CDL-V2 -> CDL-V3 -> CDL-V4",
        "CDL-V5 -> CDL-V7",
        "CDL-V4 <-> CDL-V6",
        "CDL-V1 has no V-series ordering constraint",
        "non-comparable by design",
        "tested graph-entry and reuse-value tie-back requirements",
        "concrete evaluation protocol with explicit tolerance bounds",
    ):
        assert token in text



def test_phase_317_gate_is_no_write_by_default_and_opt_in_write_uses_override_only(tmp_path: Path) -> None:
    canonical_before = SNAPSHOT_PATH.read_bytes()
    canonical_hash_before = hashlib.sha256(canonical_before).hexdigest()
    canonical_mtime_before = SNAPSHOT_PATH.stat().st_mtime_ns

    result = _run_gate([], env=_clean_phase_317_gate_env())
    assert result.returncode == 0
    assert "phase_317_verdict=pass" in result.stdout

    canonical_after = SNAPSHOT_PATH.read_bytes()
    canonical_hash_after = hashlib.sha256(canonical_after).hexdigest()
    canonical_mtime_after = SNAPSHOT_PATH.stat().st_mtime_ns
    assert canonical_hash_after == canonical_hash_before
    assert canonical_mtime_after == canonical_mtime_before

    override_path = tmp_path / "phase_316_override_snapshot.json"
    env = _clean_phase_317_gate_env()
    env["ILC_PHASE_317_ALLOW_SNAPSHOT_WRITE"] = "1"
    env["ILC_PHASE_316_SNAPSHOT_PATH"] = str(override_path)
    result_override = _run_gate([], env=env)
    assert result_override.returncode == 0
    assert override_path.exists()

    canonical_after_override = SNAPSHOT_PATH.read_bytes()
    canonical_hash_after_override = hashlib.sha256(canonical_after_override).hexdigest()
    canonical_mtime_after_override = SNAPSHOT_PATH.stat().st_mtime_ns
    assert canonical_hash_after_override == canonical_hash_before
    assert canonical_mtime_after_override == canonical_mtime_before



def test_no_decision_log_mutation_in_phase_326_commit() -> None:
    commit_ref = _resolve_phase_326_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed



def test_no_ilc_core_runtime_mutation_in_phase_326_commit() -> None:
    commit_ref = _resolve_phase_326_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_326_runtime_mutations:{forbidden}"
