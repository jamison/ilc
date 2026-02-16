from pathlib import Path


CANON_PATH = Path("docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md")
REFERENCE_PATH = Path("docs/reference/ilc_comprehensive_reference_glossary_v0.1.md")
SPEC_PATH = Path("docs/specs/ilc_replay_routing_ops_term_contracts_v0.1.md")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_phase_991_spec_exists_and_scoped_terms_present() -> None:
    text = _read(SPEC_PATH)
    assert "ILC Replay Routing and Operations Term Contracts v0.1" in text
    for term in (
        "Backwards Verifiability",
        "Task Routing Protocol (TRP)",
        "Graph KPIs",
        "Devnet Topology",
        "Staking",
    ):
        assert term in text


def test_phase_991_canonical_glossary_has_contract_section() -> None:
    text = _read(CANON_PATH)
    assert "2.7 Replay, Routing, and Operations Contracts (Phase 991)" in text
    for term in (
        "Backwards Verifiability",
        "Task Routing Protocol (TRP)",
        "Graph KPIs",
        "Devnet Topology",
        "Staking",
    ):
        assert f"**{term}**" in text


def test_phase_991_reference_statuses_promoted_to_active_contract() -> None:
    text = _read(REFERENCE_PATH)
    assert (
        "| **Staking** | Economic collateral posted by agents/operators to align "
        "incentives and absorb penalties. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Backwards Verifiability** | Ability to replay and re-verify state "
        "from earlier history or genesis checkpoints. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Task Routing Protocol (TRP)** | Routing lifecycle for dispatching "
        "workloads/tasks to appropriate execution/verifier paths. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Graph KPIs** | Aggregated graph/network indicators used for "
        "diagnostics, governance tuning, and release gating evidence. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
    assert (
        "| **Devnet Topology** | Explicit peer/agent arrangement used in simulation "
        "and development-network validation. | "
        "**Canonical-adjacent (active contract)** |"
    ) in text
