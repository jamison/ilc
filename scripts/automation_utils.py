import os
import json
import time
from pathlib import Path

AUTOMATION_DIR = Path("automation")
STATE_DIR = AUTOMATION_DIR / "state"
REPORTS_DIR = AUTOMATION_DIR / "reports"
LOCK_FILE = AUTOMATION_DIR / ".batch_loop.lock"
HEARTBEAT_FILE = STATE_DIR / "loop_heartbeat.json"

def ensure_dirs():
    """Ensure automation directories exist."""
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

def acquire_lock():
    """Acquire lock file. Returns True if successful, False if locked."""
    if LOCK_FILE.exists():
        # Check if stale (e.g. > 1 hour)
        if time.time() - LOCK_FILE.stat().st_mtime > 3600:
            print("Found stale lock file. Overwriting.")
        else:
            return False
    
    LOCK_FILE.write_text(str(os.getpid()))
    return True

def release_lock():
    """Release lock file."""
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()

def update_heartbeat():
    """Update heartbeat file with current timestamp."""
    data = {"last_beat": time.time(), "pid": os.getpid()}
    HEARTBEAT_FILE.write_text(json.dumps(data))

if __name__ == "__main__":
    import sys
    cmd = sys.argv[1]
    if cmd == "init":
        ensure_dirs()
    elif cmd == "lock":
        if not acquire_lock():
            sys.exit(1)
    elif cmd == "unlock":
        release_lock()
    elif cmd == "heartbeat":
        update_heartbeat()
