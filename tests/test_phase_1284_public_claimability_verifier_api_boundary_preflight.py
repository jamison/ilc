from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = ROOT / "docs/specs/ilc_public_claimability_verifier_api_boundary_preflight_1284_v0.1.md"
WALKTHROUGH = (
    ROOT
    / "docs/phases/phase_1284_public_claimability_verifier_api_boundary_preflight_walkthrough.md"
)
PLANNING = ROOT / "docs/PLANNING_INDEX.md"
STATUS = ROOT / "docs/phases/STATUS.md"
ROADMAP = ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
CAPSULE = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.51.md"
CDL_REGISTER = ROOT / "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SWEEPER_RUNTIME = ROOT / "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py"
CLAIMABILITY_RUNTIME = ROOT / "ilc_core/ledger/claimability_proof_binding_runtime.py"

REQUIRED_TOKENS = (
    "public_claimability_verifier_api_boundary_preflight_phase_1284.v0.1",
    "claimability_api_public_serving_not_enabled_phase_1284",
    "claimability_verifier_authority_not_activated_phase_1284",
    "wallet_withdrawal_transfer_spend_still_blocked_phase_1284",
    "public_rc_exclude_internal_helper_required_phase_1284",
)

CARRY_FORWARD_TOKENS = (
    "public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api",
    "phase_1285_transport_principal_public_path_activation_preflight_next",
    "public_rc_remains_blocked_after_phase_1284",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1284_required_tokens_are_published_across_frontier_docs() -> None:
    for path in (SPEC, WALKTHROUGH, PLANNING, STATUS, ROADMAP, CAPSULE):
        text = read(path)
        for token in REQUIRED_TOKENS + CARRY_FORWARD_TOKENS:
            assert token in text


def test_phase_1284_records_discovery_discipline_and_source_expansion() -> None:
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
        "docs/specs/ilc_public_claimability_authority_decision_preflight_1283_v0.1.md",
        "docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md",
        "docs/specs/ilc_cdl048_conversion_sweeper_runtime_skeleton_1274_v0.1.md",
        "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md",
        "ilc_core/ledger/claimability_proof_binding_runtime.py",
        "ilc_core/ledger/cdl048_conversion_sweeper_runtime.py",
    ):
        assert source in spec


def test_phase_1284_boundary_verdict_does_not_grant_public_api_or_claimability() -> None:
    spec = read(SPEC)

    assert "public_claimability_verifier_api_boundary_verdict_phase_1284=internal_boundary_only_no_public_api" in spec
    assert "No public verifier service is authorized" in spec
    assert "No public claim endpoint, HTTP route" in spec
    assert "FastAPI router" in spec
    assert "socket listener" in spec
    assert "non-loopback bind" in spec
    assert "wildcard bind" in spec
    assert "public host bind" in spec
    assert "wallet write path" in spec
    assert "ECU mint endpoint" in spec
    assert "ILC settlement endpoint" in spec


def test_phase_1284_adds_no_new_runtime_helper_and_keeps_existing_helpers_excluded() -> None:
    spec = read(SPEC)
    walkthrough = read(WALKTHROUGH)
    sweeper_header = "\n".join(read(SWEEPER_RUNTIME).splitlines()[:5])
    claimability_header = "\n".join(read(CLAIMABILITY_RUNTIME).splitlines()[:5])

    assert "No new runtime helper was introduced in this phase" in spec
    assert "No new runtime helper was introduced" in walkthrough
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in sweeper_header
    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in claimability_header
    assert "Phase 1255 source allowlist rules already exclude header-marked internal helpers" in spec
    assert "Phase 1284 does not promote either helper into a public RC package" in walkthrough


def test_phase_1284_future_public_presentation_preconditions_remain_open() -> None:
    spec = read(SPEC)

    for phrase in (
        "Field-level public disclosure",
        "privacy filtering",
        "nullifier/claim-registry semantics",
        "TransportPrincipal binding",
        "replay prevention for submitted public claims",
        "release allowlist promotion",
        "not sufficient for public claim submission semantics",
    ):
        assert phrase in spec


def test_phase_1284_frontier_routes_to_sensitive_phase_1285() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    status = read(STATUS)

    assert "Window 1281-1288 is OPEN through Phase 1284" in planning
    assert "Window 1281-1288 is open through Phase 1284" in capsule
    assert "## Phase 1284" in status
    assert "Phase 1285 is sensitive and requires explicit `GO Phase 1285`" in planning
    assert "Phase 1285 remains pending and SENSITIVE" in capsule
    assert "Phase 1285 - TransportPrincipal public-path activation preflight" in status


def test_phase_1284_public_rc_blockers_remain_explicit() -> None:
    for path in (SPEC, WALKTHROUGH, PLANNING, ROADMAP, CAPSULE, STATUS):
        text = read(path)
        assert "public_rc_remains_blocked_after_phase_1284" in text
        assert "TransportPrincipal public-path activation" in text
        assert "sidecar public projection" in text
        assert "release" in text
        assert "v0.2 signing" in text
        assert "wallet withdrawal" in text


def test_phase_1284_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    register = read(CDL_REGISTER)

    assert "public_claimability_verifier_api_boundary_preflight_phase_1284.v0.1" not in register
    assert "| CDL-087 |" in register
    assert "| ratified |" in register
    assert "| CDL-088 |" not in register
    assert "cdl087_ratified_phase_1278_fix1" in register


def test_phase_1284_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=load_bearing_spec_added:docs/specs/ilc_public_claimability_verifier_api_boundary_preflight_1284_v0.1.md -> ecu/ilc/public_rc",
        "graph_delta=support_tests_added:tests/test_phase_1284_public_claimability_verifier_api_boundary_preflight.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1284_public_claimability_verifier_api_boundary_preflight_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.51.md -> planning/frontier",
    )
    for graph_delta in expected:
        assert graph_delta in read(SPEC)
        assert graph_delta in read(WALKTHROUGH)
        assert graph_delta in read(STATUS)
