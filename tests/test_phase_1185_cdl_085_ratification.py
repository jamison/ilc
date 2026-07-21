import subprocess
from decimal import Decimal
from pathlib import Path


CDL_REGISTER = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")
RATIFICATION_EVIDENCE = Path(
    "docs/specs/ilc_cdl_085_ratification_evidence_1185_v0.1.md"
)


def test_cdl_085_ratified_in_register() -> None:
    content = CDL_REGISTER.read_text(encoding="utf-8")
    assert "cdl_085_ratified_phase_1185" in content
    assert "ratified_phase: 1185" in content


def test_ratification_evidence_exists() -> None:
    assert RATIFICATION_EVIDENCE.exists()


def test_ratification_evidence_token() -> None:
    content = RATIFICATION_EVIDENCE.read_text(encoding="utf-8")
    assert "cdl_085_ratified_phase_1185" in content
    assert 'EDGE_MINT_PHI_BOUND = Decimal("0.60")' in content


def test_phi_bound_is_decimal() -> None:
    from ilc_core.types import EDGE_MINT_PHI_BOUND

    assert isinstance(EDGE_MINT_PHI_BOUND, Decimal)
    assert EDGE_MINT_PHI_BOUND == Decimal("0.60")


def test_cdl_085_dependency_token() -> None:
    import ilc_core.economics.epoch_attribution_settle_runtime as rt

    assert rt.CDL_085_DEPENDENCY == "cdl_085_werner_phi_bound_ratified_1185.v0.1"


def test_runtime_version_updated() -> None:
    import ilc_core.economics.epoch_attribution_settle_runtime as rt

    assert rt.EPOCH_ATTRIBUTION_SETTLE_RUNTIME_VERSION == (
        "epoch_attribution_settle_runtime_GAP_CDL060.v0.8"
    )


def test_runtime_imports_phi_bound() -> None:
    import ilc_core.economics.epoch_attribution_settle_runtime as rt

    assert rt.EDGE_MINT_PHI_BOUND == Decimal("0.60")


def test_phi_bound_runtime_suppresses_excess_provenance_ecu() -> None:
    from ilc_core.economics.epoch_attribution_settle_runtime import (
        AttributionEvent,
        settle_attribution_batch,
    )
    from ilc_core.types import EdgeType, EpochAttributionBatch

    batch = EpochAttributionBatch(epoch=1)
    for index in range(1, 5):
        batch.add_event(
            AttributionEvent(
                edge_type=EdgeType.PROVENANCE,
                target_creator_id="unused_target_creator",
                star_node_id=None,
                epoch=1,
                provenance_chain=((f"node_{index}", f"creator_{index}"),),
            )
        )
    batch.seal()
    emitted_tokens: list[str] = []

    payouts = settle_attribution_batch(
        batch,
        stake_map={},
        emitted_tokens=emitted_tokens,
        epoch_node_mint_count=5,
    )

    assert ("creator_4", Decimal("0")) not in payouts
    assert payouts[-1] == ("creator_3", Decimal("0.090000000"))
    assert "edge_mint_phi_bound_exceeded" in emitted_tokens


def test_cdl_085_prelock_historical() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "509b6c6f:docs/specs/ilc_cdl_085_prelock_spec_1177_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "cdl_085_prelock_committed_phase_1177" in result.stdout


def test_cdl_085_opening_historical() -> None:
    result = subprocess.run(
        [
            "git",
            "show",
            "ee0f6b48:docs/specs/ilc_cdl_085_werner_phi_bound_opening_1172_v0.1.md",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "cdl_085_open_phase_1172" in result.stdout
