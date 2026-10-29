# SPDX-License-Identifier: AGPL-3.0-only
"""Public, side-effect-free economic activation state.

Activation-capable implementations may remain outside the public-RC package.
Public runtime code still needs one canonical fail-closed value when deciding
whether a guarded path is available.
"""

from __future__ import annotations


TREASURY_DISTRIBUTION_NOT_ACTIVATED = True


__all__ = ["TREASURY_DISTRIBUTION_NOT_ACTIVATED"]
