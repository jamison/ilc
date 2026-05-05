"""
Fetch and verify registry bundles from local or remote sources.

Supports:
- Local path (copy)
- file:// URL (copy)
- https:// URL (download zip/tar, requires --allow-network)
"""

import hashlib
import json
import shutil
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from ilc_core.ledger.canon_bundle_key_registry_bundle import (
    verify_registry_bundle,
    BUNDLE_DIR_NAME,
)


def _canonicalize_source(source: str) -> str:
    """Canonicalize source string for logging/comparison."""
    parsed = urlparse(source)
    if parsed.scheme == "file":
        return str(Path(parsed.path).resolve())
    if parsed.scheme in ("http", "https"):
        return source.rstrip("/")
    return str(Path(source).resolve())


def _is_safe_archive_path(path_str: str) -> bool:
    """Check if archive path is safe (no traversal, no absolute paths)."""
    if path_str.startswith("/"):
        return False
    parts = Path(path_str).parts
    return ".." not in parts


def _download_url(url: str, dest_path: Path, timeout: int) -> dict:
    """Download a URL to a file."""
    import ssl
    import urllib.error
    import urllib.request

    class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, _req, _fp, code, _msg, _headers, newurl):
            raise urllib.error.URLError(
                f"fetch_redirect_not_permitted: {code} -> {newurl}"
            )

    try:
        ctx = ssl.create_default_context()
        opener = urllib.request.build_opener(
            _NoRedirectHandler,
            urllib.request.HTTPSHandler(context=ctx),
        )
        with opener.open(url, timeout=timeout) as response:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(response, f)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": f"source_download_failed:{e}"}


def _extract_zip(archive_path: Path, dest_dir: Path) -> dict:
    """Extract zip archive safely."""
    try:
        with zipfile.ZipFile(str(archive_path), "r") as zf:
            for name in zf.namelist():
                if not _is_safe_archive_path(name):
                    return {"ok": False, "error": "archive_path_traversal"}
            zf.extractall(dest_dir)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": f"archive_extract_failed:{e}"}


def _extract_tar(archive_path: Path, dest_dir: Path) -> dict:
    """Extract tar archive safely."""
    try:
        with tarfile.open(str(archive_path), "r:*") as tf:
            for member in tf.getmembers():
                if not _is_safe_archive_path(member.name):
                    return {"ok": False, "error": "archive_path_traversal"}
            tf.extractall(dest_dir, filter="data")
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": f"archive_extract_failed:{e}"}


def _extract_archive(archive_path: Path, dest_dir: Path) -> dict:
    """Extract zip or tar archive with path traversal protection."""
    path_str = str(archive_path)
    
    if zipfile.is_zipfile(path_str):
        return _extract_zip(archive_path, dest_dir)
    
    if tarfile.is_tarfile(path_str):
        return _extract_tar(archive_path, dest_dir)
    
    return {"ok": False, "error": "archive_format_unknown"}


def _fetch_remote_source(source: str, temp_dir: Path, allow_network: bool, timeout: int) -> dict:
    """Attempt to fetch from remote HTTPS source."""
    if not source.startswith("https://"):
        return {"ok": True, "skipped": True}
        
    if not allow_network:
         return {"ok": False, "error": "network_not_allowed"}
    
    archive_path = temp_dir / "bundle_archive"
    dl_result = _download_url(source, archive_path, timeout)
    if not dl_result["ok"]:
        return {"ok": False, "error": dl_result["error"]}
    
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)
    ext_result = _extract_archive(archive_path, extract_dir)
    if not ext_result["ok"]:
        return {"ok": False, "error": ext_result["error"]}
        
    # Find bundle dir
    entries = [p for p in extract_dir.iterdir()]
    if len(entries) != 1 or not entries[0].is_dir():
         return {"ok": False, "error": "bundle_layout_invalid"}
         
    return {"ok": True, "bundle_dir": entries[0]}


def _fetch_local_source(source: str, temp_dir: Path) -> dict:
    """Attempt to fetch from local path or file:// URL."""
    parsed = urlparse(source)
    if parsed.scheme == "https":
         return {"ok": True, "skipped": True}
         
    if parsed.scheme == "file":
        path = Path(parsed.path)
    else:
        path = Path(source)
        
    if not path.exists():
        return {"ok": False, "error": "source_not_found"}
        
    if path.is_dir():
        bundle_dir = temp_dir / path.name
        shutil.copytree(path, bundle_dir)
        return {"ok": True, "bundle_dir": bundle_dir}
    
    # Archive
    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir(exist_ok=True)
    ext_result = _extract_archive(path, extract_dir)
    if not ext_result["ok"]:
        return {"ok": False, "error": ext_result["error"]}
        
    entries = [p for p in extract_dir.iterdir()]
    if len(entries) != 1 or not entries[0].is_dir():
         return {"ok": False, "error": "bundle_layout_invalid"}
         
    return {"ok": True, "bundle_dir": entries[0]}


def _resolve_bundle_dir(source: str, temp_dir: Path, allow_network: bool, timeout: int) -> dict:
    """Resolve source to a local directory containing the bundle."""
    # Try remote
    remote = _fetch_remote_source(source, temp_dir, allow_network, timeout)
    if not remote.get("skipped"):
        return remote
        
    # Try local
    local = _fetch_local_source(source, temp_dir)
    if not local.get("skipped"):
        return local
        
    return {"ok": False, "error": "source_scheme_unsupported"}


def _install_bundle(bundle_dir: Path, dest_dir: Path, force: bool, warnings: list) -> dict:
    """Install verified bundle to destination."""
    target = dest_dir / BUNDLE_DIR_NAME
    if target.exists():
        if not force:
            return {"ok": False, "error": "bundle_exists"}
        shutil.rmtree(target)
    
    dest_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(bundle_dir), str(target))
    
    return {"ok": True, "installed_path": str(target)}


def fetch_registry_bundle(
    source: str,
    key: bytes,
    dest_dir: Path,
    force: bool = False,
    allow_network: bool = False,
    timeout: int = 20,
    keep_temp: bool = False,
    strict: bool = True,
) -> dict:
    """
    Fetch and verify a registry bundle.
    
    Args:
        source: Local path, file:// URL, or https:// URL.
        key: Verification key bytes.
        dest_dir: Destination directory for installed bundle.
        force: If True, overwrite existing bundle.
        allow_network: If True, allow https:// URLs.
        timeout: Timeout for network requests in seconds.
        keep_temp: If True, keep temp dir on failure.
        strict: If True, use strict validation.
    
    Returns:
        Dict with {ok, errors, warnings, bundle_dir, installed_to}.
    """
    temp_dir = None
    warnings = []
    
    try:
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="registry_bundle_"))
        
        # Resolve source to bundle directory
        resolve_result = _resolve_bundle_dir(source, temp_dir, allow_network, timeout)
        if not resolve_result["ok"]:
            return {"ok": False, "errors": [resolve_result["error"]], "warnings": []}
        
        bundle_dir = resolve_result["bundle_dir"]
        
        # Verify bundle
        verify_result = verify_registry_bundle(bundle_dir, key, strict=strict)
        if not verify_result["ok"]:
            return {
                "ok": False,
                "errors": ["bundle_verify_failed"] + verify_result.get("errors", []),
                "warnings": verify_result.get("warnings", []),
            }
        warnings.extend(verify_result.get("warnings", []))
        
        # Install to destination
        install_result = _install_bundle(bundle_dir, dest_dir, force, warnings)
        if not install_result["ok"]:
             return {"ok": False, "errors": [install_result["error"]], "warnings": warnings}
        
        return {
            "ok": True,
            "errors": [],
            "warnings": warnings,
            "bundle_dir": install_result["installed_path"],
            "installed_to": str(dest_dir),
            "registry_hash": verify_result.get("registry_hash"),
            "key_id": verify_result.get("key_id"),
        }
        
    except Exception as e:
        return {"ok": False, "errors": [f"fetch_failed:{e}"], "warnings": []}
    
    finally:
        # Cleanup temp dir
        if temp_dir and temp_dir.exists() and not keep_temp:
            shutil.rmtree(temp_dir, ignore_errors=True)

