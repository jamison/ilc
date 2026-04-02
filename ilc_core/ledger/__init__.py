# ILC Ledger Backend
"""Ledger backend for ILC settlement."""

from typing import Optional
from ilc_core.ledger.backend import LedgerBackend, InMemoryLedgerBackend
from ilc_core.ledger.lmdb_backend import LmdbLedgerBackend
from ilc_core.ledger.persistent_backend import FileLedgerBackend


def get_ledger_backend(kind: str, storage_dir: Optional[str] = None) -> LedgerBackend:
    """
    Get a ledger backend instance.
    
    Args:
        kind: "memory", "file", or "lmdb"
        storage_dir: Required if kind is persistent
    """
    if kind == "memory":
        return InMemoryLedgerBackend()
    elif kind == "file":
        if not storage_dir:
            raise ValueError("storage_dir is required for file backend")
        return FileLedgerBackend(storage_dir)
    elif kind == "lmdb":
        if not storage_dir:
            raise ValueError("storage_dir is required for lmdb backend")
        return LmdbLedgerBackend(storage_dir)
    else:
        raise ValueError(f"Unknown ledger backend kind: {kind}")
