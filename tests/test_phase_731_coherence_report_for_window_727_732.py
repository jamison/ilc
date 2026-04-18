from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = REPO_ROOT / "docs/specs/ilc_coherence_report_731_v0.1.md"
WALKTHROUGH = (
    REPO_ROOT
    / "docs/phases/phase_731_g8_coherence_report_for_window_727_732_walkthrough.md"
)
STATUS = REPO_ROOT / "docs/phases/STATUS.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_artifact_exists():
    assert ARTIFACT.exists(), "phase 731 coherence report must exist"


def test_headings_and_tokens_present():
    text = _read(ARTIFACT)
    headings = [
        "## 1. Baseline",
        "## 2. Completed in-window artifacts",
        "## 3. Boundary confirmations",
        "## 4. Track B verification",
        "## 5. Carry-forward into closure",
        "## 6. Closure-readiness verdict",
        "## 7. Source inputs",
    ]
    for heading in headings:
        assert heading in text, f"missing heading: {heading}"
    tokens = [
        "window_727_732_coherence_report_published",
        "adjacent_gated_economy_hardening_window_coherent",
        "no_cdl_ratification_occurred_in_window_727_732",
        "no_financial_shard_activation_occurred_in_window_727_732",
        "track_b_status_verified_from_status_tail",
    ]
    for token in tokens:
        assert token in text, f"missing token: {token}"


def test_completed_outputs_are_listed():
    text = _read(ARTIFACT)
    required = [
        "ilc_phase_727_732_sequence_lock_v0.1.md",
        "ilc_adjacent_gated_economy_carry_forward_selection_728_v0.1.md",
        "ilc_rights_licenses_and_gated_access_surfaces_disposition_729_v0.1.md",
        "ilc_private_gated_shard_header_and_capability_token_contract_hardening_730_v0.1.md",
    ]
    for item in required:
        assert item in text, f"artifact must name completed output {item}"


def test_boundary_confirmations_are_explicit():
    text = _read(ARTIFACT)
    required = [
        "No CDL ratification occurred in Window `727-732`.",
        "No financial-shard activation occurred in Window `727-732`.",
        "`CDL-062` remained the separate sovereign-substrate research lane",
        "ADR-0022 remained the architectural boundary anchor",
        "no mutation of `ilc_core/` or `ilc_consensus/` occurred in Phases `727-730`",
    ]
    for item in required:
        assert item in text, f"artifact must confirm boundary {item}"


def test_track_b_and_a_series_routing_are_explicit():
    text = _read(ARTIFACT)
    assert (
        "`M-016 complete; next planned phase M-017 (Workload E: Validator Operability)`"
        in text
    )
    for item in ["`A1`", "`A2`", "`A3`", "`A4`", "`A5`", "`A6`", "`A7`", "`A8`"]:
        assert item in text, f"artifact must route audit item {item}"


def test_phase_732_carry_forward_is_explicit():
    text = _read(ARTIFACT)
    required = [
        "publish capsule `v5.0`",
        "publish the Window `727-732` closure gate",
        "advance `PLANNING_INDEX.md` to the true post-`732` frontier",
        "review the launch roadmap and update it if the window changed any live",
    ]
    for item in required:
        assert item in text, f"artifact must carry forward closure item {item}"


def test_walkthrough_exists():
    assert WALKTHROUGH.exists(), "phase 731 walkthrough must exist after backfill"


def test_status_records_phase_731():
    text = _read(STATUS)
    assert "## Phase 731" in text, "STATUS must include a Phase 731 entry"
    assert (
        "Phase 732 — capsule v5.0 and window 727-732 closure gate." in text
    ), "STATUS must point to Phase 732"
