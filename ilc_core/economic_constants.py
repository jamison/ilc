# SPDX-License-Identifier: AGPL-3.0-only
"""Canonical protocol economic constants shared across runtime packages."""

from __future__ import annotations

from decimal import Decimal

C_MAX_ILC = Decimal("25920000")

__all__ = ["C_MAX_ILC"]
