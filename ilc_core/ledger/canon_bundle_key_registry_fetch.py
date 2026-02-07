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


def _is_safe_archive_path(path_str: str) -> bool:
    """Check if archive path is safe (no traversal, no absolute paths)."""
    if path_str.startswith("/"):
        return False
    parts = Path(path_str).parts
    return ".." not in parts


def _download_url(url: str, dest_path: Path, timeout: int) -> dict:
    """Download a URL to a file."""
    import urllib.request
    import ssl
    
    try:
        ctx = ssl.create_default_context()
        with urllib.request.urlopen(url, timeout=timeout, context=ctx) as response:
            with open(dest_path, "wb") as f:
                shutil.copyfileobj(response, f)
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": f"source_download_failed:{e}"}


def _extract_archive(archive_path: Path, dest_dir: Path) -> dict:
    """Extract zip or tar archive with path traversal protection."""
    archive_path_str = str(archive_path)
    
    # Try zip first
    if zipfile.is_zipfile(archive_path_str):
        try:
            with zipfile.ZipFile(archive_path_str, "r") as zf:
                for name in zf.namelist():
                    if not _is_safe_archive_path(name):
                        return {"ok": False, "error": "archive_path_traversal"}
                zf.extractall(dest_dir)
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": f"archive_extract_failed:{e}"}
    
    # Try tar
    if tarfile.is_tarfile(archive_path_str):
        try:
            with tarfile.open(archive_path_str, "r:*") as tf:
                for member in tf.getmembers():
                    if not _is_safe_archive_path(member.name):
                        return {"ok": False, "error": "archive_path_traversal"}
                tf.extractall(dest_dir, filter="data")
            return {"ok": True}
        except Exception as e:
            return {"ok": False, "error": f"archive_extract_failed:{e}"}
    
    return {"ok": False, "error": "archive_format_unknown"}


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
    parsed = urlparse(source)
    temp_dir = None
    warnings = []
    
    try:
        # Create temp directory
        temp_dir = Path(tempfile.mkdtemp(prefix="registry_bundle_"))
        
        # Handle different source types
        if parsed.scheme == "https":
            if not allow_network:
                return {"ok": False, "errors": ["network_not_allowed"], "warnings": []}
            
            # Download archive
            archive_path = temp_dir / "bundle_archive"
            download_result = _download_url(source, archive_path, timeout)
            if not download_result["ok"]:
                return {"ok": False, "errors": [download_result["error"]], "warnings": []}
            
            # Extract archive
            extract_dir = temp_dir / "extracted"
            extract_dir.mkdir()
            extract_result = _extract_archive(archive_path, extract_dir)
            if not extract_result["ok"]:
                return {"ok": False, "errors": [extract_result["error"]], "warnings": []}
            
            # Find bundle directory
            entries = [p for p in extract_dir.iterdir()]
            if len(entries) != 1 or not entries[0].is_dir():
                return {"ok": False, "errors": ["bundle_layout_invalid"], "warnings": []}
            bundle_dir = entries[0]
            
        elif parsed.scheme == "file" or parsed.scheme == "":
            # Local path or file:// URL
            if parsed.scheme == "file":
                source_path = Path(parsed.path)
            else:
                source_path = Path(source)
            
            if not source_path.exists():
                return {"ok": False, "errors": ["source_not_found"], "warnings": []}
            
            if source_path.is_dir():
                # Copy directory
                bundle_dir = temp_dir / source_path.name
                shutil.copytree(source_path, bundle_dir)
            else:
                # Assume it's an archive
                extract_dir = temp_dir / "extracted"
                extract_dir.mkdir()
                extract_result = _extract_archive(source_path, extract_dir)
                if not extract_result["ok"]:
                    return {"ok": False, "errors": [extract_result["error"]], "warnings": []}
                
                entries = [p for p in extract_dir.iterdir()]
                if len(entries) != 1 or not entries[0].is_dir():
                    return {"ok": False, "errors": ["bundle_layout_invalid"], "warnings": []}
                bundle_dir = entries[0]
        else:
            return {"ok": False, "errors": ["source_scheme_unsupported"], "warnings": []}
        
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
        target = dest_dir / BUNDLE_DIR_NAME
        if target.exists():
            if not force:
                return {"ok": False, "errors": ["bundle_exists"], "warnings": warnings}
            shutil.rmtree(target)
        
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(bundle_dir), str(target))
        
        return {
            "ok": True,
            "errors": [],
            "warnings": warnings,
            "bundle_dir": str(target),
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
