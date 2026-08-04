# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import replace
from decimal import Decimal
from pathlib import Path
import re
from unittest.mock import patch

import lmdb
import pytest
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.serialization import Encoding, NoEncryption, PrivateFormat

from ilc_core.ecu.ecu_fast_path_intent import ECUFastPathIntent, TransferClass
from ilc_core.ecu.ecu_transfer_context_verifier import (
    ECUContextVerificationError,
    ECUTransferContextVerifier,
)
from ilc_core.epoch.genesis_settlement_destination import GENESIS_AGENT1_AGENT_ID
from ilc_core.genesis.genesis_value_action_guard import (
    GENESIS_VALUE_CERTIFICATE_SCHEMA_VERSION,
    GENESIS_VALUE_GUARD_VERSION,
    GENESIS_VALUE_NETWORK_ID,
    GENESIS_VALUE_NONCE_DOMAIN,
    GenesisValueActionPolicyCertificate,
    GenesisValueGuardError,
    compute_certificate_payload_sha256,
    enforce_genesis_value_guard,
    validate_genesis_value_certificate,
)
from ilc_core.value_action import ilc_transfer_intent
from ilc_core.value_action.action_nonce_store import ActionNonceStore
from ilc_core.value_action.ilc_transfer_intent import ILCTransferIntent
from ilc_core.value_action.ilc_transfer_ledger import ILCTransferLedger
from ilc_core.value_action.local_signing_provider import LocalEd25519SigningProvider

RECIPIENT_AGENT_ID = "b" * 96
NON_GENESIS_AGENT_ID = "a" * 96
GUARD_MODULE_PATH = Path("ilc_core/genesis/genesis_value_action_guard.py")


class _GraphReader:
    def get_node(self, anchor: str) -> object | None:
        if anchor == "graph:work-context":
            return {"id": anchor}
        return None


class _SignerAuthority:
    def __init__(self, agent_id: str, public_key_bytes: bytes) -> None:
        self._agent_id = agent_id
        self._public_key_bytes = public_key_bytes

    def is_signer_authorized(
        self,
        agent_id: str,
        public_key_bytes: bytes,
        *,
        action_scope: str,
    ) -> bool:
        return (
            agent_id == self._agent_id
            and public_key_bytes == self._public_key_bytes
            and action_scope == "ILC_TRANSFER"
        )


@pytest.fixture
def lmdb_env(tmp_path: Path):
    env = lmdb.open(str(tmp_path / "genesis-value-guard.lmdb"), max_dbs=8, map_size=8 * 1024 * 1024)
    try:
        yield env
    finally:
        env.close()


@pytest.fixture(autouse=True)
def test_balance_seed_authorized(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ILC_TEST_BALANCE_SEED_AUTHORIZED", "1")


@pytest.fixture
def private_key() -> ed25519.Ed25519PrivateKey:
    return ed25519.Ed25519PrivateKey.generate()


@pytest.fixture
def key_uri(tmp_path: Path, private_key: ed25519.Ed25519PrivateKey) -> str:
    key_path = tmp_path / "genesis-transfer-key.pem"
    key_path.write_bytes(
        private_key.private_bytes(
            Encoding.PEM,
            PrivateFormat.PKCS8,
            NoEncryption(),
        )
    )
    return key_path.as_uri()


def _cert(**overrides: object) -> GenesisValueActionPolicyCertificate:
    cert = GenesisValueActionPolicyCertificate(
        schema_version=GENESIS_VALUE_CERTIFICATE_SCHEMA_VERSION,
        certificate_id="genesis-value-policy-cert-test",
        genesis_agent_id=GENESIS_AGENT1_AGENT_ID,
        network_id=GENESIS_VALUE_NETWORK_ID,
        effective_epoch_start=0,
        effective_epoch_end=3,
        allowed_action_classes=frozenset({"CONTRIBUTION", "PAYMENT"}),
        allowed_recipient_policy="graph_context_required",
        per_transfer_cap_micro_ecu=1_000_000_000,
        per_epoch_cap_micro_ecu=5_000_000_000,
        per_transfer_cap_micro_ilc=1_000_000_000,
        per_epoch_cap_micro_ilc=5_000_000_000,
        nonce_domain=GENESIS_VALUE_NONCE_DOMAIN,
        guardian_public_key_root="c" * 64,
        guardian_threshold=2,
        guardian_key_count=3,
        guardian_signature_scheme="Ed25519-COSE-Sign1",
        certificate_payload_sha256="0" * 64,
        certificate_sig={
            "threshold": 2,
            "signatures": [
                {"guardian": "guardian-1", "signature": "sig-1"},
                {"guardian": "guardian-2", "signature": "sig-2"},
            ],
        },
    )
    cert = replace(cert, **overrides)
    return replace(cert, certificate_payload_sha256=compute_certificate_payload_sha256(cert))


def _ecu_intent(**overrides: object) -> ECUFastPathIntent:
    fields = {
        "sender_agent_id": GENESIS_AGENT1_AGENT_ID,
        "recipient_agent_id": RECIPIENT_AGENT_ID,
        "amount_ecu": Decimal("1"),
        "transfer_class": TransferClass.CONTRIBUTION,
        "graph_context_anchor": "graph:work-context",
        "express_consent": None,
        "nonce": "genesis-ecu-nonce-1",
        "created_epoch": 1,
    }
    fields.update(overrides)
    return ECUFastPathIntent(**fields)


def _ilc_env(
    *,
    sender_agent_id: str = GENESIS_AGENT1_AGENT_ID,
    nonce_counter: int = 1,
    amount_ilc: Decimal = Decimal("10"),
):
    return ILCTransferIntent.create(
        sender_agent_id=sender_agent_id,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        amount_ilc=amount_ilc,
        nonce=f"{sender_agent_id}:nonce:{nonce_counter:020d}",
        epoch=1,
        memo="agreement:genesis-public-rc",
        graph_context_anchor="graph:work-context",
    )


def _sign(env, key_uri: str):
    return LocalEd25519SigningProvider().sign_envelope(env, key_uri)


def _raises_guard(token: str, **overrides: object) -> None:
    cert = overrides.pop("certificate", _cert())
    params = {
        "source_agent_id": GENESIS_AGENT1_AGENT_ID,
        "certificate": cert,
        "action_class": "CONTRIBUTION",
        "amount_micro_unit": 1_000_000,
        "current_epoch": 1,
        "recipient_agent_id": RECIPIENT_AGENT_ID,
        "graph_context_anchor": "graph:work-context",
        "consent_or_agreement_reference": None,
        "unit": "ECU",
        "current_epoch_spent_micro_unit": 0,
    }
    params.update(overrides)
    with pytest.raises(GenesisValueGuardError, match=f"^{token}$"):
        enforce_genesis_value_guard(**params)


def test_valid_certificate_within_epoch_accepted() -> None:
    validate_genesis_value_certificate(_cert())
    enforce_genesis_value_guard(
        source_agent_id=GENESIS_AGENT1_AGENT_ID,
        certificate=_cert(),
        action_class="CONTRIBUTION",
        amount_micro_unit=1_000_000,
        current_epoch=1,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        graph_context_anchor="graph:work-context",
        consent_or_agreement_reference=None,
        unit="ECU",
        current_epoch_spent_micro_unit=0,
    )


def test_certificate_wrong_agent_id_rejected() -> None:
    with pytest.raises(GenesisValueGuardError, match="genesis_value_certificate_agent_mismatch"):
        validate_genesis_value_certificate(_cert(genesis_agent_id=NON_GENESIS_AGENT_ID))


def test_certificate_expired_epoch_rejected() -> None:
    _raises_guard("genesis_value_certificate_expired", current_epoch=4)


def test_certificate_not_yet_active_rejected() -> None:
    _raises_guard(
        "genesis_value_certificate_not_yet_active",
        certificate=_cert(effective_epoch_start=1, effective_epoch_end=3),
        current_epoch=0,
    )


def test_certificate_disallowed_action_class_rejected() -> None:
    cert = _cert(allowed_action_classes=frozenset({"CONTRIBUTION"}))
    _raises_guard(
        "genesis_value_certificate_action_class_not_allowed",
        certificate=cert,
        action_class="PAYMENT",
        consent_or_agreement_reference="agreement:test",
    )


def test_certificate_per_transfer_cap_exact_value_accepted() -> None:
    enforce_genesis_value_guard(
        source_agent_id=GENESIS_AGENT1_AGENT_ID,
        certificate=_cert(),
        action_class="CONTRIBUTION",
        amount_micro_unit=1_000_000_000,
        current_epoch=1,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        graph_context_anchor="graph:work-context",
        consent_or_agreement_reference=None,
        unit="ECU",
        current_epoch_spent_micro_unit=0,
    )


def test_certificate_per_transfer_cap_exceeded_rejected() -> None:
    _raises_guard(
        "genesis_value_per_transfer_cap_exceeded",
        amount_micro_unit=1_000_000_001,
    )


def test_certificate_empty_sig_rejected() -> None:
    with pytest.raises(GenesisValueGuardError, match="signature"):
        validate_genesis_value_certificate(_cert(certificate_sig={"threshold": 2, "signatures": []}))


def test_certificate_requires_genesis_agent_id() -> None:
    with pytest.raises(GenesisValueGuardError, match="genesis_value_certificate_agent_mismatch"):
        validate_genesis_value_certificate(_cert(genesis_agent_id="d" * 96))


def test_recipient_policy_graph_context_required_without_anchor_rejected() -> None:
    _raises_guard("genesis_value_graph_context_required", graph_context_anchor=None)


def test_recipient_policy_graph_context_required_with_anchor_passes() -> None:
    enforce_genesis_value_guard(
        source_agent_id=GENESIS_AGENT1_AGENT_ID,
        certificate=_cert(),
        action_class="CONTRIBUTION",
        amount_micro_unit=1_000_000,
        current_epoch=1,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        graph_context_anchor="graph:work-context",
        consent_or_agreement_reference=None,
        unit="ECU",
        current_epoch_spent_micro_unit=0,
    )


def test_non_genesis_agent_with_no_cert_passes() -> None:
    enforce_genesis_value_guard(
        source_agent_id=NON_GENESIS_AGENT_ID,
        certificate=None,
        action_class="PAYMENT",
        amount_micro_unit=1,
        current_epoch=None,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        graph_context_anchor=None,
        consent_or_agreement_reference=None,
        unit="ILC",
        current_epoch_spent_micro_unit=None,
    )


def test_non_genesis_agent_with_any_cert_ignored() -> None:
    enforce_genesis_value_guard(
        source_agent_id=NON_GENESIS_AGENT_ID,
        certificate=_cert(effective_epoch_end=0),
        action_class="PAYMENT",
        amount_micro_unit=1,
        current_epoch=None,
        recipient_agent_id=RECIPIENT_AGENT_ID,
        graph_context_anchor=None,
        consent_or_agreement_reference=None,
        unit="ILC",
        current_epoch_spent_micro_unit=None,
    )


def test_non_integer_amount_rejected_by_validation() -> None:
    _raises_guard("genesis_value_amount_micro_unit_invalid", amount_micro_unit=object())


def test_nan_and_infinity_epoch_rejected_by_validation() -> None:
    _raises_guard("genesis_value_current_epoch_invalid", current_epoch=Decimal("NaN"))
    _raises_guard("genesis_value_current_epoch_invalid", current_epoch=Decimal("Infinity"))


def test_empty_allowed_action_classes_rejected() -> None:
    with pytest.raises(GenesisValueGuardError, match="genesis_value_certificate_action_classes_empty"):
        validate_genesis_value_certificate(_cert(allowed_action_classes=frozenset()))


def test_per_epoch_cap_enforced_without_redistribution() -> None:
    _raises_guard(
        "genesis_value_per_epoch_cap_exceeded",
        amount_micro_unit=1,
        current_epoch_spent_micro_unit=5_000_000_000,
    )


def test_ecu_verifier_genesis_sender_without_certificate_rejected() -> None:
    verifier = ECUTransferContextVerifier(graph_reader=_GraphReader())
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ECUContextVerificationError, match="genesis_value_certificate_required"):
            verifier.verify(_ecu_intent())


def test_ecu_verifier_genesis_sender_with_valid_certificate_passes() -> None:
    verifier = ECUTransferContextVerifier(
        graph_reader=_GraphReader(),
        genesis_value_certificate=_cert(),
        current_epoch=1,
        genesis_epoch_spent_micro_ecu=0,
    )
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        verifier.verify(_ecu_intent())


def test_ecu_verifier_non_genesis_sender_unaffected() -> None:
    verifier = ECUTransferContextVerifier(graph_reader=_GraphReader())
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        verifier.verify(_ecu_intent(sender_agent_id=NON_GENESIS_AGENT_ID))


def test_ecu_verifier_genesis_certificate_expired_raises() -> None:
    verifier = ECUTransferContextVerifier(
        graph_reader=_GraphReader(),
        genesis_value_certificate=_cert(effective_epoch_end=0),
        current_epoch=1,
        genesis_epoch_spent_micro_ecu=0,
    )
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ECUContextVerificationError, match="genesis_value_certificate_expired"):
            verifier.verify(_ecu_intent())


def test_ecu_verifier_requires_epoch_spend_for_genesis_certificate() -> None:
    verifier = ECUTransferContextVerifier(
        graph_reader=_GraphReader(),
        genesis_value_certificate=_cert(),
        current_epoch=1,
    )
    with patch("ilc_core.ecu.ecu_transfer_context_verifier.ECU_FAST_PATH_TRANSFER_ENABLED", True):
        with pytest.raises(ECUContextVerificationError, match="genesis_value_epoch_spend_required"):
            verifier.verify(_ecu_intent())


def test_ilc_verifier_genesis_sender_without_certificate_rejected(
    lmdb_env,
    key_uri: str,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)

    with patch("ilc_core.value_action.ilc_transfer_intent.ILC_TRANSFER_ENABLED", True):
        with pytest.raises(ValueError, match="genesis_value_certificate_required"):
            ledger.execute_transfer(_sign(_ilc_env(), key_uri), nonce_store)

    assert nonce_store.peek_counter(GENESIS_AGENT1_AGENT_ID) == 0
    assert ledger.get_balance(GENESIS_AGENT1_AGENT_ID) == Decimal("0")


def test_ilc_verifier_genesis_sender_with_valid_certificate_passes(
    lmdb_env,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env, genesis_value_certificate=_cert())
    nonce_store = ActionNonceStore(lmdb_env)
    provider = LocalEd25519SigningProvider()
    public_key_bytes = private_key.public_key().public_bytes_raw()
    ledger.seed_balance_for_test(GENESIS_AGENT1_AGENT_ID, Decimal("20"))

    with patch("ilc_core.value_action.ilc_transfer_intent.ILC_TRANSFER_ENABLED", True):
        entry = ledger.execute_transfer(
            _sign(_ilc_env(), key_uri),
            nonce_store,
            signature_verifier=provider,
            signer_authority=_SignerAuthority(GENESIS_AGENT1_AGENT_ID, public_key_bytes),
            sender_public_key_bytes=public_key_bytes,
        )

    assert entry.sender_agent_id == GENESIS_AGENT1_AGENT_ID
    assert ledger.get_balance(GENESIS_AGENT1_AGENT_ID) == Decimal("10")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("10")


def test_ilc_verifier_non_genesis_sender_unaffected(
    lmdb_env,
    key_uri: str,
    private_key,
) -> None:
    ledger = ILCTransferLedger(lmdb_env)
    nonce_store = ActionNonceStore(lmdb_env)
    provider = LocalEd25519SigningProvider()
    public_key_bytes = private_key.public_key().public_bytes_raw()
    ledger.seed_balance_for_test(NON_GENESIS_AGENT_ID, Decimal("20"))
    env = _sign(_ilc_env(sender_agent_id=NON_GENESIS_AGENT_ID), key_uri)

    with patch("ilc_core.value_action.ilc_transfer_intent.ILC_TRANSFER_ENABLED", True):
        entry = ledger.execute_transfer(
            env,
            nonce_store,
            signature_verifier=provider,
            signer_authority=_SignerAuthority(NON_GENESIS_AGENT_ID, public_key_bytes),
            sender_public_key_bytes=public_key_bytes,
        )

    assert entry.sender_agent_id == NON_GENESIS_AGENT_ID
    assert ledger.get_balance(NON_GENESIS_AGENT_ID) == Decimal("10")


def test_ilc_genesis_per_epoch_cap_rejects_second_transfer_without_mutation(
    lmdb_env,
    key_uri: str,
    private_key,
) -> None:
    cert = _cert(per_transfer_cap_micro_ilc=1_000_000, per_epoch_cap_micro_ilc=1_500_000)
    ledger = ILCTransferLedger(lmdb_env, genesis_value_certificate=cert)
    nonce_store = ActionNonceStore(lmdb_env)
    provider = LocalEd25519SigningProvider()
    public_key_bytes = private_key.public_key().public_bytes_raw()
    ledger.seed_balance_for_test(GENESIS_AGENT1_AGENT_ID, Decimal("5"))

    with patch("ilc_core.value_action.ilc_transfer_intent.ILC_TRANSFER_ENABLED", True):
        ledger.execute_transfer(
            _sign(_ilc_env(amount_ilc=Decimal("1"), nonce_counter=1), key_uri),
            nonce_store,
            signature_verifier=provider,
            signer_authority=_SignerAuthority(GENESIS_AGENT1_AGENT_ID, public_key_bytes),
            sender_public_key_bytes=public_key_bytes,
        )
        with pytest.raises(ValueError, match="genesis_value_per_epoch_cap_exceeded"):
            ledger.execute_transfer(
                _sign(_ilc_env(amount_ilc=Decimal("1"), nonce_counter=2), key_uri),
                nonce_store,
                signature_verifier=provider,
                signer_authority=_SignerAuthority(GENESIS_AGENT1_AGENT_ID, public_key_bytes),
                sender_public_key_bytes=public_key_bytes,
            )

    assert nonce_store.peek_counter(GENESIS_AGENT1_AGENT_ID) == 1
    assert ledger.get_balance(GENESIS_AGENT1_AGENT_ID) == Decimal("4")
    assert ledger.get_balance(RECIPIENT_AGENT_ID) == Decimal("1")


def test_plate3_shamir_shares_not_imported_in_guard_module() -> None:
    source = GUARD_MODULE_PATH.read_text(encoding="utf-8").lower()

    assert "shamir" not in source
    assert "plate_3" not in source
    assert "recovery_share" not in source


def test_no_float_in_guard_module() -> None:
    source = GUARD_MODULE_PATH.read_text(encoding="utf-8")

    assert "float" not in source
    assert re.search(r"0\.[0-9]", source) is None
    assert GENESIS_VALUE_GUARD_VERSION == "genesis_value_action_guard_GAP_GENESIS_VALUE_02_v0_1"
