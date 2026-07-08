from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_root_license_file_exists_with_layered_terms() -> None:
    license_path = _repo_root() / "LICENSE"
    assert license_path.exists()

    body = license_path.read_text(encoding="utf-8")
    assert "ILC Layered License Notice" in body
    assert "AGPL-3.0-only" in body
    assert "LICENSING.md" in body
    assert "does not use a blanket MIT license" in body


def test_pyproject_license_declares_runtime_agpl() -> None:
    pyproject_path = _repo_root() / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    assert 'license = {text = "AGPL-3.0-only"}' in content


def test_layered_license_zone_table_exists() -> None:
    licensing_path = _repo_root() / "LICENSING.md"
    assert licensing_path.exists()

    content = licensing_path.read_text(encoding="utf-8")
    # HISTORICAL_SNAPSHOT: Phase 997 originally pinned tokenized license-zone
    # labels. LICENSING.md is now prose/table authority, so preserve the same
    # layered-license contract without requiring obsolete token strings.
    for token in (
        "A blanket MIT license is not the current project posture",
        "AGPL-3.0-only during bootstrap",
        "Genesis canonical artifacts",
        "CC BY 4.0 style attribution terms",
        "All Rights Reserved - Patent Pending",
        "Trademark/canonical-identity policy; no grant by code license",
        "Future Genesis governance review may modify",
    ):
        assert token in content


def test_public_patent_and_third_party_notices_exist() -> None:
    patents = _repo_root() / "PATENTS.md"
    third_party = _repo_root() / "THIRD_PARTY_NOTICES.md"

    assert patents.exists()
    assert third_party.exists()

    patent_text = patents.read_text(encoding="utf-8")
    third_party_text = third_party.read_text(encoding="utf-8")

    assert "THIRD_PARTY_NOTICES.md" in patent_text
    assert "third_party_original_licenses_preserved_public_rc_2026_06_03" in third_party_text
    assert "lmdb_dependency_notice_recorded_public_rc_2026_06_03" in third_party_text
