#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Serve Graph Viz directly from a local Atlas LMDB.

PUBLIC_RC_EXCLUDE: graph_viz_live_server_research_tool
PUBLIC_RC_EXCLUDE_REASON: Local read-only visualisation server for unsigned
Atlas projections; no signing, upload, publication, activation, or canonical
graph mutation.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import sys
from datetime import UTC, datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from ilc_core.storage.genesis_atlas_candidate_lmdb_adapter import GenesisAtlasCandidateStore
from ilc_core.storage.lmdb_public_runtime import _encode_json
from tools.graph_viz_3d import _build_graph_data, _html
from tools.graph_viz_export import DEFAULT_LMDB_ROOT, REPO_ROOT, VIEWS, build_view


SERVER_VERSION = "graph_viz_live_server_v0.1"
MAX_MAX_NODES = 100_000


def _live_lmdb_digest(nodes: list[dict[str, Any]], edges: list[dict[str, Any]]) -> str:
    """Digest the live row-store view used for this response."""
    return hashlib.sha256(_encode_json({"edges": edges, "nodes": nodes})).hexdigest()


def _read_lmdb_rows(lmdb_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not lmdb_root.exists():
        raise FileNotFoundError(f"graph_viz_lmdb_missing:{lmdb_root}")
    store = GenesisAtlasCandidateStore(lmdb_root)
    try:
        return store.iter_nodes(), store.iter_edges()
    finally:
        store.close()


def _builder_lmdb_root_arg(lmdb_root: Path) -> Path:
    """Return a path value accepted by graph_viz_export.build_view metadata code."""
    if not lmdb_root.is_absolute():
        return lmdb_root
    try:
        lmdb_root.relative_to(REPO_ROOT)
    except ValueError:
        return Path(lmdb_root.name)
    return lmdb_root


def build_live_graph_payload(
    *,
    lmdb_root: Path,
    view: str,
) -> dict[str, Any]:
    """Build one Graph Viz JSON payload directly from the current LMDB rows."""
    if view not in VIEWS:
        raise ValueError(f"graph_viz_unknown_view:{view}")

    nodes, edges = _read_lmdb_rows(lmdb_root)
    live_digest = _live_lmdb_digest(nodes, edges)
    metadata_seed = {
        "lmdb_path": str(lmdb_root),
        "node_digest": live_digest,
        "phase": "graph-viz-live",
    }
    payload = build_view(
        view=view,
        nodes=nodes,
        edges=edges,
        digest_manifest=metadata_seed,
        lmdb_root=_builder_lmdb_root_arg(lmdb_root),
        omit_export_time=False,
    )
    payload["metadata"].update(
        {
            "intermediary_file_used": False,
            "lmdb_root": str(lmdb_root),
            "lmdb_digest_sha256": live_digest,
            "lmdb_digest_scope": "live_nodes_edges_row_store",
            "server_version": SERVER_VERSION,
            "source_candidate_path": str(lmdb_root),
            "source_candidate_sha256": live_digest,
        }
    )
    return payload


def _parse_max_nodes(value: str | None) -> int | None:
    if value in (None, ""):
        return None
    try:
        parsed = int(value)
    except ValueError as exc:
        raise ValueError("graph_viz_max_nodes_invalid") from exc
    if parsed <= 0 or parsed > MAX_MAX_NODES:
        raise ValueError("graph_viz_max_nodes_out_of_bounds")
    return parsed


def render_live_html(
    *,
    graph_payload: dict[str, Any],
    view: str,
    max_nodes: int | None,
) -> str:
    nodes, links = _build_graph_data(graph_payload, max_nodes=max_nodes)
    title = f"ILC Genesis Atlas Live LMDB ({len(nodes):,}n / {len(links):,}e)"
    rendered = _html(
        nodes,
        links,
        title,
        sprite_manifest=None,
        core_only=False,
        metadata=graph_payload.get("metadata") if isinstance(graph_payload.get("metadata"), dict) else {},
    )
    query = {"view": view}
    if max_nodes is not None:
        query["max_nodes"] = str(max_nodes)
    refresh_href = "/graph?" + urlencode(query)
    api_href = "/api/graph?" + urlencode(query)
    controls = (
        '<div id="lmdb-live-controls">'
        "Live LMDB mode: no out/viz_exports JSON intermediary. "
        f'<a href="{html.escape(refresh_href)}">Refresh from LMDB</a> | '
        f'<a href="{html.escape(api_href)}">View JSON</a>'
        "</div>"
    )
    style = (
        "<style>"
        "#lmdb-live-controls{position:fixed;top:30px;left:10px;z-index:10;"
        "font:12px monospace;color:#d6ffd6;background:rgba(0,0,0,.72);"
        "padding:4px 8px;border:1px solid #335533;border-radius:4px}"
        "#lmdb-live-controls a{color:#8ee8ff}"
        "</style>"
    )
    rendered = rendered.replace("</head>", f"{style}</head>", 1)
    marker = '<div id="panel">'
    return rendered.replace(marker, f"{controls}\n{marker}", 1)


class _LiveGraphHandler(BaseHTTPRequestHandler):
    server: "_LiveGraphServer"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("graph-viz-live: " + fmt % args + "\n")

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        if parsed.path in ("", "/"):
            self._redirect("/graph")
            return
        if parsed.path == "/graph":
            self._handle_graph_html(parsed.query)
            return
        if parsed.path == "/api/graph":
            self._handle_graph_json(parsed.query)
            return
        if parsed.path == "/api/status":
            self._handle_status()
            return
        self._send_json({"error": "graph_viz_route_not_found"}, HTTPStatus.NOT_FOUND)

    def _request_params(self, query: str) -> tuple[str, int | None]:
        params = parse_qs(query, keep_blank_values=False)
        view = params.get("view", [self.server.default_view])[0]
        if view not in VIEWS:
            raise ValueError(f"graph_viz_unknown_view:{view}")
        max_nodes = _parse_max_nodes(params.get("max_nodes", [None])[0])
        return view, max_nodes

    def _handle_graph_html(self, query: str) -> None:
        try:
            view, max_nodes = self._request_params(query)
            payload = build_live_graph_payload(lmdb_root=self.server.lmdb_root, view=view)
            body = render_live_html(graph_payload=payload, view=view, max_nodes=max_nodes).encode("utf-8")
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_bytes(body, "text/html; charset=utf-8", HTTPStatus.OK)

    def _handle_graph_json(self, query: str) -> None:
        try:
            view, max_nodes = self._request_params(query)
            payload = build_live_graph_payload(lmdb_root=self.server.lmdb_root, view=view)
            if max_nodes is not None:
                nodes, links = _build_graph_data(payload, max_nodes=max_nodes)
                payload = {
                    "edges": links,
                    "metadata": {
                        **payload["metadata"],
                        "max_nodes_applied": max_nodes,
                        "rendered_edge_count": len(links),
                        "rendered_node_count": len(nodes),
                    },
                    "nodes": nodes,
                }
        except Exception as exc:
            self._send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
            return
        self._send_json(payload, HTTPStatus.OK)

    def _handle_status(self) -> None:
        payload = {
            "default_view": self.server.default_view,
            "lmdb_root": str(self.server.lmdb_root),
            "read_only_boundary": True,
            "server_time_utc": datetime.now(UTC).isoformat(timespec="seconds"),
            "server_version": SERVER_VERSION,
            "views": list(VIEWS),
        }
        self._send_json(payload, HTTPStatus.OK)

    def _redirect(self, location: str) -> None:
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.end_headers()

    def _send_json(self, payload: dict[str, Any], status: HTTPStatus) -> None:
        self._send_bytes(_encode_json(payload) + b"\n", "application/json; charset=utf-8", status)

    def _send_bytes(self, body: bytes, content_type: str, status: HTTPStatus) -> None:
        self.send_response(status)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Type", content_type)
        self.end_headers()
        self.wfile.write(body)


class _LiveGraphServer(ThreadingHTTPServer):
    def __init__(
        self,
        server_address: tuple[str, int],
        *,
        lmdb_root: Path,
        default_view: str,
    ) -> None:
        self.lmdb_root = lmdb_root
        self.default_view = default_view
        super().__init__(server_address, _LiveGraphHandler)


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve Graph Viz directly from the local Atlas LMDB.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--lmdb-root", type=Path, default=DEFAULT_LMDB_ROOT)
    parser.add_argument("--view", choices=VIEWS, default="public-material")
    args = parser.parse_args()

    if not args.lmdb_root.exists():
        raise SystemExit(f"graph_viz_lmdb_missing:{args.lmdb_root}")

    server = _LiveGraphServer(
        (args.host, args.port),
        lmdb_root=args.lmdb_root,
        default_view=args.view,
    )
    print(
        f"Graph Viz live LMDB server: http://{args.host}:{args.port}/graph?view={args.view}",
        file=sys.stderr,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nGraph Viz live LMDB server stopped.", file=sys.stderr)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
