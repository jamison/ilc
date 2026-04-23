"""Gate tests for ADR-0034 D2d sealed-sender mechanism."""

from pathlib import Path


ADR_PATH = Path("docs/adr/ADR_0034_D2d_Sealed_Sender_Mechanism.md")


def _read() -> str:
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_0034_exists_and_is_accepted() -> None:
    text = _read()
    assert "**Status:** Accepted" in text
    assert "`run_h013_d2d_sealed_sender_adr_verdict=accepted`" in text


def test_all_mechanism_options_are_evaluated() -> None:
    text = _read()
    assert "Option A: one-hop relay concealment" in text
    assert "Option B: fixed-size Sphinx-style onion envelope" in text
    assert "Option C: SURB reply block" in text
    assert "**Accepted**" in text


def test_cdl_060_single_hop_boundary_is_explicit() -> None:
    text = _read()
    assert "CDL-060" in text
    assert "unbounded multi-hop" in text
    assert "one bounded relay leg plus one terminal delivery leg" in text


def test_cdl_061_outer_envelope_unchanged() -> None:
    text = _read()
    assert "CDL-061" in text
    for field in ("`message_id`", "`payload_cid`", "`channel_id`", "`sender_peer_id`"):
        assert field in text
    assert "inside" in text


def test_h015_boundary_is_separate_from_h013() -> None:
    text = _read()
    assert "H-015 owns" in text
    assert "H-013 owns" in text
    assert "`selected_relay_peer_id + sealed_payload_cid + opaque_channel_id`" in text


def test_non_authorizations_block_runtime_and_cdl_claims() -> None:
    text = _read()
    assert "does not authorize" in text
    assert "implementation of H-013" in text
    assert "mutation, opening, or prelocking of any CDL row" in text
    assert "activation of Tier 3" in text
