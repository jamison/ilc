#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ilc_core.testing.ratification_mutation_scope_guardrail import (  # noqa: E402
    parse_decision_register_rows,
)


DECISION_LOG_PATH = Path("docs/specs/ilc_constitutional_decision_log_v0.1.md")

EXPECTED_RATIFIED_STATE = {
    "CDL-029": {"status": "ratified", "ratified_phase": "272"},
    "CDL-026": {"status": "ratified", "ratified_phase": "273"},
    "CDL-028": {"status": "ratified", "ratified_phase": "274"},
    "CDL-027": {"status": "ratified", "ratified_phase": "276"},
    "CDL-030": {"status": "ratified", "ratified_phase": "277"},
}


def _raise_mismatch(cdl_id: str, field: str, expected: str, actual: str) -> None:
    raise SystemExit(
        "phase_279_cdl_state_mismatch: "
        f"{cdl_id}.{field} expected={expected!r} actual={actual!r}"
    )


def main() -> None:
    text = DECISION_LOG_PATH.read_text(encoding="utf-8")
    rows = parse_decision_register_rows(text)

    for cdl_id, expected_fields in EXPECTED_RATIFIED_STATE.items():
        row = rows.get(cdl_id)
        if row is None:
            raise SystemExit(f"phase_279_missing_cdl_row: {cdl_id}")

        for field_name, expected_value in expected_fields.items():
            actual_value = row.get(field_name, "")
            if actual_value != expected_value:
                _raise_mismatch(
                    cdl_id=cdl_id,
                    field=field_name,
                    expected=expected_value,
                    actual=actual_value,
                )

    print("Phase 279 ratified-state check: PASS")


if __name__ == "__main__":
    main()
