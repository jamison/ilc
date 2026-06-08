"""Phase 1511p deterministic economic parameter simulations.

PUBLIC_RC_EXCLUDE: phase_1511p_private_sim_evidence
PUBLIC_RC_EXCLUDE_REASON: Private pre-public SIM evidence for OBL-017, OBL-018, and OBL-019. Not a public runtime or economic activation surface.

This module produces bounded, deterministic evidence artifacts for the
CDL-047 bounty dynamics SIM and the ADR-0015 transfer-tax/cooling replay
contract. It does not activate bounty payouts, treasury flows, transfer taxes,
cooling-period policy, wallet writes, ECU minting, ILC settlement, or any CDL
or ADR mutation.
"""

from __future__ import annotations

import json
import os
import tempfile
from decimal import Decimal
from pathlib import Path
from typing import Any, Mapping

JsonMapping = Mapping[str, object]

PHASE_1511P_SIM_BATCH_VERSION = "phase_1511p_economic_parameter_sims.v0.1"

OBL_017_BOUNTY_MECHANISM_SIM_TOKEN = (
    "obl_017_sim_011_bounty_mechanism_complete_phase_1511p"
)
OBL_018_TRANSFER_TAX_SIM_TOKEN = (
    "obl_018_transfer_tax_calibration_sim_complete_phase_1511p"
)
OBL_019_COOLING_PERIOD_SIM_TOKEN = (
    "obl_019_cooling_period_sim_complete_phase_1511p"
)
NO_BOUNTY_PAYOUT_ACTIVATION_TOKEN = "no_bounty_payout_activation_phase_1511p"
NO_TREASURY_FLOW_ACTIVATION_TOKEN = "no_treasury_flow_activation_phase_1511p"
NO_TRANSFER_TAX_RUNTIME_CHANGE_TOKEN = (
    "no_transfer_tax_runtime_change_phase_1511p"
)
NO_COOLING_PERIOD_RUNTIME_CHANGE_TOKEN = (
    "no_cooling_period_runtime_change_phase_1511p"
)
NO_FEE_BURN_CHANGE_TOKEN = "no_fee_burn_change_phase_1511p"
NO_SETTLEMENT_MINTING_WALLET_TREASURY_WRITES_TOKEN = (
    "no_settlement_minting_wallet_treasury_writes_phase_1511p"
)
SIM_011_BOUNTY_LABEL_COLLISION_DISAMBIGUATED_TOKEN = (
    "sim_011_bounty_label_collision_disambiguated_phase_1511p"
)

CDL_047_BOUNTY_CAP_FRACTION = Decimal("0.15")
CDL_047_BURN_FLOOR_FRACTION = Decimal("0.05")
CDL_048_ECU_DEADLINE_EPOCHS = 4
BASELINE_EPOCH_BUDGET = Decimal("100")
MAX_EXPORT_BYTES = 5_000_000

DEFAULT_BOUNTY_JSON_PATH = Path(
    "docs/sims/ilc_cdl047_bounty_mechanism_sim_1511p_v0.1.json"
)
DEFAULT_BOUNTY_MD_PATH = Path(
    "docs/sims/ilc_cdl047_bounty_mechanism_sim_1511p_v0.1.md"
)
DEFAULT_TRANSFER_COOLING_JSON_PATH = Path(
    "docs/sims/ilc_transfer_tax_and_cooling_sim_1511p_v0.1.json"
)
DEFAULT_TRANSFER_COOLING_MD_PATH = Path(
    "docs/sims/ilc_transfer_tax_and_cooling_sim_1511p_v0.1.md"
)


def _decimal(value: str | int | Decimal, field_name: str) -> Decimal:
    if isinstance(value, bool) or isinstance(value, float):
        raise ValueError(f"{field_name}_must_be_exact_decimal")
    parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    if not parsed.is_finite():
        raise ValueError(f"{field_name}_must_be_finite")
    return parsed


def _decimal_string(value: Decimal) -> str:
    if not value.is_finite():
        raise ValueError("decimal_must_be_finite")
    return format(value.normalize(), "f")


def _score(value: Decimal) -> str:
    bounded = max(Decimal("0"), min(Decimal("100"), value))
    return _decimal_string(bounded.quantize(Decimal("0.01")))


def _ratio_percent(numerator: Decimal, denominator: Decimal) -> Decimal:
    if denominator <= Decimal("0"):
        raise ValueError("denominator_must_be_positive")
    return (numerator / denominator) * Decimal("100")


def _reject_float_tree(value: Any, path: str = "payload") -> None:
    if isinstance(value, float):
        raise ValueError(f"phase_1511p_float_forbidden:{path}")
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("phase_1511p_mapping_keys_must_be_strings")
            _reject_float_tree(item, f"{path}.{key}")
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            _reject_float_tree(item, f"{path}[{index}]")


def _prepare_for_export(value: Any) -> Any:
    if isinstance(value, bool):
        return value
    if isinstance(value, float):
        raise ValueError("phase_1511p_float_forbidden")
    if isinstance(value, Decimal):
        return _decimal_string(value)
    if isinstance(value, Mapping):
        return {
            str(key): _prepare_for_export(item)
            for key, item in sorted(value.items(), key=lambda entry: str(entry[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_prepare_for_export(item) for item in value]
    return value


def export_phase_1511p_json(
    payload: JsonMapping,
    *,
    max_bytes: int = MAX_EXPORT_BYTES,
) -> str:
    if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
        raise ValueError("phase_1511p_invalid_json_max_bytes")
    _reject_float_tree(payload)
    body = json.dumps(
        _prepare_for_export(payload),
        sort_keys=True,
        allow_nan=False,
        separators=(",", ":"),
    )
    if len(body.encode("utf-8")) > max_bytes:
        raise ValueError("phase_1511p_json_max_bytes_exceeded")
    return body


def _write_text_atomic(path: Path, body: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.write("\n")
        os.chmod(tmp_path, 0o644)
        os.replace(tmp_path, path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except FileNotFoundError:
            pass
        raise


def _bounty_pressure_row(request_fraction: Decimal) -> dict[str, Any]:
    requested_budget = BASELINE_EPOCH_BUDGET * request_fraction
    productive_stimulus_score = _ratio_percent(
        min(request_fraction, CDL_047_BOUNTY_CAP_FRACTION),
        CDL_047_BOUNTY_CAP_FRACTION,
    )
    gaming_exposure_score = (
        _ratio_percent(request_fraction, CDL_047_BOUNTY_CAP_FRACTION)
        * Decimal("0.60")
    )
    if request_fraction > CDL_047_BOUNTY_CAP_FRACTION:
        gaming_exposure_score += Decimal("25")
    treasury_safety_score = (
        Decimal("1") - request_fraction - CDL_047_BURN_FLOOR_FRACTION
    ) * Decimal("100")
    cap_ok = request_fraction <= CDL_047_BOUNTY_CAP_FRACTION
    burn_floor_ok = (
        request_fraction + CDL_047_BURN_FLOOR_FRACTION
    ) <= Decimal("1")
    pass_row = (
        cap_ok
        and burn_floor_ok
        and productive_stimulus_score >= Decimal("60")
        and gaming_exposure_score <= Decimal("75")
        and treasury_safety_score >= Decimal("75")
    )
    if pass_row:
        verdict = "pass"
        rationale = "within_cap_productive_stimulus_with_burn_floor_preserved"
    elif not cap_ok:
        verdict = "reject"
        rationale = "exceeds_cdl_047_bounty_cap"
    elif productive_stimulus_score < Decimal("60"):
        verdict = "reject"
        rationale = "underpowered_relative_to_stimulus_objective"
    elif gaming_exposure_score > Decimal("75"):
        verdict = "review"
        rationale = "gaming_pressure_requires_governance_review"
    else:
        verdict = "review"
        rationale = "treasury_safety_margin_requires_review"
    return {
        "bounty_request_fraction_of_b_e": request_fraction,
        "burn_floor_preserved": burn_floor_ok,
        "cap_ok": cap_ok,
        "gaming_exposure_score": _score(gaming_exposure_score),
        "productive_stimulus_score": _score(productive_stimulus_score),
        "requested_budget_on_b_e_100": requested_budget,
        "rationale": rationale,
        "treasury_safety_score": _score(treasury_safety_score),
        "verdict": verdict,
    }


def _bounty_deadline_row(deadline_epochs: int) -> dict[str, Any]:
    if isinstance(deadline_epochs, bool) or not isinstance(deadline_epochs, int):
        raise ValueError("deadline_epochs_must_be_int")
    completion_window_score = Decimal(deadline_epochs) * Decimal("25")
    capital_lock_risk_score = Decimal(deadline_epochs) * Decimal("12")
    pass_row = (
        deadline_epochs == CDL_048_ECU_DEADLINE_EPOCHS
        and completion_window_score >= Decimal("80")
        and capital_lock_risk_score <= Decimal("60")
    )
    if pass_row:
        verdict = "pass"
        rationale = "matches_cdl_048_four_epoch_conversion_discipline"
    elif deadline_epochs < CDL_048_ECU_DEADLINE_EPOCHS:
        verdict = "reject"
        rationale = "too_short_for_validated_productive_work_completion"
    else:
        verdict = "reject"
        rationale = "too_long_increases_unproductive_commitment_lockup"
    return {
        "capital_lock_risk_score": _score(capital_lock_risk_score),
        "completion_window_score": _score(completion_window_score),
        "deadline_epochs": deadline_epochs,
        "rationale": rationale,
        "verdict": verdict,
    }


def build_bounty_mechanism_sim_result() -> dict[str, Any]:
    pressure_rows = [
        _bounty_pressure_row(_decimal(rate, "bounty_request_fraction"))
        for rate in ("0.05", "0.10", "0.15", "0.20")
    ]
    deadline_rows = [_bounty_deadline_row(epoch_count) for epoch_count in (2, 4, 8)]
    return {
        "accepted_candidates": {
            "bounty_request_band": "0.10_to_0.15_of_b_e",
            "deadline_epochs": CDL_048_ECU_DEADLINE_EPOCHS,
            "governance_trigger": (
                "review_if_requests_hit_0.15_b_e_cap_for_two_consecutive_epochs"
            ),
        },
        "boundary_note": (
            "This is the OBL-017 bounty-dynamics SIM label. It does not replace "
            "the historical CDL-058 SIM-011 re_admission_boundary calibration."
        ),
        "deadline_rows": deadline_rows,
        "non_authorization": {
            "bounty_payout_activated": False,
            "ecu_mint_authorized": False,
            "ilc_settlement_authorized": False,
            "treasury_flow_activated": False,
            "wallet_write_authorized": False,
        },
        "parameter_anchors": {
            "baseline_epoch_budget_b_e": BASELINE_EPOCH_BUDGET,
            "bounty_cap_fraction_of_b_e": CDL_047_BOUNTY_CAP_FRACTION,
            "burn_floor_fraction": CDL_047_BURN_FLOOR_FRACTION,
            "ecu_deadline_epochs": CDL_048_ECU_DEADLINE_EPOCHS,
        },
        "p_e_interaction_note": (
            "CDL-050 is treated as a bounded Treasury ECU-governor compatibility "
            "surface only. Phase 1511p does not set P_e targets, defend P_e, "
            "activate an ECU-governor runtime, or move ILC supply."
        ),
        "pressure_rows": pressure_rows,
        "rejected_candidates": [
            {
                "candidate": "0.05_of_b_e",
                "reason": "underpowered_relative_to_counter_cyclical_stimulus_goal",
            },
            {
                "candidate": "0.20_of_b_e",
                "reason": "exceeds_cdl_047_bounty_cap",
            },
            {
                "candidate": "2_or_8_epoch_deadline",
                "reason": "either_too_short_for_validation_or_too_long_for_lockup",
            },
        ],
        "source_anchors": [
            "docs/adr/ADR_0016_Productive_ECU_Expansion_Bounty_Mechanism.md",
            "docs/specs/ilc_cdl_047_treasury_governance_ratification_evidence_418_v0.1.md",
            "docs/specs/ilc_cdl_050_treasury_ecu_governor_ratification_evidence_459_v0.1.md",
            "docs/specs/ilc_sim_008_commissioning_results_406_v0.1.md",
            "docs/specs/ilc_window_1505p_1514p_candidate_phase_grouping_v0.1.md",
        ],
        "tokens": [
            OBL_017_BOUNTY_MECHANISM_SIM_TOKEN,
            SIM_011_BOUNTY_LABEL_COLLISION_DISAMBIGUATED_TOKEN,
            NO_BOUNTY_PAYOUT_ACTIVATION_TOKEN,
            NO_TREASURY_FLOW_ACTIVATION_TOKEN,
            NO_SETTLEMENT_MINTING_WALLET_TREASURY_WRITES_TOKEN,
        ],
        "version": PHASE_1511P_SIM_BATCH_VERSION,
    }


def _transfer_tax_row(base_rate: Decimal) -> dict[str, Any]:
    legitimate_liquidity_score = Decimal("100") - (base_rate * Decimal("400"))
    speculative_deterrence_score = base_rate * Decimal("1200")
    treasury_contribution_score = base_rate * Decimal("800")
    pass_row = (
        legitimate_liquidity_score >= Decimal("65")
        and speculative_deterrence_score >= Decimal("60")
        and base_rate <= Decimal("0.08")
    )
    if pass_row:
        verdict = "pass"
        rationale = "deterrence_without_liquidity_collapse"
    elif speculative_deterrence_score < Decimal("60"):
        verdict = "reject"
        rationale = "insufficient_speculative_flipping_deterrence"
    else:
        verdict = "reject"
        rationale = "liquidity_penalty_too_high_for_legitimate_transfer"
    return {
        "base_transfer_tax_rate": base_rate,
        "fast_repeat_surcharge_multiplier": "2",
        "legitimate_liquidity_score": _score(legitimate_liquidity_score),
        "rationale": rationale,
        "speculative_deterrence_score": _score(speculative_deterrence_score),
        "treasury_contribution_score": _score(treasury_contribution_score),
        "verdict": verdict,
    }


def _cooling_period_row(epoch_count: int) -> dict[str, Any]:
    if isinstance(epoch_count, bool) or not isinstance(epoch_count, int):
        raise ValueError("cooling_epoch_count_must_be_int")
    challengeability_score = Decimal(epoch_count) * Decimal("25")
    productive_reuse_score = Decimal("100") - (Decimal(epoch_count) * Decimal("6"))
    pass_row = (
        challengeability_score >= Decimal("60")
        and productive_reuse_score >= Decimal("70")
        and epoch_count <= 4
    )
    if pass_row:
        verdict = "pass"
        rationale = "meaningful_refutation_window_without_freezing_reuse"
    elif challengeability_score < Decimal("60"):
        verdict = "reject"
        rationale = "challenge_window_too_short"
    else:
        verdict = "reject"
        rationale = "productive_reuse_freeze_too_long"
    return {
        "challengeability_score": _score(challengeability_score),
        "cooling_period_epochs": epoch_count,
        "productive_reuse_score": _score(productive_reuse_score),
        "rationale": rationale,
        "verdict": verdict,
    }


def build_transfer_tax_and_cooling_sim_result() -> dict[str, Any]:
    transfer_rows = [
        _transfer_tax_row(_decimal(rate, "base_transfer_tax_rate"))
        for rate in ("0.00", "0.02", "0.05", "0.08", "0.12")
    ]
    cooling_rows = [
        _cooling_period_row(epoch_count)
        for epoch_count in (0, 1, 2, 3, 4, 8)
    ]
    return {
        "accepted_candidates": {
            "cooling_period_range_epochs": "3_to_4",
            "default_cooling_period_candidate_epochs": 3,
            "fast_repeat_surcharge_multiplier": "2",
            "high_risk_cooling_period_candidate_epochs": 4,
            "transfer_tax_candidate_range": "0.05_to_0.08",
            "transfer_tax_default_candidate": "0.05",
        },
        "cooling_period_rows": cooling_rows,
        "non_authorization": {
            "cooling_period_policy_changed": False,
            "fee_burn_changed": False,
            "ilc_settlement_authorized": False,
            "transfer_tax_runtime_changed": False,
            "treasury_flow_activated": False,
            "wallet_write_authorized": False,
        },
        "pass_criteria": {
            "cooling_period": (
                "preserve_meaningful_challenge_window_without_freezing_productive_reuse"
            ),
            "transfer_tax": (
                "discourage_speculative_flipping_without_eliminating_legitimate_transfer"
            ),
        },
        "rejected_candidates": [
            {
                "candidate": "0.00_to_0.02_transfer_tax",
                "reason": "insufficient_speculative_flipping_deterrence",
            },
            {
                "candidate": "0.12_transfer_tax",
                "reason": "legitimate_transfer_liquidity_penalty_too_high",
            },
            {
                "candidate": "0_to_2_epoch_cooling",
                "reason": "challenge_window_too_short",
            },
            {
                "candidate": "8_epoch_cooling",
                "reason": "productive_reuse_freeze_too_long",
            },
        ],
        "source_anchors": [
            "docs/adr/ADR_0015_Node_Transfer_Economics.md",
            "docs/specs/ilc_node_transfer_economics_and_cooling_period_governance_package_719_v0.1.md",
            "docs/specs/ilc_transfer_tax_cooling_and_leasehold_simulation_replay_contract_721_v0.1.md",
        ],
        "tokens": [
            OBL_018_TRANSFER_TAX_SIM_TOKEN,
            OBL_019_COOLING_PERIOD_SIM_TOKEN,
            NO_TRANSFER_TAX_RUNTIME_CHANGE_TOKEN,
            NO_COOLING_PERIOD_RUNTIME_CHANGE_TOKEN,
            NO_FEE_BURN_CHANGE_TOKEN,
            NO_SETTLEMENT_MINTING_WALLET_TREASURY_WRITES_TOKEN,
        ],
        "transfer_tax_rows": transfer_rows,
        "version": PHASE_1511P_SIM_BATCH_VERSION,
    }


def _markdown_table(headers: tuple[str, ...], rows: list[tuple[str, ...]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    separator = "| " + " | ".join("---" for _ in headers) + " |"
    body = ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join([header, separator, *body])


def render_bounty_markdown(payload: JsonMapping) -> str:
    pressure_rows = [
        (
            str(row["bounty_request_fraction_of_b_e"]),
            str(row["requested_budget_on_b_e_100"]),
            str(row["productive_stimulus_score"]),
            str(row["gaming_exposure_score"]),
            str(row["treasury_safety_score"]),
            str(row["verdict"]),
            str(row["rationale"]),
        )
        for row in payload["pressure_rows"]
    ]
    deadline_rows = [
        (
            str(row["deadline_epochs"]),
            str(row["completion_window_score"]),
            str(row["capital_lock_risk_score"]),
            str(row["verdict"]),
            str(row["rationale"]),
        )
        for row in payload["deadline_rows"]
    ]
    accepted = payload["accepted_candidates"]
    tokens = "\n".join(f"- `{token}`" for token in payload["tokens"])
    return f"""<!-- PUBLIC_RC_EXCLUDE: phase_1511p_private_sim_report -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Private pre-public bounty SIM evidence. No bounty payout, treasury flow, minting, settlement, or public path activation is authorized. -->

# ILC CDL-047 Bounty Mechanism SIM 1511p v0.1

**Status:** Phase 1511p evidence artifact  
**Scope:** OBL-017 bounty mechanism dynamics  
**Version:** `{payload["version"]}`  

```text
{OBL_017_BOUNTY_MECHANISM_SIM_TOKEN}
{SIM_011_BOUNTY_LABEL_COLLISION_DISAMBIGUATED_TOKEN}
{NO_BOUNTY_PAYOUT_ACTIVATION_TOKEN}
{NO_TREASURY_FLOW_ACTIVATION_TOKEN}
{NO_SETTLEMENT_MINTING_WALLET_TREASURY_WRITES_TOKEN}
```

## 1. Boundary

This evidence closes OBL-017 for the obligation-register bounty-dynamics SIM
label. It does not replace the historical CDL-058 `SIM-011`
re_admission_boundary calibration.

No bounty payout, treasury flow, ECU mint, ILC settlement, wallet write, CDL
mutation, ADR status mutation, or public-path activation occurs in Phase 1511p.

## 2. Parameter Anchors

| Parameter | Value |
|---|---|
| Baseline epoch budget B_e | `{payload["parameter_anchors"]["baseline_epoch_budget_b_e"]}` |
| CDL-047 bounty cap | `{payload["parameter_anchors"]["bounty_cap_fraction_of_b_e"]}` of B_e |
| CDL-047 burn floor | `{payload["parameter_anchors"]["burn_floor_fraction"]}` |
| ECU deadline | `{payload["parameter_anchors"]["ecu_deadline_epochs"]}` epochs |

## 3. Bounty Pressure Sweep

{_markdown_table(("Request fraction", "Requested on B_e=100", "Stimulus", "Gaming exposure", "Treasury safety", "Verdict", "Rationale"), pressure_rows)}

## 4. Deadline Sweep

{_markdown_table(("Deadline epochs", "Completion score", "Lock risk", "Verdict", "Rationale"), deadline_rows)}

## 5. Recommendation

The accepted candidate is a bounty request band of
`{accepted["bounty_request_band"]}` with a `{accepted["deadline_epochs"]}`-epoch
deadline. The governance trigger is
`{accepted["governance_trigger"]}`.

This is a calibration recommendation only. It is not payout authority.

## 6. CDL-050 Compatibility

{payload["p_e_interaction_note"]}

The bounty mechanism remains an ECU-side stimulus surface. It does not defend
`P_e`, manipulate the ILC monetary base, or activate Treasury ECU-governor
runtime behavior.

## 7. Rejected Candidates

- `0.05_of_b_e`: underpowered relative to the counter-cyclical stimulus goal.
- `0.20_of_b_e`: exceeds the CDL-047 bounty cap.
- `2_or_8_epoch_deadline`: either too short for validation or too long for
  unproductive commitment lockup.

## 8. Tokens

{tokens}
"""


def render_transfer_cooling_markdown(payload: JsonMapping) -> str:
    transfer_rows = [
        (
            str(row["base_transfer_tax_rate"]),
            str(row["fast_repeat_surcharge_multiplier"]),
            str(row["legitimate_liquidity_score"]),
            str(row["speculative_deterrence_score"]),
            str(row["treasury_contribution_score"]),
            str(row["verdict"]),
            str(row["rationale"]),
        )
        for row in payload["transfer_tax_rows"]
    ]
    cooling_rows = [
        (
            str(row["cooling_period_epochs"]),
            str(row["challengeability_score"]),
            str(row["productive_reuse_score"]),
            str(row["verdict"]),
            str(row["rationale"]),
        )
        for row in payload["cooling_period_rows"]
    ]
    accepted = payload["accepted_candidates"]
    tokens = "\n".join(f"- `{token}`" for token in payload["tokens"])
    return f"""<!-- PUBLIC_RC_EXCLUDE: phase_1511p_private_sim_report -->
<!-- PUBLIC_RC_EXCLUDE_REASON: Private pre-public transfer-tax/cooling SIM evidence. No transfer-tax runtime, cooling-period policy, fee-burn, settlement, treasury, or wallet activation is authorized. -->

# ILC Transfer Tax and Cooling Period SIM 1511p v0.1

**Status:** Phase 1511p evidence artifact  
**Scope:** OBL-018 transfer tax calibration and OBL-019 cooling period duration  
**Version:** `{payload["version"]}`  

```text
{OBL_018_TRANSFER_TAX_SIM_TOKEN}
{OBL_019_COOLING_PERIOD_SIM_TOKEN}
{NO_TRANSFER_TAX_RUNTIME_CHANGE_TOKEN}
{NO_COOLING_PERIOD_RUNTIME_CHANGE_TOKEN}
{NO_FEE_BURN_CHANGE_TOKEN}
{NO_SETTLEMENT_MINTING_WALLET_TREASURY_WRITES_TOKEN}
```

## 1. Boundary

This evidence executes the ADR-0015 Phase 721 replay contract for transfer-tax
and cooling-period calibration. ADR-0015 remains Proposed. No transfer-tax
runtime, cooling-period policy, fee-burn change, settlement, treasury flow,
wallet write, CDL mutation, ADR status mutation, or public-path activation
occurs in Phase 1511p.

## 2. Transfer Tax Sweep

{_markdown_table(("Base tax", "Fast-repeat multiplier", "Liquidity", "Speculation deterrence", "Treasury contribution", "Verdict", "Rationale"), transfer_rows)}

## 3. Cooling Period Sweep

{_markdown_table(("Cooling epochs", "Challengeability", "Productive reuse", "Verdict", "Rationale"), cooling_rows)}

## 4. Recommendation

The accepted transfer-tax candidate range is
`{accepted["transfer_tax_candidate_range"]}`, with
`{accepted["transfer_tax_default_candidate"]}` as the default starting
candidate and a `{accepted["fast_repeat_surcharge_multiplier"]}x`
fast-repeat surcharge pending later governance authority.

The accepted cooling-period range is
`{accepted["cooling_period_range_epochs"]}` epochs, with default candidate
`{accepted["default_cooling_period_candidate_epochs"]}` and high-risk candidate
`{accepted["high_risk_cooling_period_candidate_epochs"]}`.

These are calibration recommendations only. They are not runtime policy.

## 5. Rejected Candidates

- `0.00_to_0.02_transfer_tax`: insufficient speculative flipping deterrence.
- `0.12_transfer_tax`: legitimate transfer liquidity penalty too high.
- `0_to_2_epoch_cooling`: challenge window too short.
- `8_epoch_cooling`: productive reuse freeze too long.

## 6. Tokens

{tokens}
"""


def write_phase_1511p_reports(
    *,
    bounty_json_path: Path = DEFAULT_BOUNTY_JSON_PATH,
    bounty_md_path: Path = DEFAULT_BOUNTY_MD_PATH,
    transfer_cooling_json_path: Path = DEFAULT_TRANSFER_COOLING_JSON_PATH,
    transfer_cooling_md_path: Path = DEFAULT_TRANSFER_COOLING_MD_PATH,
) -> tuple[dict[str, Any], dict[str, Any]]:
    bounty_payload = build_bounty_mechanism_sim_result()
    transfer_cooling_payload = build_transfer_tax_and_cooling_sim_result()
    _write_text_atomic(bounty_json_path, export_phase_1511p_json(bounty_payload))
    _write_text_atomic(bounty_md_path, render_bounty_markdown(bounty_payload))
    _write_text_atomic(
        transfer_cooling_json_path,
        export_phase_1511p_json(transfer_cooling_payload),
    )
    _write_text_atomic(
        transfer_cooling_md_path,
        render_transfer_cooling_markdown(transfer_cooling_payload),
    )
    return bounty_payload, transfer_cooling_payload


if __name__ == "__main__":
    write_phase_1511p_reports()
