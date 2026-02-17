from __future__ import annotations

import base64
from pathlib import Path

from ilc_core.cli._key_utils import load_key_bytes_with_b64_fallback


CLI_KEY_REGISTRY_FILES = [
    "ilc_core/cli/canon_bundle_key_registry.py",
    "ilc_core/cli/canon_bundle_key_registry_bundle.py",
    "ilc_core/cli/canon_bundle_key_registry_channel_sign.py",
    "ilc_core/cli/canon_bundle_key_registry_channel_verify.py",
    "ilc_core/cli/canon_bundle_key_registry_fetch.py",
    "ilc_core/cli/canon_bundle_key_registry_promotion.py",
    "ilc_core/cli/canon_bundle_key_registry_sync.py",
]


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_targeted_cli_modules_no_longer_define_local_key_loader() -> None:
    root = _repo_root()
    for rel_path in CLI_KEY_REGISTRY_FILES:
        text = (root / rel_path).read_text(encoding="utf-8")
        assert "def _load_key_bytes(" not in text
        assert "load_key_bytes_with_b64_fallback" in text


def test_shared_key_loader_prefers_valid_base64(tmp_path: Path) -> None:
    raw = b"0123456789abcdef0123456789abcdef"
    key_path = tmp_path / "key.txt"
    key_path.write_bytes(base64.b64encode(raw))
    assert load_key_bytes_with_b64_fallback(key_path) == raw


def test_shared_key_loader_falls_back_to_raw_bytes(tmp_path: Path) -> None:
    raw = b"not_base64_key_material"
    key_path = tmp_path / "key.txt"
    key_path.write_bytes(raw)
    assert load_key_bytes_with_b64_fallback(key_path) == raw
