import hashlib
import os
from decimal import Decimal
from pathlib import Path

import pytest

from ilc_core.economics.epoch_attribution_settle_runtime import PROVENANCE_DECAY_ALPHA
from ilc_core.network.d2d import persistent_fetch_rate_limiter_runtime as rate_limiter
from ilc_core.node import tier3_runtime_linkage_runtime as tier3


SELFTEST_MODE = os.environ.get("ILC_PHASE_1208_GATE_SELFTEST") == "1"

SEQ_LOCK = Path("docs/specs/ilc_phase_1200_1208_sequence_lock_v0.1.md")
DELIBERATION = Path("docs/specs/ilc_cdl_086_deliberation_1203_v0.1.md")
PRELOCK = Path("docs/specs/ilc_cdl_086_prelock_spec_1204_v0.1.md")
SIGNING_SKIP = Path("docs/phases/phase_1205_v0_2_signing_ceremony_walkthrough.md")
PERMANENCE = Path("docs/specs/ilc_truth_primitive_permanence_governance_1206_v0.1.md")
COHERENCE = Path("docs/specs/ilc_integration_coherence_report_1207_v0.1.md")
CAPSULE = Path("docs/specs/ilc_antigravity_context_capsule_v5.46.md")
HANDOFF = Path("docs/specs/ilc_window_1200_1208_handoff_1208_v0.1.md")
STATUS = Path("docs/phases/STATUS.md")
PLANNING_INDEX = Path("docs/PLANNING_INDEX.md")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_cat0_selftest_env_required() -> None:
    if not SELFTEST_MODE:
        pytest.skip("ILC_PHASE_1208_GATE_SELFTEST not set — skip in regression mode")
    assert SELFTEST_MODE is True


def test_cat1_sequence_lock_exists_and_token_present() -> None:
    content = SEQ_LOCK.read_text(encoding="utf-8")
    assert "window_1200_1208_sequence_lock_committed" in content


def test_cat2_tier3_runtime_version_contains_1201() -> None:
    assert "1201" in tier3.TIER3_RUNTIME_LINKAGE_VERSION


def test_cat3_tier3_validators_callable() -> None:
    assert callable(tier3.validate_schema_node)
    assert callable(tier3.validate_runtime_node)


def test_cat4_persistent_rate_limiter_version_contains_1202() -> None:
    assert "1202" in rate_limiter.PERSISTENT_RATE_LIMITER_VERSION


def test_cat5_persistent_rate_limiter_save_load_callable() -> None:
    assert callable(rate_limiter.PersistentFetchRateLimiter.save)
    assert callable(rate_limiter.PersistentFetchRateLimiter.load)


def test_cat6_cdl_086_deliberation_token_present() -> None:
    assert "cdl_086_deliberation_committed_phase_1203" in DELIBERATION.read_text(
        encoding="utf-8"
    )


def test_cat7_cdl_086_prelock_or_deferred_token_present() -> None:
    content = PRELOCK.read_text(encoding="utf-8")
    assert "cdl_086_prelock_committed_phase_1204" in content


def test_cat8_v0_2_signing_signed_or_deferred() -> None:
    content = SIGNING_SKIP.read_text(encoding="utf-8")
    assert "v0_2_signing_ceremony_deferred_pending_signing_authorization" in content


def test_cat9_truth_primitive_permanence_routed() -> None:
    assert "truth_primitive_permanence_governance_routed_phase_1206" in PERMANENCE.read_text(
        encoding="utf-8"
    )


def test_cat10_coherence_report_1207_exists() -> None:
    assert COHERENCE.exists()
    assert "coherence_report_1207_verdict=pass" in COHERENCE.read_text(encoding="utf-8")


def test_cat11_capsule_v5_46_exists_and_supersedes_v5_45() -> None:
    content = CAPSULE.read_text(encoding="utf-8")
    assert "capsule_v5_46_supersedes_v5_45" in content


def test_cat12_signed_genesis_v0_1_hash_unchanged_in_sequence_lock() -> None:
    content = SEQ_LOCK.read_text(encoding="utf-8")
    assert "ddc686019018e05f3d88be1a879663c7c2756823bf8bc7fbf980743a92fc6c3c" in content


def test_cat13_immutable_diagnostic_sha_matches_committed_value() -> None:
    assert (
        _sha256(Path("out/genesis_compile_coverage_diagnostic_v0.1.json"))
        == "5a67a91974e2d89ac1e40616085bbaa347893d72c7b8ba38410f0eeec81dcb56"
    )


def test_cat14_provenance_decay_alpha_unchanged() -> None:
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")


def test_cat15_handoff_closure_tokens_present() -> None:
    content = HANDOFF.read_text(encoding="utf-8")
    assert "window_1200_1208_closed_phase_1208" in content
    assert "window_1200_1208_closure_gate_verdict=pass" in content


def test_cat16_status_and_planning_closed() -> None:
    status = STATUS.read_text(encoding="utf-8")
    planning = PLANNING_INDEX.read_text(encoding="utf-8")
    assert "## Phase 1208" in status
    assert "window_1200_1208_closure_gate_verdict=pass" in status
    assert "Window 1200-1208 is CLOSED" in planning
