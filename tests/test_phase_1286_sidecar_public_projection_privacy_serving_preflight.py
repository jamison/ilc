from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = ROOT / "docs/specs/ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1286_sidecar_public_projection_privacy_serving_preflight_walkthrough.md"
)
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SIDECAR_HELPER = ROOT / "ilc_core/graph/sidecar_public_path_preflight.py"

REQUIRED_TOKENS = (
    "sidecar_public_projection_privacy_serving_preflight_phase_1286.v0.1",
    "sidecar_public_serving_not_enabled_phase_1286",
    "non_loopback_bind_not_enabled_phase_1286",
    "public_projection_endpoint_not_enabled_phase_1286",
    "transport_principal_activation_required_before_public_projection_phase_1286",
)

CARRY_FORWARD_TOKENS = (
    "sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving",
    "no_new_public_listener_phase_1286",
    "peer_discovery_not_enabled_phase_1286",
    "phase_1287_release_publication_signing_authorization_preflight_next",
    "public_rc_remains_blocked_after_phase_1286",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1286_required_tokens_are_published_across_frontier_docs() -> None:
    for path in (SPEC, WALKTHROUGH, PLANNING, STATUS, ROADMAP, CAPSULE):
        text = read(path)
        for token in REQUIRED_TOKENS + CARRY_FORWARD_TOKENS:
            assert token in text


def test_phase_1286_records_discovery_discipline_and_source_expansion() -> None:
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
        "docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md",
        "docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md",
        "docs/specs/ilc_cdl_087_ratification_evidence_1278_fix1_v0.1.md",
        "docs/specs/ilc_sidecar_loopback_projection_endpoint_boundary_1268_v0.1.md",
        "ilc_core/graph/sidecar_public_path_preflight.py",
        "ilc_core/graph/sidecar_query_runtime.py",
    ):
        assert source in spec


def test_phase_1286_preserves_no_public_projection_serving() -> None:
    spec = read(SPEC)

    assert "sidecar_public_projection_privacy_serving_verdict_phase_1286=preflight_only_no_public_serving" in spec
    assert "No public sidecar/projection serving is authorized" in spec
    assert "No public projection endpoint is authorized" in spec
    assert "No non-loopback bind, wildcard bind, public host bind" in spec
    assert "listener" in spec
    assert "peer discovery" in spec
    assert "public fetch serving" in spec
    assert "public P2P exposure" in spec


def test_phase_1286_keeps_existing_helper_excluded_and_adds_no_runtime_helper() -> None:
    spec = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    helper_header = "\n".join(read(SIDECAR_HELPER).splitlines()[:5])

    assert "No new runtime helper was introduced in Phase 1286" in spec
    assert "Phase 1286 introduced no runtime helper" in walkthrough
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in helper_header
    assert "Phase 1286 does not promote the Phase 1278 helper into a public RC package" in spec


def test_phase_1286_records_privacy_and_abuse_risks() -> None:
    spec = read(SPEC)

    for phrase in (
        "graph-membership leakage",
        "serving-peer leakage",
        "fetch-incentive",
        "stable node or principal correlation",
        "cross-epoch correlation",
        "query abuse",
        "scraping",
        "result-size amplification",
        "public-safe field filtering",
        "hostile-network validation",
    ):
        assert phrase in spec


def test_phase_1286_frontier_routes_to_phase_1287_preflight() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    status = read(STATUS)

    assert "Phase 1286" in planning
    assert "Phase 1286" in capsule
    assert "## Phase 1286" in status
    assert "phase_1287_release_publication_signing_authorization_preflight_next" in planning
    assert "public_rc_remains_blocked_after_phase_1286" in planning


def test_phase_1286_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    register = read(CDL_REGISTER)

    assert "sidecar_public_projection_privacy_serving_preflight_phase_1286.v0.1" not in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "| CDL-088 |" not in register


def test_phase_1286_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_sidecar_public_projection_privacy_serving_preflight_1286_v0.1.md -> sidecar/public_path",
        "graph_delta=support_tests_added:tests/test_phase_1286_sidecar_public_projection_privacy_serving_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1286_sidecar_public_projection_privacy_serving_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in read(SPEC)
        assert graph_delta in read(WALKTHROUGH)
        assert graph_delta in read(STATUS)
