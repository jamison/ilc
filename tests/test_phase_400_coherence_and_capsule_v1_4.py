"""Contract tests for Phase 400 coherence and capsule v1.4 artifact set."""

from __future__ import annotations

from pathlib import Path
import subprocess


COHERENCE_PATH = Path("docs/specs/ilc_integration_coherence_report_400_v0.1.md")
CAPSULE_PATH = Path("docs/specs/ilc_antigravity_context_capsule_v1.4.md")
ADM_PATH = Path("docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md")
DECISION_LOG_PATH = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SUBJECT_TOKEN = "docs(g8): phase 400 coherence and capsule v1.4"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_coherence_artifact_exists_with_required_headings() -> None:
    assert COHERENCE_PATH.exists()
    text = _read(COHERENCE_PATH)
    for heading in (
        "## 1. Scope and non-ratifying boundary",
        "## 2. Constitutional settlement state (CDL-039/040/041/043/044)",
        "## 3. V-series runtime implementation state",
        "## 4. Historical-test hardening continuity",
        "## 5. Runtime-integrity carry-forward note",
        "## 6. Wallet-agnostic signing and boundary continuity",
        "## 7. Window-401 closure readiness and 402+ forward boundary",
        "## 8. Non-goals and canonical anchors",
    ):
        assert heading in text


def test_coherence_contains_required_tokens_and_coverage() -> None:
    text = _read(COHERENCE_PATH)
    for token in (
        "CDL-044 ratification closes the named CDL-039 retention_epochs forward obligation.",
        "No decision-log mutation occurred. No ilc_core runtime files were changed.",
        "Wallet-agnostic signing carry-forward remains active: ILC protocol signing is wallet-agnostic, signer-lineage lifecycle is protocol-layer, and signing-provider key custody remains an operator concern.",
        "Runtime-integrity note: CDL-V1/V2/V3/V7 validators reject non-finite numeric inputs (NaN/Inf).",
        "ADM-003 interface-contract closure is now explicitly anchored at `docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md`.",
        "`CDL_V2_DEPENDENCY` imports `CDL_V1_DEPENDENCY`,",
        "`CDL_V3_DEPENDENCY` imports `CDL_V2_DEPENDENCY`,",
        "`CDL_V7` runtime imports `CDL_V3_DEPENDENCY`.",
        "CDL-039",
        "CDL-040",
        "CDL-041",
        "CDL-043",
        "CDL-044",
    ):
        assert token in text


def test_capsule_v1_4_exists_self_contained_and_supersedes_v1_3() -> None:
    assert CAPSULE_PATH.exists()
    text = _read(CAPSULE_PATH)
    assert "Supersedes: docs/specs/ilc_antigravity_context_capsule_v1.3.md" in text
    assert "This capsule is self-contained." in text
    for heading in (
        "## 1. Project identity",
        "## 2. Core architectural invariants",
        "## 3. Project state (as of Phase 400 completion)",
        "## 4. Constitutional ratification state",
        "## 5. Runtime implementation state",
        "## 6. Runtime-integrity and validation guarantees",
        "## 7. Wallet-agnostic signing continuity",
        "## 8. Window 401 and 402+ forward boundary",
        "## 9. Change log from v1.3",
        "## 10. Key canonical anchors",
    ):
        assert heading in text


def test_capsule_contains_required_state_and_boundary_tokens() -> None:
    text = _read(CAPSULE_PATH)
    for token in (
        "CDL-044 is ratified as of Phase 399 and closes the retention_epochs constitutional amendment obligation created by CDL-039 ratification.",
        "CDL-V1 temporal decay, CDL-V2 sybil resistance, CDL-V3 diversity floor, and CDL-V7 Popperian gate are computationally enforced.",
        "Runtime-integrity note: V-series validators reject non-finite numeric inputs (NaN/Inf).",
        "Wallet-agnostic signing remains mandatory: signer-lineage lifecycle is protocol-layer and signing-provider key custody is an operator concern.",
        "ADM-003 v0.2 adds explicit signing-provider interface contract closure for wallet-agnostic implementation lanes.",
    ):
        assert token in text


def test_adm_003_v0_2_interface_contract_tokens_present() -> None:
    assert ADM_PATH.exists()
    text = _read(ADM_PATH)
    for token in (
        "sign_digest(kid: str, payload_hash: bytes, context: dict) -> signature_bytes",
        "resolve_public_key(kid: str) -> cose_key_or_jwk",
        'provider_capabilities() -> {"detached_signing": bool, "key_exportable": bool, "attestation": bool}',
        "The signing-provider interface is deterministic at the protocol boundary: identical (kid, payload_hash, context) input must produce verifiable detached signatures without exposing private key material to protocol state.",
    ):
        assert token in text


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def _resolve_phase_400_commit_ref_or_fail() -> str:
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
        if subject.strip().lower() == SUBJECT_TOKEN.lower():
            matching_commits.append(commit_hash)

    required_paths = {
        "docs/specs/ilc_integration_coherence_report_400_v0.1.md",
        "docs/specs/ilc_antigravity_context_capsule_v1.4.md",
        "docs/specs/ilc_adm_003_reference_agent_architecture_v0.2.md",
        "tests/test_phase_400_coherence_and_capsule_v1_4.py",
    }
    for commit_ref in matching_commits:
        changed = _changed_paths_for_commit(commit_ref)
        if required_paths.issubset(changed):
            return commit_ref

    if matching_commits:
        raise AssertionError("phase_400_commit_subject_present_but_no_qualifying_coherence_commit")
    raise AssertionError("phase_400_commit_not_present_in_local_history")


def test_phase_400_commit_touched_required_paths_and_not_decision_log() -> None:
    commit_ref = _resolve_phase_400_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    assert DECISION_LOG_PATH not in changed


def test_phase_400_commit_touched_no_ilc_core_paths() -> None:
    commit_ref = _resolve_phase_400_commit_ref_or_fail()
    changed = _changed_paths_for_commit(commit_ref)
    forbidden = [path for path in changed if path.startswith("ilc_core/")]
    assert not forbidden, f"phase_400_runtime_mutations:{forbidden}"
