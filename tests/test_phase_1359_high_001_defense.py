from __future__ import annotations

import io
import logging
from pathlib import Path

import pytest

from ilc_core.identity.log_redaction_runtime import (
    AGENT_ID_PLAINTEXT_REDACTED_VALIDATOR_LOGS_TOKEN,
    HIGH_001_LOG_REDACTION_RUNTIME_VERSION,
    SENDER_PRIVACY_CLAIM_BLOCKER_CLEARED_TOKEN,
    AgentIDLogRedactionFilter,
    redact_agent_id_for_log,
    redact_agent_ids_in_log_message,
)
from ilc_core.privacy.transfer_mixing_framework import (
    ACTIVATION_GATE_REQUIRED,
    MIXING_FRAMEWORK_NOT_ACTIVATED_PRODUCTION_TOKEN,
    TRANSFER_MIXING_K_ANONYMITY_FRAMEWORK_TOKEN,
    build_transfer_mixing_framework_quote,
    route_transfer_through_mixing_framework,
)


ROOT = Path(__file__).resolve().parents[1]
LOG_RUNTIME = ROOT / "ilc_core/identity/log_redaction_runtime.py"
MIXING_RUNTIME = ROOT / "ilc_core/privacy/transfer_mixing_framework.py"
NODE_RS = ROOT / "ilc_consensus/src/node.rs"
LIB_RS = ROOT / "ilc_consensus/src/lib.rs"
ONBOARDING_PY = ROOT / "ilc_core/economics/onboarding.py"
AGENT_PY = ROOT / "ilc_core/agent.py"
BENCHMARK_PY = ROOT / "ilc_core/mining/benchmark.py"

AGENT_ID = "a" * 96


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_1359_tokens_and_versions_present() -> None:
    assert HIGH_001_LOG_REDACTION_RUNTIME_VERSION == (
        "high_001_log_redaction_runtime_phase_1359.v0.1"
    )
    assert AGENT_ID_PLAINTEXT_REDACTED_VALIDATOR_LOGS_TOKEN == (
        "agent_id_plaintext_redacted_validator_logs_phase_1359"
    )
    assert SENDER_PRIVACY_CLAIM_BLOCKER_CLEARED_TOKEN == (
        "sender_privacy_claim_blocker_cleared_phase_1359"
    )
    assert TRANSFER_MIXING_K_ANONYMITY_FRAMEWORK_TOKEN == (
        "transfer_mixing_k_anonymity_framework_phase_1359"
    )
    assert MIXING_FRAMEWORK_NOT_ACTIVATED_PRODUCTION_TOKEN == (
        "mixing_framework_not_activated_production_phase_1359"
    )


def test_redaction_is_deterministic_epoch_scoped_and_non_plaintext() -> None:
    token_a = redact_agent_id_for_log(AGENT_ID, protocol_epoch=1359)
    token_b = redact_agent_id_for_log(AGENT_ID, protocol_epoch=1359)
    token_c = redact_agent_id_for_log(AGENT_ID, protocol_epoch=1360)

    assert token_a == token_b
    assert token_a != token_c
    assert AGENT_ID not in token_a
    assert token_a.startswith("[agent_id:redacted:v1:epoch=1359:sha256=")


def test_redaction_filter_fires_before_log_write() -> None:
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.addFilter(AgentIDLogRedactionFilter([AGENT_ID], protocol_epoch=1359))

    logger = logging.getLogger("phase_1359_high_001_test")
    logger.handlers = []
    logger.propagate = False
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    logger.info("validator accepted agent_id=%s", AGENT_ID)
    handler.flush()

    output = stream.getvalue()
    assert AGENT_ID not in output
    assert "[agent_id:redacted:v1:epoch=1359:sha256=" in output


def test_log_message_redaction_replaces_string_and_bytes_forms() -> None:
    binary_id = bytes.fromhex("ab" * 48)
    message = f"string={AGENT_ID} bytes={binary_id.hex()}"

    redacted = redact_agent_ids_in_log_message(
        message,
        [AGENT_ID, binary_id],
        protocol_epoch=1359,
    )

    assert AGENT_ID not in redacted
    assert binary_id.hex() not in redacted
    assert redacted.count("[agent_id:redacted:v1:epoch=1359:sha256=") == 2


def test_log_redaction_bounds_fail_closed() -> None:
    with pytest.raises(ValueError, match="log_redaction_protocol_epoch_must_be_non_negative"):
        redact_agent_id_for_log(AGENT_ID, protocol_epoch=-1)
    with pytest.raises(ValueError, match="log_redaction_message_exceeds_bound"):
        redact_agent_ids_in_log_message("x" * 65_537, [AGENT_ID], protocol_epoch=1359)
    with pytest.raises(ValueError, match="log_redaction_agent_ids_exceed_bound"):
        redact_agent_ids_in_log_message(
            "ok",
            [f"agent-{index:03d}" for index in range(129)],
            protocol_epoch=1359,
        )


def test_python_plaintext_agentid_log_sites_use_redaction_helper() -> None:
    for path in (ONBOARDING_PY, AGENT_PY, BENCHMARK_PY):
        text = _read(path)
        assert "redact_agent_id_for_log" in text

    assert "[Vault] Issued starter credit %s to %s" in _read(ONBOARDING_PY)
    assert "agent_claim_minted agent=%s node=%s" in _read(AGENT_PY)
    assert "[Benchmark] Initializing CapProof for %s" in _read(BENCHMARK_PY)


def test_rust_validator_log_redaction_surface_remains_locked() -> None:
    node_rs = _read(NODE_RS)
    lib_rs = _read(LIB_RS)

    assert "layer1_agentid_log_hygiene_applied" in node_rs
    assert '#[cfg(not(feature = "debug_agent_ids"))]' in node_rs
    assert "[redacted:agent_id]" in node_rs
    assert "fmt_object_ref(&transfer.object_ref)" in node_rs
    assert "debug_agent_ids enables plaintext AgentID logging" in lib_rs
    assert "not(debug_assertions)" in lib_rs


def test_transfer_mixing_framework_is_default_off_and_uses_locked_row5_parameters() -> None:
    quote = build_transfer_mixing_framework_quote(requested_transfer_count=30)

    assert ACTIVATION_GATE_REQUIRED is True
    assert quote.activation_gate_required is True
    assert quote.production_route_active is False
    assert quote.primary_k == 30
    assert quote.fallback_k == 20
    assert quote.release_jitter_epochs == 3
    assert quote.framework_token == TRANSFER_MIXING_K_ANONYMITY_FRAMEWORK_TOKEN
    assert quote.not_activated_token == MIXING_FRAMEWORK_NOT_ACTIVATED_PRODUCTION_TOKEN

    with pytest.raises(ValueError, match=MIXING_FRAMEWORK_NOT_ACTIVATED_PRODUCTION_TOKEN):
        route_transfer_through_mixing_framework({"transfer": "placeholder"}, protocol_epoch=1359)


def test_phase_1359_new_runtime_code_avoids_banned_patterns() -> None:
    for path in (LOG_RUNTIME, MIXING_RUNTIME):
        text = _read(path)
        assert "import random" not in text
        assert "assert " not in text
        assert "time.time" not in text
        assert "datetime.now" not in text
        assert "float(" not in text
