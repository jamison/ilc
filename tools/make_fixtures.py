#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""
Convenience wrapper for deterministic Cluster A replay-proof fixture generation.
"""

import runpy
from pathlib import Path


if __name__ == "__main__":
    script = Path("tests/fixtures/cluster_a_replay_proof_v0_1/generate_fixtures.py")
    runpy.run_path(str(script), run_name="__main__")
