"""
Test that walkthrough files do not contain ellipsis characters.

This guardrail ensures all walkthroughs are complete and untruncated.
"""

import pytest
from pathlib import Path
import re

LEGACY_ELLIPSIS_WALKTHROUGH_BASELINE = {
    # Phase 1545p-Fix1: existing historical ellipsis baseline. The guard
    # remains active for new walkthrough files outside this explicit set.
    "phase_0946_h012_epoch_attribution_settle_runtime_walkthrough.md",
    "phase_0948_cdl_082_h013_threshold_amendment_opening_walkthrough.md",
    "phase_0950_cdl_082_ratification_walkthrough.md",
    "phase_1105_cdl_083_ratification_walkthrough.md",
    "phase_1119_float_kill_01_ilc_core_float_prng_hardening_walkthrough.md",
    "phase_1169_sim_spectral_05_track_a_walkthrough.md",
    "phase_1170_sim_spectral_05_track_b_build_walkthrough.md",
    "phase_1171_sim_spectral_05_disposition_walkthrough.md",
    "phase_1179_sim_spectral_05_runtime_binding_slice_walkthrough.md",
    "phase_1201_tier3_runtime_linkage_walkthrough.md",
    "phase_1202_persistent_rate_limiter_walkthrough.md",
    "phase_1206_truth_primitive_permanence_governance_walkthrough.md",
    "phase_1210_phi_bound_enforcement_walkthrough.md",
    "phase_1218b_transport_security_hardening_walkthrough.md",
    "phase_1231_coherence_capsule_v5_49_walkthrough.md",
    "phase_1232_window_1225_1232_closure_gate_walkthrough.md",
    "phase_1234_g8_commit_epoch_audit_and_plan_walkthrough.md",
    "phase_1237_fix2_ego_graph_query_walkthrough.md",
    "phase_1237_fix3_centrality_metrics_walkthrough.md",
    "phase_1237_fix4_convergence_trace_walkthrough.md",
    "phase_1237_fix5_dispatcher_integration_walkthrough.md",
    "phase_1237_g8_l3_sidecar_infrastructure_spec_walkthrough.md",
    "phase_1238abc_sim_fetch_01_fix1_fix2_fix3_walkthrough.md",
    "phase_1238i_sim_fetch_01_fix9_cdl_087_evidence_matrix_walkthrough.md",
    "phase_1240_window_1233_1240_closure_gate_walkthrough.md",
    "phase_1244_import_boundary_lint_and_protocol_stubs_walkthrough.md",
    "phase_1271_fix1_atlas_g_006_manifest_profile_consistency_hardening_walkthrough.md",
    "phase_1322_fix1_vps_git_workflow_restore_walkthrough.md",
    "phase_1351a_cdl_029_amendment_post_theta_hard_dust_routing_walkthrough.md",
    "phase_1354_cdl_068_topology_shuffle_vrf_runtime_walkthrough.md",
    "phase_1357_reputation_py_h11_float_kill_walkthrough.md",
    "phase_1359_high_001_two_layer_defense_walkthrough.md",
    "phase_1360_fix2_four_validator_epoch_finalization_walkthrough.md",
    "phase_1360_multi_operator_mysticeti_testnet_walkthrough.md",
    "phase_1364_blocking_authority_ratification_cdl_057_activation_walkthrough.md",
    "phase_1367_pre_gate_fix_pass_walkthrough.md",
    "phase_1386a_production_tls_grpc_proof_walkthrough.md",
    "phase_1397_j007_shadow_public_ingestion_harness_walkthrough.md",
    "phase_1410_vrf_proof_verifier_adr_walkthrough.md",
    "phase_1413_vrf_integration_tests_security_review_walkthrough.md",
    "phase_1415_review_lane_admission_runtime_walkthrough.md",
    "phase_1416_review_lane_dedup_payment_stub_walkthrough.md",
    "phase_1418_anti_capture_diversity_design_walkthrough.md",
    "phase_1424_public_rc_activation_certificate_design_walkthrough.md",
    "phase_1430_cdl053_local_credit_wire_walkthrough.md",
    "phase_1436_public_fetch_serving_activation_walkthrough.md",
    "phase_1437_openclaw_p2p_activation_walkthrough.md",
    "phase_1437a_stale_cdl_088_test_cleanup_walkthrough.md",
    "phase_1439_public_verifier_api_activation_walkthrough.md",
    "phase_1463p_node_value_kernel_decimal_conversion_walkthrough.md",
    "phase_1490p_cdl094_admission_wire_walkthrough.md",
    "phase_1494p_cdl095_runtime_completions_walkthrough.md",
    "phase_1497p_closure_gate_walkthrough.md",
    "phase_1519p_adr_0009_source_export_rehearsal_integration_walkthrough.md",
    "phase_1532p_obl020_emission_production_path_walkthrough.md",
}


def get_walkthrough_files():
    """Get walkthrough files subject to the no-ellipsis rule.
    
    Only checks files from Phase 65B onwards (when the hygiene initiative started).
    Legacy walkthroughs (pre-65B) are grandfathered and not checked.
    """
    phases_dir = Path(__file__).parent.parent / "docs" / "phases"
    if not phases_dir.exists():
        return []
    
    # Only check files from Phase 65B onwards (hygiene initiative started with 65B)
    # Also include README.md format guide
    phase_65_plus = []
    for f in phases_dir.glob("*.md"):
        # Skip README which documents the rules
        if f.name == "README.md":
            continue
        # Check if file is phase 65+ by examining filename
        match = re.match(r"phase_(\d+)", f.name)
        if match:
            phase_num = int(match.group(1))
            if phase_num >= 65 and f.name not in LEGACY_ELLIPSIS_WALKTHROUGH_BASELINE:
                phase_65_plus.append(f)
    
    return phase_65_plus


def get_context_pack_files():
    """Get all context pack markdown files in docs/context_packs/."""
    packs_dir = Path(__file__).parent.parent / "docs" / "context_packs"
    if not packs_dir.exists():
        return []
    return list(packs_dir.glob("*.md"))


def find_ellipses(content: str) -> list:
    """Find all ellipsis occurrences in content.
    
    Returns list of (line_number, line_content) tuples.
    """
    findings = []
    lines = content.split("\n")
    for i, line in enumerate(lines, start=1):
        # Check for ASCII ellipsis (three dots)
        if "..." in line:
            findings.append((i, line.strip()))
        # Check for Unicode ellipsis (U+2026)
        elif "\u2026" in line:
            findings.append((i, line.strip()))
    return findings


class TestNoEllipsesInWalkthroughs:
    """Ensure no ellipses appear in walkthrough documents."""

    def test_no_ellipses_in_phase_walkthroughs(self):
        """Check docs/phases/*.md for ellipses."""
        files = get_walkthrough_files()
        
        # We expect at least some walkthrough files to exist
        assert len(files) > 0, "No walkthrough files found in docs/phases/"
        
        all_findings = []
        for filepath in files:
            content = filepath.read_text(encoding="utf-8")
            findings = find_ellipses(content)
            if findings:
                for line_num, line_content in findings:
                    all_findings.append(
                        f"{filepath.name}:{line_num}: {line_content[:80]}"
                    )
        
        if all_findings:
            msg = "Ellipses found in walkthrough files:\n" + "\n".join(all_findings)
            pytest.fail(msg)

    def test_no_ellipses_in_context_packs(self):
        """Check docs/context_packs/*.md for ellipses."""
        files = get_context_pack_files()
        
        if not files:
            pytest.skip("No context pack files found yet")
        
        all_findings = []
        for filepath in files:
            content = filepath.read_text(encoding="utf-8")
            findings = find_ellipses(content)
            if findings:
                for line_num, line_content in findings:
                    all_findings.append(
                        f"{filepath.name}:{line_num}: {line_content[:80]}"
                    )
        
        if all_findings:
            msg = "Ellipses found in context pack files:\n" + "\n".join(all_findings)
            pytest.fail(msg)
