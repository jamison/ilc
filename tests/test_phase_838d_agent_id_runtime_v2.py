"""Phase 838d — CDL-069 agent_id_runtime v0.2 tests.

Covers:
  - derive_agent_id_v2 (identity_seed, SHA-384, 96 hex chars)
  - verify_agent_id_v2
  - is_v2_agent_id / is_legacy_agent_id discriminators
  - Legacy path (derive_agent_id) unchanged
  - Version and dependency tokens
"""
from __future__ import annotations

import hashlib

import pytest

from ilc_core.identity.agent_id_runtime import (
    AGENT_ID_RUNTIME_VERSION,
    CDL_042_DEPENDENCY,
    CDL_069_AMENDMENT,
    AgentIdentityError,
    derive_agent_id,
    derive_agent_id_v2,
    is_legacy_agent_id,
    is_v2_agent_id,
    verify_agent_id,
    verify_agent_id_v2,
)

_SEED_32 = bytes(range(32))           # 32 distinct bytes
_SEED_32_B = bytes(range(1, 33))      # different seed


# ---------------------------------------------------------------------------
# Version and dependency tokens
# ---------------------------------------------------------------------------

def test_version_bumped_to_v2() -> None:
    assert AGENT_ID_RUNTIME_VERSION == "agent_id_runtime_838d.v0.2"


def test_cdl_042_dependency_unchanged() -> None:
    assert CDL_042_DEPENDENCY == "cdl_042_ratified_407.v0.1"


def test_cdl_069_amendment_token_present() -> None:
    assert CDL_069_AMENDMENT == "cdl_069_opens_phase_838"


# ---------------------------------------------------------------------------
# derive_agent_id_v2 — CDL-069 canonical path
# ---------------------------------------------------------------------------

def test_v2_returns_96_hex_chars() -> None:
    result = derive_agent_id_v2(_SEED_32)
    assert len(result) == 96
    assert all(c in "0123456789abcdef" for c in result)


def test_v2_is_deterministic() -> None:
    assert derive_agent_id_v2(_SEED_32) == derive_agent_id_v2(_SEED_32)


def test_v2_differs_for_different_seeds() -> None:
    assert derive_agent_id_v2(_SEED_32) != derive_agent_id_v2(_SEED_32_B)


def test_v2_known_vector() -> None:
    """Lock exact SHA-384 derivation formula."""
    seed = b"\x00" * 32
    domain = b"ilc-agent-id-v1:"
    expected = hashlib.sha384(domain + seed).hexdigest()
    assert derive_agent_id_v2(seed) == expected


def test_v2_rejects_non_bytes() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        derive_agent_id_v2("not bytes")  # type: ignore[arg-type]
    assert "cdl_069_agent_id_invalid_seed_type" in exc.value.token


def test_v2_rejects_wrong_length() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        derive_agent_id_v2(b"\x00" * 16)
    assert "cdl_069_agent_id_invalid_seed_length" in exc.value.token


def test_v2_rejects_empty_bytes() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        derive_agent_id_v2(b"")
    assert "cdl_069_agent_id_invalid_seed_length" in exc.value.token


def test_v2_rejects_33_bytes() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        derive_agent_id_v2(b"\x00" * 33)
    assert "cdl_069_agent_id_invalid_seed_length" in exc.value.token


def test_v2_no_prefix() -> None:
    """CDL-069 agent_id has no 'agent-' prefix — it is a raw 96-char hex string."""
    result = derive_agent_id_v2(_SEED_32)
    assert not result.startswith("agent-")


# ---------------------------------------------------------------------------
# verify_agent_id_v2
# ---------------------------------------------------------------------------

def test_verify_v2_correct() -> None:
    agent_id = derive_agent_id_v2(_SEED_32)
    assert verify_agent_id_v2(agent_id, _SEED_32)


def test_verify_v2_wrong_seed() -> None:
    agent_id = derive_agent_id_v2(_SEED_32)
    assert not verify_agent_id_v2(agent_id, _SEED_32_B)


def test_verify_v2_wrong_length_returns_false() -> None:
    assert not verify_agent_id_v2("a" * 64, _SEED_32)


def test_verify_v2_rejects_non_string() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        verify_agent_id_v2(12345, _SEED_32)  # type: ignore[arg-type]
    assert "cdl_069_agent_id_invalid_id_type" in exc.value.token


# ---------------------------------------------------------------------------
# v2 / legacy discriminators
# ---------------------------------------------------------------------------

def test_is_v2_agent_id_true_for_96_hex() -> None:
    agent_id = derive_agent_id_v2(_SEED_32)
    assert is_v2_agent_id(agent_id)


def test_is_v2_agent_id_false_for_legacy() -> None:
    legacy = derive_agent_id(b"\x01" * 48)
    assert not is_v2_agent_id(legacy)


def test_is_legacy_agent_id_true() -> None:
    legacy = derive_agent_id(b"\x01" * 48)
    assert is_legacy_agent_id(legacy)


def test_is_legacy_agent_id_false_for_v2() -> None:
    v2 = derive_agent_id_v2(_SEED_32)
    assert not is_legacy_agent_id(v2)


def test_discriminators_are_mutually_exclusive() -> None:
    v2 = derive_agent_id_v2(_SEED_32)
    legacy = derive_agent_id(b"\x01" * 48)
    assert is_v2_agent_id(v2) and not is_legacy_agent_id(v2)
    assert is_legacy_agent_id(legacy) and not is_v2_agent_id(legacy)


# ---------------------------------------------------------------------------
# Legacy path unchanged (CDL-042 backward compatibility)
# ---------------------------------------------------------------------------

def test_legacy_derive_unchanged() -> None:
    pk = b"\x42" * 96
    expected = "agent-" + hashlib.sha256(b"ilc-agent-id-v1:" + pk).hexdigest()
    assert derive_agent_id(pk) == expected


def test_legacy_verify_unchanged() -> None:
    pk = b"\x42" * 96
    agent_id = derive_agent_id(pk)
    assert verify_agent_id(agent_id, pk)


def test_legacy_rejects_empty_key() -> None:
    with pytest.raises(AgentIdentityError) as exc:
        derive_agent_id(b"")
    assert "cdl_042_agent_id_empty_key" in exc.value.token


def test_v2_and_legacy_produce_different_ids_for_same_bytes() -> None:
    """Ensures the two paths cannot be confused even with 32-byte inputs."""
    seed = _SEED_32
    v2_id = derive_agent_id_v2(seed)
    legacy_id = derive_agent_id(seed)
    assert v2_id != legacy_id
    assert len(v2_id) == 96
    assert legacy_id.startswith("agent-")
