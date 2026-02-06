"""Shared utilities for canon bundle modules."""

import re
from collections import Counter
from hashlib import sha256
from pathlib import Path
from typing import Optional, List


def file_sha256(path: Path) -> Optional[str]:
    """Compute SHA-256 hexdigest of a file's bytes, or None if file doesn't exist."""
    if not path.exists():
        return None
    h = sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def derive_key_id(key_bytes: bytes) -> str:
    """Derive a stable 16-character key identifier from key bytes."""
    return sha256(key_bytes).hexdigest()[:16]



# Known issue patterns for normalization
KNOWN_ISSUE_MAP = {
    "missing required file": "manifest_missing",
    "manifest is missing": "manifest_missing",
    "signature missing": "signature_missing",
    "signature mismatch": "signature_mismatch",
    "audit write failed": "audit_write_failed",
}


def normalize_issue(issue: str) -> str:
    """
    Return a stable category for an error/warning string.
    
    If already snake_case, return as-is. Otherwise map common patterns
    to known keys, or convert spaces to underscores.
    """
    s = issue.strip().lower()
    if re.fullmatch(r"[a-z0-9_]+", s):
        return s
    for frag, key in KNOWN_ISSUE_MAP.items():
        if frag in s:
            return key
    return s.replace(" ", "_")


def normalize_issue_list(issues: List[str]) -> List[str]:
    """Normalize a list of issues to stable categories."""
    return [normalize_issue(i) for i in issues]


def normalized_multiset(issues: List[str]) -> Counter:
    """Return a Counter (multiset) of normalized issue categories."""
    return Counter(normalize_issue_list(issues))
