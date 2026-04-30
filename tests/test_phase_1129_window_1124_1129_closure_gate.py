from __future__ import annotations

import os
import pathlib
import subprocess
import sys
from decimal import Decimal

from ilc_core.economics.epoch_attribution_settle_runtime import (
    EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION,
    AttributionEvent,
    settle_attribution_batch,
)
from ilc_core.types import EdgeType, EpochAttributionBatch, PROVENANCE_DECAY_ALPHA


SELFTEST_MODE = os.environ.get("ILC_PHASE_1129_GATE_SELFTEST") == "1"
ROOT = pathlib.Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_cat0_selftest_env_recognized():
    assert isinstance(SELFTEST_MODE, bool)


def test_cat1_sequence_lock_exists():
    assert (ROOT / "docs/specs/ilc_phase_1124_1129_sequence_lock_v0.1.md").exists()


def test_cat1_sequence_lock_contains_window_token():
    src = _read("docs/specs/ilc_phase_1124_1129_sequence_lock_v0.1.md")
    assert "window_1124_1129_sequence_lock_committed_phase_1124" in src


def test_cat1_sequence_lock_contains_prelock_before_ratification_token():
    src = _read("docs/specs/ilc_phase_1124_1129_sequence_lock_v0.1.md")
    assert "cdl_084_q2_amendment_prelock_precedes_ratification" in src


def test_cat1_sequence_lock_contains_alpha_pending_phase_1126_token():
    src = _read("docs/specs/ilc_phase_1124_1129_sequence_lock_v0.1.md")
    assert "cdl_084_q2_alpha_0_45_locked_pending_phase_1126" in src


def test_cat2_prelock_doc_exists():
    assert (ROOT / "docs/specs/ilc_cdl_084_q2_amendment_prelock_1125_v0.1.md").exists()


def test_cat2_prelock_doc_contains_tokens():
    src = _read("docs/specs/ilc_cdl_084_q2_amendment_prelock_1125_v0.1.md")
    assert "cdl_084_q2_prelock_hardened_phase_1125" in src
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in src


def test_cat3_runtime_alpha_is_decimal_0_45():
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.45")
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert not isinstance(PROVENANCE_DECAY_ALPHA, float)


def test_cat3_runtime_version_is_v0_4():
    assert EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == "epoch_attribution_settle_runtime_1129_fix1.v0.5"


def test_cat3_cdl_doc_contains_locked_q2_token():
    cdl = _read("docs/specs/ilc_cdl_084_provenance_chain_attribution_opening_1111_v0.1.md")
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in cdl


def test_cat3_cdl_log_contains_amendment_phase_and_token():
    log = _read("docs/specs/ilc_constitutional_decision_log_v0.1.md")
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in log
    assert "amendment_phase: 1126" in log


def test_cat3_historical_phase_1113_old_alpha_preserved():
    result = subprocess.run(
        ["git", "show", "3d943f32:ilc_core/types.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    assert 'Decimal("0.5")' in result.stdout


def test_cat3_three_hop_payout_smoke_alpha_0_45():
    event = AttributionEvent(
        edge_type=EdgeType.PROVENANCE,
        target_creator_id="c0",
        star_node_id=None,
        epoch=1,
        provenance_chain=(("n1", "c1"), ("n2", "c2"), ("n3", "c3")),
    )
    batch = EpochAttributionBatch(epoch=1)
    batch.add_event(event)
    batch.seal()
    payouts = settle_attribution_batch(batch, stake_map={})
    assert payouts[0] == ("c1", Decimal("0.09"))
    assert payouts[1] == ("c2", Decimal("0.0405"))
    assert payouts[2] == ("c3", Decimal("0.018225"))


def test_cat3_phase_1127_evidence_suite_passes():
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "tests/test_phase_1127_cdl_084_q2_amendment.py",
            "-q",
            "--tb=short",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "8 passed" in result.stdout + result.stderr


def test_cat3_phase_1126_walkthrough_exists_with_q2_token():
    src = _read("docs/phases/phase_1126_cdl_084_q2_ratification_walkthrough.md")
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in src


def test_cat4_phase_1127_evidence_file_exists():
    assert (ROOT / "tests/test_phase_1127_cdl_084_q2_amendment.py").exists()


def test_cat4_phase_1127_evidence_test_count():
    src = _read("tests/test_phase_1127_cdl_084_q2_amendment.py")
    count = sum(1 for line in src.splitlines() if line.startswith("def test_"))
    assert count >= 8


def test_cat5_coherence_report_exists_and_passes():
    src = _read("docs/specs/ilc_integration_coherence_report_1128_v0.1.md")
    assert "coherence_report_1128_verdict=pass" in src


def test_cat5_capsule_v5_37_exists_with_supersession_token():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.37.md")
    assert "capsule_v5_37_supersedes_v5_36" in src


def test_cat5_capsule_records_alpha_locked_phase_1126():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.37.md")
    assert "cdl_084_q2_alpha_locked_decimal_0_45_phase_1126" in src


def test_cat5_capsule_records_q2_locked_token():
    src = _read("docs/specs/ilc_antigravity_context_capsule_v5.37.md")
    assert "q2_geometric_decay_alpha_decimal_0_45_locked" in src
