#!/usr/bin/env python3
"""Register Fix85 phase files in the unified Atlas LMDB.

PUBLIC_RC_EXCLUDE: fix85_register_phase_files_local_only
PUBLIC_RC_EXCLUDE_REASON: Local Atlas LMDB support registration;
not Genesis signing, public graph upload, canonical graph mutation,
runtime activation, or public RC publication.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.storage.genesis_atlas_lmdb_writer import (  # noqa: E402
    AtlasLmdbSafeWriter,
    AtlasPhaseFileRegistration,
)

PHASE = "1545p-Fix85"
LMDB_ROOT = REPO_ROOT / "out/genesis_base_graph_v0.4_unified.lmdb"

SCANNER_PATH      = REPO_ROOT / "tools/rc_visibility_scanner.py"
TEST_PATH         = REPO_ROOT / "tests/test_phase_1545p_fix85_public_private_node_encoding.py"
WALKTHROUGH_PATH  = REPO_ROOT / "docs/phases/phase_1545p_fix85_public_private_node_encoding_walkthrough.md"


def _verify_tokens() -> None:
    if not (LMDB_ROOT / "data.mdb").exists():
        raise ValueError(f"fix85_lmdb_missing:{LMDB_ROOT}")
    if not SCANNER_PATH.exists():
        raise ValueError(f"fix85_scanner_missing:{SCANNER_PATH}")
    if not TEST_PATH.exists():
        raise ValueError(f"fix85_tests_missing:{TEST_PATH}")
    if not WALKTHROUGH_PATH.exists():
        raise ValueError(f"fix85_walkthrough_missing:{WALKTHROUGH_PATH}")


def _phase_file_registrations() -> list[AtlasPhaseFileRegistration]:
    return [
        AtlasPhaseFileRegistration(
            path=SCANNER_PATH.relative_to(REPO_ROOT),
            node_kind="phase_support_spec",
            graph_projection="support_candidate_graph",
            required_edges=(("IMPLEMENTS", f"phase:{PHASE.lower().replace('-', '_')}"),),
        ),
        AtlasPhaseFileRegistration(
            path=TEST_PATH.relative_to(REPO_ROOT),
            node_kind="phase_test",
            graph_projection="support_candidate_graph",
            required_edges=(("TESTS", f"phase:{PHASE.lower().replace('-', '_')}"),),
        ),
        AtlasPhaseFileRegistration(
            path=WALKTHROUGH_PATH.relative_to(REPO_ROOT),
            node_kind="phase_walkthrough",
            graph_projection="support_candidate_graph",
            required_edges=(("EVIDENCES", f"phase:{PHASE.lower().replace('-', '_')}"),),
        ),
    ]


def run(*, dry_run: bool = False) -> dict[str, Any]:
    _verify_tokens()
    writer = AtlasLmdbSafeWriter(LMDB_ROOT)
    try:
        receipt = writer.register_phase_files(
            PHASE,
            _phase_file_registrations(),
            dry_run=dry_run,
        )
        if receipt.get("status") != "PASS" and not dry_run:
            raise ValueError(f"fix85_phase_file_registration_failed:{receipt}")
        nodes = list(writer.store.iter_nodes())
        edges = list(writer.store.iter_edges())
        receipt["final_counts"] = {"nodes": len(nodes), "edges": len(edges)}
        return receipt
    finally:
        writer.store.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Register Fix85 phase files in Atlas LMDB")
    parser.add_argument("--dry-run", action="store_true", help="dry run only")
    args = parser.parse_args()
    result = run(dry_run=args.dry_run)
    print(json.dumps(result, indent=2, default=str))
