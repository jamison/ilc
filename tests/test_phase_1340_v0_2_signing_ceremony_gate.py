from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.rc import genesis_v0_2_signing_ceremony_gate as gate


ROOT = Path(__file__).resolve().parents[1]


def _load_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def _canonical_hash(payload: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(payload, allow_nan=False, separators=(",", ":"), sort_keys=True).encode(
            "utf-8"
        )
    ).hexdigest()


def test_phase_1340_report_records_signed_gate_result() -> None:
    report = _load_json("docs/specs/ilc_v0_2_signing_ceremony_gate_1340_v0.1.json")

    assert report["schema_version"] == gate.PHASE_1340_VERSION
    assert report["gate_result"] == "v0_2_signed"
    assert report["v0_2_signing_ceremony_gate_verdict"] == (
        "v0_2_signing_ceremony_gate_verdict=pass"
    )
    assert report["required_tokens"] == gate.phase_1340_required_tokens()
    assert report["authority"]["explicit_authority_present"] is True
    assert report["phase_1339_dependency"]["dependency_result"] == "pass"
    assert report["phase_1335_dependency"]["dependency_result"] == "pass"
    assert report["public_rc_remains_blocked"] is True
    assert "phase_1341_public_rc_publication_claim_gate_next" == report["next_phase"]
    assert "public_rc_remains_blocked_after_phase_1340" in report["non_claims"]


def test_phase_1340_root_envelope_hash_and_signature_verify() -> None:
    report = _load_json("docs/specs/ilc_v0_2_signing_ceremony_gate_1340_v0.1.json")
    root_envelope = _load_json(report["root_envelope"]["path"])
    signature = (ROOT / report["signature"]["path"]).read_text(encoding="utf-8").strip()
    public_key_hex = report["phase_1335_dependency"]["public_key_metadata"]["public_key_hex"]

    envelope_for_hash = dict(root_envelope)
    envelope_for_hash["envelope_hash"] = "sha256:" + "0" * 64
    assert root_envelope["envelope_hash"] == _canonical_hash(envelope_for_hash)
    assert root_envelope["envelope_hash"] == report["root_envelope"]["envelope_hash"]

    public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
    public_key.verify(bytes.fromhex(signature), gate.canonical_json(root_envelope).encode("utf-8"))
    assert report["signature"]["verification_result"] == "signature_verified"
    assert report["signature"]["signature_produced"] is True
    assert len(signature) == 128


def test_phase_1340_artifacts_do_not_record_secret_material() -> None:
    checked_paths = [
        "docs/specs/ilc_v0_2_signing_ceremony_gate_1340_v0.1.json",
        "docs/specs/ilc_v0_2_signing_ceremony_gate_1340_v0.1.md",
        "out/genesis_atlas_v0_2_signing_root_envelope_phase_1340.json",
        "out/genesis_atlas_v0_2_signing_root_envelope_phase_1340.sig",
    ]
    forbidden = ("BEGIN PRIVATE KEY", "END PRIVATE KEY", "/".join((".ilc", "private")))
    for path in checked_paths:
        text = (ROOT / path).read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text


def test_phase_1340_validator_accepts_committed_report() -> None:
    report = _load_json("docs/specs/ilc_v0_2_signing_ceremony_gate_1340_v0.1.json")

    assert gate.validate_v0_2_signing_ceremony_gate(report)["gate_result"] == "v0_2_signed"
