# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from .server import create_app

# Dedicated ASGI surface for uvicorn/module importers.
app = create_app()
