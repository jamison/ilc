import json
from pathlib import Path

import pytest

from ilc_core.rc import release_keys_envelopes_generation_gate as gate


def _write_canon_docs(repo_root: Path) -> None:
    adr = repo_root / "docs/adr"
    adr.mkdir(parents=True)
    (adr / "ADR_0036_Operational_Release_Key_Genesis_Binding.md").write_text(
        "\n".join(
            [
                "# ADR-0036",
                "",
                "**Status:** Accepted",
                "",
                "Operational release key Genesis binding.",
            ]
        ),
        encoding="utf-8",
    )
    (adr / "adr_0036_acceptance_review_1173_v0.1.md").write_text(
        "adr_0036_accepted_phase_1173\n",
        encoding="utf-8",
    )
    (adr / "ADR_0037_Genesis_Canonical_Lineage_Contract.md").write_text(
        "\n".join(
            [
                "# ADR-0037",
                "",
                "**Status:** Accepted",
                "",
                gate.GENESIS_ROOT_ENVELOPE_HASH.removeprefix("sha256:"),
            ]
        ),
        encoding="utf-8",
    )


def _write_phase_1334_report(repo_root: Path, *, drift: bool = False) -> Path:
    artifact_path = repo_root / "out/release_artifacts/phase_1334/source.tar.gz"
    artifact_path.parent.mkdir(parents=True)
    artifact_path.write_bytes(b"phase 1334 source artifact\n")
    digest = gate._sha256_file(artifact_path)
    recorded_digest = "0" * 64 if drift else digest
    report = {
        "artifacts": [
            {
                "artifact_id": "ilc-artifact:source-release-tarball@phase-1334",
                "artifact_type": "source_release_tarball",
                "canonical_hash": f"sha256:{recorded_digest}",
                "path": artifact_path.relative_to(repo_root).as_posix(),
                "signing_status": "unsigned",
            }
        ],
        "manifest_hash": "a" * 64,
        "next_phase": "phase_1335_release_keys_envelopes_generation_gate_next",
        "public_rc_remains_blocked": True,
        "release_artifact_production_gate_verdict": (
            "release_artifact_production_gate_verdict=pass"
        ),
        "result": "artifacts_produced_unsigned",
        "schema_version": "release_artifact_production_gate_phase_1334.v0.1",
    }
    path = repo_root / gate.PHASE_1334_REPORT_PATH
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(report, sort_keys=True), encoding="utf-8")
    return path


def _prepare_repo(tmp_path: Path, *, drift: bool = False) -> Path:
    repo_root = tmp_path / "repo"
    repo_root.mkdir()
    _write_canon_docs(repo_root)
    _write_phase_1334_report(repo_root, drift=drift)
    return repo_root


def test_phase_1335_generates_public_metadata_and_external_key(tmp_path: Path) -> None:
    repo_root = _prepare_repo(tmp_path)
    key_path = tmp_path / "external/phase_1335/release-key.pem"

    manifest = gate.build_release_keys_envelopes_generation_gate(
        authority_token=gate.EXPLICIT_AUTHORITY_PHRASE,
        repo_root=repo_root,
        external_key_path=key_path,
    )

    assert manifest["result"] == "keys_envelopes_generated"
    assert manifest["release_keys_envelopes_generation_gate_verdict"] == (
        "release_keys_envelopes_generation_gate_verdict=pass"
    )
    assert key_path.exists()
    assert key_path.stat().st_mode & 0o777 == 0o600
    assert manifest["secret_material_boundary"]["secret_material_written_to_repo"] is False
    assert manifest["secret_material_boundary"]["private_material_path_recorded_in_repo"] is False
    assert manifest["release_key_registration"]["signing_status"] == "unsigned"
    assert manifest["release_envelope_candidate"]["signature_produced"] is False
    assert manifest["release_envelope_candidate"]["signing_status"] == "unsigned"
    assert manifest["non_authorization_floor"]["release_signature_production_authorized"] is False
    assert manifest["next_phase"] == gate.PHASE_1336_PUBLIC_CLAIMABILITY_API_GATE_NEXT_TOKEN


def test_phase_1335_reuses_existing_external_key(tmp_path: Path) -> None:
    repo_root = _prepare_repo(tmp_path)
    key_path = tmp_path / "external/phase_1335/release-key.pem"

    first = gate.build_release_keys_envelopes_generation_gate(
        authority_token=gate.EXPLICIT_AUTHORITY_PHRASE,
        repo_root=repo_root,
        external_key_path=key_path,
    )
    second = gate.build_release_keys_envelopes_generation_gate(
        authority_token=gate.EXPLICIT_AUTHORITY_PHRASE,
        repo_root=repo_root,
        external_key_path=key_path,
    )

    assert first["public_key_metadata"] == second["public_key_metadata"]
    assert first["release_key_registration"] == second["release_key_registration"]


def test_phase_1335_blocks_without_exact_authority_and_generates_no_key(
    tmp_path: Path,
) -> None:
    repo_root = _prepare_repo(tmp_path)
    key_path = tmp_path / "external/phase_1335/release-key.pem"

    manifest = gate.build_release_keys_envelopes_generation_gate(
        authority_token="GO Phase 1335",
        repo_root=repo_root,
        external_key_path=key_path,
    )

    assert manifest["result"] == "blocked_no_authority"
    assert "missing_explicit_phase_1335_authority" in manifest["blockers"]
    assert manifest["release_key_registration"] is None
    assert not key_path.exists()


def test_phase_1335_refuses_secret_material_path_inside_repo(tmp_path: Path) -> None:
    repo_root = _prepare_repo(tmp_path)
    key_path = repo_root / "private/release-key.pem"

    with pytest.raises(ValueError, match="phase_1335_secret_material_path_must_be_outside_repo"):
        gate.build_release_keys_envelopes_generation_gate(
            authority_token=gate.EXPLICIT_AUTHORITY_PHRASE,
            repo_root=repo_root,
            external_key_path=key_path,
        )


def test_phase_1335_blocks_phase_1334_artifact_hash_drift_without_key(
    tmp_path: Path,
) -> None:
    repo_root = _prepare_repo(tmp_path, drift=True)
    key_path = tmp_path / "external/phase_1335/release-key.pem"

    manifest = gate.build_release_keys_envelopes_generation_gate(
        authority_token=gate.EXPLICIT_AUTHORITY_PHRASE,
        repo_root=repo_root,
        external_key_path=key_path,
    )

    assert manifest["result"] == "blocked_with_findings"
    assert "phase_1334_source_release_artifact_hash_drift" in manifest["blockers"]
    assert not key_path.exists()


def test_phase_1335_reports_do_not_contain_secret_material(tmp_path: Path) -> None:
    repo_root = _prepare_repo(tmp_path)
    key_path = tmp_path / "external/phase_1335/release-key.pem"
    manifest = gate.build_release_keys_envelopes_generation_gate(
        authority_token=gate.EXPLICIT_AUTHORITY_PHRASE,
        repo_root=repo_root,
        external_key_path=key_path,
    )
    json_text = gate.pretty_json(manifest)
    markdown = gate.render_markdown_report(manifest)

    for text in (json_text, markdown):
        assert "BEGIN PRIVATE KEY" not in text
        assert "END PRIVATE KEY" not in text
        assert key_path.as_posix() not in text
