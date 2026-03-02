from __future__ import annotations

import subprocess
from pathlib import Path


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_336_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v0.8.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
PHASE_336_COMMIT_SUBJECT = "docs(g8): phase 336 coherence and capsule v0.8"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_336_commit_ref() -> str:
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
        if subject.strip() == PHASE_336_COMMIT_SUBJECT:
            matching_commits.append(commit_hash)

    required_paths = {
        str(COHERENCE_PATH),
        str(CAPSULE_PATH),
        "tests/test_integration_coherence_336.py",
    }
    for commit_ref in matching_commits:
        changed_paths = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed_paths):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_336_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_336_commit_not_present_in_local_history")


def test_coherence_report_has_required_sections_and_tokens() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)

    for heading in (
        "## 1. Scope",
        "## 2. Window 328-335 ratification alignment",
        "## 3. Evaluation panel architecture canonicalization",
        "## 4. L-tier disambiguation and governance boundary",
        "## 5. ADM-003 carry-forward gap",
        "## 6. V-series closure and deferred inventory",
        "## 7. Non-goals and explicit boundaries",
    ):
        assert heading in text

    for token in (
        "CDL-024 (Phase 329)",
        "CDL-V1 (Phase 330)",
        "CDL-V2 (Phase 331)",
        "CDL-V3 (Phase 332)",
        "CDL-V5 (Phase 333)",
        "CDL-V4 + CDL-V6 (Phase 334)",
        "CDL-V7 (Phase 335)",
        "All V-series CDLs are now ratified; only CDL-021 remains open.",
        "CDL-021 remains open and milestone-triggered/deferred.",
        "panel_size=8",
        "independence_k=3",
        "outsider_seat=true",
        "Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat",
        "quorum k=5 of m=7",
        "VRF-selected outsider seat",
        "VRF-selected outsider seat is the anti-capture mechanism",
        "trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2",
        "CDL-V3 cluster diversity floor operationalizes independence_k=3",
        "CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism",
        "The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.",
        "L0=3 is architecturally safe because CDL-V7's Popperian gate ensures L0 basic statements are independently and directly verifiable.",
        "Low quorum is a design pressure toward correct decomposition granularity, not a shortcut.",
        "The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.",
        "Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention, not by evaluation-panel quorum vote.",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md currently omits the 7+1 evaluation panel as an agent behavioral role.",
        "This gap must be resolved before Window 338+ implementation begins.",
    ):
        assert token in text


def test_capsule_v0_8_has_required_sections_and_tokens() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)

    for heading in (
        "## 1. Project Identity",
        "## 2. Core Architectural Invariants",
        "## 3. Project State (as of Phase 336 completion)",
        "## 4. Window 328-335 Constitutional State",
        "## 5. Evaluation Panel Architecture",
        "## 6. L-Tier Disambiguation",
        "## 7. CDL-V Authority and Sequencing Carry-Forward",
        "## 8. ADM-003 Carry-Forward Gap",
        "## 9. Implementation Frontier",
        "## 10. Key Canonical Anchors",
    ):
        assert heading in text

    for token in (
        "Supersedes: `docs/specs/ilc_antigravity_context_capsule_v0.7.md`",
        "Phase 336 complete",
        "Phase 337 next",
        "Window 328-337 closure lane remains pending.",
        "CDL-024 is ratified.",
        "CDL-V1 through CDL-V7 are ratified.",
        "CDL-021 remains open and milestone-triggered/deferred.",
        "panel_size=8",
        "independence_k=3",
        "outsider_seat=true",
        "Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat",
        "quorum k=5 of m=7",
        "VRF-selected outsider seat",
        "VRF-selected outsider seat is the anti-capture mechanism",
        "trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2",
        "CDL-V3 cluster diversity floor operationalizes independence_k=3",
        "CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism",
        "The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.",
        "The 7+1 panel quorum mechanism governs knowledge claim evaluation for task outputs, decomposition validity, and ILC attribution; it does not govern constitutional or genesis-layer protocol changes.",
        "Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention.",
        "CDL-V2 -> CDL-V3 -> CDL-V4",
        "CDL-V4 <-> CDL-V6",
        "CDL-V5 -> CDL-V7",
        "CDL-V1 has no V-series ordering constraint",
        "docs/specs/ilc_adm_001_protocol_native_bundle_distribution_v0.2.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md currently omits the 7+1 evaluation panel as an agent behavioral role.",
        "This gap must be resolved before Window 338+ implementation begins.",
    ):
        assert token in text


def test_ratification_summary_tokens_are_complete() -> None:
    coherence_text = _read(COHERENCE_PATH)
    capsule_text = _read(CAPSULE_PATH)

    for token in (
        "CDL-024 (Phase 329)",
        "CDL-V1 (Phase 330)",
        "CDL-V2 (Phase 331)",
        "CDL-V3 (Phase 332)",
        "CDL-V5 (Phase 333)",
        "CDL-V4 + CDL-V6 (Phase 334)",
        "CDL-V7 (Phase 335)",
        "All V-series CDLs are now ratified; only CDL-021 remains open.",
    ):
        assert token in coherence_text

    for token in (
        "CDL-024 is ratified.",
        "CDL-V1 through CDL-V7 are ratified.",
        "CDL-021 remains open and milestone-triggered/deferred.",
    ):
        assert token in capsule_text


def test_panel_and_adm_gap_tokens_are_present_in_both_artifacts() -> None:
    coherence_text = _read(COHERENCE_PATH)
    capsule_text = _read(CAPSULE_PATH)

    shared_tokens = (
        "panel_size=8",
        "independence_k=3",
        "outsider_seat=true",
        "Quorum: k=5 of m=7 reviewers with VRF-selected outsider seat",
        "quorum k=5 of m=7",
        "VRF-selected outsider seat",
        "VRF-selected outsider seat is the anti-capture mechanism",
        "trust-tier quorum ladder: L0=3, L1=5, L2=7, L3=9, appeals escalate by +2",
        "CDL-V3 cluster diversity floor operationalizes independence_k=3",
        "CDL-V7 Popperian gate is the test specification; the 7+1 panel is the testing mechanism",
        "The quorum ladder L-tiers correspond to graph epistemic tiers, not protocol/genesis-layer authority tiers and not agent reputation tiers.",
        "task outputs, decomposition validity, and ILC attribution",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.1.md currently omits the 7+1 evaluation panel as an agent behavioral role.",
        "This gap must be resolved before Window 338+ implementation begins.",
    )
    for token in shared_tokens:
        assert token in coherence_text
        assert token in capsule_text

    assert "Low quorum is a design pressure toward correct decomposition granularity, not a shortcut." in coherence_text
    assert (
        "Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention, not by evaluation-panel quorum vote."
        in coherence_text
    )
    assert (
        "Genesis and constitutional changes are governed by the CDL process plus Genesis-epoch founder authority (CDL-023), CDL-V4 reopening protocol, and CDL-V6 emergency intervention."
        in capsule_text
    )


def test_no_decision_log_mutation_in_phase_336_commit() -> None:
    commit_ref = _resolve_phase_336_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_no_ilc_core_runtime_mutation_in_phase_336_commit() -> None:
    commit_ref = _resolve_phase_336_commit_ref()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_336_runtime_mutations:{forbidden}"
