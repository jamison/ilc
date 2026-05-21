"""Phase 1413 VRF integration tests and security review.

Required token:
vrf_integration_tests_complete_phase_1413

These tests use fixed RFC 9381 Appendix B.4 public proof vectors only. They do
not generate proofs or hold private keys.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from ilc_core.epistemic import jury_assignment_runtime as jury_runtime
from ilc_core.epistemic import vrf_proof_verifier as verifier
from ilc_core.epistemic.jury_activation_gate import (
    GateConditionStatus,
    evaluate_jury_activation_gate,
)
from ilc_core.epistemic.jury_assignment_runtime import (
    EligibleAgent,
    JuryAssignmentError,
    quote_jury_assignment,
)


_TOKEN_VRF_TESTS_COMPLETE = "vrf_integration_tests_complete_phase_1413"

REPO = Path(__file__).parent.parent
VRF_PATH = REPO / "ilc_core/epistemic/vrf_proof_verifier.py"
JURY_PATH = REPO / "ilc_core/epistemic/jury_assignment_runtime.py"

RFC_B4_VECTORS = (
    {
        "public_key": bytes.fromhex(
            "d75a980182b10ab7d54bfed3c964073a0ee172f3daa62325af021a68f707511a"
        ),
        "alpha": b"",
        "pi": bytes.fromhex(
            "7d9c633ffeee27349264cf5c667579fc583b4bda63ab71d001f89c10003ab"
            "46f14adf9a3cd8b8412d9038531e865c341cafa73589b023d14311c331a9ad15ff"
            "2fb37831e00f0acaa6d73bc9997b06501"
        ),
    },
    {
        "public_key": bytes.fromhex(
            "3d4017c3e843895a92b70aa74d1b7ebc9c982ccf2ec4968cc0cd55f12af4660c"
        ),
        "alpha": bytes.fromhex("72"),
        "pi": bytes.fromhex(
            "47b327393ff2dd81336f8a2ef10339112401253b3c714eeda879f12c50907"
            "2ef055b48372bb82efbdce8e10c8cb9a2f9d60e93908f93df1623ad78a86a028d6"
            "bc064dbfc75a6a57379ef855dc6733801"
        ),
    },
    {
        "public_key": bytes.fromhex(
            "fc51cd8e6218a1a38da47ed00230f0580816ed13ba3303ac5deb911548908025"
        ),
        "alpha": bytes.fromhex("af82"),
        "pi": bytes.fromhex(
            "926e895d308f5e328e7aa159c06eddbe56d06846abf5d98c2512235eaa57f"
            "dce35b46edfc655bc828d44ad09d1150f31374e7ef73027e14760d42e77341fe05"
            "467bb286cc2c9d7fde29120a0b2320d04"
        ),
    },
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _make_agent(agent_id: str, index: int, *, outsider: bool = False) -> EligibleAgent:
    return EligibleAgent(
        agent_id=agent_id,
        cluster_id=f"cluster-{index % 4}",
        operator_domain=f"operator-{index % 5}",
        identity_lineage_ref=f"lineage-{agent_id}",
        outsider_candidate_flag=outsider,
        capability_tier_or_lane_score="tier1",
    )


def _agent_pool() -> list[EligibleAgent]:
    agents = [_make_agent(f"r{index}", index) for index in range(1, 8)]
    agents.append(_make_agent("o1", 101, outsider=True))
    return agents


def _proofs_for(agents: list[EligibleAgent]) -> dict[str, dict[str, bytes]]:
    proofs: dict[str, dict[str, bytes]] = {}
    for index, agent in enumerate(agents):
        vector = RFC_B4_VECTORS[index % len(RFC_B4_VECTORS)]
        proofs[agent.agent_id] = {
            "public_key": vector["public_key"],
            "pi": vector["pi"],
        }
    return proofs


def _patch_alpha_to_rfc_vectors(monkeypatch: pytest.MonkeyPatch, agents: list[EligibleAgent]) -> None:
    alpha_by_agent = {
        agent.agent_id: RFC_B4_VECTORS[index % len(RFC_B4_VECTORS)]["alpha"]
        for index, agent in enumerate(agents)
    }

    def fixture_alpha(*, agent: EligibleAgent, **_kwargs: object) -> bytes:
        return alpha_by_agent[agent.agent_id]

    monkeypatch.setattr(jury_runtime, "_canonical_vrf_alpha", fixture_alpha)


def _quote_kwargs(agents: list[EligibleAgent]) -> dict[str, object]:
    return {
        "review_epoch": 1,
        "review_lane": "objective",
        "claim_or_task_id": "cid-phase-1413",
        "author_agent_id": "author",
        "author_operator_domain": "author-domain",
        "eligible_agents": agents,
    }


def test_phase_1413_token_is_recorded_in_test_header() -> None:
    assert _TOKEN_VRF_TESTS_COMPLETE == "vrf_integration_tests_complete_phase_1413"
    assert _TOKEN_VRF_TESTS_COMPLETE in _read(Path(__file__))


def test_no_import_random_in_vrf_proof_verifier() -> None:
    assert "import random" not in _read(VRF_PATH)


def test_no_import_random_in_jury_assignment_runtime() -> None:
    assert "import random" not in _read(JURY_PATH)


def test_no_assert_statements_in_phase_1411_or_1412_runtime_modules() -> None:
    for path in (VRF_PATH, JURY_PATH):
        tree = ast.parse(_read(path), filename=str(path))
        assert not [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]


def test_production_assignment_flag_true_and_non_audit_high_value_fails_closed() -> None:
    agents = _agent_pool()

    assert jury_runtime.PRODUCTION_ASSIGNMENT_NOT_ACTIVATED is True
    with pytest.raises(JuryAssignmentError, match="production_assignment_not_activated"):
        quote_jury_assignment(
            **_quote_kwargs(agents),
            is_high_value_slot=True,
            assignment_nonce="phase-1413-audit-nonce",
            vrf_proofs=_proofs_for(agents),
        )


def test_valid_rfc_9381_appendix_b4_proof_round_trip() -> None:
    vector = RFC_B4_VECTORS[0]

    assert (
        verifier.verify_vrf_proof(
            pi=vector["pi"],
            public_key=vector["public_key"],
            alpha=vector["alpha"],
        )
        is True
    )


def test_tampered_rfc_9381_appendix_b4_challenge_returns_false() -> None:
    vector = RFC_B4_VECTORS[1]
    tampered = bytearray(vector["pi"])
    tampered[32] ^= 1

    assert (
        verifier.verify_vrf_proof(
            pi=bytes(tampered),
            public_key=vector["public_key"],
            alpha=vector["alpha"],
        )
        is False
    )


def test_malformed_public_key_raises_vrf_verification_error() -> None:
    vector = RFC_B4_VECTORS[0]

    with pytest.raises(verifier.VRFVerificationError, match="vrf_public_key_wrong_length"):
        verifier.verify_vrf_proof(pi=vector["pi"], public_key=b"", alpha=vector["alpha"])


def test_non_bytes_inputs_raise_before_crypto_operations() -> None:
    vector = RFC_B4_VECTORS[0]

    with pytest.raises(verifier.VRFVerificationError, match="vrf_pi_must_be_bytes"):
        verifier.verify_vrf_proof(
            pi=bytearray(vector["pi"]),
            public_key=vector["public_key"],
            alpha=vector["alpha"],
        )
    with pytest.raises(verifier.VRFVerificationError, match="vrf_public_key_must_be_bytes"):
        verifier.verify_vrf_proof(
            pi=vector["pi"],
            public_key=bytearray(vector["public_key"]),
            alpha=vector["alpha"],
        )
    with pytest.raises(verifier.VRFVerificationError, match="vrf_alpha_must_be_bytes"):
        verifier.verify_vrf_proof(
            pi=vector["pi"],
            public_key=vector["public_key"],
            alpha=bytearray(vector["alpha"]),
        )


def test_epoch_hash_shadow_path_unchanged_for_non_high_value_assignment() -> None:
    quote = quote_jury_assignment(**_quote_kwargs(_agent_pool()))

    assert quote.assignment_mode == "epoch_hash_shadow"
    assert "epoch_hash_shadow_assignment_only_phase_j006" in quote.phase_tokens
    assert jury_runtime._TOKEN_VRF_INTEGRATED not in quote.phase_tokens
    assert quote.vrf_excluded_agents == []


def test_vrf_integration_path_uses_verifier_and_returns_verified_mode(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agents = _agent_pool()
    _patch_alpha_to_rfc_vectors(monkeypatch, agents)

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="phase-1413-audit-nonce",
        vrf_proofs=_proofs_for(agents),
        _audit_only=True,
    )

    assert quote.assignment_mode == "vrf_verified"
    assert jury_runtime._TOKEN_VRF_INTEGRATED in quote.phase_tokens
    assert len(quote.regular_panel) == 7
    assert len(quote.outsider_panel) == 1
    assert quote.vrf_excluded_agents == []


def test_invalid_candidate_proof_is_excluded_from_vrf_ordering(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    agents = _agent_pool()
    replacement = _make_agent("r8", 108)
    agents.append(replacement)
    _patch_alpha_to_rfc_vectors(monkeypatch, agents)
    proofs = _proofs_for(agents)
    tampered = bytearray(proofs["r8"]["pi"])
    tampered[32] ^= 1
    proofs["r8"] = {**proofs["r8"], "pi": bytes(tampered)}

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="phase-1413-audit-nonce",
        vrf_proofs=proofs,
        _audit_only=True,
    )

    assert "r8" in quote.vrf_excluded_agents
    assert "vrf_proof_invalid_phase_1411" in quote.vrf_exclusion_reasons["r8"]
    assert "r8" not in quote.regular_panel


def test_j008_vrf_condition_is_met_after_phase_1425_and_authorized_after_1427() -> None:
    report = evaluate_jury_activation_gate()
    condition_by_id = {condition.condition_id: condition for condition in report.conditions}

    assert condition_by_id["VRF_VERIFIER_IMPLEMENTED"].status is GateConditionStatus.MET
    assert "VRF_VERIFIER_IMPLEMENTED" not in report.blocking_not_met
    assert report.verdict == "PASS"
    assert report.production_activated is True


def test_no_private_key_or_local_proof_generation_paths_in_phase_1411_to_1413_files() -> None:
    checked_paths = (
        VRF_PATH,
        JURY_PATH,
        REPO / "tests/test_phase_1411_vrf_proof_verifier.py",
        REPO / "tests/test_phase_1412_vrf_integration.py",
        Path(__file__),
    )
    forbidden_fragments = tuple(
        "".join(parts)
        for parts in (
            ("Signing", "Key"),
            ("Private", "Key"),
            ("Ed25519", "Private", "Key"),
            ("nacl", ".", "signing"),
            ("crypto", "_sign", "_seed", "_keypair"),
            ("crypto", "_vrf", "_prove"),
            ("ECVRF", "_prove"),
        )
    )

    for path in checked_paths:
        source = _read(path)
        for fragment in forbidden_fragments:
            assert fragment not in source, f"{fragment} found in {path}"
