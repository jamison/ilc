from pathlib import Path


MANIFEST = Path("docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md")
CHECKLIST = Path("docs/specs/ilc_distribution_channel_integrity_checklist_1213_v0.1.md")


def _manifest_text() -> str:
    return MANIFEST.read_text(encoding="utf-8")


def _checklist_text() -> str:
    return CHECKLIST.read_text(encoding="utf-8")


def test_release_artifact_manifest_schema_exists():
    assert MANIFEST.exists()


def test_distribution_channel_integrity_checklist_exists():
    assert CHECKLIST.exists()


def test_prep_artifacts_contain_tokens():
    assert "release_artifact_manifest_schema_committed_phase_1213" in _manifest_text()
    assert "distribution_channel_integrity_checklist_committed_phase_1213" in _checklist_text()


def test_manifest_schema_contains_required_fields_and_hash_rule():
    text = _manifest_text()
    for field in (
        "artifact_id",
        "artifact_type",
        "canonical_hash",
        "lineage_reference",
        "produced_phase",
        "ratification_token",
        "signing_status",
    ):
        assert field in text
    assert "^sha256:[0-9a-f]{64}$" in text
    assert "SHA-512 and MD5" in text


def test_manifest_schema_contains_exhaustive_artifact_types():
    text = _manifest_text()
    for artifact_type in (
        "runtime_module",
        "genesis_bundle",
        "cli_binary",
        "documentation_bundle",
        "source_release_tarball",
        "public_repository_tag",
        "container_image",
        "star_map_release_envelope",
        "operator_bootstrap_bundle",
        "verification_bundle",
    ):
        assert artifact_type in text
    assert "Any unlisted type is invalid" in text


def test_checklist_contains_required_public_distribution_gates():
    text = _checklist_text()
    for item in (
        "Signing verification",
        "Lineage chain verification",
        "ADR-0036 compliance",
        "ADR-0037 compliance",
        "CDL-086 ratification check",
        "Counsel disposition check",
        "No public-launch implication",
    ):
        assert item in text
    assert "cdl_086_ratified_phase_1214" in text


def test_prep_artifacts_preserve_non_claims():
    assert "does not ratify CDL-086" in _manifest_text()
    assert "does not ratify CDL-086" in _checklist_text()
    assert "does not authorize public release" in _checklist_text()
