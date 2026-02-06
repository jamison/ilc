"""
Key registry for canon bundle signing key rotation.

Tracks current, previous, and deprecated keys to support key lifecycle management.
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class KeyRegistry:
    """Registry of signing keys with lifecycle status."""
    current_keys: List[str] = field(default_factory=list)
    previous_keys: List[str] = field(default_factory=list)
    deprecated_keys: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        """Return True if registry has no keys configured."""
        return not self.current_keys and not self.previous_keys and not self.deprecated_keys

    def status(self, key_id: str) -> str:
        """Return the lifecycle status of a key_id."""
        # If registry is empty, only allow all keys when explicitly enabled.
        if self.is_empty():
            if os.environ.get("ILC_ALLOW_EMPTY_KEY_REGISTRY") == "1":
                return "current"
            return "unknown"
        if key_id in self.current_keys:
            return "current"
        if key_id in self.previous_keys:
            return "previous"
        if key_id in self.deprecated_keys:
            return "deprecated"
        return "unknown"



# Default registry for MVP (placeholder key_ids)
DEFAULT_REGISTRY = KeyRegistry(
    current_keys=[],
    previous_keys=[],
    deprecated_keys=[],
)


def load_registry(path: Optional[Path] = None) -> KeyRegistry:
    """
    Load key registry from JSON file or return defaults.
    
    Args:
        path: Optional path to registry JSON file.
              Falls back to ILC_KEY_REGISTRY_PATH env var if not provided.
    
    Returns:
        KeyRegistry instance.
    """
    if path is None:
        env_path = os.environ.get("ILC_KEY_REGISTRY_PATH")
        if env_path:
            path = Path(env_path)
    
    if path and path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return KeyRegistry(
                current_keys=data.get("current_keys", []),
                previous_keys=data.get("previous_keys", []),
                deprecated_keys=data.get("deprecated_keys", []),
            )
        except (json.JSONDecodeError, OSError):
            pass
    
    return DEFAULT_REGISTRY


# Module-level registry instance (lazy loaded on first use)
_registry: Optional[KeyRegistry] = None


def get_registry() -> KeyRegistry:
    """Get the global key registry instance."""
    global _registry
    if _registry is None:
        _registry = load_registry()
    return _registry


def set_registry(registry: KeyRegistry) -> None:
    """Set the global key registry (for testing)."""
    global _registry
    _registry = registry


def reset_registry() -> None:
    """Reset the global registry to force reload."""
    global _registry
    _registry = None
