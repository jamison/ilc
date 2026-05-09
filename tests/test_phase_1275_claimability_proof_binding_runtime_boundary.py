from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from ilc_core.ledger.cdl048_conversion_sweeper_runtime import (
    conversion_receipt_payload,
    convert_ecu_lot,
    empty_conversion_sweeper_state,
    register_ecu_lot,
)
from ilc_core.ledger.claimability_proof_binding_runtime import (
    CLAIMABILITY_PROOF_BINDING_RUNTIME_VERSION,
    NON_LOOPBACK_CLAIMABILITY_API_BLOCKED_TOKEN,
    PUBLIC_CLAIMABILITY_NOT_ACTIVATED_TOKEN,
    SETTLED_ROOT_WALLET_ROOT_RECEIPT_BINDING_TOKEN,
    ClaimabilityProofBindingRuntimeError,
    build_claimability_proof_binding,
    canonical_claimability_proof_json,
    canonical_json,
    claimability_proof_payload,
    claimability_proof_ref,
    latest_balance_receipt_ref,
)
from ilc_core.rc.package_profile_ci_gate import build_package_profile_ci_audit
from ilc_core.rc.package_profiles import PROFILE_OPENCLAW_SKILL_CLAIMABLE


RUNTIME_PATH = Path("ilc_core/ledger/claimability_proof_binding_runtime.py")
SPEC_PATH = Path("docs/specs/ilc_claimability_proof_binding_runtime_boundary_1275_v0.1.md")
WALKTHROUGH_PATH = Path("docs/phases/phase_1275_claimability_proof_binding_runtime_boundary_walkthrough.md")
STATUS_PATH = Path("docs/phases/STATUS.md")
PLANNING_INDEX_PATH = Path("docs/PLANNING_INDEX.md")
ROADMAP_PATH = Path("docs/specs/ilc_launch_roadmap_three_machines_seven_agents_v1.1.md")
GUARDRAIL_PATH = Path("tools/check_sensitive_runtime_coding_taboos.py")
CDL_REGISTER_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
AGENTS_PATH = Path("AGENTS.md")
ALLOWLIST_PROCEDURE_PATH = Path(
    "docs/specs/ilc_public_source_allowlist_export_procedure_1255_v0.1.md"
)
PUBLIC_RC_EXCLUDE_MARKER = (
    "PUBLIC_RC_EXCLUDE: internal_phase_helper_not_public_rc_launch_surface"
)
REQUIRED_TOKENS = (
    "claimability_proof_binding_runtime_boundary_phase_1275.v0.1",
    "settled_root_wallet_root_receipt_binding_recorded_phase_1275",
    "non_loopback_claimability_api_still_blocked_phase_1275",
    "public_claimability_not_activated_phase_1275",
)


def _sha_ref(prefix: str, char: str) -> str:
    return f"{prefix}:{char * 64}"


def _latest_balance_receipt() -> dict[str, str]:
    return {
        "epoch_id": "epoch:0012",
        "reward_delta_ilc": "1.25",
        "balance_after_ilc": "1.25",
        "settlement_status": "applied",
    }


def _conversion_receipt_payload() -> dict[str, object]:
    state = register_ecu_lot(
        empty_conversion_sweeper_state(),
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        amount_ecu="10.5",
        issue_epoch=8,
        origin="epoch-attribution:alpha",
        funding_provenance=["receipt:001"],
    )
    result = convert_ecu_lot(
        state,
        lot_id="lot:alpha",
        agent_id="agent:alpha",
        conversion_epoch=12,
        settled_runtime_epoch=12,
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
    )
    return conversion_receipt_payload(result.receipt)


def _binding():
    return build_claimability_proof_binding(
        agent_id="agent:alpha",
        epoch_id="epoch:0012",
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        latest_balance_receipt=_latest_balance_receipt(),
        history_digest="c" * 64,
        conversion_receipt=_conversion_receipt_payload(),
    )


def _error_token(exc_info: pytest.ExceptionInfo[BaseException]) -> str | None:
    return getattr(exc_info.value, "token", None)


def _rehash_conversion_receipt(payload: dict[str, object]) -> dict[str, object]:
    active = dict(payload)
    active.pop("receipt_sha256", None)
    active["receipt_sha256"] = hashlib.sha256(canonical_json(active).encode("utf-8")).hexdigest()
    return active


def test_required_tokens_and_public_non_activation_flags_are_bound() -> None:
    binding = _binding()
    payload = claimability_proof_payload(binding)

    assert CLAIMABILITY_PROOF_BINDING_RUNTIME_VERSION == (
        "claimability_proof_binding_runtime_boundary_phase_1275.v0.1"
    )
    for token in REQUIRED_TOKENS:
        assert token in payload["tokens"]
    assert SETTLED_ROOT_WALLET_ROOT_RECEIPT_BINDING_TOKEN in payload["tokens"]
    assert NON_LOOPBACK_CLAIMABILITY_API_BLOCKED_TOKEN in payload["tokens"]
    assert PUBLIC_CLAIMABILITY_NOT_ACTIVATED_TOKEN in payload["tokens"]
    assert payload["claimability_state"] == "proof_bound_local_only"
    assert payload["public_claimability_activated"] is False
    assert payload["non_loopback_claimability_api_enabled"] is False
    assert payload["wallet_withdrawal_enabled"] is False
    assert payload["wallet_transfer_enabled"] is False
    assert payload["wallet_spend_enabled"] is False
    assert payload["ecu_mint_authorized"] is False
    assert payload["ilc_settlement_authorized"] is False
    assert payload["transport_principal_required_before_non_loopback"] is True


def test_proof_binding_records_roots_receipt_history_epoch_and_agent_identity() -> None:
    binding = _binding()
    payload = claimability_proof_payload(binding)

    assert payload["canonical_agent_identity"] == "agent:alpha"
    assert payload["epoch_id"] == "epoch:0012"
    assert payload["settled_runtime_root"] == _sha_ref("settled_runtime_sha256", "b")
    assert payload["wallet_state_root"] == _sha_ref("wallet_state_sha256", "a")
    assert payload["latest_balance_receipt"] == _latest_balance_receipt()
    assert payload["latest_balance_receipt_ref"] == latest_balance_receipt_ref(
        _latest_balance_receipt()
    )
    assert payload["latest_balance_receipt_ref"].startswith("balance_receipt_sha256:")
    assert payload["history_digest"] == "c" * 64
    assert payload["conversion_receipt_sha256"] == payload["conversion_receipt"]["receipt_sha256"]
    assert payload["conversion_key_sha256"] == payload["conversion_receipt"]["conversion_key_sha256"]
    assert payload["conversion_lot_id"] == "lot:alpha"
    assert payload["conversion_epoch"] == 12
    assert payload["conversion_deadline_epoch"] == 12


def test_canonical_json_and_proof_ref_are_stable_and_ordered() -> None:
    binding = _binding()
    payload = claimability_proof_payload(binding)

    assert canonical_json({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert canonical_claimability_proof_json(binding) == canonical_json(payload)
    assert claimability_proof_ref(binding) == (
        f"claimability_proof_sha256:{payload['proof_binding_sha256']}"
    )

    changed = build_claimability_proof_binding(
        agent_id="agent:alpha",
        epoch_id="epoch:0012",
        settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
        wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
        latest_balance_receipt=_latest_balance_receipt(),
        history_digest="d" * 64,
        conversion_receipt=_conversion_receipt_payload(),
    )
    assert changed.proof_binding_sha256 != binding.proof_binding_sha256


@pytest.mark.parametrize(
    ("overrides", "token"),
    (
        ({"settled_runtime_root": "settled_runtime_sha256:short"}, "claimability_settled_runtime_root_invalid"),
        ({"wallet_state_root": "wallet_state_sha256:short"}, "claimability_wallet_state_root_invalid"),
        ({"history_digest": "short"}, "claimability_history_digest_invalid"),
    ),
)
def test_digest_and_root_length_validation_fails_closed(
    overrides: dict[str, object],
    token: str,
) -> None:
    kwargs: dict[str, object] = {
        "agent_id": "agent:alpha",
        "epoch_id": "epoch:0012",
        "settled_runtime_root": _sha_ref("settled_runtime_sha256", "b"),
        "wallet_state_root": _sha_ref("wallet_state_sha256", "a"),
        "latest_balance_receipt": _latest_balance_receipt(),
        "history_digest": "c" * 64,
        "conversion_receipt": _conversion_receipt_payload(),
    }
    kwargs.update(overrides)
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
        build_claimability_proof_binding(**kwargs)
    assert _error_token(exc_info) == token


def test_latest_balance_receipt_epoch_mismatch_and_float_fail_closed() -> None:
    bad_epoch = _latest_balance_receipt()
    bad_epoch["epoch_id"] = "epoch:0011"
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as epoch_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=bad_epoch,
            history_digest="c" * 64,
            conversion_receipt=_conversion_receipt_payload(),
        )
    assert _error_token(epoch_exc) == "claimability_latest_balance_receipt_epoch_mismatch"

    float_receipt: dict[str, object] = _latest_balance_receipt()
    float_receipt["reward_delta_ilc"] = 1.25
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as float_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=float_receipt,
            history_digest="c" * 64,
            conversion_receipt=_conversion_receipt_payload(),
        )
    assert _error_token(float_exc) == "claimability_float_forbidden"

    binding = _binding()
    binding.latest_balance_receipt["reward_delta_ilc"] = 1.25
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as payload_float_exc:
        claimability_proof_payload(binding)
    assert _error_token(payload_float_exc) == "claimability_float_forbidden"


@pytest.mark.parametrize(
    "field",
    ("reward_delta_ilc", "balance_after_ilc"),
)
def test_latest_balance_receipt_rejects_non_finite_and_non_numeric_decimal_strings(
    field: str,
) -> None:
    for bad_value in ("NaN", "Infinity", "not-a-number"):
        receipt = _latest_balance_receipt()
        receipt[field] = bad_value
        with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
            build_claimability_proof_binding(
                agent_id="agent:alpha",
                epoch_id="epoch:0012",
                settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
                wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
                latest_balance_receipt=receipt,
                history_digest="c" * 64,
                conversion_receipt=_conversion_receipt_payload(),
            )
        assert _error_token(exc_info) == "claimability_latest_balance_receipt_invalid"

    negative_balance = _latest_balance_receipt()
    negative_balance["balance_after_ilc"] = "-0.1"
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as negative_balance_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=negative_balance,
            history_digest="c" * 64,
            conversion_receipt=_conversion_receipt_payload(),
        )
    assert _error_token(negative_balance_exc) == "claimability_latest_balance_receipt_invalid"


def test_conversion_receipt_must_match_agent_roots_and_non_activation_semantics() -> None:
    receipt = _conversion_receipt_payload()
    agent_mismatch = dict(receipt)
    agent_mismatch["agent_id"] = "agent:other"
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as agent_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=_latest_balance_receipt(),
            history_digest="c" * 64,
            conversion_receipt=agent_mismatch,
        )
    assert _error_token(agent_exc) == "claimability_conversion_receipt_hash_mismatch"

    wallet_mismatch = _conversion_receipt_payload()
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as wallet_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "d"),
            latest_balance_receipt=_latest_balance_receipt(),
            history_digest="c" * 64,
            conversion_receipt=wallet_mismatch,
        )
    assert _error_token(wallet_exc) == "claimability_conversion_receipt_wallet_root_mismatch"

    activated = _conversion_receipt_payload()
    activated["public_claimability_activated"] = True
    activated = _rehash_conversion_receipt(activated)
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as activated_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=_latest_balance_receipt(),
            history_digest="c" * 64,
            conversion_receipt=activated,
        )
    assert _error_token(activated_exc) == "claimability_conversion_receipt_activation_forbidden"


def test_conversion_receipt_rechecks_deadline_math_and_conversion_key_derivation() -> None:
    late = _conversion_receipt_payload()
    late["conversion_epoch"] = 99
    late["settled_runtime_epoch"] = 99
    late = _rehash_conversion_receipt(late)
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as late_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=_latest_balance_receipt(),
            history_digest="c" * 64,
            conversion_receipt=late,
        )
    assert _error_token(late_exc) == "claimability_conversion_receipt_invalid"

    wrong_deadline = _conversion_receipt_payload()
    wrong_deadline["deadline_epoch"] = 999
    wrong_deadline = _rehash_conversion_receipt(wrong_deadline)
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as deadline_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=_latest_balance_receipt(),
            history_digest="c" * 64,
            conversion_receipt=wrong_deadline,
        )
    assert _error_token(deadline_exc) == "claimability_conversion_receipt_invalid"

    key_tampered = _conversion_receipt_payload()
    key_tampered["conversion_key_sha256"] = "d" * 64
    key_tampered = _rehash_conversion_receipt(key_tampered)
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as key_exc:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=_sha_ref("settled_runtime_sha256", "b"),
            wallet_state_root=_sha_ref("wallet_state_sha256", "a"),
            latest_balance_receipt=_latest_balance_receipt(),
            history_digest="c" * 64,
            conversion_receipt=key_tampered,
        )
    assert _error_token(key_exc) == "claimability_conversion_key_sha256_invalid"


def test_settled_runtime_root_rejects_wallet_state_root_namespace() -> None:
    wallet_root = _sha_ref("wallet_state_sha256", "a")
    receipt = _conversion_receipt_payload()
    receipt["settled_runtime_root"] = wallet_root
    receipt = _rehash_conversion_receipt(receipt)
    with pytest.raises(ClaimabilityProofBindingRuntimeError) as exc_info:
        build_claimability_proof_binding(
            agent_id="agent:alpha",
            epoch_id="epoch:0012",
            settled_runtime_root=wallet_root,
            wallet_state_root=wallet_root,
            latest_balance_receipt=_latest_balance_receipt(),
            history_digest="c" * 64,
            conversion_receipt=receipt,
        )
    assert _error_token(exc_info) == "claimability_settled_runtime_root_invalid"


def test_runtime_source_contains_no_public_api_or_wallet_authority() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")

    forbidden_terms = (
        "FastAPI",
        "APIRouter",
        "HTTPServer",
        "requests.",
        "aiohttp",
        "def withdraw",
        "def transfer",
        "def spend",
        "def mint",
        "def settle",
        "datetime.now",
        "time.time",
        "random.",
        "assert ",
    )
    for term in forbidden_terms:
        assert term not in source


def test_internal_helper_is_marked_and_absent_from_current_public_claimable_profile() -> None:
    source = RUNTIME_PATH.read_text(encoding="utf-8")
    header = "\n".join(source.splitlines()[:6])

    assert PUBLIC_RC_EXCLUDE_MARKER in header
    assert "PUBLIC_RC_EXCLUDE_REASON: local Phase 1275 proof-binding scaffold only." in header
    assert "PUBLIC_RC_INCLUDE_REQUIRES:" in header

    audit = build_package_profile_ci_audit()
    claimable_files = {
        file_record["path"]
        for measurement in audit["profiles"][PROFILE_OPENCLAW_SKILL_CLAIMABLE][
            "surface_measurements"
        ].values()
        for file_record in measurement["files"]
    }
    assert RUNTIME_PATH.as_posix() not in claimable_files

    assert "PUBLIC_RC_EXCLUDE" in AGENTS_PATH.read_text(encoding="utf-8")
    assert "PUBLIC_RC_EXCLUDE" in ALLOWLIST_PROCEDURE_PATH.read_text(encoding="utf-8")
    assert PUBLIC_RC_EXCLUDE_MARKER in SPEC_PATH.read_text(encoding="utf-8")
    assert PUBLIC_RC_EXCLUDE_MARKER in WALKTHROUGH_PATH.read_text(encoding="utf-8")


def test_phase_1275_docs_status_guardrail_and_cdl_register_non_mutation() -> None:
    for path in (
        RUNTIME_PATH,
        SPEC_PATH,
        WALKTHROUGH_PATH,
        STATUS_PATH,
        PLANNING_INDEX_PATH,
        ROADMAP_PATH,
    ):
        text = path.read_text(encoding="utf-8")
        for token in REQUIRED_TOKENS:
            assert token in text

    guardrail = GUARDRAIL_PATH.read_text(encoding="utf-8")
    assert "ilc_core/ledger/claimability_proof_binding_runtime.py" in guardrail

    cdl_register = CDL_REGISTER_PATH.read_text(encoding="utf-8")
    assert "cdl087_ratification_authorization_preflight_phase_1276.v0.1" not in cdl_register
    assert "claimability_proof_binding_runtime_boundary_phase_1275.v0.1" not in cdl_register
