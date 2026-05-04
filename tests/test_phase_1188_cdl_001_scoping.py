from pathlib import Path


SCOPING_DOC = Path("docs/specs/ilc_cdl_001_genesis_blocker_scoping_1188_v0.1.md")
CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")


def test_cdl_001_scoping_doc_exists() -> None:
    assert SCOPING_DOC.exists()


def test_cdl_001_scoping_token() -> None:
    content = SCOPING_DOC.read_text(encoding="utf-8")
    assert "cdl_001_genesis_blocker_scoping_committed_phase_1188" in content


def test_cdl_001_identifier_collision_recorded() -> None:
    content = SCOPING_DOC.read_text(encoding="utf-8")
    assert "Identifier Collision Notice" in content
    assert "historical ratified `CDL-001`" in content


def test_existing_cdl_001_register_row_not_mutated_to_genesis_blocker() -> None:
    content = CDL_REGISTER.read_text(encoding="utf-8")
    cdl_001_row = next(line for line in content.splitlines() if line.startswith("| CDL-001 |"))
    assert "Canonical signer lineage definition" in cdl_001_row
    assert "genesis_blocker" not in cdl_001_row
