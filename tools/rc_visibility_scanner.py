"""rc_visibility_scanner.py — standalone RC visibility header scanner.

Scans source files for PUBLIC_RC_EXCLUDE and genesis_private_historical_material
headers to classify each file as: public | excluded | private_historical | unknown.

No ilc_core/ dependency. Mirrors the bytes-in check in
ilc_core/rc/source_allowlist_export_rehearsal.py line 286.

PUBLIC_RC_EXCLUDE: graph_viz_3d_research_tool
PUBLIC_RC_EXCLUDE_REASON: Visualization support helper; no signing, no canonical
graph mutation, no public RC activation.
"""

from __future__ import annotations

from pathlib import Path

# Byte markers — bytes `in` check only (NOT regex).
# Mirrors ilc_core/rc/source_allowlist_export_rehearsal.py line 286.
PUBLIC_RC_EXCLUDE_MARKER = b"PUBLIC_RC_EXCLUDE"
PRIVATE_HISTORICAL_MARKER = b"genesis_private_historical_material"

# OOM guard: if more than MAX_FILES paths are passed, skip paths under "out/"
# (treat as "excluded") to avoid scanning the full generated-artifact tree.
MAX_FILES = 20_000


def scan_rc_visibility(
    source_paths: list[str],
    repo_root: Path,
) -> dict[str, str]:
    """Scan source files for RC visibility markers.

    Returns a dict mapping each source_path to one of:
      "public"            — no PUBLIC_RC_EXCLUDE marker found
      "excluded"          — PUBLIC_RC_EXCLUDE marker found (no private_historical)
      "private_historical"— both PUBLIC_RC_EXCLUDE and genesis_private_historical_material
      "unknown"           — file missing or OSError during read

    Logic:
      - Read only the first 2000 bytes of each file (headers are always at top).
      - If more than MAX_FILES paths, skip any path under "out/" (mark as "excluded").
    """
    over_limit = len(source_paths) > MAX_FILES

    result: dict[str, str] = {}
    for sp in source_paths:
        # OOM guard: skip "out/" paths when over limit
        if over_limit and (sp.startswith("out/") or "/out/" in sp):
            result[sp] = "excluded"
            continue

        full = repo_root / sp
        if not full.exists():
            result[sp] = "unknown"
            continue
        try:
            payload = full.read_bytes()[:2000]
        except OSError:
            result[sp] = "unknown"
            continue

        if PUBLIC_RC_EXCLUDE_MARKER in payload:
            if PRIVATE_HISTORICAL_MARKER in payload:
                result[sp] = "private_historical"
            else:
                result[sp] = "excluded"
        else:
            result[sp] = "public"

    return result
