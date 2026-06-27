# SPDX-License-Identifier: AGPL-3.0-only
"""Compatibility module for the Phase 1567 prompt verification command."""

from tests.test_phase_1567_block6_tailscale_topology_deploy import (  # noqa: F401
    test_phase_1567_codex_harness_is_rehearsal_only,
    test_phase_1567_completion_tokens_are_emitted,
    test_phase_1567_non_authorization_boundary_is_preserved,
    test_phase_1567_openclaw_refresh_is_confirmed_without_clawhub_publication,
    test_phase_1567_records_passing_four_node_topology,
)
