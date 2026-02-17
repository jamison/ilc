from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_root_license_file_exists_with_mit_terms() -> None:
    license_path = _repo_root() / "LICENSE"
    assert license_path.exists()

    body = license_path.read_text(encoding="utf-8")
    assert "MIT License" in body
    assert "Permission is hereby granted, free of charge" in body
    assert "THE SOFTWARE IS PROVIDED \"AS IS\"" in body


def test_pyproject_license_declares_mit() -> None:
    pyproject_path = _repo_root() / "pyproject.toml"
    content = pyproject_path.read_text(encoding="utf-8")
    assert 'license = {text = "MIT"}' in content
