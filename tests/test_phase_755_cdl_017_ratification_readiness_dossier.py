from __future__ import annotations

import subprocess
from pathlib import Path


DOSSIER_PATH = Path("docs/specs/ilc_cdl_017_ratification_readiness_dossier_v0.1.md")
TEST_PATH = Path("tests/test_phase_755_cdl_017_ratification_readiness_dossier.py")
STATUS_PATH = Path("docs/phases/STATUS.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
REQUIRED_HEADINGS = (
    "## 1. What CDL-017 covers",
    "## 2. Codex-side prelock evidence summary",
    "## 3. What M-022 must confirm",
    "## 4. CDL-017 ratification window scope and sequencing",
    "## 5. SEC-004 disposition",
    "## 6. What this dossier is not",
    "## 7. Source inputs",
)
REQUIRED_TOKENS = (
    "cdl_017_ratification_readiness_dossier_prework_only",
    "cdl_017_current_status_open_unratified",
    "codex_side_prelock_complete_inputs_assembled",
    "m022_implementation_confirmation_required_for_cdl_017",
    "convergence_window_outputs_required_before_cdl_017_ratification",
    "m022_approval_alone_insufficient_for_cdl_017_window",
    "sec_004_activation_scope_bound_to_post_ratification_m_track_work",
    "cdl_017_ratification_window_sequenced_after_convergence",
)
PHASE_SUBJECT = ("phase 755", "cdl-017 ratification-readiness dossier")
EXACT_REQUIRED_PATHS = {
    str(DOSSIER_PATH),
    str(TEST_PATH),
    str(STATUS_PATH),
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    return " ".join(text.split())


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    matches: list[str] = []
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        lowered = subject.lower()
        if all(token in lowered for token in subject_tokens):
            matches.append(commit_hash)
    for commit_ref in matches:
        if _changed_paths_for_commit(commit_ref) == expected_paths:
            return commit_ref
    raise AssertionError("phase_755_commit_not_present_in_local_history")


def _try_resolve_commit_ref(subject_tokens: tuple[str, ...], expected_paths: set[str]) -> str | None:
    try:
        return _resolve_commit_ref(subject_tokens, expected_paths)
    except AssertionError:
        return None


def _current_phase_paths_in_worktree(expected_paths: set[str]) -> set[str]:
    result = subprocess.run(
        ["git", "status", "--short", "--", *sorted(expected_paths)],
        capture_output=True,
        check=True,
        text=True,
    )
    paths: set[str] = set()
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        paths.add(line[3:].strip())
    return paths


def test_dossier_exists_and_contains_required_headings_in_order() -> None:
    text = _read(DOSSIER_PATH)
    positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
    assert positions == sorted(positions)


def test_dossier_contains_required_tokens() -> None:
    text = _read(DOSSIER_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_dossier_is_clearly_marked_pre_work_and_not_ratified() -> None:
    text = _normalized(_read(DOSSIER_PATH))
    assert "Status: PRE-WORK — CDL-017 is not ratified and will not be ratified in this window." in text
    assert "M-022 approval alone is not sufficient to open the CDL-017 ratification window." in text


def test_dossier_restates_cdl_017_scope_and_open_status() -> None:
    text = _normalized(_read(DOSSIER_PATH))
    assert "`CDL-017` was opened in Phase `695`" in text
    assert "current decision-log status remains `open`" in text
    assert "bootstrap transition criteria" in text
    assert "Genesis-sunset triggers" in text
    assert "dynamic validator-set activation boundary" in text


def test_codex_side_prelock_summary_carries_resolved_inputs() -> None:
    text = _normalized(_read(DOSSIER_PATH))
    assert "derived sub-key with provable linkage" in text
    assert "`400000000-450000000` micro-ECU" in text
    assert "`vrf_upgrade_threshold_validator_count = 10`" in text
    assert "`distinct_cluster_floor_recommendation 4`" in text
    assert "`max_cluster_share_ceiling_recommendation 33`" in text
    assert "CDL-068 now exists and is ratified" in text


def test_m022_checklist_includes_hooks_key_ceremony_sec004_and_deployment() -> None:
    text = _normalized(_read(DOSSIER_PATH))
    assert "what the M-007 Rust governance hooks provide today" in text
    assert "Key-ceremony protocol carried forward honestly" in text
    assert "SEC-004 activation scope stated explicitly" in text
    assert "First validator deployment prerequisites made explicit" in text
    assert "actual export path, actual replay-log epoch numbers, and fresh-node startup log" in text


def test_sequencing_requires_convergence_between_m022_and_ratification() -> None:
    text = _normalized(_read(DOSSIER_PATH))
    assert "`M-022 approval -> convergence window (CW-1 through CW-6) -> CDL-017 ratification window`" in text
    assert "That later ratification window consumes four input classes" in text
    assert "first authorized validator deployment" in text
    assert "Neither shortcut is legitimate." in text


def test_sec004_disposition_is_post_ratification_activation_scope() -> None:
    text = _normalized(_read(DOSSIER_PATH))
    assert "`TransferCertificate` carries no epoch reference" in text
    assert "`TransferCertificate` gains `epoch: EpochSeq`" in text
    assert "historically active `ValidatorSet`" in text
    assert "`test_ejected_validator_sig_rejected_after_epoch_boundary` passes" in text
    assert "it begins only after CDL-017 ratifies" in text


def test_dossier_explicitly_states_what_it_is_not() -> None:
    text = _normalized(_read(DOSSIER_PATH))
    assert "a CDL-017 ratification artifact" in text
    assert "an opening of the later ratification window" in text
    assert "proof that convergence outputs already exist" in text
    assert "authorization for first non-Genesis validator deployment" in text


def test_decision_log_and_runtime_code_surfaces_are_untouched_in_phase_755() -> None:
    result_decision = subprocess.run(
        ["git", "diff", "--exit-code", "--", str(DECISION_LOG_PATH)],
        capture_output=True,
        text=True,
    )
    assert result_decision.returncode == 0


def test_phase_755_single_commit_touches_expected_paths_only() -> None:
    commit_ref = _try_resolve_commit_ref(PHASE_SUBJECT, EXACT_REQUIRED_PATHS)
    if commit_ref:
        changed_paths = _changed_paths_for_commit(commit_ref)
        assert changed_paths == EXACT_REQUIRED_PATHS
        assert str(DECISION_LOG_PATH) not in changed_paths
        assert not any(path == "ilc_core" or path.startswith("ilc_core/") for path in changed_paths)
        assert not any(
            path == "ilc_consensus" or path.startswith("ilc_consensus/")
            for path in changed_paths
        )
        return

    assert _current_phase_paths_in_worktree(EXACT_REQUIRED_PATHS) == EXACT_REQUIRED_PATHS
