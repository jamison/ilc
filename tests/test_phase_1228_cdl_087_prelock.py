from pathlib import Path
import subprocess


SPEC = Path("docs/specs/ilc_cdl_087_prelock_spec_1228_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1228_cdl_087_prelock_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")
PHASE_1227_COMMIT = "2d833fcf"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1228_prelock_file_exists_and_token_present():
    text = _read(SPEC)

    assert text.strip()
    assert "cdl_087_prelock_committed_phase_1228" in text
    assert "cdl_087_not_ratified_phase_1228" in text


def test_phase_1228_q1_q5_resolved_without_tbd_markers():
    text = _read(SPEC)

    for marker in (
        "## 3. Q1 Resolution",
        "## 4. Q2 Resolution",
        "## 5. Q3 Resolution",
        "## 6. Q4 Resolution",
        "## 10. Q5 Resolution",
    ):
        assert marker in text
    assert "TBD" not in text


def test_phase_1228_ratification_conditions_all_listed():
    text = _read(SPEC)

    required = [
        "SIM-FETCH-01 passes",
        "Tier A/B/C artifact classification is implemented",
        "Bootstrap snapshot format is implemented",
        "Required observability signals",
        "CDL-077 static rate limiter remains active",
        "fetch_incentive_hypergraph_slice_projection_required_phase_1229",
    ]
    for condition in required:
        assert condition in text


def test_phase_1228_historical_opening_state_verified_at_phase_1227_commit():
    result = subprocess.run(
        [
            "git",
            "show",
            f"{PHASE_1227_COMMIT}:docs/specs/ilc_constitutional_decision_log_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=True,
    )

    for line in result.stdout.splitlines():
        if line.startswith("| CDL-087 |"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            assert cells[0] == "CDL-087"
            assert cells[3].lower() == "open"
            return
    raise AssertionError("CDL-087 row not found at Phase 1227 commit")


def test_phase_1228_pull_first_framing_and_non_bypass_present():
    text = _read(SPEC)
    normalized = " ".join(text.split())

    assert "cdl_087_pull_first_availability_not_service_mandate" in text
    assert "transport_abuse_circuit_breaker_not_final_scaling_policy" in text
    assert "does not constitutionalize a top-down universal service mandate" in normalized
    assert "does not supersede or weaken the circuit breaker" in text


def test_phase_1228_terminology_lock_and_privacy_mechanics_present():
    text = _read(SPEC)
    normalized = " ".join(text.lower().split())

    assert "Graph Node" in text
    assert "Serving peer" in text
    assert "Bare \"node\" must not be used for serving infrastructure" in text
    assert "No mandatory public inventory" in text
    assert "Unlinkability deferred" in text
    assert "direct fetch peers remain visible at the cdl-077 layer" in normalized


def test_phase_1228_walkthrough_and_status_advanced():
    walkthrough = _read(WALKTHROUGH)
    status = _read(STATUS)

    assert "**Status:** complete" in walkthrough
    assert "cdl_087_prelock_committed_phase_1228" in walkthrough
    assert "## Phase 1228" in status
    assert "Phase 1229 — Agent graph projection interface runtime" in status
