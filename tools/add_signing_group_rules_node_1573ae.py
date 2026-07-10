#!/usr/bin/env python3
"""Add the Phase 1573ae SigningGroupRulesNode to the local unsigned Atlas LMDB.

PUBLIC_RC_EXCLUDE: block6_lmdb_maintenance_tool
PUBLIC_RC_EXCLUDE_REASON: Local unsigned Atlas LMDB maintenance script. No public
graph publication, Genesis signing, public RC activation, runtime activation, or
release authority.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from ilc_core.cli.atlas_lmdb_cli import handle_atlas_apply_node_edge_plan
from ilc_core.storage.genesis_atlas_lmdb_writer import write_json_atomic


DEFAULT_LMDB = Path("out/genesis_base_graph_v0.4_unified.lmdb")
DEFAULT_PLAN = Path("out/phase_1573ae/signing_group_rules_node_plan.json")
DEFAULT_RECEIPT = Path("out/phase_1573ae/signing_group_rules_node_receipt.json")
PHASE = "1573ae"
CDL_098_RATIFICATION = (
    "docs/specs/ilc_cdl_098_genesis_graph_update_authority_ratification_evidence_1573a_v0.1.md"
)
CDL_098_NODE_ID = "cdl:CDL-098"
SIGNING_GROUP_RULES_NODE_ID = "knowledge:signing_group_rules:atlas_slice_manifest_signing_v0.1"


def build_plan() -> dict[str, Any]:
    """Return the safe-writer node-edge plan for the manifest signing-rules node."""
    return {
        "phase": PHASE,
        "metadata": {
            "authority_basis": "CDL-098 Section 2g",
            "operation": "phase_1573ae_signing_group_rules_node_registration",
            "source": (
                "docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md + "
                "docs/specs/ilc_atlas_slice_manifest_build_pipeline_v0.1.md"
            ),
        },
        "nodes": [
            {
                "candidate_id": CDL_098_NODE_ID,
                "node_kind": "cdl_node",
                "node_type": "ConstitutionalDecisionNode",
                "cdl_id": "CDL-098",
                "source_path": CDL_098_RATIFICATION,
                "label": "CDL-098 Genesis Graph Update Authority",
                "summary": (
                    "Authority alias for ratified CDL-098, used as the safe-writer "
                    "GOVERNS source for graph curation knowledge nodes."
                ),
                "tier": "genesis_core",
                "graph_projection": "genesis_core_star_map",
                "graph_delta": "load_bearing_artifact_added",
            },
            {
                "candidate_id": SIGNING_GROUP_RULES_NODE_ID,
                "node_kind": "knowledge_node",
                "node_type": "SigningGroupRulesNode",
                "authority": CDL_098_NODE_ID,
                "authorized_projections": [
                    "genesis_core_star_map",
                    "public_protocol_graph",
                    "support_candidate_graph",
                ],
                "forbidden_public_projections": [
                    "excluded_private_material",
                    "review_required",
                ],
                "quorum_spec": {
                    "authority_basis": "CDL-098 Section 2g",
                    "rule": "Genesis signing ceremony or later CDL-authorized signing group required",
                    "human_go_required": True,
                    "no_self_authorization": True,
                },
                "key_type": "ml_dsa_65",
                "expiry_condition": "superseded_by_later_cdl_or_signing_group_rules_node",
                "source_path": "docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md",
                "supporting_spec_path": "docs/specs/ilc_atlas_slice_manifest_build_pipeline_v0.1.md",
                "label": "AtlasSliceManifest signing group rules v0.1",
                "summary": (
                    "ADR-0020 knowledge node defining public manifest-signing authority "
                    "boundaries for AtlasSliceManifest records."
                ),
                "tier": "public_release_candidate_material",
                "graph_projection": "public_protocol_graph",
                "graph_delta": "load_bearing_artifact_added",
            },
        ],
        "edges": [
            {
                "source": CDL_098_NODE_ID,
                "edge_type": "GOVERNS",
                "target": SIGNING_GROUP_RULES_NODE_ID,
            }
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lmdb", type=Path, default=DEFAULT_LMDB)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--receipt", type=Path, default=DEFAULT_RECEIPT)
    args = parser.parse_args()

    plan = build_plan()
    write_json_atomic(args.plan, plan)
    receipt = handle_atlas_apply_node_edge_plan(
        lmdb_path=str(args.lmdb),
        input_path=str(args.plan),
        write=True,
        receipt_path=str(args.receipt),
    )
    print(json.dumps(receipt, sort_keys=True, separators=(",", ":"), allow_nan=False))


if __name__ == "__main__":
    main()
