from __future__ import annotations

import ast
import sys
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

import ilc_core.network.d2d.truth_primitive_gossip_runtime as gossip_runtime
import ilc_core.sidecars.confidential_coordination_shard as ccss_001
from ilc_core.identity.agent_id_runtime import derive_agent_id_v2
from ilc_core.ledger.backend import InMemoryLedgerBackend
from ilc_core.ledger.exact_numeric import decimal_to_canonical_string
from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d.bootstrap_fetch_runtime import verify_bootstrap_bundle_signature


ROOT = Path(__file__).resolve().parents[1]
AGENT_ID_RUNTIME = ROOT / "ilc_core/identity/agent_id_runtime.py"
BOOTSTRAP_RUNTIME = ROOT / "ilc_core/network/d2d/bootstrap_fetch_runtime.py"
GENESIS_RECORD_SCHEMA = ROOT / "ilc_core/identity/genesis_record_schema.py"
TRUTH_GOSSIP_RUNTIME = ROOT / "ilc_core/network/d2d/truth_primitive_gossip_runtime.py"
SPEC_DOC = ROOT / "docs/specs/ilc_phase_1331_fix1_pre_1332_security_hardening_v0.1.md"
WALKTHROUGH_DOC = (
    ROOT / "docs/phases/phase_1331_fix1_pre_1332_security_hardening_walkthrough.md"
)
STATUS_DOC = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"
CAPSULE_V5_55 = ROOT / "docs/specs/ilc_antigravity_context_capsule_v5.55.md"
ROADMAP_V1_1 = (
    ROOT / "docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md"
)
CDL_069_OPENING = (
    ROOT
    / "docs/specs/ilc_cdl_069_pq_identity_and_epoch_endorsement_protocol_opening_838_v0.1.md"
)

REQUIRED_TOKENS = (
    "phase_1331_fix1_pre_1332_security_hardening.v0.1",
    "ccss_001_pre_serialization_budget_backported_phase_1331_fix1",
    "truth_primitive_gossip_redirect_guard_added_phase_1331_fix1",
    "bootstrap_signature_env_bypass_removed_phase_1331_fix1",
    "identity_seed_commitment_domain_separator_applied_phase_1331_fix1",
    "exact_numeric_non_finite_canonical_string_rejected_phase_1331_fix1",
    "ledger_balance_read_decimal_boundary_phase_1331_fix1",
    "agent_id_assert_removed_phase_1331_fix1",
    "phase_1332_final_deterministic_code_security_audit_still_next_after_fix1",
    "public_rc_remains_blocked_after_phase_1331_fix1",
)


class _RejectingOqsSignature:
    def __init__(self, _algorithm: str) -> None:
        pass

    def verify(
        self,
        _signed_bytes: bytes,
        _sig_bytes: bytes,
        _pubkey_bytes: bytes,
    ) -> bool:
        return False


class _RejectingOqsModule:
    Signature = _RejectingOqsSignature


def test_ccss_001_rejects_payload_byte_budget_before_json_dumps(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(ccss_001, "_MAX_CANONICAL_JSON_BYTES", 16)

    def fail_dumps(*_args: object, **_kwargs: object) -> str:
        raise AssertionError("json.dumps should not run after byte-budget rejection")

    monkeypatch.setattr(ccss_001.json, "dumps", fail_dumps)

    with pytest.raises(ccss_001.ConfidentialCoordinationShardError) as exc:
        ccss_001.canonical_ccss_001_json({"payload": "x" * 17})

    assert exc.value.token == "ccss_001_payload_size_exceeded_phase_1324"


def test_ccss_001_rejects_oversized_integer_before_stringification() -> None:
    with pytest.raises(ccss_001.ConfidentialCoordinationShardError) as exc:
        ccss_001.canonical_ccss_001_json(
            {"payload": ccss_001._MAX_CANONICAL_JSON_INT_ABS + 1}
        )

    assert exc.value.token == "ccss_001_payload_int_invalid_phase_1324"


def test_truth_primitive_gossip_channel_satisfies_cdl_039() -> None:
    headers = gossip_transport.build_gossip_headers(
        gossip_type=gossip_runtime.TRUTH_PRIMITIVE_GOSSIP_TYPE,
        channel=gossip_runtime.TRUTH_PRIMITIVE_GOSSIP_CHANNEL,
        epoch=1,
        hop_count=gossip_transport.HOP_COUNT_SINGLE,
        signature="UNSIGNED",
        content_type="application/json",
    )

    assert headers["ILC-Channel"] == gossip_runtime.TRUTH_PRIMITIVE_GOSSIP_CHANNEL


def test_truth_primitive_gossip_uses_no_redirect_opener(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    class FakeResponse:
        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_args: object) -> None:
            return None

        def getcode(self) -> int:
            return 202

    class FakeOpener:
        def open(self, request: object, *, timeout: float) -> FakeResponse:
            captured["request"] = request
            captured["timeout"] = timeout
            return FakeResponse()

    def fake_build_opener(*handlers: object) -> FakeOpener:
        captured["handlers"] = handlers
        return FakeOpener()

    monkeypatch.setattr(gossip_runtime.urllib.request, "build_opener", fake_build_opener)

    assert gossip_runtime._send_to_peer("https://peer.ilc.example", b"{}", 1) is True
    assert gossip_runtime._NoRedirectHandler in captured["handlers"]


def test_bootstrap_signature_env_bypass_is_not_present(monkeypatch: pytest.MonkeyPatch) -> None:
    bundle = {
        "schema_version": "bootstrap_bundle_v1",
        "bundle_cid": "bafyreiabc001",
        "genesis_cid": "bafyreigenesis",
        "peers": [],
        "signed_by": "aabbcc" * 20,
        "signature": "ddeeff" * 20,
        "cdl_version": "cdl_079_bootstrap_bundle_v1",
    }

    monkeypatch.setenv("ILC_BOOTSTRAP_SKIP_SIG_VERIFY", "1")
    monkeypatch.setitem(sys.modules, "oqs", _RejectingOqsModule())

    assert verify_bootstrap_bundle_signature(bundle, "aabbcc" * 20) is False
    assert "ILC_BOOTSTRAP_SKIP_SIG_VERIFY" not in BOOTSTRAP_RUNTIME.read_text(
        encoding="utf-8"
    )


def test_identity_seed_commitment_uses_domain_separator() -> None:
    text = GENESIS_RECORD_SCHEMA.read_text(encoding="utf-8")

    assert '_IDENTITY_SEED_COMMIT_DOMAIN: bytes = b"ilc-seed-commit-v1:"' in text
    assert "hashlib.sha384(_IDENTITY_SEED_COMMIT_DOMAIN + identity_seed)" in text


def test_decimal_canonical_string_rejects_non_finite_values() -> None:
    for value in (Decimal("NaN"), Decimal("Infinity"), Decimal("-Infinity")):
        with pytest.raises(ValueError, match="invalid_exact_numeric_value"):
            decimal_to_canonical_string(value)


def test_agent_id_runtime_has_no_production_assert() -> None:
    tree = ast.parse(AGENT_ID_RUNTIME.read_text(encoding="utf-8"))

    assert not any(isinstance(node, ast.Assert) for node in ast.walk(tree))
    assert derive_agent_id_v2(b"\x01" * 32)


def test_ledger_get_balance_returns_decimal_not_float() -> None:
    ledger = InMemoryLedgerBackend()

    assert ledger.get_balance("missing") == Decimal("0")
    assert isinstance(ledger.get_balance("missing"), Decimal)
    ledger._set_balance("agent:a", "1.25")
    assert ledger.get_balance("agent:a") == Decimal("1.25")
    assert isinstance(ledger.get_balance("agent:a"), Decimal)


@pytest.mark.parametrize(
    "path",
    (SPEC_DOC, WALKTHROUGH_DOC, STATUS_DOC, PLANNING_INDEX),
)
def test_phase_1331_fix1_tokens_are_recorded(path: Path) -> None:
    text = path.read_text(encoding="utf-8")

    for token in REQUIRED_TOKENS:
        assert token in text


def test_cdl_069_runtime_formula_supersedes_bare_hash_in_current_docs() -> None:
    capsule = CAPSULE_V5_55.read_text(encoding="utf-8")
    roadmap = ROADMAP_V1_1.read_text(encoding="utf-8")
    opening = CDL_069_OPENING.read_text(encoding="utf-8")

    canonical_formula = (
        'identity_seed_commitment = sha384("ilc-seed-commit-v1:" || identity_seed)'
    )
    assert canonical_formula in capsule
    assert canonical_formula in roadmap
    assert 'sha384("ilc-seed-commit-v1:" || identity_seed)' in opening
    assert "current runtime bare-hash path" not in capsule
    assert "current `sha384(identity_seed)` runtime code" not in roadmap
    assert "Supersession note: CDL-069 ratification evidence" in opening
