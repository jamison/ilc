"""Genesis Agent 1 permanent keypair generator.

Phase 838a — run ONCE to establish the permanent Genesis Agent 1 identity.

SECURITY CONTRACT:
  - The secret key is printed to stdout ONCE and never written to any file by
    this tool.
  - Use --pubkey-record <path> to write a verification file (pk + agent_id
    ONLY, no sk) to cold storage media.
  - Before running: `unset HISTFILE` in your terminal session.
  - After running: close the terminal window to clear scrollback.

`genesis_agent1_keygen_838a_published`
"""
from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KEYGEN_BIN_DEFAULT = REPO_ROOT / "ilc_consensus" / "target" / "debug" / "keygen"

TOOL_VERSION = "genesis_agent1_keygen_838a.v0.1"

# Import CDL-042 derivation directly from the runtime module.
# This guarantees the agent_id produced here matches what the live system uses.
sys.path.insert(0, str(REPO_ROOT))
from ilc_core.identity.agent_id_runtime import derive_agent_id  # noqa: E402


def _run_keygen(keygen_bin: Path) -> tuple[str, str]:
    """Call keygen --print, return (sk_hex, pk_hex). Nothing is written to disk."""
    if not keygen_bin.exists():
        print(
            f"ERROR: keygen binary not found at {keygen_bin}\n"
            "Build it with: cd ilc_consensus && cargo build --bin keygen",
            file=sys.stderr,
        )
        sys.exit(1)

    result = subprocess.run(
        [str(keygen_bin), "--print"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"ERROR: keygen exited {result.returncode}:\n{result.stderr}", file=sys.stderr)
        sys.exit(1)

    sk_hex = ""
    pk_hex = ""
    for line in result.stdout.splitlines():
        line = line.strip()
        if line.startswith("sk="):
            sk_hex = line[3:]
        elif line.startswith("pk="):
            pk_hex = line[3:]

    if len(sk_hex) != 64:
        print(f"ERROR: expected 64-char sk_hex, got {len(sk_hex)!r}", file=sys.stderr)
        sys.exit(1)
    if len(pk_hex) != 96:
        print(f"ERROR: expected 96-char pk_hex, got {len(pk_hex)!r}", file=sys.stderr)
        sys.exit(1)

    return sk_hex, pk_hex


def _derive(pk_hex: str) -> str:
    """Derive agent_id from pk_hex using CDL-042 runtime derivation."""
    return derive_agent_id(bytes.fromhex(pk_hex))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate the Genesis Agent 1 permanent keypair (run once).",
    )
    parser.add_argument(
        "--keygen-bin",
        type=Path,
        default=KEYGEN_BIN_DEFAULT,
        help="Path to the keygen binary (default: ilc_consensus/target/debug/keygen)",
    )
    parser.add_argument(
        "--pubkey-record",
        type=Path,
        default=None,
        help=(
            "Write a verification record (pk + agent_id, NO sk) to this path. "
            "Safe to write to cold-storage media."
        ),
    )
    args = parser.parse_args()

    ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    sk_hex, pk_hex = _run_keygen(args.keygen_bin)
    agent_id = _derive(pk_hex)

    # -----------------------------------------------------------------------
    # Print the full record to stdout — this is the ONE moment the sk appears.
    # -----------------------------------------------------------------------
    print("=" * 72)
    print("  GENESIS AGENT 1 KEYGEN RECORD")
    print(f"  tool:      {TOOL_VERSION}")
    print(f"  timestamp: {ts}")
    print("=" * 72)
    print()
    print(f"  pk_hex:    {pk_hex}")
    print(f"  agent_id:  {agent_id}")
    print()
    print("  WARNING: SECRET KEY — write this down NOW, then close this terminal.")
    print(f"  sk_hex:    {sk_hex}")
    print()
    print("=" * 72)
    print()

    # -----------------------------------------------------------------------
    # Optionally write a pubkey-only verification record to cold storage media.
    # The sk is NOT in this file.
    # -----------------------------------------------------------------------
    if args.pubkey_record is not None:
        record_path = args.pubkey_record
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_text(
            "\n".join([
                "GENESIS AGENT 1 PUBKEY VERIFICATION RECORD",
                f"tool:      {TOOL_VERSION}",
                f"timestamp: {ts}",
                "",
                f"pk_hex:    {pk_hex}",
                f"agent_id:  {agent_id}",
                "",
                "NOTE: Secret key is NOT stored here.",
                "      Verify agent_id by running:",
                "        python3 -c \"",
                "import sys; sys.path.insert(0, '<repo>');",
                "from ilc_core.identity.agent_id_runtime import derive_agent_id;",
                "print(derive_agent_id(bytes.fromhex('<pk_hex>')))",
                "        \"",
                "",
                "genesis_agent1_pubkey_record_838a",
            ]),
            encoding="utf-8",
        )
        print(f"  Pubkey record written to: {record_path}")
        print("  (This file contains pk + agent_id only — no sk.)")
        print()


if __name__ == "__main__":
    main()
