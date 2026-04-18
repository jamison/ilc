"""
M-015 Workload C: Partition/Heal/Recovery — results artifact tests.

Each test anchors to a literal token from the actual run.  Generic prose
searches are avoided; only tokens that appear verbatim in the runner output
or results doc are used.
"""
import os

ARTIFACT_PATH = "docs/research/ilc_mysticeti_workload_c_results_M015_v0.1.md"


def _artifact() -> str:
    with open(ARTIFACT_PATH, "r") as f:
        return f.read()


# ── Test 1: artifact exists ────────────────────────────────────────────────────

def test_m015_artifact_exists():
    assert os.path.exists(ARTIFACT_PATH), "M-015 results artifact missing"


# ── Test 2: pre-partition epoch 1 committed by all 4 validators ───────────────

def test_m015_pre_partition_epoch1_all_four_validators():
    content = _artifact()
    for vid in [1, 2, 3, 4]:
        assert f"validator_id={vid} epoch_record_committed:epoch=1 CONFIRMED" in content, (
            f"Pre-partition epoch=1 CONFIRMED token missing for validator_id={vid}"
        )


# ── Test 3: B-side silence during partition ────────────────────────────────────
# The runner emits `m015_bside_epoch2_silence_confirmed` for each B-side validator
# that has NOT committed epoch=2 while offline.

def test_m015_bside_epoch2_silence_during_partition():
    content = _artifact()
    assert "m015_bside_epoch2_silence_confirmed" in content, (
        "B-side silence token missing — V3/V4 must not commit epoch=2 while offline"
    )
    # Must appear for both V3 and V4 (runner emits one per validator)
    assert content.count("m015_bside_epoch2_silence_confirmed") >= 2, (
        "B-side silence token must appear for both V3 and V4"
    )


# ── Test 4: post-heal B-side commits epoch 2 ──────────────────────────────────

def test_m015_post_heal_bside_epoch2_committed():
    content = _artifact()
    for vid in [3, 4]:
        assert f"validator_id={vid} epoch_record_committed:epoch=2 POST-HEAL CONFIRMED" in content, (
            f"Post-heal epoch=2 commit token missing for validator_id={vid}"
        )


# ── Test 5: recovery within 10 epochs ─────────────────────────────────────────

def test_m015_recovery_within_10_epochs():
    content = _artifact()
    assert "m015_recovery_within_10_epochs=0" in content, (
        "Recovery-time token missing or not ≤10 epochs"
    )


# ── Test 6: no-loss — epoch 1 persists after heal ─────────────────────────────

def test_m015_no_loss_epoch1_aside():
    content = _artifact()
    assert "m015_no_loss_epoch1_aside=confirmed" in content, (
        "No-loss token missing — epoch 1 must persist on A-side through heal"
    )
    # Runner also emits per-validator no-loss tokens
    assert "m015_no_loss_confirmed" in content, (
        "m015_no_loss_confirmed runner token absent from results doc"
    )


# ── Test 7: TLA+ Spec C referenced per criterion ──────────────────────────────

def test_m015_tla_spec_c_referenced():
    content = _artifact()
    assert "ilc_partition_heal" in content, (
        "TLA+ Spec C filename (ilc_partition_heal) not referenced in results doc"
    )
    # Must cite NoNewGlobalCommitDuringPartition and EventualCommit by name
    assert "NoNewGlobalCommitDuringPartition" in content, (
        "TLA+ invariant NoNewGlobalCommitDuringPartition not cited"
    )
    assert "EventualCommit" in content, (
        "TLA+ property EventualCommit not cited"
    )


# ── Test 8: explicit overall PASS verdict ─────────────────────────────────────

def test_m015_overall_pass_verdict():
    content = _artifact()
    assert "run_m015_workload_c_verdict=pass" in content, (
        "Overall PASS verdict token missing from results doc"
    )
