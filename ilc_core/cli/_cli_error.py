# SPDX-License-Identifier: AGPL-3.0-only
"""Shared structured CLI error helpers."""

from __future__ import annotations

import json
import sys
from typing import NoReturn, TypedDict

EXIT_ERROR = 2


class CliErrorPayload(TypedDict, total=False):
    ok: bool
    error: str
    file: str
    detail: str


def build_cli_error_payload(
    error: str, *, file: str | None = None, detail: str | None = None
) -> CliErrorPayload:
    payload: CliErrorPayload = {"ok": False, "error": error}
    if file is not None:
        payload["file"] = file
    if detail is not None:
        payload["detail"] = detail
    return payload


def emit_cli_error(
    error: str,
    *,
    file: str | None = None,
    detail: str | None = None,
    exit_code: int = EXIT_ERROR,
) -> NoReturn:
    print(json.dumps(build_cli_error_payload(error, file=file, detail=detail)))
    sys.exit(exit_code)
