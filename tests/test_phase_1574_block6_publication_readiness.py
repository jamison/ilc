from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/specs/ilc_block6_public_rc_activation_matrix_1574_v0.1.md"
AUDIT = ROOT / "docs/specs/ilc_block6_publication_readiness_audit_1574_v0.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.73_block6.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PATENTS = (
    ROOT
    / "docs/specs/ilc_us_provisional_patent_application_numbers_received_2026_06_10_v0.1.md"
)
WALKTHROUGH = ROOT / "docs/phases/phase_1574_block6_publication_readiness_walkthrough.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_activation_matrix_exists_with_required_guard_rows() -> None:
    text = _read(MATRIX)
    required_surfaces = [
        "ADR-0009 bundle distribution",
        "ADR-0035 type registry runtime",
        "CDL-096 Werner flow-governor runtime",
        "OBL-020 emission engine",
        "CDL-048 mandatory ECU-to-ILC conversion",
        "OBL-021 validator admission/ejection",
        "OBL-022 treasury/reward/ejected-stake distribution",
        "OBL-027 productive ECU expansion bounty",
        "Rust P2P bridge",
        "OpenClaw/ClawHub listing",
        "Genesis core star-map and AtlasSliceManifest signing",
        "CCSS-SPECTRAL route-token non-disclosure claim",
        "MCP tool service surface",
    ]
    for surface in required_surfaces:
        assert surface in text


def test_public_rc_live_rows_have_rationales() -> None:
    text = _read(MATRIX)
    live_rows = []
    for line in text.splitlines():
        if "`public_rc_live`" not in line or not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if cells and cells[0].isdigit():
            live_rows.append(line)
    assert live_rows
    for row in live_rows:
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        assert len(cells) >= 5
        assert cells[-1] and cells[-1] != "`public_rc_live`"


def test_readiness_audit_exists_with_all_checks() -> None:
    text = _read(AUDIT)
    for expected in [
        "PUBLIC_RC_EXCLUDE sweep",
        "Source allowlist export rehearsal",
        "Patent application number confirmation",
        "Boolean token census orphan review",
        "Activation matrix",
        "Genesis base graph publication status",
        "CCSS privacy boundary",
        "Capsule v5.73",
    ]:
        assert expected in text


def test_patent_numbers_document_has_all_five_numbers_and_exclusion_header() -> None:
    text = _read(PATENTS)
    assert "PUBLIC_RC_EXCLUDE:" in "\n".join(text.splitlines()[:8])
    for number in ["64/231,844", "64/231,845", "64/231,846", "64/231,847", "64/231,848"]:
        assert number in text


def test_phase_1574_status_tokens_present() -> None:
    text = _read(STATUS)
    for token in [
        "block6_publication_readiness_audit_committed_phase_1574",
        "public_rc_activation_matrix_committed_phase_1574",
        "public_rc_exclude_sweep_passed_phase_1574",
        "source_allowlist_export_rehearsal_passed_phase_1574",
        "patent_application_numbers_confirmed_phase_1574",
        "capsule_v5_73_produced_phase_1574",
        "boolean_token_census_orphan_review_complete_phase_1574",
        "openclaw_clawhub_activation_matrix_row_decided_phase_1574",
        "public_path_blocked_pending_final_gate_phase_1574",
        "openclaw_clawhub_not_published_pending_phase_1575",
    ]:
        assert token in text


def test_capsule_and_walkthrough_record_non_authorization_floor() -> None:
    capsule = _read(CAPSULE)
    walkthrough = _read(WALKTHROUGH)
    assert "GO PUBLIC-RC-GATE-001" in capsule
    assert "OpenClaw" in capsule and "Default-off" in capsule
    assert "Phase 1574 did not authorize public RC" in walkthrough
