from __future__ import annotations

from pathlib import Path


ROOT = Path(".")


def test_root_has_no_legacy_rtf_artifacts() -> None:
    assert not (ROOT / "2025_11_19_v0.1_Genesis.config.json.rtf").exists()
    assert not (ROOT / "2025_11_19_v1.1_ILC_Master_Node_Schema.json.rtf").exists()
    assert (ROOT / "docs/archive/legacy_root_artifacts/2025_11_19_v0.1_Genesis.config.json.rtf").exists()
    assert (ROOT / "docs/archive/legacy_root_artifacts/2025_11_19_v1.1_ILC_Master_Node_Schema.json.rtf").exists()


def test_fixture_wrapper_relocated_to_tools() -> None:
    assert not (ROOT / "make_fixtures.py").exists()
    assert (ROOT / "tools/make_fixtures.py").exists()


def test_manifest_excludes_archive_and_chat_corpus() -> None:
    manifest = (ROOT / "MANIFEST.in").read_text(encoding="utf-8")
    assert "prune Z_Past_Chats" in manifest
    assert "prune docs/archive" in manifest
    assert "exclude *.rtf" in manifest


def test_gitignore_declares_chat_corpus_ignore_policy() -> None:
    ignore_text = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "Z_Past_Chats/" in ignore_text
