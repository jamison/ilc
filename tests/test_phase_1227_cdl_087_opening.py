from pathlib import Path


REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
SPEC = Path("docs/specs/ilc_cdl_087_canonical_fetch_distribution_policy_opening_1227_v0.1.md")
WALKTHROUGH = Path("docs/phases/phase_1227_cdl_087_opening_walkthrough.md")
STATUS = Path("docs/phases/STATUS.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _cdl_087_row() -> str:
    for line in _read(REGISTER).splitlines():
        if line.startswith("| CDL-087 |"):
            return line
    raise AssertionError("CDL-087 row not found")


def test_phase_1227_cdl_087_opening_row_later_ratified():
    row = _cdl_087_row()
    cells = [cell.strip() for cell in row.strip().strip("|").split("|")]

    assert cells[0] == "CDL-087"
    assert cells[3].lower() == "ratified"
    assert "Canonical fetch distribution policy" in cells[2]
    assert "SIM-FETCH-01" in row
    assert "opening_token: cdl_087_canonical_fetch_distribution_policy_opened_phase_1227" in row
    assert "ratified_phase: 1278 Fix1" in row


def test_phase_1227_opening_spec_exists_and_token_present():
    text = _read(SPEC)

    assert text.strip()
    assert "cdl_087_canonical_fetch_distribution_policy_opened_phase_1227" in text
    assert "fetch_distribution_architecture_reframed_phase_1222" in text


def test_phase_1227_non_ratifying_boundary_and_sim_gate_recorded():
    text = _read(SPEC)

    assert "cdl_087_not_ratified_phase_1227" in text
    assert "No ratification act is authorized in Phase 1227 or Phase 1228" in text
    assert "SIM-FETCH-01 evidence" in text


def test_phase_1227_scope_excludes_reciprocal_scoring_and_preserves_cdl_077():
    text = _read(SPEC)

    assert "CDL-077 WANT-BLOCK limiting remains active" in text
    assert "Reciprocal scoring" in text
    assert "does not supersede CDL-077" in text
    assert "Publicly verifiable reads do not create an unlimited service obligation" in text


def test_phase_1227_walkthrough_and_status_advanced():
    walkthrough = _read(WALKTHROUGH)
    status = _read(STATUS)

    assert "**Status:** complete" in walkthrough
    assert "cdl_087_canonical_fetch_distribution_policy_opened_phase_1227" in walkthrough
    assert "## Phase 1227" in status
    assert "Phase 1228 — CDL-087 prelock" in status
