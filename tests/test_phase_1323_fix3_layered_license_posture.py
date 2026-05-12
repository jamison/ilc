from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read(path: str) -> str:
    return (_repo_root() / path).read_text(encoding="utf-8")


def test_phase_1323_fix3_tokens_are_recorded() -> None:
    spec = _read("docs/specs/ilc_layered_license_posture_1323_fix3_v0.1.md")
    for token in (
        "phase_1323_fix3_layered_license_posture.v0.1",
        "blanket_mit_license_removed_phase_1323_fix3",
        "agpl_runtime_default_recorded_phase_1323_fix3",
        "licensing_zone_table_committed_phase_1323_fix3",
        "genesis_canonical_identity_zone_recorded_phase_1323_fix3",
        "patent_pending_zone_reserved_phase_1323_fix3",
        "whitepaper_mit_language_replaced_phase_1323_fix3",
        "ip_series_confirmed_as_ip001_to_ip006_phase_1323_fix3",
        "public_rc_remains_blocked_after_phase_1323_fix3",
    ):
        assert token in spec


def test_layered_license_posture_replaces_blanket_mit() -> None:
    license_notice = _read("LICENSE")
    licensing = _read("LICENSING.md")
    pyproject = _read("pyproject.toml")

    assert "ILC Layered License Notice" in license_notice
    assert "does not use a blanket MIT license" in license_notice
    assert "AGPL-3.0-only" in license_notice
    assert 'license = {text = "AGPL-3.0-only"}' in pyproject

    for token in (
        "ilc_layered_license_posture_v0.1",
        "mit_for_all_zones_rejected_layered_license_posture",
        "agpl_default_runtime_license_posture",
        "genesis_canonical_identity_license_zone",
        "public_docs_cc_by_4_0_zone",
        "patent_pending_all_rights_reserved_zone",
        "trademark_identity_not_granted_by_code_license",
        "counsel_review_future_modification_expected",
    ):
        assert token in licensing


def test_current_whitepapers_do_not_retain_stale_mit_license_claims() -> None:
    stale_phrases = (
        "**License:** MIT",
        "ILC is released under the MIT license",
        "under the MIT license",
    )
    paths = (
        "docs/whitepaper/ilc_whitepaper_agent_edition_v0.1.md",
        "docs/whitepaper/ilc_whitepaper_agent_edition_v0.1_1.md",
        "docs/whitepaper/ilc_whitepaper_agent_edition_v0.2.md",
        "docs/whitepaper/ilc_whitepaper_working_draft_v6_0.md",
        "docs/whitepaper_drafts/ilc_whitepaper_agent_edition_v0.1.md",
        "docs/whitepaper_drafts/ilc_whitepaper_agent_edition_v0.1_1.md",
        "docs/whitepaper_drafts/ilc_whitepaper_agent_edition_v0.2.md",
        "docs/whitepaper_drafts/ilc_whitepaper_working_draft_v6_0.md",
    )

    for path in paths:
        body = _read(path)
        for phrase in stale_phrases:
            assert phrase not in body, path
        assert "layered" in body.lower()


def test_ip_series_and_planning_backfill_are_current() -> None:
    spec = _read("docs/specs/ilc_layered_license_posture_1323_fix3_v0.1.md")
    for phase in ("IP-001", "IP-002", "IP-003", "IP-004", "IP-005", "IP-006"):
        assert phase in spec
    assert "not a current `P-series` or `L-series`" in spec

    planning_docs = (
        "docs/phases/STATUS.md",
        "docs/PLANNING_INDEX.md",
        "docs/specs/ilc_antigravity_context_capsule_v5.54.md",
        "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md",
    )
    for path in planning_docs:
        body = _read(path)
        assert "phase_1323_fix3_layered_license_posture.v0.1" in body, path
        assert "public_rc_remains_blocked_after_phase_1323_fix3" in body, path
