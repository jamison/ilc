from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "docs/specs/ilc_peer_funded_bounty_spec_1550p_v0.1.md"
REGISTER = ROOT / "docs/specs/ilc_open_obligation_register_v0.1.md"
STATUS = ROOT / "docs/phases/STATUS.md"
PRODUCTIVE_RUNTIME = ROOT / "ilc_core/economics/productive_ecu_expansion_bounty_runtime.py"
PEER_RUNTIME = ROOT / "ilc_core/economics/peer_funded_bounty_runtime.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_peer_funded_bounty_spec_records_required_tokens_and_sections() -> None:
    text = read(SPEC)

    required = [
        "obl_029_peer_funded_bounty_spec_committed_phase_1550p",
        "obl_029_closed_phase_1550p",
        "peer_funded_bounty_runtime_not_activated_phase_1550p",
        "no_bounty_payout_activation_phase_1550p",
        "Future Lifecycle",
        "Required Future Runtime Invariants",
        "Anti-Gaming Constraints",
        "Relationship to Funding Requests",
        "Minimum Future CDL Questions",
    ]
    for needle in required:
        assert needle in text


def test_peer_funded_bounty_spec_distinguishes_obl027_and_cdl047() -> None:
    text = read(SPEC)

    assert "Protocol-issued bounty accounting only" in text
    assert "explicitly excludes peer-funded bounties" in text
    assert "Treasury-funded or protocol-issued bounties are top-down stimulus" in text
    assert "Peer-funded bounties are demand-side pull" in text
    assert "CDL-047 treasury governance" in text
    assert "not the funding source for peer-funded bounties" in text


def test_peer_funded_bounty_spec_requires_escrow_finality_and_anti_gaming() -> None:
    text = read(SPEC)

    for needle in (
        "non-custodial escrow by default",
        "no payout before panel finality",
        "no ECU creation without validated productive work",
        "no debt: if escrow or cap is insufficient, the bounty does not proceed",
        "Self-bounty farming",
        "Sybil fund splitting",
        "Escrow spoofing",
        "Funder exit manipulation",
    ):
        assert needle in text


def test_phase_1550p_does_not_add_peer_funded_runtime_and_obl027_runtime_excludes_it() -> None:
    assert not PEER_RUNTIME.exists()

    runtime = read(PRODUCTIVE_RUNTIME)
    assert "PEER_FUNDED_BOUNTIES_EXCLUDED_TOKEN" in runtime
    assert "peer_funded_bounty_excluded=True" in runtime
    assert "productive ecu expansion bounty" in runtime.lower()


def test_phase_1550p_obl029_closed_and_status_records_non_activation() -> None:
    register = read(REGISTER)
    row = next(line for line in register.splitlines() if line.startswith("| OBL-029 |"))
    assert "| closed |" in row
    assert "obl_029_closed_phase_1550p" in row
    assert "ilc_peer_funded_bounty_spec_1550p_v0.1.md" in row
    assert "peer_funded_bounty_runtime_not_activated_phase_1550p" in row
    assert "no_bounty_payout_activation_phase_1550p" in row

    for obl in ("OBL-023", "OBL-024", "OBL-028"):
        other = next(line for line in register.splitlines() if line.startswith(f"| {obl} |"))
        assert "| closed |" in other

    status = read(STATUS)
    assert "## Phase 1550p - OBL-029 Peer-Funded Bounty Spec" in status
    assert "obl_029_peer_funded_bounty_spec_committed_phase_1550p" in status
    assert "No bounty payout activation" in status
