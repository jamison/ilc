from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OBL_REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
LEDGER = ROOT / "docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json"


BATCH_079_TARGETS = {
    "docs/specs/ilc_cdl_sigma_01_ratification_evidence_1573e_v0.1.md",
    "docs/specs/ilc_constitutional_decision_log_v0.1.md",
    "ilc_core/network/d2d/spectral_beacon.py",
    "ilc_core/network/d2d/spectral_route_token.py",
    "ilc_core/network/d2d/spectral_sigma_policy.py",
    "tools/sim_ccss_spectral_01_adversary_model.py",
}

BATCH_080_TARGETS = {
    "docs/specs/ilc_obl039_obl040_pre_rc_closure_record_1573l_v0.1.md",
    "docs/specs/ilc_ccss_public_rc_privacy_claim_boundary_1573o_v0.1.md",
    "docs/specs/ilc_ccss_metadata_leakage_audit_1573p_v0.1.md",
    "docs/specs/ilc_ccss_cover_batching_design_1573r_v0.1.md",
    "docs/specs/ilc_ccss_contact_gate_policy_spec_1573s_v0.1.md",
    "ilc_core/ccss/contact_gate.py",
    "tools/sim/sim_ccss_side_channel_1573q.py",
}


def _obl_rows() -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    for line in OBL_REGISTER.read_text().splitlines():
        if line.startswith("| OBL-"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            rows[parts[0]] = parts
    return rows


def _ledger_annotations() -> list[dict[str, object]]:
    return json.loads(LEDGER.read_text())["annotations"]


def test_phase_1573u_sweeps_all_48_obligation_rows() -> None:
    rows = _obl_rows()
    assert len(rows) == 48
    assert all(row[3] for row in rows.values())
    assert "obligation_register_sweep_complete_phase_1573u" in OBL_REGISTER.read_text()


def test_only_non_closed_rows_are_external_invariant_or_post_patent() -> None:
    rows = _obl_rows()
    non_closed = {
        obl_id: row[3]
        for obl_id, row in rows.items()
        if not row[3].startswith("closed")
    }
    assert non_closed == {}
    assert rows["OBL-001"][3].startswith("closed - provisional application-number evidence recorded")
    assert rows["OBL-002"][3] == "closed - converted to standing release-control invariant"
    assert rows["OBL-030"][3] == "closed - routed to post-public-RC Atlas of Cliffs side-project plan"
    assert "Written USPTO filing receipts remain pending" in rows["OBL-001"][4]
    assert "Standing invariant" in rows["OBL-002"][4]
    assert rows["OBL-030"][5] == "Post-public-RC personal/Genesis side-project lane"


def test_phase_1573u_status_records_sweep_and_non_activation_tokens() -> None:
    status = STATUS.read_text()
    for token in (
        "atlas_ledger_batch_079_phase_1573e_1573i_registered_phase_1573u",
        "atlas_ledger_batch_080_phase_1573j_current_registered_phase_1573u",
        "atlas_ledger_field_rename_conversion_candidate_fixed_phase_1573u",
        "obl_register_sweep_complete_phase_1573u",
        "pre_1573v_coherence_check_pass_phase_1573u",
        "all_pre_rc_blocking_obl_rows_closed_or_routed_phase_1573u",
        "public_path_remains_blocked_phase_1573u",
    ):
        assert token in status


def test_fix38_conversion_candidate_field_rename_is_repaired() -> None:
    hits = [
        annotation
        for annotation in _ledger_annotations()
        if annotation.get("candidate_id") == "conversion_candidate_runtime_1573j"
    ]
    assert len(hits) == 1
    assert hits[0]["repo_path"] == "ilc_core/ledger/conversion_candidate_runtime.py"
    assert "path" not in hits[0]


def test_fix38_batch_079_and_080_targets_are_registered() -> None:
    annotations = _ledger_annotations()
    by_batch = {}
    for annotation in annotations:
        by_batch.setdefault(annotation.get("annotation_batch"), set()).add(
            annotation.get("repo_path")
        )

    assert (
        len(by_batch["manual_batch_079_phase_1573e_1573i_retroactive"])
        == 19
    )
    assert len(by_batch["manual_batch_080_phase_1573j_current"]) == 45
    assert BATCH_079_TARGETS <= by_batch[
        "manual_batch_079_phase_1573e_1573i_retroactive"
    ]
    assert BATCH_080_TARGETS <= by_batch[
        "manual_batch_080_phase_1573j_current"
    ]


def test_fix38_recent_backfill_summaries_are_not_file_headers() -> None:
    for annotation in _ledger_annotations():
        if annotation.get("annotation_batch") not in {
            "manual_batch_079_phase_1573e_1573i_retroactive",
            "manual_batch_080_phase_1573j_current",
        }:
            continue
        summary = str(annotation.get("manual_read_summary", ""))
        assert not summary.startswith("SPDX-License-Identifier")
        assert not summary.startswith("!/usr/bin/env")


def test_ledger_target_backfill_does_not_claim_historical_gap_closure() -> None:
    register = " ".join(OBL_REGISTER.read_text().lower().split())
    assert "full historical pre-protocol fix38 gap remains large" in register
    assert "separate catch-up backlog" in register
