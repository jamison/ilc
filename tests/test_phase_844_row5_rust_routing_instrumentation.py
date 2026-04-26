"""Phase 844 Row-5 Rust routing instrumentation gate test.

Verifies that handle_broadcast_honest in node.rs has been instrumented with
the four privacy-lane routing log tokens per the Phase 844 sequence lock.

Token: row5_rust_integration_sim_leakage_03_sequence_lock_active
"""
import subprocess
from pathlib import Path

REPO = Path(__file__).parent.parent
NODE_RS = REPO / "ilc_consensus" / "src" / "node.rs"

ROUTING_TOKENS = [
    "privacy_lane_routing:class=contribution",
    "privacy_lane_routing:class=payment_express",
    "privacy_lane_routing:class=payment_express_rejected",
    "privacy_lane_routing:class=payment_default",
]

PHASE_844_TOKENS = [
    "row5_rust_integration_sim_leakage_03_sequence_lock_active",
    "row5_rust_integration_sim_leakage_03_window_844_847",
    "d3_authorized_after_gate826_pull_confirmed",
]


def node_rs_text() -> str:
    return NODE_RS.read_text()


def test_node_rs_exists():
    assert NODE_RS.exists(), f"node.rs not found at {NODE_RS}"


def test_all_four_routing_tokens_in_node_rs():
    text = node_rs_text()
    for token in ROUTING_TOKENS:
        assert token in text, (
            f"Missing routing token in node.rs: {token!r}\n"
            f"Phase 844 requires all four TransferClass routing paths to be logged."
        )


def test_routing_log_prefix_in_node_rs():
    """The [row5_privacy_lane] log prefix scopes the output for grep in Phase 845."""
    assert "[row5_privacy_lane]" in node_rs_text(), (
        "Missing [row5_privacy_lane] log prefix — SIM-LEAKAGE-03 grep relies on this."
    )


def test_contribution_path_before_payment_express():
    """Contribution is the mandatory case — must appear before Payment variants."""
    text = node_rs_text()
    pos_contribution = text.find("privacy_lane_routing:class=contribution")
    pos_express = text.find("privacy_lane_routing:class=payment_express\"")
    assert pos_contribution < pos_express, (
        "Contribution routing token must appear before Payment express token "
        "— match arm ordering in handle_broadcast_honest."
    )


def test_express_rejected_present_in_node_rs():
    """payment_express_rejected covers the case where agent_acknowledged_timing_disclosure is false."""
    assert "privacy_lane_routing:class=payment_express_rejected" in node_rs_text()


def test_routing_block_after_verify_sender_sig():
    """Routing decision must come after verify_transfer_sender_sig, not before."""
    text = node_rs_text()
    pos_verify = text.find("verify_transfer_sender_sig(&transfer)")
    pos_routing = text.find("[row5_privacy_lane]")
    assert pos_verify < pos_routing, (
        "Routing instrumentation must appear after verify_transfer_sender_sig — "
        "only authenticated transfers should be routed."
    )


def test_routing_block_before_in_flight_insert():
    """Routing decision must come before the in_flight table lock."""
    text = node_rs_text()
    pos_routing = text.find("[row5_privacy_lane]")
    pos_in_flight = text.find("let mut table = self.in_flight.lock().await;")
    assert pos_routing < pos_in_flight, (
        "Routing instrumentation must appear before the in_flight table insertion — "
        "routing is a pre-insert decision."
    )


def test_stored_checkpoint_signers_fix_in_testnet_fault_sim():
    """All StoredCheckpoint initializers in node.rs include the signers field.

    HIGH-002 Phase A added signers: Vec<ValidatorID> to StoredCheckpoint.
    The testnet_fault_sim test initializers must carry that field or the
    testnet_fault_sim feature build fails.

    We check this by verifying that every line containing 'StoredCheckpoint {'
    is followed within 10 lines by 'signers:'.
    """
    lines = node_rs_text().splitlines()
    violations = []
    for i, line in enumerate(lines):
        if "StoredCheckpoint {" in line:
            window = lines[i : i + 10]
            if not any("signers:" in l for l in window):
                violations.append(f"Line {i+1}: {line.strip()!r} — no signers: within 10 lines")
    assert not violations, (
        "StoredCheckpoint initializers missing signers field:\n" +
        "\n".join(violations)
    )


def test_rust_build_release_passes():
    """Confirm the release binary still builds after Phase 844 changes."""
    result = subprocess.run(
        [
            str(Path.home() / ".cargo" / "bin" / "cargo"),
            "build",
            "--release",
            "--features", "testnet_fault_sim",
            "--bin", "validator_harness",
        ],
        cwd=REPO / "ilc_consensus",
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PROTOC": "/usr/local/bin/protoc"},
    )
    assert result.returncode == 0, (
        f"Release build failed after Phase 844 changes:\n{result.stderr[-2000:]}"
    )


def test_rust_test_suite_passes_with_testnet_fault_sim():
    """Full Rust test suite passes with testnet_fault_sim feature."""
    result = subprocess.run(
        [
            str(Path.home() / ".cargo" / "bin" / "cargo"),
            "test",
            "--features", "testnet_fault_sim",
        ],
        cwd=REPO / "ilc_consensus",
        capture_output=True,
        text=True,
        env={**__import__("os").environ, "PROTOC": "/usr/local/bin/protoc"},
    )
    assert result.returncode == 0, (
        f"Rust test suite failed:\n{result.stderr[-2000:]}"
    )


def test_sequence_lock_doc_exists():
    seq_lock = REPO / "docs" / "phases" / "phase_844_row5_rust_integration_sim_leakage_03_sequence_lock.md"
    assert seq_lock.exists(), "Phase 844 sequence lock document missing"


def test_sequence_lock_tokens():
    seq_lock = REPO / "docs" / "phases" / "phase_844_row5_rust_integration_sim_leakage_03_sequence_lock.md"
    text = seq_lock.read_text()
    for token in PHASE_844_TOKENS:
        assert token in text, f"Missing token in sequence lock: {token!r}"


def test_no_cdl_mutation_in_phase_844():
    """Phase 844 must not mutate any CDL document."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD~1", "HEAD"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    changed = result.stdout.splitlines()
    cdl_changes = [f for f in changed if "cdl_" in f.lower() and f.endswith(".md")]
    assert not cdl_changes, (
        f"Phase 844 must not mutate CDL documents. Changed:\n" +
        "\n".join(cdl_changes)
    )
