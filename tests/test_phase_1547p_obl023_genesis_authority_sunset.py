from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_genesis_authority_sunset_spec_1547p_v0.1.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_genesis_authority_sunset_spec_closes_obl023_without_activation() -> None:
    text = read(SPEC)

    required = [
        "obl_023_genesis_authority_sunset_spec_committed_phase_1547p",
        "obl_023_closed_phase_1547p",
        "genesis_authority_not_sunset_phase_1547p",
        "public_path_remains_blocked_phase_1547p",
        "House",
        "Court",
        "Executive / Autopilot",
        "Boot",
        "Transition",
        "Mature",
        "Sunset Trigger Framework",
        "Handoff Event Sequence",
    ]
    for needle in required:
        assert needle in text

    forbidden_claims = [
        "Genesis authority has already sunset.",
        "This specification does not sunset Genesis authority",
        "Actual sunset remains a future governance event",
    ]
    for needle in forbidden_claims:
        assert needle in text


def test_obl023_row_is_closed_and_only_obl023_is_closed_by_phase_1547p() -> None:
    register = read(REGISTER)

    row = next(line for line in register.splitlines() if line.startswith("| OBL-023 |"))
    assert "| closed |" in row
    assert "obl_023_closed_phase_1547p" in row
    assert "docs/specs/ilc_genesis_authority_sunset_spec_1547p_v0.1.md" in row

    for obl in ("OBL-024", "OBL-028", "OBL-029"):
        other = next(line for line in register.splitlines() if line.startswith(f"| {obl} |"))
        assert "closed_phase_1547p" not in other


def test_status_records_phase_1547p_frontier() -> None:
    status = read(STATUS)

    assert "## Phase 1547p - OBL-023 Genesis Authority Sunset Spec" in status
    assert "obl_023_genesis_authority_sunset_spec_committed_phase_1547p" in status
    assert "obl_023_closed_phase_1547p" in status
    assert "No CDL mutation" in status
    assert "No Genesis authority sunset" in status
