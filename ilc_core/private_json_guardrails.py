"""PUBLIC_RC_EXCLUDE: private_json_guardrail_helpers
PUBLIC_RC_EXCLUDE_REASON: Internal helper for private harness/bundle artifacts; not a public protocol API.
"""

from __future__ import annotations

import json
from collections.abc import Mapping


class FrozenDict(dict[object, object]):
    """JSON-serializable immutable dict for private canonical artifacts."""

    def _immutable(self, *_args: object, **_kwargs: object) -> None:
        raise TypeError("frozen_dict_is_immutable")

    __setitem__ = _immutable
    __delitem__ = _immutable
    clear = _immutable
    pop = _immutable
    popitem = _immutable
    setdefault = _immutable
    update = _immutable


def reject_float(value: object, token: str) -> None:
    if isinstance(value, float):
        raise ValueError(token)
    if isinstance(value, Mapping):
        for key, nested in value.items():
            reject_float(key, token)
            reject_float(nested, token)
        return
    if isinstance(value, (list, tuple)):
        for nested in value:
            reject_float(nested, token)


def normalize_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: normalize_json_value(nested) for key, nested in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize_json_value(nested) for nested in value]
    return value


def freeze_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return FrozenDict({key: freeze_json_value(nested) for key, nested in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze_json_value(nested) for nested in value)
    return value


def thaw_json_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {key: thaw_json_value(nested) for key, nested in value.items()}
    if isinstance(value, (list, tuple)):
        return [thaw_json_value(nested) for nested in value]
    return value


def canonical_json(payload: Mapping[str, object], *, float_token: str) -> str:
    reject_float(payload, float_token)
    return json.dumps(
        thaw_json_value(payload),
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def require_sha256_hex(value: str, token: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(char not in "0123456789abcdef" for char in value)
    ):
        raise ValueError(token)


def require_digest_ref(value: str, token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ValueError(token)
    if ":" not in value:
        require_sha256_hex(value, token)
        return
    namespace, digest = value.split(":", 1)
    if namespace == "":
        raise ValueError(token)
    require_sha256_hex(digest, token)
