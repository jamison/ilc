#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import sqlite3
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


UUID_RE = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")


@dataclass
class SessionIndexEntry:
    id: str
    thread_name: str
    updated_at: str


@dataclass
class SessionScan:
    thread_id: str
    path: str
    first_ts: str | None
    last_ts: str | None
    inferred_title: str | None
    rolled_back_events: int


def parse_args() -> argparse.Namespace:
    home = Path.home()
    parser = argparse.ArgumentParser(
        description="Diagnose Codex chat rollback state and optionally rebuild ~/.codex/session_index.jsonl."
    )
    parser.add_argument(
        "--codex-home",
        default=str(home / ".codex"),
        help="Codex home directory. Default: ~/.codex",
    )
    parser.add_argument(
        "--antigravity-root",
        default=str(home / "Library/Application Support/Antigravity"),
        help="Antigravity user-data root. Default: ~/Library/Application Support/Antigravity",
    )
    parser.add_argument(
        "--thread-id",
        default="",
        help="Optional thread id to focus log snippets on.",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Optional path to write a JSON diagnostic report.",
    )
    parser.add_argument(
        "--write-session-index",
        action="store_true",
        help="Rewrite ~/.codex/session_index.jsonl using the latest timestamps from raw session logs.",
    )
    parser.add_argument(
        "--backup-dir",
        default="",
        help="Optional backup directory for writable operations. Default: ~/.codex/repair_backups/<timestamp>",
    )
    return parser.parse_args()


def now_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def parse_thread_id(path: Path) -> str | None:
    matches = UUID_RE.findall(path.name)
    if not matches:
        return None
    return matches[-1]


def iso_from_unix(ts: int | float | None) -> str | None:
    if ts is None:
        return None
    return (
        datetime.fromtimestamp(ts, tz=timezone.utc)
        .isoformat(timespec="milliseconds")
        .replace("+00:00", "Z")
    )


def load_session_index(path: Path) -> list[SessionIndexEntry]:
    entries: list[SessionIndexEntry] = []
    if not path.exists():
        return entries
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            entries.append(
                SessionIndexEntry(
                    id=obj["id"],
                    thread_name=obj["thread_name"],
                    updated_at=obj["updated_at"],
                )
            )
    return entries


def infer_title_from_payload(payload: dict[str, Any]) -> str | None:
    payload_type = payload.get("type")
    if payload_type == "agent_message":
        message = payload.get("message")
        if isinstance(message, str):
            stripped = message.strip()
            if stripped and len(stripped) <= 200:
                return stripped
    return None


def infer_title_from_response_item(obj: dict[str, Any], payload: dict[str, Any]) -> str | None:
    if obj.get("type") != "response_item":
        return None
    if payload.get("type") != "message":
        return None
    if payload.get("role") != "assistant":
        return None
    for item in payload.get("content") or []:
        if item.get("type") != "output_text":
            continue
        text = item.get("text")
        if isinstance(text, str):
            stripped = text.strip()
            if stripped and len(stripped) <= 200:
                return stripped
    return None


def scan_sessions(sessions_root: Path) -> dict[str, SessionScan]:
    scans: dict[str, SessionScan] = {}
    for path in sorted(sessions_root.rglob("*.jsonl")):
        if path.name.startswith("."):
            continue
        thread_id = parse_thread_id(path)
        if thread_id is None:
            continue
        first_ts: str | None = None
        last_ts: str | None = None
        inferred_title: str | None = None
        rolled_back_events = 0
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                ts = obj.get("timestamp")
                if first_ts is None and isinstance(ts, str):
                    first_ts = ts
                if isinstance(ts, str):
                    last_ts = ts
                payload = obj.get("payload")
                if not isinstance(payload, dict):
                    continue
                if inferred_title is None:
                    inferred_title = infer_title_from_payload(payload)
                if inferred_title is None:
                    inferred_title = infer_title_from_response_item(obj, payload)
                if payload.get("type") == "thread_rolled_back":
                    rolled_back_events += 1
        scans[thread_id] = SessionScan(
            thread_id=thread_id,
            path=str(path),
            first_ts=first_ts,
            last_ts=last_ts,
            inferred_title=inferred_title,
            rolled_back_events=rolled_back_events,
        )
    return scans


def load_threads_state(state_path: Path) -> dict[str, dict[str, Any]]:
    if not state_path.exists():
        return {}
    result: dict[str, dict[str, Any]] = {}
    query = """
        select id, title, rollout_path, created_at, updated_at
        from threads
        order by updated_at desc
    """
    with sqlite3.connect(state_path) as con:
        for row in con.execute(query):
            thread_id, title, rollout_path, created_at, updated_at = row
            result[str(thread_id)] = {
                "id": thread_id,
                "title": title,
                "rollout_path": rollout_path,
                "created_at": iso_from_unix(created_at),
                "updated_at": iso_from_unix(updated_at),
            }
    return result


def load_backfill_state(state_path: Path) -> dict[str, Any]:
    if not state_path.exists():
        return {}
    query = """
        select status, last_watermark, last_success_at, updated_at
        from backfill_state
        where id = 1
    """
    with sqlite3.connect(state_path) as con:
        row = con.execute(query).fetchone()
    if row is None:
        return {}
    status, last_watermark, last_success_at, updated_at = row
    return {
        "status": status,
        "last_watermark": last_watermark,
        "last_success_at": iso_from_unix(last_success_at),
        "updated_at": iso_from_unix(updated_at),
    }


def load_sqlite_kv(db_path: Path, keys: list[str]) -> dict[str, str | None]:
    if not db_path.exists():
        return {key: None for key in keys}
    values: dict[str, str | None] = {}
    with sqlite3.connect(db_path) as con:
        for key in keys:
            row = con.execute("select value from ItemTable where key = ?", (key,)).fetchone()
            values[key] = row[0] if row else None
    return values


def find_recent_codex_logs(antigravity_root: Path, thread_id: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    log_paths = sorted(
        antigravity_root.glob("logs/*/window*/exthost/openai.chatgpt/Codex.log"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    needles = [
        "Codex chat session item provider not registered",
        "persistExtendedHistory override was provided and ignored",
        "maybe_resume_success",
    ]
    for path in log_paths[:3]:
        lines_for_path: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                if not any(needle in line for needle in needles):
                    continue
                if thread_id and "maybe_resume_success" in line and thread_id not in line:
                    continue
                if thread_id and "persistExtendedHistory" in line and thread_id not in line:
                    continue
                lines_for_path.append({"line": number, "text": line.rstrip()})
        if lines_for_path:
            matches.append({"path": str(path), "matches": lines_for_path})
    return matches


def build_repaired_session_index(
    existing_entries: list[SessionIndexEntry],
    scans: dict[str, SessionScan],
) -> tuple[list[SessionIndexEntry], list[dict[str, Any]]]:
    repaired: list[SessionIndexEntry] = []
    stale: list[dict[str, Any]] = []
    for entry in existing_entries:
        scan = scans.get(entry.id)
        updated_at = scan.last_ts if scan and scan.last_ts else entry.updated_at
        repaired_entry = SessionIndexEntry(
            id=entry.id,
            thread_name=entry.thread_name,
            updated_at=updated_at,
        )
        repaired.append(repaired_entry)
        if scan and scan.last_ts and scan.last_ts != entry.updated_at:
            stale.append(
                {
                    "id": entry.id,
                    "thread_name": entry.thread_name,
                    "index_updated_at": entry.updated_at,
                    "latest_session_timestamp": scan.last_ts,
                    "rolled_back_events": scan.rolled_back_events,
                    "session_path": scan.path,
                }
            )
    repaired.sort(key=lambda item: item.updated_at, reverse=True)
    return repaired, stale


def ensure_backup_dir(codex_home: Path, explicit_backup_dir: str) -> Path:
    if explicit_backup_dir:
        backup_dir = Path(explicit_backup_dir).expanduser()
    else:
        backup_dir = codex_home / "repair_backups" / now_stamp()
    backup_dir.mkdir(parents=True, exist_ok=True)
    return backup_dir


def write_session_index(
    session_index_path: Path,
    repaired_entries: list[SessionIndexEntry],
    backup_dir: Path,
) -> dict[str, str]:
    backup_path = backup_dir / "session_index.jsonl.bak"
    shutil.copy2(session_index_path, backup_path)
    content = "".join(
        json.dumps(asdict(entry), ensure_ascii=True, separators=(",", ":")) + "\n"
        for entry in repaired_entries
    )
    session_index_path.write_text(content, encoding="utf-8")
    return {
        "backup_path": str(backup_path),
        "session_index_path": str(session_index_path),
    }


def build_report(
    codex_home: Path,
    antigravity_root: Path,
    thread_id: str,
) -> tuple[dict[str, Any], list[SessionIndexEntry], list[SessionIndexEntry]]:
    session_index_path = codex_home / "session_index.jsonl"
    state_path = codex_home / "state_5.sqlite"
    sessions_root = codex_home / "sessions"
    existing_entries = load_session_index(session_index_path)
    scans = scan_sessions(sessions_root)
    repaired_entries, stale_entries = build_repaired_session_index(existing_entries, scans)
    threads_state = load_threads_state(state_path)
    backfill_state = load_backfill_state(state_path)

    global_storage = antigravity_root / "User" / "globalStorage" / "state.vscdb"
    global_keys = load_sqlite_kv(
        global_storage,
        [
            "chat.ChatSessionStore.index",
            "workbench.view.extension.codexViewContainer.state.hidden",
            "workbench.view.extension.codexSecondaryViewContainer.state.hidden",
        ],
    )

    workspace_storage_root = antigravity_root / "User" / "workspaceStorage"
    workspace_state = []
    if workspace_storage_root.exists():
        for db_path in sorted(workspace_storage_root.glob("*/state.vscdb")):
            workspace_json = db_path.parent / "workspace.json"
            workspace_descriptor = json.loads(
                workspace_json.read_text(encoding="utf-8", errors="replace")
            )
            workspace_state.append(
                {
                    "db_path": str(db_path),
                    "workspace": workspace_descriptor,
                    "keys": load_sqlite_kv(
                        db_path,
                        [
                            "chat.ChatSessionStore.index",
                            "memento/webviewView.chatgpt.sidebarView",
                            "memento/webviewView.chatgpt.sidebarSecondaryView",
                            "workbench.view.extension.codexViewContainer.state",
                            "workbench.view.extension.codexSecondaryViewContainer.state",
                        ],
                    ),
                }
            )

    report = {
        "generated_at": datetime.now(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z"),
        "codex_home": str(codex_home),
        "antigravity_root": str(antigravity_root),
        "thread_id_focus": thread_id or None,
        "session_index_path": str(session_index_path),
        "session_index_entries_before": [asdict(entry) for entry in existing_entries],
        "session_index_repair_preview": [asdict(entry) for entry in repaired_entries],
        "session_index_stale_entries": stale_entries,
        "sessions_scanned": {thread_id: asdict(scan) for thread_id, scan in scans.items()},
        "threads_state": threads_state,
        "backfill_state": backfill_state,
        "antigravity": {
            "global_storage_state": {
                "db_path": str(global_storage),
                "keys": global_keys,
            },
            "workspace_storage_state": workspace_state,
            "recent_codex_log_matches": find_recent_codex_logs(antigravity_root, thread_id),
        },
    }
    return report, existing_entries, repaired_entries


def main() -> int:
    args = parse_args()
    codex_home = Path(args.codex_home).expanduser()
    antigravity_root = Path(args.antigravity_root).expanduser()
    session_index_path = codex_home / "session_index.jsonl"

    report, existing_entries, repaired_entries = build_report(
        codex_home=codex_home,
        antigravity_root=antigravity_root,
        thread_id=args.thread_id.strip(),
    )

    if args.report:
        report_path = Path(args.report).expanduser()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")

    stale_entries = report["session_index_stale_entries"]
    print(f"session_index_entries_before={len(existing_entries)}")
    print(f"session_index_stale_entries={len(stale_entries)}")
    for item in stale_entries:
        print(
            "stale "
            f"id={item['id']} "
            f"title={item['thread_name']!r} "
            f"index_updated_at={item['index_updated_at']} "
            f"latest_session_timestamp={item['latest_session_timestamp']}"
        )

    if args.write_session_index:
        if not session_index_path.exists():
            raise SystemExit(f"session index missing: {session_index_path}")
        backup_dir = ensure_backup_dir(codex_home, args.backup_dir)
        write_info = write_session_index(
            session_index_path=session_index_path,
            repaired_entries=repaired_entries,
            backup_dir=backup_dir,
        )
        print(f"session_index_rewritten={write_info['session_index_path']}")
        print(f"backup_created={write_info['backup_path']}")

    log_matches = report["antigravity"]["recent_codex_log_matches"]
    if log_matches:
        print(f"recent_codex_logs_with_matches={len(log_matches)}")
        for match in log_matches:
            print(f"log_match_file={match['path']}")
            for line in match["matches"][:3]:
                print(f"  line={line['line']} {line['text']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
