from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = ROOT / "docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1283_public_claimability_authority_decision_preflight_walkthrough.md"
)
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SWEEPER_RUNTIME = ROOT / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
CLAIMABILITY_RUNTIME = ROOT / "ilc_core/ledger/claimability_proof_binding_runtime.py"

REQUIRED_TOKENS = (
    "public_claimability_authority_decision_preflight_phase_1283.v0.1",
    "public_claimability_activation_requires_explicit_human_authorization_phase_1283",
    "public_claimability_activation_not_authorized_by_default_phase_1283",
    "wallet_withdrawal_transfer_spend_still_blocked_phase_1283",
    "claimability_human_question_escalation_required_phase_1283",
    "public_claimability_authority_verdict_phase_1283=no_activation_no_public_api",
    "phase_1284_claimability_verifier_api_boundary_preflight_next",
    "public_rc_remains_blocked_after_phase_1283",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1283_required_tokens_are_published_across_frontier_docs() -> None:
    for path in (SPEC, WALKTHROUGH, PLANNING, STATUS, ROADMAP, CAPSULE):
        text = read(path)
        for token in REQUIRED_TOKENS:
            assert token in text


def test_phase_1283_authority_verdict_does_not_grant_public_claimability() -> None:
    spec = read(SPEC)

    assert "public_claimability_authority_verdict_phase_1283=no_activation_no_public_api" in spec
    assert "Phase 1283 does not grant public claimability authority" in spec
    assert "No public or non-loopback claimability API is authorized" in spec
    assert "No wallet withdrawal, transfer, spend, signing, or ledger-write authority" in spec
    assert "No ECU mint, ILC settlement, withdrawal runtime" in spec
    assert "No source export, release artifact, release key, release envelope" in spec
    assert "No public claim endpoint, HTTP route, socket listener, non-loopback bind" in spec


def test_phase_1283_records_discovery_discipline_and_source_expansion() -> None:
    for path in (SPEC, WALKTHROUGH):
        text = read(path)
        for phrase in (
            "§0a Known-token audit",
            "§0b Concept-discovery search",
            "§0c Contradiction and non-claim search",
            "§0d Source expansion and newly discovered tokens",
            "Exact-token `rg`",
        ):
            assert phrase in text

    spec = read(SPEC)
    for source in (
        "docs/specs/ilc_phase_1281_1288_sequence_lock_v0.1.md",
        "docs/specs/ilc_window_1281_1288_candidate_phase_grouping_v0.1.md",
        "docs/specs/ilc_gap13_claimability_conversion_sweeper_preflight_1270_v0.1.md",
        "docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md",
        "docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md",
        "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md",
        "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
        "ilc_core/ledger/claimability_proof_binding_runtime.py",
    ):
        assert source in spec


def test_phase_1283_keeps_internal_helpers_excluded_from_public_rc_surface() -> None:
    sweeper_header = "\n".join(read(SWEEPER_RUNTIME).splitlines()[:5])
    claimability_header = "\n".join(read(CLAIMABILITY_RUNTIME).splitlines()[:5])
    spec = read(SPEC)

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in sweeper_header
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in claimability_header
    assert "The Phase 1274 and Phase 1275 helpers remain internal phase helpers" in spec
    assert "retain their `PUBLIC_RC_EXCLUDE` launch-surface exclusion" in spec
    assert "release allowlist review has not promoted the internal helpers" in spec


def test_phase_1283_frontier_routes_to_sensitive_phase_1284() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    status = read(STATUS)

    assert "public_claimability_authority_decision_preflight_phase_1283.v0.1" in planning
    assert "Window 1281-1288 executed through Phase 1288" in planning
    assert "public_claimability_authority_decision_preflight_phase_1283.v0.1" in capsule
    assert "## Phase 1283" in status
    assert "Phase 1284 - Public claimability verifier/API boundary preflight" in status
    assert "Phase 1285" in capsule
    assert "Phase 1285 - TransportPrincipal public-path activation preflight" in status


def test_phase_1283_public_rc_blockers_remain_explicit() -> None:
    for path in (SPEC, WALKTHROUGH, PLANNING, ROADMAP, CAPSULE, STATUS):
        text = read(path)
        assert "public_rc_remains_blocked_after_phase_1283" in text

    for path in (SPEC, WALKTHROUGH, CAPSULE, STATUS):
        text = read(path)
        assert "public claimability verifier/API boundary" in text
        assert "TransportPrincipal public-path activation" in text
        assert "sidecar public projection" in text
        assert "release" in text
        assert "v0.2 signing" in text


def test_phase_1283_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    register = read(CDL_REGISTER)

    assert "public_claimability_authority_decision_preflight_phase_1283.v0.1" not in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "| CDL-088 |" in register
    assert "cdl_088_ratified_phase_1376" in register
    assert "cdl087_ratified_phase_1278_fix1" in register

    phase_text = read(SPEC) + "\n" + read(WALKTHROUGH)
    assert "CDL mutation" in phase_text
    assert "CDL-088 opening" in phase_text


def test_phase_1283_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md -> ecu/ilc/public_rc",
        "graph_delta=support_tests_added:tests/test_phase_1283_public_claimability_authority_decision_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1283_public_claimability_authority_decision_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in read(SPEC)
        assert graph_delta in read(WALKTHROUGH)
        assert graph_delta in read(STATUS)
