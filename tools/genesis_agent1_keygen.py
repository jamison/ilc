"""Genesis Agent 1 permanent PQ keypair generator — Phase 838a.

Calls the pq_keygen Rust binary (CDL-069 compliant) and optionally writes
a pubkey-only verification record to cold-storage media (e.g. USB drive).

SECURITY CONTRACT:
  - Secret seed material is printed to stdout ONCE and never written to disk.
  - Use --pubkey-record <path> to write a verification file (public fields only,
    NO secret seeds) to cold-storage media.
  - Before running: `unset HISTFILE` in your terminal session.
  - After running: close the terminal window to clear scrollback.

`genesis_agent1_keygen_838a_published`
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PQ_KEYGEN_BIN_DEFAULT = (
    REPO_ROOT / "ilc_consensus" / "target" / "debug" / "pq_keygen"
)

TOOL_VERSION = "genesis_agent1_keygen_838a.v0.2"

# CDL-042 runtime derivation is used for the legacy BLS agent_id; the new
# PQ agent_id is derived inside the Rust binary via SHA-384(domain || identity_seed).
# We import it here to keep the module importable and satisfy the test contract.
sys.path.insert(0, str(REPO_ROOT))
from ilc_core.identity.agent_id_runtime import derive_agent_id  # noqa: E402


def _derive(pk_hex: str) -> str:
    """Legacy BLS agent_id derivation (CDL-042). Not used for PQ genesis records."""
    return derive_agent_id(bytes.fromhex(pk_hex))


def _run_pq_keygen(
    pq_keygen_bin: Path,
    pubkey_record: Path | None,
) -> subprocess.CompletedProcess[str]:
    """Invoke the pq_keygen Rust binary.  Returns the completed process."""
    if not pq_keygen_bin.exists():
        print(
            f"ERROR: pq_keygen binary not found at {pq_keygen_bin}\n"
            "Build it with: cd ilc_consensus && cargo build --bin pq_keygen",
            file=sys.stderr,
        )
        sys.exit(1)

    cmd: list[str] = [str(pq_keygen_bin)]
    if pubkey_record is not None:
        cmd += ["--pubkey-record", str(pubkey_record)]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(
            f"ERROR: pq_keygen exited {result.returncode}:\n{result.stderr}",
            file=sys.stderr,
        )
        sys.exit(result.returncode)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate the Genesis Agent 1 permanent PQ keypair (run once). "
            "Calls the pq_keygen Rust binary (CDL-069 compliant)."
        ),
    )
    parser.add_argument(
        "--pq-keygen-bin",
        type=Path,
        default=PQ_KEYGEN_BIN_DEFAULT,
        help=(
            "Path to the pq_keygen binary "
            "(default: ilc_consensus/target/debug/pq_keygen)"
        ),
    )
    parser.add_argument(
        "--pubkey-record",
        type=Path,
        default=None,
        help=(
            "Write a verification record (public fields only, NO secret seeds) "
            "to this path.  Safe to write to cold-storage media."
        ),
    )
    args = parser.parse_args()

    result = _run_pq_keygen(args.pq_keygen_bin, args.pubkey_record)

    # Forward the binary's stdout/stderr verbatim.
    sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)


if __name__ == "__main__":
    main()
