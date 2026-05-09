from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = ROOT / "docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1285_transport_principal_public_path_activation_preflight_walkthrough.md"
)
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
TP_HELPER = ROOT / "ilc_core/network/d2d/transport_principal_public_path_preflight.py"

REQUIRED_TOKENS = (
    "transport_principal_public_path_activation_preflight_phase_1285.v0.1",
    "transport_principal_public_p2p_not_activated_phase_1285",
    "public_fetch_serving_not_enabled_phase_1285",
    "requester_id_fallback_still_forbidden_phase_1285",
    "transport_principal_lifecycle_revocation_replay_required_phase_1285",
)

CARRY_FORWARD_TOKENS = (
    "transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation",
    "transport_principal_public_path_authority_not_activated_phase_1285",
    "phase_1286_sidecar_public_projection_privacy_serving_preflight_next",
    "public_rc_remains_blocked_after_phase_1285",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1285_required_tokens_are_published_across_frontier_docs() -> None:
    for path in (SPEC, WALKTHROUGH, PLANNING, STATUS, ROADMAP, CAPSULE):
        text = read(path)
        for token in REQUIRED_TOKENS + CARRY_FORWARD_TOKENS:
            assert token in text


def test_phase_1285_records_discovery_discipline_and_source_expansion() -> None:
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
        "docs/specs/ilc_transport_principal_public_path_adr_runtime_preflight_1277_v0.1.md",
        "docs/specs/ilc_transport_principal_runtime_identity_pre_public_path_1267_v0.1.md",
        "docs/specs/ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md",
        "ilc_core/network/d2d/transport_principal_public_path_preflight.py",
    ):
        assert source in spec


def test_phase_1285_preserves_no_public_path_activation() -> None:
    spec = read(SPEC)

    assert "transport_principal_public_path_activation_verdict_phase_1285=preflight_only_no_public_path_activation" in spec
    assert "No public P2P exposure is authorized" in spec
    assert "No public fetch serving is authorized" in spec
    assert "No public P2P exposure, public fetch serving, non-loopback sidecar/projection serving" in spec
    assert "public listener" in spec
    assert "public host bind" in spec
    assert "wildcard bind" in spec
    assert "peer discovery" in spec


def test_phase_1285_keeps_existing_helper_excluded_and_adds_no_runtime_helper() -> None:
    spec = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    helper_header = "\n".join(read(TP_HELPER).splitlines()[:5])

    assert "No new runtime helper was introduced in Phase 1285" in spec
    assert "No new runtime helper was introduced" in walkthrough
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in helper_header
    assert "Phase 1285 does not promote the Phase 1277 helper into a public RC package" in spec


def test_phase_1285_lifecycle_revocation_replay_and_fallback_requirements_remain_open() -> None:
    spec = read(SPEC)

    for phrase in (
        "credential issuer",
        "credential issue, expiry, rotation, and renewal rules",
        "revocation-set authority",
        "replay-cache scope",
        "admission-key derivation",
        "ban-key derivation",
        "rate-limit-key derivation",
        "privacy mode selection",
        "hostile-network validation",
        "requester_id",
        "client_ip",
        "AgentID",
        "harness_identity",
    ):
        assert phrase in spec


def test_phase_1285_frontier_routes_to_phase_1286_preflight() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    status = read(STATUS)

    assert "Window 1281-1288 is OPEN through Phase 1286" in planning
    assert "Window 1281-1288 is open through Phase 1286" in capsule
    assert "## Phase 1285" in status
    assert "phase_1286_sidecar_public_projection_privacy_serving_preflight_next" in planning
    assert "## Phase 1286" in status
    assert "phase_1287_release_publication_signing_authorization_preflight_next" in planning


def test_phase_1285_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    register = read(CDL_REGISTER)

    assert "transport_principal_public_path_activation_preflight_phase_1285.v0.1" not in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "| CDL-088 |" not in register


def test_phase_1285_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_transport_principal_public_path_activation_preflight_1285_v0.1.md -> transport/identity",
        "graph_delta=support_tests_added:tests/test_phase_1285_transport_principal_public_path_activation_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1285_transport_principal_public_path_activation_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in read(SPEC)
        assert graph_delta in read(WALKTHROUGH)
        assert graph_delta in read(STATUS)
