# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = REPO_ROOT / "docs" / "specs" / "ilc_ccss_cover_batching_design_1573r_v0.1.md"
SIM_JSON_PATH = REPO_ROOT / "docs" / "sims" / "ilc_ccss_side_channel_sim_1573q_v0.1.json"
PROMPT_1574_PATH = (
    REPO_ROOT
    / "docs"
    / "antigravity_tasks"
    / "antigravity_prompt__phase_1574_g10_block6_publication_readiness_audit.md"
)
STATUS_PATH = REPO_ROOT / "docs" / "phases" / "STATUS.md"


def test_phase_1573r_design_uses_1573q_recommended_profile() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    sim = json.loads(SIM_JSON_PATH.read_text(encoding="utf-8"))
    profile = sim["recommended_controls_for_1573r"]
    assert profile["policy_token"] == "ccss_pre_rc_cover_batch_profile_v1_candidate"
    assert "ccss_pre_rc_cover_batch_profile_v1_candidate" in spec
    assert "120 seconds" in spec
    assert "128 indistinguishable bundles" in spec
    assert "8 cover bundles per real bundle" in spec
    assert "route_purpose_visible_to_relay\": false" in spec
    assert "relay-path rotation" in spec


def test_phase_1573r_fixed_bundle_ttl_and_offline_policy_are_specified() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    assert '"bundle_size_bytes": 65536' in spec
    assert "`bundle_ttl_windows` | 5" in spec
    assert "`bundle_ttl_seconds` | 600" in spec
    assert "`offline_mailbox_retention_windows` | 20" in spec
    assert "`offline_mailbox_retention_seconds` | 2400" in spec
    assert "`recipient_pull_required` | true" in spec
    assert "`public_delivery_claim` | false" in spec


def test_phase_1573r_future_runtime_guard_is_required_not_cleared() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    assert "CCSS_COVER_BATCHING_NOT_ACTIVATED = True" in spec
    assert "does not activate the profile" in spec
    assert "does not authorize stronger public claims" in spec
    assert "public-RC gate authorization" in spec


def test_phase_1573r_claim_boundary_preserves_nonclaims() -> None:
    spec = SPEC_PATH.read_text(encoding="utf-8")
    forbidden_claims = [
        "ILC proves network anonymity.",
        "ILC provides formal differential privacy for CCSS traffic.",
        "ILC is Signal-equivalent.",
        "ILC hides timing, size, and relay-path metadata against global observers.",
    ]
    for claim in forbidden_claims:
        assert claim in spec
    assert "not a formal anonymity or\ndifferential privacy proof" in spec


def test_phase_1574_prompt_requires_1573r_for_stronger_ccss_claims() -> None:
    text = PROMPT_1574_PATH.read_text(encoding="utf-8")
    assert "ccss_side_channel_sim_committed_phase_1573q" in text
    assert "ccss_cover_batching_design_committed_phase_1573r" in text
    assert "ccss_pre_rc_cover_batch_profile_v1_candidate" in text
    assert "configured anonymity-set and metadata-minimization" in text


def test_phase_1573r_status_tokens_present() -> None:
    text = STATUS_PATH.read_text(encoding="utf-8")
    assert "ccss_cover_batching_design_committed_phase_1573r" in text
    assert "ccss_fixed_bundle_shape_specified_phase_1573r" in text
    assert "ccss_ttl_drop_policy_specified_phase_1573r" in text
    assert "ccss_offline_recipient_policy_specified_phase_1573r" in text
    assert "ccss_cover_batching_not_activated_phase_1573r" in text
    assert "public_path_remains_blocked_phase_1573r" in text
