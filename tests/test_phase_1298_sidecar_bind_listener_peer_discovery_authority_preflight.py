from pathlib import Path

from tools.validate_phase_prompt import validate


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_sidecar_bind_listener_peer_discovery_authority_preflight_1298_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1298_g8_sidecar_bind_listener_peer_discovery_authority_preflight.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = (
    "docs/phases/"
    "phase_1298_sidecar_bind_listener_peer_discovery_authority_preflight_walkthrough.md"
)
LOCK = "docs/specs/ilc_phase_1289_1302_sequence_lock_v0.1.md"
GUIDANCE = "docs/specs/ilc_window_1289_1302_candidate_phase_grouping_v0.1.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"
SIDECAR_HELPER = "ilc_core/graph/sidecar_public_path_preflight.py"
SIDECAR_RUNTIME = "ilc_core/graph/sidecar_query_runtime.py"

REQUIRED_TOKENS = (
    "sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1",
    "sidecar_bind_listener_peer_discovery_verdict_phase_1298=preflight_only_no_public_serving",
    "non_loopback_bind_not_enabled_phase_1298",
    "public_listener_not_enabled_phase_1298",
    "peer_discovery_not_enabled_phase_1298",
    "public_sidecar_projection_serving_not_enabled_phase_1298",
    "public_rc_remains_blocked_after_phase_1298",
    "phase_1299_release_allowlist_artifact_genesis_readiness_preflight_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1298_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:7]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1298_prompt_uses_active_1289_1302_preflight_scope() -> None:
    prompt_path = ROOT / PROMPT
    prompt = read(PROMPT)

    assert validate(prompt_path) == []
    assert "Sidecar Bind Listener Peer Discovery Authority Preflight" in prompt
    assert "ilc_phase_1289_1302_sequence_lock_v0.1.md" in prompt
    assert "ilc_window_1289_1302_candidate_phase_grouping_v0.1.md" in prompt
    assert "ilc_antigravity_context_capsule_v5.52.md" in prompt
    assert "ilc_sidecar_non_loopback_public_path_preflight_1278_v0.1.md" in prompt
    assert "ilc_phase_1289_1296_sequence_lock_v0.1.md" not in prompt
    assert "Window 1289-1296" not in prompt


def test_phase_1298_active_lock_controls_bind_listener_scope() -> None:
    lock = read(LOCK)
    guidance = read(GUIDANCE)
    spec = read(SPEC)

    assert (
        "| 10 | 1298 | Sidecar bind, listener, peer-discovery authority preflight | SENSITIVE |"
        in lock
    )
    assert (
        "| 1298 | Sidecar bind, listener, peer-discovery authority preflight | SENSITIVE"
        in guidance
    )
    assert "GO Phase 1298" in spec
    assert "preflight only / no public serving" in spec
    assert "Phase 1299 is sensitive and requires explicit `GO Phase 1299`" in spec


def test_phase_1298_authority_table_records_no_bind_listener_or_discovery() -> None:
    spec = read(SPEC)

    for phrase in (
        "Bind Listener Peer Discovery Authority Table",
        "Local in-process sidecar query runtime",
        "Loopback-only historical boundary",
        "no new listener",
        "Non-loopback bind",
        "Wildcard bind",
        "Public host bind",
        "Public listener",
        "Socket listener",
        "HTTP route",
        "Peer discovery",
        "Public sidecar/projection serving",
        "Public P2P",
        "Public fetch serving",
        "Not enabled",
        "not activated",
    ):
        assert phrase in spec

    for token in (
        "non_loopback_bind_not_enabled_phase_1298",
        "public_listener_not_enabled_phase_1298",
        "peer_discovery_not_enabled_phase_1298",
        "public_sidecar_projection_serving_not_enabled_phase_1298",
    ):
        assert token in spec


def test_phase_1298_runtime_readback_keeps_helper_non_serving() -> None:
    helper = read(SIDECAR_HELPER)
    runtime = read(SIDECAR_RUNTIME)

    assert "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface" in helper
    assert "no listener, bind, or serving surface" in helper
    assert "does not open a\nlistener" in helper
    assert "bind a socket" in helper
    assert "serve projection data" in helper
    assert "enable peer discovery" in helper
    assert "sidecar_public_serving_not_enabled_phase_1278" in helper
    assert "no_new_public_listener_phase_1278" in helper
    assert "non_loopback_bind_not_enabled_phase_1278" in helper
    assert "public_projection_endpoint_not_enabled_phase_1278" in helper

    assert "import socket" not in helper
    assert "FastAPI" not in helper
    assert "uvicorn" not in helper
    assert "HTTPServer" not in helper

    assert "DEFAULT_SIDECAR_EXPORT_MAX_BYTES = 10_000_000" in runtime
    assert "DEFAULT_SIDECAR_EXPORT_MAX_RESULTS = 1_000" in runtime
    assert "sort_keys=True" in runtime
    assert "allow_nan=False" in runtime
    assert "sidecar_export_float_values_forbidden" in runtime
    assert "sidecar_export_decimal_must_be_finite" in runtime


def test_phase_1298_non_claims_keep_serving_release_and_economics_blocked() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "public sidecar/projection serving",
            "public projection endpoint",
            "non-loopback bind",
            "wildcard bind",
            "public host bind",
            "public listener",
            "socket listener",
            "HTTP route",
            "peer discovery",
            "public fetch serving",
            "public P2P",
            "TransportPrincipal public-path activation",
            "public credential issuer authority",
            "public revocation registry",
            "public replay cache",
            "admission policy activation",
            "ban registry activation",
            "public rate-limit state",
            "privacy policy activation",
            "helper promotion",
            "marker removal",
            "source allowlist export",
            "public repository publication",
            "public package publication",
            "release artifact",
            "release-key generation",
            "release envelope",
            "public claimability",
            "public verifier service",
            "wallet withdrawal",
            "wallet transfer",
            "wallet spend",
            "ECU minting",
            "ILC settlement",
            "CDL-088",
            "Genesis",
            "v0.2 signing",
        ):
            assert phrase in text


def test_phase_1298_frontier_docs_advance_to_1299_without_activation() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)
    status = read(STATUS)

    assert "Window 1289-1302 is OPEN through Phase 1298" in planning
    assert "Window 1289-1302 is open through Phase 1298" in capsule
    assert "Window 1289-1302 OPEN through Phase 1298" in roadmap
    assert "Phase 1299 is sensitive" in planning
    assert "Phase 1299 is sensitive" in capsule
    assert "Phase 1299 is the next sensitive phase" in roadmap
    assert "Phase 1299 - Release allowlist, artifact, Genesis readiness preflight" in status


def test_phase_1298_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    spec = read(SPEC)

    assert (
        "sidecar_bind_listener_peer_discovery_authority_preflight_phase_1298.v0.1"
        not in cdl
    )
    assert "| CDL-088 |" not in cdl
    assert "CDL-088 opening" in spec
    assert "CDL mutation" in spec
