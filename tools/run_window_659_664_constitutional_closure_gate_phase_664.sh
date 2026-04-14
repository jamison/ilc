#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PATH=.venv/bin:$PATH .venv/bin/pytest \
  tests/test_phase_659_window_659_664_sequence_lock.py \
  tests/test_phase_660_coupling_surface_inventory_and_invariant_matrix.py \
  tests/test_phase_661_coupling_counterexample_and_row_sharpening.py \
  tests/test_phase_662_cdl_065_opening_and_admissibility_matrix.py \
  tests/test_phase_663_cdl_065_ratification_and_row6_closure_candidate.py \
  tests/test_phase_664_window_659_664_closure_and_handoff.py \
  -q
