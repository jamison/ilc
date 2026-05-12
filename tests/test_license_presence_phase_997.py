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
    for token in (
        "ilc_layered_license_posture_v0.1",
        "mit_for_all_zones_rejected_layered_license_posture",
        "agpl_default_runtime_license_posture",
        "genesis_canonical_identity_license_zone",
        "public_docs_cc_by_4_0_zone",
        "patent_pending_all_rights_reserved_zone",
        "trademark_identity_not_granted_by_code_license",
        "counsel_review_future_modification_expected",
    ):
        assert token in content
