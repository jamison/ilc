# SPDX-License-Identifier: AGPL-3.0-or-later
from __future__ import annotations

from .server import create_app

# Dedicated ASGI surface for uvicorn/module importers.
app = create_app()
