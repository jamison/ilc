"""
Sync state management for canon bundle key registry.

Persists the last seen channel sequence and hash to prevent rollback attacks.
"""

import json
import fcntl
import os
import tempfile
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Generator


@dataclass(frozen=True)
class ChannelFreshnessState:
    seen_seq: int
    seen_hash: str
    updated_at: str


@contextmanager
def file_lock(path: Path) -> Generator[None, None, None]:
    """
    Acquire an exclusive lock on a file path.
    Creates a separate .lock file to avoid locking the content file itself during atomic replacement.
    """
    lock_path = path.with_suffix(path.suffix + ".lock")
    with open(lock_path, "w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX)
            yield
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)


def load_sync_state(path: Path) -> Optional[ChannelFreshnessState]:
    """
    Load sync state from file.
    Returns None if file doesn't exist or is invalid.
    """
    if not path.exists():
        return None
        
    try:
        content = path.read_text(encoding="utf-8")
        data = json.loads(content)
        
        return ChannelFreshnessState(
            seen_seq=data["seen_seq"],
            seen_hash=data["seen_hash"],
            updated_at=data["updated_at"],
        )
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return None


def write_sync_state(path: Path, state: ChannelFreshnessState) -> None:
    """
    Write sync state atomically.
    """
    data = {
        "seen_seq": state.seen_seq,
        "seen_hash": state.seen_hash,
        "updated_at": state.updated_at,
    }
    
    fd, tmp_str = tempfile.mkstemp(
        dir=str(path.parent), prefix=f".{path.stem}.", suffix=".tmp"
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(json.dumps(data, indent=2, sort_keys=True))
        os.replace(tmp_str, path)
    except Exception:
        try:
            os.unlink(tmp_str)
        except OSError:
            pass
        raise


def evaluate_channel_freshness(
    seen_seq: Optional[int],
    seen_hash: Optional[str],
    curr_seq: int,
    curr_hash: str,
) -> tuple[bool, Optional[str]]:
    """
    Evaluate if current channel is fresh relative to seen state.
    
    Returns:
        (ok, error_code)
        error_code is None if ok.
    """
    # 1. No prior state -> accept
    if seen_seq is None:
        return True, None
        
    # 2. Strict monotonicity
    if curr_seq > seen_seq:
        return True, None
        
    # 3. Idempotency or conflict
    if curr_seq == seen_seq:
        if curr_hash == seen_hash:
            return True, None
        return False, "channel_seq_hash_conflict"
        
    # 4. Rollback
    return False, "channel_rollback_detected"
