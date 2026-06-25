# SPDX-License-Identifier: AGPL-3.0-only
"""D2d TLS verification policy helpers.

The insecure skip path is retained only for local development and private
testbeds. Public mode always verifies peer TLS, regardless of local env/config
escape hatches.
"""

from __future__ import annotations

import os
import warnings

D2D_PUBLIC_MODE_ENV = "ILC_D2D_PUBLIC_MODE"
D2D_INSECURE_SKIP_TLS_VERIFY_ENV = "ILC_D2D_INSECURE_SKIP_TLS_VERIFY"


def should_disable_tls_verification(*, insecure_requested: bool, stacklevel: int = 2) -> bool:
    """Return True only for explicit non-public dev/test TLS bypass requests."""

    if os.environ.get(D2D_PUBLIC_MODE_ENV) == "1":
        return False
    if insecure_requested:
        warnings.warn(
            f"{D2D_INSECURE_SKIP_TLS_VERIFY_ENV} is active: TLS verification is "
            "disabled only for local dev/test contexts and is prohibited when "
            f"{D2D_PUBLIC_MODE_ENV}=1.",
            RuntimeWarning,
            stacklevel=stacklevel,
        )
        return True
    return False


__all__ = [
    "D2D_INSECURE_SKIP_TLS_VERIFY_ENV",
    "D2D_PUBLIC_MODE_ENV",
    "should_disable_tls_verification",
]
