import base64
from pathlib import Path

import pytest

from ilc_core.epistemic import jury_assignment_runtime as runtime
from ilc_core.epistemic.jury_assignment_runtime import (
    EligibleAgent,
    JuryAssignmentError,
    quote_jury_assignment,
)


REPO = Path(__file__).parent.parent
RUNTIME_PATH = REPO / "ilc_core/epistemic/jury_assignment_runtime.py"

RFC_B4_FIXTURES = (
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


def _make_agent(agent_id: str, index: int, *, outsider: bool = False) -> EligibleAgent:
    return EligibleAgent(
        agent_id=agent_id,
        cluster_id=f"cluster-{index % 4}",
        operator_domain=f"operator-{index % 5}",
        identity_lineage_ref=f"lineage-{agent_id}",
        outsider_candidate_flag=outsider,
        capability_tier_or_lane_score="tier1",
    )


def _vrf_pool(*, regular_count: int = 8) -> list[EligibleAgent]:
    agents = [
        _make_agent(f"r{index}", index)
        for index in range(1, regular_count + 1)
    ]
    agents.append(_make_agent("o1", 101, outsider=True))
    return agents


def _proofs_for(agents: list[EligibleAgent]) -> dict[str, dict[str, bytes]]:
    proofs: dict[str, dict[str, bytes]] = {}
    for index, agent in enumerate(agents):
        fixture = RFC_B4_FIXTURES[index % len(RFC_B4_FIXTURES)]
        proofs[agent.agent_id] = {
            "public_key": fixture["public_key"],
            "pi": fixture["pi"],
        }
    return proofs


def _b64u_unpadded(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _b64u_proofs_for(agents: list[EligibleAgent]) -> dict[str, dict[str, str]]:
    proofs: dict[str, dict[str, str]] = {}
    for index, agent in enumerate(agents):
        fixture = RFC_B4_FIXTURES[index % len(RFC_B4_FIXTURES)]
        proofs[agent.agent_id] = {
            "public_key_b64u": _b64u_unpadded(fixture["public_key"]),
            "pi_b64u": _b64u_unpadded(fixture["pi"]),
        }
    return proofs


def _patch_alpha_to_rfc_fixtures(monkeypatch, agents: list[EligibleAgent]) -> None:
    alpha_by_agent = {
        agent.agent_id: RFC_B4_FIXTURES[index % len(RFC_B4_FIXTURES)]["alpha"]
        for index, agent in enumerate(agents)
    }

    def fixture_alpha(*, agent: EligibleAgent, **_kwargs) -> bytes:
        return alpha_by_agent[agent.agent_id]

    monkeypatch.setattr(runtime, "_canonical_vrf_alpha", fixture_alpha)


def _quote_kwargs(agents: list[EligibleAgent]) -> dict:
    return {
        "review_epoch": 1,
        "review_lane": "objective",
        "claim_or_task_id": "cid-phase-1412",
        "author_agent_id": "author",
        "author_operator_domain": "author-domain",
        "eligible_agents": agents,
    }


def test_non_high_value_call_still_uses_epoch_hash_shadow() -> None:
    quote = quote_jury_assignment(**_quote_kwargs(_vrf_pool()))

    assert quote.assignment_mode == "epoch_hash_shadow"
    assert "epoch_hash_shadow_assignment_only_phase_j006" in quote.phase_tokens
    assert runtime._TOKEN_VRF_INTEGRATED not in quote.phase_tokens
    assert quote.vrf_excluded_agents == []


def test_high_value_call_without_audit_guard_fails_closed(monkeypatch) -> None:
    agents = _vrf_pool()
    _patch_alpha_to_rfc_fixtures(monkeypatch, agents)

    with pytest.raises(JuryAssignmentError, match="production_assignment_not_activated"):
        quote_jury_assignment(
            **_quote_kwargs(agents),
            is_high_value_slot=True,
            assignment_nonce="audit-nonce",
            vrf_proofs=_proofs_for(agents),
        )


def test_high_value_audit_call_uses_vrf_verified_mode(monkeypatch) -> None:
    agents = _vrf_pool()
    _patch_alpha_to_rfc_fixtures(monkeypatch, agents)

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="audit-nonce",
        vrf_proofs=_proofs_for(agents),
        _audit_only=True,
    )

    assert quote.assignment_mode == "vrf_verified"
    assert runtime._TOKEN_VRF_INTEGRATED in quote.phase_tokens
    assert "epoch_hash_shadow_assignment_only_phase_j006" in quote.phase_tokens
    assert len(quote.regular_panel) == 7
    assert len(quote.outsider_panel) == 1
    assert quote.vrf_excluded_agents == []


def test_high_value_audit_call_accepts_adr_style_b64u_records(monkeypatch) -> None:
    agents = _vrf_pool()
    _patch_alpha_to_rfc_fixtures(monkeypatch, agents)

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="audit-nonce",
        vrf_proofs=_b64u_proofs_for(agents),
        _audit_only=True,
    )

    assert quote.assignment_mode == "vrf_verified"
    assert runtime._TOKEN_VRF_INTEGRATED in quote.phase_tokens
    assert quote.vrf_excluded_agents == []


def test_canonical_vrf_alpha_uses_adr_0042_closed_field_set() -> None:
    agent = _make_agent("r1", 1)

    alpha = runtime._canonical_vrf_alpha(
        review_epoch=1,
        review_lane="objective",
        claim_or_task_id="cid-phase-1412",
        assignment_nonce="nonce-1",
        agent=agent,
    )

    assert alpha == (
        b'{"assignment_nonce":"nonce-1","capability_tier_or_lane_score":"tier1",'
        b'"claim_or_task_id":"cid-phase-1412","cluster_id":"cluster-1",'
        b'"domain_separator":"ilc.vrf.jury_assignment.v1",'
        b'"eligible_agent_id":"r1","identity_lineage_ref":"lineage-r1",'
        b'"outsider_candidate_flag":false,"review_epoch":1,"review_lane":"objective"}'
    )


def test_missing_vrf_proof_excludes_candidate_visibly(monkeypatch) -> None:
    agents = _vrf_pool(regular_count=8)
    _patch_alpha_to_rfc_fixtures(monkeypatch, agents)
    proofs = _proofs_for(agents)
    proofs.pop("r8")

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="audit-nonce",
        vrf_proofs=proofs,
        _audit_only=True,
    )

    assert "r8" in quote.vrf_excluded_agents
    assert quote.vrf_exclusion_reasons["r8"] == "vrf_proof_missing_for_candidate"
    assert "r8" not in quote.regular_panel


def test_invalid_vrf_proof_excludes_candidate_visibly(monkeypatch) -> None:
    agents = _vrf_pool(regular_count=8)
    _patch_alpha_to_rfc_fixtures(monkeypatch, agents)
    proofs = _proofs_for(agents)
    tampered = bytearray(proofs["r8"]["pi"])
    tampered[32] ^= 1
    proofs["r8"] = {**proofs["r8"], "pi": bytes(tampered)}

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="audit-nonce",
        vrf_proofs=proofs,
        _audit_only=True,
    )

    assert "r8" in quote.vrf_excluded_agents
    assert "vrf_proof_invalid_phase_1411" in quote.vrf_exclusion_reasons["r8"]
    assert "r8" not in quote.regular_panel


def test_malformed_vrf_b64u_record_excludes_candidate_visibly(monkeypatch) -> None:
    agents = _vrf_pool(regular_count=8)
    _patch_alpha_to_rfc_fixtures(monkeypatch, agents)
    proofs = _proofs_for(agents)
    proofs["r8"] = {
        "public_key_b64u": "not valid!!!",
        "pi": proofs["r8"]["pi"],
    }

    quote = quote_jury_assignment(
        **_quote_kwargs(agents),
        is_high_value_slot=True,
        assignment_nonce="audit-nonce",
        vrf_proofs=proofs,
        _audit_only=True,
    )

    assert "r8" in quote.vrf_excluded_agents
    assert quote.vrf_exclusion_reasons["r8"] == "vrf_b64u_decode_failed_for_candidate"
    assert "r8" not in quote.regular_panel


def test_production_assignment_flag_remains_true() -> None:
    assert runtime.PRODUCTION_ASSIGNMENT_NOT_ACTIVATED is True


def test_jury_assignment_runtime_has_no_random_or_private_key_paths() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")

    assert "import random" not in source
    assert "secrets.SystemRandom" not in source
    assert "Signing" + "Key" not in source
    assert "Private" + "Key" not in source
    assert "ECVRF_" + "prove" not in source


def test_phase_1412_tests_do_not_generate_vrf_proofs() -> None:
    source = Path(__file__).read_text(encoding="utf-8")

    assert "Signing" + "Key" not in source
    assert "Private" + "Key" not in source
    assert "ECVRF_" + "prove" not in source
    assert "nonce_" + "generation" not in source
