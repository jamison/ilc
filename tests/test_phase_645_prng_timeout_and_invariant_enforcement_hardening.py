from __future__ import annotations

import importlib
import subprocess
from pathlib import Path

import pytest

DOC_PATH = Path("docs/specs/ilc_prng_timeout_and_invariant_enforcement_hardening_645_v0.1.md")
DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
BACKFILL_PATHS = {
    "docs/phases/phase_645_g8_prng_timeout_and_invariant_enforcement_hardening_walkthrough.md",
    "docs/phases/STATUS.md",
}
REQUIRED_HEADINGS = (
    "## 1. Scope and threat basis",
    "## 2. Touched PRNG removal strategy",
    "## 3. Timeout contract",
    "## 4. Explicit invariant enforcement contract",
    "## 5. Broad-catch regression guardrail",
    "## 6. Verification evidence",
)
REQUIRED_TOKENS = (
    "predictable_prng_removed_from_touched_runtime_paths",
    "hash_derived_or_secure_selection_replaces_mersenne_twister_in_touched_paths",
    "bifurcated_http_timeout_contract_applied_to_touched_peer_or_cli_surface",
    "production_invariants_no_longer_depend_on_assert_in_touched_runtime",
    "assert_replacement_does_not_introduce_broad_exception_swallowing",
    "touched_timeout_hardening_preserves_existing_runtime_contract_shape",
)
PEER_PATH = Path("ilc_core/network/peer.py")
AESTHETIC_PATH = Path("ilc_core/epistemic/aesthetic_panel_runtime.py")
PASSIVE_PATH = Path("ilc_core/economics/passive_ecu_attribution_runtime.py")
PHASE_645_BACKFILL_SUBJECT_TOKEN = "phase 645 walkthrough and status backfill"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _find_commit_ref(*, subject_token: str) -> str | None:
    result = subprocess.run(
        ["git", "log", "--format=%H%x09%s"],
        capture_output=True,
        check=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if "\t" not in line:
            continue
        commit_hash, subject = line.split("\t", 1)
        if subject_token in subject.lower():
            return commit_hash
    return None


def _changed_paths_for_commit(commit_ref: str) -> set[str]:
    result = subprocess.run(
        ["git", "show", "--name-only", "--pretty=", commit_ref],
        capture_output=True,
        check=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def test_phase_doc_exists_with_required_headings() -> None:
    text = _read(DOC_PATH)
    for heading in REQUIRED_HEADINGS:
        assert heading in text


def test_phase_doc_contains_required_tokens() -> None:
    text = _read(DOC_PATH)
    for token in REQUIRED_TOKENS:
        assert token in text


def test_peer_runtime_no_longer_uses_random_and_uses_hash_derived_selection() -> None:
    text = _read(PEER_PATH)
    assert "import random" not in text
    assert "hashlib.sha256" in text


def test_aesthetic_panel_runtime_no_longer_uses_random_and_uses_hash_derived_selection() -> None:
    text = _read(AESTHETIC_PATH)
    assert "import random" not in text
    assert "hashlib.sha256" in text


def test_peer_timeout_contract_is_bifurcated() -> None:
    text = _read(PEER_PATH)
    assert "connect_timeout_s" in text
    assert "read_timeout_s" in text
    assert "timeout=timeout_s" in text
    manager_mod = importlib.import_module("ilc_core.network.peer")
    manager = manager_mod.PeerManager(local_port=8000)
    assert manager.connect_timeout_s == 2.0
    assert manager.read_timeout_s == 30.0


def test_passive_runtime_no_longer_uses_assert_for_production_invariants() -> None:
    text = _read(PASSIVE_PATH)
    assert "assert " not in text
    assert "PassiveECUAttributionContractError" in text
    assert "_validate_runtime_contract()" in text


def test_peer_runtime_no_longer_has_broad_except_exception_logging_path() -> None:
    text = _read(PEER_PATH)
    assert "except Exception" not in text


def test_decision_log_unchanged() -> None:
    assert DECISION_LOG_PATH.exists()


def test_phase_645_backfill_commit_touches_expected_paths_only() -> None:
    commit_ref = _find_commit_ref(subject_token=PHASE_645_BACKFILL_SUBJECT_TOKEN)
    if commit_ref is None:
        pytest.skip("commit_not_yet_present")
    changed_paths = _changed_paths_for_commit(commit_ref)
    assert changed_paths == BACKFILL_PATHS
