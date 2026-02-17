from __future__ import annotations

from pathlib import Path


def test_config_readme_exists_and_documents_default_json_policy() -> None:
    readme_path = Path("config/README.md")
    assert readme_path.exists()
    text = readme_path.read_text(encoding="utf-8")
    assert "governance_mvp.json" in text
    assert "hardware_archetypes_mvp.json" in text
    assert "Default load path is `config/governance_mvp.json`." in text
    assert "Default load path is `config/hardware_archetypes_mvp.json`." in text


def test_config_readme_documents_yaml_optional_fallback() -> None:
    text = Path("config/README.md").read_text(encoding="utf-8")
    assert "Explicit YAML paths (`.yaml` or `.yml`) are supported" in text
    assert "loader checks sibling `.json`" in text


def test_root_readme_links_to_config_readme() -> None:
    root_readme = Path("README.md").read_text(encoding="utf-8")
    assert "`config/README.md`" in root_readme
