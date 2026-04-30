from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

from ilc_core.types import PROVENANCE_DECAY_ALPHA


ROOT = Path(__file__).resolve().parents[1]
RUN02 = ROOT / "docs/sims/sim_provenance_01/results_phase_1121_run_02.md"
DISPOSITION = ROOT / "docs/sims/sim_provenance_01/alpha_disposition_phase_1121.md"
RUN02_JSON = ROOT / "out/sim_provenance_01_run02_summary.json"


def _run02_payload() -> dict:
    return json.loads(RUN02_JSON.read_text(encoding="utf-8"))


def test_r1_run02_results_exist_with_completion_token() -> None:
    assert RUN02.exists()
    text = RUN02.read_text(encoding="utf-8")
    assert "sim_provenance_01_run_02_complete_phase_1121" in text


def test_r2_run02_contains_exactly_11_alpha_candidates() -> None:
    payload = _run02_payload()
    assert payload["alphas"] == [
        "0.4",
        "0.41",
        "0.42",
        "0.43",
        "0.44",
        "0.45",
        "0.46",
        "0.47",
        "0.48",
        "0.49",
        "0.5",
    ]
    assert len(payload["rows"]) == 11


def test_r3_run02_contains_all_three_seeds_for_each_candidate() -> None:
    payload = _run02_payload()
    for row in payload["rows"]:
        assert [item["seed"] for item in row["seed_results"]] == [42, 1337, 2026]


def test_r4_alpha_disposition_exists() -> None:
    assert DISPOSITION.exists()
    assert "sim_provenance_01_alpha_disposition_phase_1121" in DISPOSITION.read_text(
        encoding="utf-8"
    )


def test_r5_disposition_contains_cdl_084_q2_q8_tokens() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    assert "q2_geometric_decay_alpha_decimal_0_5_provisional" in text
    assert "q8_epoch_mint_source_sim_provenance_01_required" in text


def test_r6_disposition_recommended_alpha_in_sweep_range() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    match = re.search(r"Recommended alpha: `(?P<alpha>0\.[0-9]+)`", text)
    assert match is not None
    alpha = Decimal(match.group("alpha"))
    assert Decimal("0.40") <= alpha <= Decimal("0.50")


def test_r7_production_alpha_remains_decimal_0_5() -> None:
    assert isinstance(PROVENANCE_DECAY_ALPHA, Decimal)
    assert PROVENANCE_DECAY_ALPHA == Decimal("0.5")


def test_r8_disposition_states_alpha_remains_provisional_and_no_cdl_mutation() -> None:
    text = DISPOSITION.read_text(encoding="utf-8")
    assert "will remain provisional" in text
    assert "No CDL mutation is authorized in Window 1118–1123" in text


def test_r9_alpha_0_50_is_seed_marginal_while_0_45_is_recommended() -> None:
    payload = _run02_payload()
    rows = {row["alpha"]: row for row in payload["rows"]}
    assert rows["0.5"]["keep_count"] == 2
    assert rows["0.45"]["keep_count"] == 3
    assert "SIM recommendation: alpha = 0.45" in DISPOSITION.read_text(encoding="utf-8")


def test_r10_run02_results_explicitly_use_q2_q8_not_q9() -> None:
    text = RUN02.read_text(encoding="utf-8") + DISPOSITION.read_text(encoding="utf-8")
    assert "q2_geometric_decay_alpha_decimal_0_5_provisional" in text
    assert "q8_epoch_mint_source_sim_provenance_01_required" in text
    assert "Q9" not in text
