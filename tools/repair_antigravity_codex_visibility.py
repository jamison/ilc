#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sqlite3
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


TARGET_THREAD_ID = "645d5cf6-9879-47e0-a888-0ce0b0788fc5"
TARGET_TITLE = "Fix Codex chat rollback (UI recovery tail Apr24)"
WORKSPACE_ID = "ece88db77be2ba340baaffeeab4e1e74"
ILC_CWD = "/Users/jamison/Documents/ILC_Main/01_Current"


def stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def log(message: str) -> None:
    print(f"{datetime.now(timezone.utc).isoformat(timespec='seconds')} {message}", flush=True)


def antigravity_running() -> bool:
    proc = subprocess.run(
        ["pgrep", "-f", "/Applications/Antigravity IDE.app/Contents/MacOS/Electron"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    return proc.returncode == 0


def wait_for_antigravity_closed(timeout_s: int) -> None:
    deadline = time.monotonic() + timeout_s
    if not antigravity_running():
        log("Antigravity IDE is already closed.")
        return
    log("Waiting for Antigravity IDE to close. Please quit it now.")
    while time.monotonic() < deadline:
        if not antigravity_running():
            log("Antigravity IDE is closed.")
            return
        time.sleep(2)
    raise SystemExit("Timed out waiting for Antigravity IDE to close; no changes made.")


def copy_sqlite_family(path: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    for suffix in ("", "-wal", "-shm"):
        src = Path(str(path) + suffix)
        if src.exists():
            dst = backup_dir / (path.name + suffix)
            shutil.copy2(src, dst)


def backup_inputs(codex_home: Path, antigravity_root: Path, backup_dir: Path) -> None:
    backup_dir.mkdir(parents=True, exist_ok=True)
    copy_sqlite_family(codex_home / "state_5.sqlite", backup_dir)
    copy_sqlite_family(codex_home / "thread_history_1.sqlite", backup_dir)
    session_index = codex_home / "session_index.jsonl"
    if session_index.exists():
        shutil.copy2(session_index, backup_dir / "session_index.jsonl")
    workspace_db = (
        antigravity_root
        / "User"
        / "workspaceStorage"
        / WORKSPACE_ID
        / "state.vscdb"
    )
    copy_sqlite_family(workspace_db, backup_dir)
    global_db = antigravity_root / "User" / "globalStorage" / "state.vscdb"
    copy_sqlite_family(global_db, backup_dir / "globalStorage")


def sqlite_exec(path: Path, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
    with sqlite3.connect(path) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(sql, params).fetchall()
        con.commit()
        return rows


def rebuild_session_index(codex_home: Path) -> list[dict[str, str]]:
    state_db = codex_home / "state_5.sqlite"
    rows = sqlite_exec(
        state_db,
        """
        SELECT id,
               COALESCE(NULLIF(name, ''), NULLIF(title, ''), NULLIF(preview, ''), id) AS thread_name,
               COALESCE(NULLIF(updated_at_ms, 0), updated_at * 1000) AS updated_at_ms
        FROM threads
        WHERE archived = 0
          AND cwd = ?
          AND rollout_path IS NOT NULL
        ORDER BY updated_at_ms DESC
        """,
        (ILC_CWD,),
    )
    entries: list[dict[str, str]] = []
    for row in rows:
        updated_at = (
            datetime.fromtimestamp(int(row["updated_at_ms"]) / 1000, tz=timezone.utc)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z")
        )
        entries.append(
            {
                "id": row["id"],
                "thread_name": row["thread_name"],
                "updated_at": updated_at,
            }
        )
    content = "".join(json.dumps(item, separators=(",", ":")) + "\n" for item in entries)
    (codex_home / "session_index.jsonl").write_text(content, encoding="utf-8")
    return entries


def repair_state(codex_home: Path, antigravity_root: Path) -> dict[str, object]:
    state_db = codex_home / "state_5.sqlite"
    before = sqlite_exec(
        state_db,
        "SELECT id, title, name, is_pinned, thread_section_id, archived, cwd FROM threads WHERE id = ?",
        (TARGET_THREAD_ID,),
    )
    if not before:
        raise SystemExit(f"Target thread missing from state DB: {TARGET_THREAD_ID}")
    row = before[0]
    if row["archived"] != 0:
        raise SystemExit(f"Target thread is archived; refusing repair: {TARGET_THREAD_ID}")
    if row["cwd"] != ILC_CWD:
        raise SystemExit(f"Target cwd mismatch; refusing repair: {row['cwd']}")

    with sqlite3.connect(state_db) as con:
        con.execute(
            """
            UPDATE threads
            SET is_pinned = 1,
                name = COALESCE(NULLIF(name, ''), ?),
                title = COALESCE(NULLIF(title, ''), ?)
            WHERE id = ?
            """,
            (TARGET_TITLE, TARGET_TITLE, TARGET_THREAD_ID),
        )
        con.commit()

    entries = rebuild_session_index(codex_home)

    workspace_db = (
        antigravity_root
        / "User"
        / "workspaceStorage"
        / WORKSPACE_ID
        / "state.vscdb"
    )
    workspace_index = None
    if workspace_db.exists():
        rows = sqlite_exec(
            workspace_db,
            "SELECT value FROM ItemTable WHERE key = 'chat.ChatSessionStore.index'",
        )
        workspace_index = rows[0]["value"] if rows else None
        if workspace_index == '{"version":1,"entries":{}}':
            # Leave the schema alone but remove the stale empty cache so the extension can
            # rebuild from Codex's session index/state on next launch.
            with sqlite3.connect(workspace_db) as con:
                con.execute(
                    "DELETE FROM ItemTable WHERE key = 'chat.ChatSessionStore.index'"
                )
                con.commit()

    after = sqlite_exec(
        state_db,
        "SELECT id, title, name, is_pinned, thread_section_id, archived, cwd FROM threads WHERE id = ?",
        (TARGET_THREAD_ID,),
    )[0]
    return {
        "before": dict(row),
        "after": dict(after),
        "session_index_entries": len(entries),
        "target_in_session_index": any(item["id"] == TARGET_THREAD_ID for item in entries),
        "workspace_index_before": workspace_index,
    }


def reopen_antigravity() -> None:
    subprocess.run(["open", "-a", "Antigravity IDE"], check=False)


def parse_args() -> argparse.Namespace:
    home = Path.home()
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-s", type=int, default=300)
    parser.add_argument("--reopen", action="store_true")
    parser.add_argument("--codex-home", default=str(home / ".codex"))
    parser.add_argument(
        "--antigravity-root",
        default=str(home / "Library/Application Support/Antigravity IDE"),
    )
    parser.add_argument(
        "--backup-root",
        default=str(home / ".codex" / "repair_backups"),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser()
    antigravity_root = Path(args.antigravity_root).expanduser()
    backup_dir = Path(args.backup_root).expanduser() / f"{stamp()}-antigravity-codex-visibility-repair"

    wait_for_antigravity_closed(args.timeout_s)
    log(f"Backing up repair inputs to {backup_dir}")
    backup_inputs(codex_home, antigravity_root, backup_dir)
    log("Applying targeted visibility repair.")
    result = repair_state(codex_home, antigravity_root)
    log(json.dumps(result, indent=2, sort_keys=True))
    if args.reopen:
        log("Reopening Antigravity IDE.")
        reopen_antigravity()
    log("Repair complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
