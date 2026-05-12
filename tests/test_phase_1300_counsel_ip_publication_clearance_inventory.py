from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SPEC = "docs/specs/ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md"
PROMPT = (
    "docs/antigravity_tasks/"
    "antigravity_prompt__phase_1300_g8_counsel_ip_publication_clearance_inventory.md"
)
PLANNING = "docs/PLANNING_INDEX.md"
STATUS = "docs/phases/STATUS.md"
CAPSULE = "docs/specs/ilc_antigravity_context_capsule_v5.52.md"
ROADMAP = "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
WALKTHROUGH = "docs/phases/phase_1300_counsel_ip_publication_clearance_inventory_walkthrough.md"
FIX1_IP = "docs/specs/ilc_phase_1280_fix1_hypergraph_laplacian_docs_hardening_v0.1.md"
CDL086_EVIDENCE = "docs/specs/ilc_cdl_086_ratification_evidence_1220_v0.1.md"
CDL086_COUNSEL = "docs/specs/ilc_cdl_086_counsel_disposition_1220_v0.1.md"
ALLOWLIST = "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md"
PREPUBLICATION = (
    "docs/specs/ilc_release_manifest_allowlist_prepublication_preflight_1279_v0.1.md"
)
PUBLICATION_PREFLIGHT = (
    "docs/specs/ilc_release_publication_signing_authorization_preflight_1287_v0.1.md"
)
PHASE_1299 = "docs/specs/ilc_release_allowlist_artifact_genesis_readiness_preflight_1299_v0.1.md"
PACKAGING_GATE = "docs/architecture/ilc_public_rc_packaging_architecture_gate_v0.1.md"
CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

REQUIRED_TOKENS = (
    "counsel_ip_publication_clearance_inventory_phase_1300.v0.1",
    "counsel_ip_publication_verdict_phase_1300=inventory_only_no_publication",
    "ip_filing_not_performed_phase_1300",
    "paper_publication_not_authorized_phase_1300",
    "public_repository_publication_not_authorized_phase_1300",
    "public_package_publication_not_authorized_phase_1300",
    "public_rc_remains_blocked_after_phase_1300",
    "phase_1301_deep_no_activation_assertion_audit_next",
)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_phase_1300_required_tokens_are_published() -> None:
    for token in REQUIRED_TOKENS:
        assert token in read(SPEC)
        assert token in read(PROMPT)
        assert token in read(PLANNING)
        assert token in read(STATUS)
        assert token in read(WALKTHROUGH)

    for token in REQUIRED_TOKENS[:7]:
        assert token in read(CAPSULE)
        assert token in read(ROADMAP)


def test_phase_1300_binds_counsel_ip_and_export_sources() -> None:
    spec = read(SPEC)
    fix1 = read(FIX1_IP)
    evidence = read(CDL086_EVIDENCE)
    counsel = read(CDL086_COUNSEL)
    allowlist = read(ALLOWLIST)
    prepublication = read(PREPUBLICATION)
    publication_preflight = read(PUBLICATION_PREFLIGHT)
    phase_1299 = read(PHASE_1299)
    packaging_gate = read(PACKAGING_GATE)

    for phrase in (
        "counsel_license_instrument_selection_required_before_public_rc",
        "counsel_cla_text_approved_required_before_external_contributors",
        "counsel_trademark_policy_published_required_before_public_launch",
        "allowlist_export_procedure_defined_required_before_public_repo_publication",
        "genesis_canonical_lineage_contract_required_before_public_rc",
        "us_provisional_patent_application_filed_required_before_public_repo_publication",
        "ip001_ip_inventory_disclosure_control_registered",
        "ip006_publication_clearance_matrix_registered",
        "PUBLIC_RC_EXCLUDE: internal_ip_publication_planning_not_public_rc_launch_surface",
        "public_rc_exclude_absence_is_not_allowlist_clearance",
        "legacy_untagged_docs_default_review_required_before_public_export",
    ):
        assert phrase in spec

    assert "ip_lane_001_plus_registered_phase_1280_fix1" in fix1
    assert "not counsel-approved legal conclusions" in evidence
    assert "NOT COUNSEL-APPROVED LEGAL CONCLUSIONS" in counsel
    assert "public_repository_publication_not_authorized_phase_1255" in allowlist
    assert "public_release_path_phase_1279=blocked_pending_counsel_publication_signing_and_final_claimability_authority" in prepublication
    assert "release_publication_signing_verdict_phase_1287=preflight_only_no_publication_no_signing" in publication_preflight
    assert "source_allowlist_export_not_executed_phase_1299" in phase_1299
    assert "counsel/IP/publication clearance state" in packaging_gate


def test_phase_1300_records_inventory_only_and_no_publication_or_filing() -> None:
    for path in (SPEC, WALKTHROUGH, STATUS):
        text = read(path)
        for phrase in (
            "counsel-approved legal conclusion",
            "final license instrument selection",
            "CLA text approval",
            "trademark filing",
            "public documentation license publication",
            "source allowlist export execution",
            "materialized export manifest production",
            "public repository publication",
            "public package publication",
            "release artifact production",
            "release-key generation",
            "release envelope production",
            "public RC claim",
            "IP filing",
            "provisional patent filing",
            "paper publication",
            "paper submission",
            "preprint release",
            "publication clearance matrix execution",
            "removal of `PUBLIC_RC_EXCLUDE`",
            "helper promotion",
            "marker removal",
            "helper stripping",
            "CDL mutation",
            "CDL-088 opening",
            "Genesis Atlas mutation",
            "v0.2 signing",
            "wallet withdrawal",
            "ECU minting",
            "ILC settlement",
        ):
            assert phrase in text

        for token in REQUIRED_TOKENS[:7]:
            assert token in text


def test_phase_1300_frontier_docs_advance_to_1301_without_public_rc_authority() -> None:
    planning = read(PLANNING)
    capsule = read(CAPSULE)
    roadmap = read(ROADMAP)
    status = read(STATUS)

    assert "Window 1289-1302 is OPEN through Phase 1300" in planning
    assert "Window 1289-1302 is open through Phase 1300" in capsule
    assert "Window 1289-1302 OPEN through Phase 1300" in roadmap
    assert "Phase 1301 is sensitive" in planning
    assert "Phase 1301 is sensitive" in capsule
    assert "Phase 1301 is the next sensitive phase" in roadmap
    assert "## Phase 1300" in status
    assert "Phase 1301 - Deep no-activation assertion audit" in status


def test_phase_1300_does_not_mutate_cdl_register_or_open_cdl088() -> None:
    cdl = read(CDL_REGISTER)
    spec = read(SPEC)

    assert "counsel_ip_publication_clearance_inventory_phase_1300.v0.1" not in cdl
    assert "| CDL-088 |" not in cdl
    assert "CDL mutation" in spec
    assert "CDL-088 opening" in spec


def test_phase_1300_graph_delta_is_recorded() -> None:
    expected = (
        "graph_delta=support_only:docs/specs/ilc_counsel_ip_publication_clearance_inventory_1300_v0.1.md -> release/publication",
        "graph_delta=support_tests_added:tests/test_phase_1300_counsel_ip_publication_clearance_inventory.py -> validation",
        "graph_delta=support_only:docs/phases/phase_1300_counsel_ip_publication_clearance_inventory_walkthrough.md -> planning/frontier",
        "graph_delta=support_only:docs/phases/STATUS.md -> planning/frontier",
        "graph_delta=support_only:docs/PLANNING_INDEX.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_antigravity_context_capsule_v5.52.md -> planning/frontier",
        "graph_delta=support_only:docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md -> planning/frontier",
    )

    for text in (read(SPEC), read(WALKTHROUGH), read(STATUS)):
        for graph_delta in expected:
            assert graph_delta in text
