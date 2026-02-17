from __future__ import annotations

from pathlib import Path


NARROWED_MODULES = (
    Path("ilc_core/encoding/cidv1.py"),
    Path("ilc_core/protocol/ndjson_bundle.py"),
    Path("ilc_core/crypto/cbor_canonical.py"),
    Path("ilc_core/eve/capsule.py"),
    Path("ilc_core/ledger/canon_export_bundle_verify_sig.py"),
    Path("ilc_core/ledger/canon_bundle_audit_artifact.py"),
    Path("ilc_core/protocol/ilc_cluster_a_replay_proof_schemas.py"),
    Path("ilc_core/protocol/ilc_cluster_a_replay_proof_batch.py"),
)


def test_phase_1011_policy_doc_exists() -> None:
    policy_path = Path("docs/specs/ilc_broad_exception_boundary_policy_v0.1.md")
    assert policy_path.exists()
    text = policy_path.read_text(encoding="utf-8")
    assert "except Exception" in text
    assert "Utility and codec modules must use specific exception families." in text


def test_phase_1011_narrowed_modules_have_no_broad_exception_catch() -> None:
    for module_path in NARROWED_MODULES:
        text = module_path.read_text(encoding="utf-8")
        assert "except Exception" not in text, module_path.as_posix()
