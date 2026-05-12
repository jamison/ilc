from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_deep_no_activation_assertion_audit_1301_v0.1.md"
PROMPT = "docs/antigravity_tasks/antigravity_prompt__phase_1301_g8_deep_no_activation_assertion_audit.md"
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1301_deep_no_activation_assertion_audit_walkthrough.md"
SERVER = "ilc_core/server.py"
ASGI = "ilc_core/asgi.py"
SIDECAR_PREFLIGHT = "ilc_core/graph/sidecar_public_path_preflight.py"
TP_PREFLIGHT = "ilc_core/network/d2d/transport_principal_public_path_preflight.py"
CLAIMABILITY = "ilc_core/ledger/claimability_proof_binding_runtime.py"
CONVERSION = "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
PACKAGE_CI = "ilc_core/rc/package_profile_ci_gate.py"
LOCAL_PREVIEW = "ilc_core/rc/local_skill_preview.py"
ATLAS = "ilc_core/rc/atlas_graph_discipline.py"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "deep_no_activation_assertion_audit_phase_1301.v0.1",
    "no_activation_audit_verdict_phase_1301=pass_or_blockers_recorded",
    "public_endpoint_activation_absent_or_blocked_phase_1301",
    "release_artifact_activation_absent_or_blocked_phase_1301",
    "genesis_signing_activation_absent_or_blocked_phase_1301",
    "wallet_ecu_ilc_activation_absent_or_blocked_phase_1301",
    "public_rc_remains_blocked_after_phase_1301",
    "phase_1302_window_1289_1302_closure_gate_next",
)

DISCOVERY_TOKENS = (
    "legacy_public_labeled_fastapi_routes_carry_forward_phase_1301",
    "legacy_public_labeled_fastapi_routes_not_public_rc_clean_phase_1301",
    "public_p2p_fetch_sidecar_activation_absent_or_blocked_phase_1301",
    "public_rc_exclude_helpers_still_internal_phase_1301",
    "source_export_publication_activation_absent_or_blocked_phase_1301",
    "cdl_mutation_cdl088_activation_absent_phase_1301",
    "phase_1302_requires_explicit_go_phase_1301",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1301_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:7]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1301_discovered_legacy_public_routes_are_recorded_as_blockers() -> None:
    spec = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    server = read(SERVER)
    asgi = read(ASGI)

    for token in DISCOVERY_TOKENS:
        assert token in spec
        assert token in walkthrough

    for route in (
        '@router.post("/v1/public/init/admission")',
        '@router.post("/v1/public/receipt")',
        '@router.get("/v1/public/receipts")',
        '@router.get("/v1/public/wallet/{agent_id}/status")',
    ):
        assert route in server

    assert "app = create_app()" in asgi
    assert "exclude, replace, or explicitly gate" in spec
    assert "not as public-RC activation authority" in spec


def test_phase_1301_runtime_helpers_remain_internal_or_declarative() -> None:
    sidecar = read(SIDECAR_PREFLIGHT)
    transport = read(TP_PREFLIGHT)
    claimability = read(CLAIMABILITY)
    conversion = read(CONVERSION)
    package_ci = read(PACKAGE_CI)
    local_preview = read(LOCAL_PREVIEW)
    atlas = read(ATLAS)

    for helper in (sidecar, transport, claimability, conversion):
        assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in helper

    assert "no listener, bind, or serving surface" in sidecar
    assert "does not open sockets" in transport
    assert "does not expose a public API" in claimability
    assert '"public_claimability_runtime_activated": False' in package_ci
    assert '"public_rc_claimed": False' in package_ci
    assert '"public_claimability_enabled": False' in local_preview
    assert '"public_p2p_enabled": False' in local_preview
    assert "no_public_rc_claim" in atlas
    assert "no_public_p2p_exposure" in atlas


def test_phase_1301_records_no_activation_boundary() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        compact = " ".join(text.split())
        for phrase in (
            "source allowlist export execution",
            "materialized export manifest production",
            "public repository publication",
            "public package publication",
            "release artifact production",
            "release-key generation",
            "release envelope production",
            "release signing material generation",
            "public RC claim",
            "public launch claim",
            "public claimability activation",
            "public verifier service activation",
            "public claim endpoint activation",
            "public P2P exposure",
            "public fetch serving activation",
            "public sidecar/projection serving",
            "non-loopback sidecar bind",
            "public listener",
            "peer discovery",
            "TransportPrincipal public-path activation",
            "helper promotion",
            "marker removal",
            "helper stripping",
            "CDL mutation",
            "CDL-088 opening",
            "Genesis Atlas mutation",
            "Genesis Atlas signing",
            "v0.2 signing",
            "wallet withdrawal",
            "wallet transfer",
            "wallet spend",
            "ECU minting",
            "ILC settlement",
        ):
            assert phrase in compact


def test_phase_1301_frontier_docs_advance_to_1302_without_public_rc_authority() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)
    status = read(STATUS)

    assert "Window 1289-1302 is OPEN through Phase 1301" in planning
    assert "Window 1289-1302 is open through Phase 1301" in capsule
    assert "Window 1289-1302 OPEN through Phase 1301" in roadmap
    assert "Phase 1302 is sensitive" in planning
    assert "Phase 1302 is sensitive" in capsule
    assert "Phase 1302 is sensitive" in roadmap
    assert "## Phase 1301" in status
    assert "Phase 1302 - Window 1289-1302 closure gate" in status


def test_phase_1301_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    spec = read(SPEC)

    assert "deep_no_activation_assertion_audit_phase_1301.v0.1" not in cdl
    assert "| CDL-088 |" not in cdl
    assert "CDL mutation" in spec
    assert "CDL-088 opening" in spec


def test_phase_1301_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=support_only:docs/specs/ilc_deep_no_activation_assertion_audit_1301_v0.1.md -> release/publication",
        "graph_delta=support_tests_added:tests/test_phase_1301_deep_no_activation_assertion_audit.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1301_deep_no_activation_assertion_audit_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )

    for text in (read(SPEC), read(WALKTHROUGH), read(STATUS)):
        for graph_delta in expected:
            assert graph_delta in text
