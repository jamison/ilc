#!/usr/bin/env python3
"""Generate a 3D force-graph visualisation of a Genesis Atlas candidate.

Usage:
    .venv/bin/python tools/graph_viz_3d.py [OPTIONS]

Options:
    --input PATH        Atlas JSON to read (default: Fix41a atlas)
    --output PATH       HTML output path (default: graphify-out/graph_3d.html)
    --open              Open in browser after generating
    --lmdb              Export a view from the verified Fix41 LMDB before rendering
    --view VIEW         LMDB view to export before rendering (default: public-material)
    --core-only         Pre-filter to authority nodes only (CDLs, ADRs, truth
                        primitives, genesis agents, artifacts, policies,
                        ceremonies) — much lighter render
    --max-nodes N       Hard cap: if node count exceeds N after other filters,
                        keep the N highest-priority nodes (default: no cap)
    --sprites PATH      JSON file mapping node IDs or group names to sprite
                        URLs (image, GIF, or data-URI).  See SPRITE_MANIFEST
                        section below for format.

Node rendering:
    Nodes are rendered as billboard sprites (flat circles always facing the
    camera) instead of 3D sphere meshes.  This cuts GPU cost by ~10x.
    One canvas texture is shared per colour group (8 textures total regardless
    of node count).

    Custom sprites override the default circle for any node type or individual
    node.  Sprites can be any URL the browser can load: PNG, JPEG, GIF
    (animated), SVG, or a data-URI.  They are rendered as THREE.SpriteMaterial
    billboards — always face-on to the camera, never perspective-distorted.

SPRITE_MANIFEST format (--sprites FILE):
    {
      "by_group": {
        "genesis_agent": "path/to/agent_icon.gif",
        "cdl":           "path/to/cdl_icon.png"
      },
      "by_id": {
        "artifact:genesis_intent_attestation_init_authority_map": "path/to/node0_avatar.gif",
        "genesis_agent:genesis_agent_01": "path/to/your_avatar.gif"
      }
    }

    Keys in "by_id" take priority over "by_group".  Any node not matched falls
    back to the shared colour-circle sprite.

PUBLIC_RC_EXCLUDE: graph_viz_3d_research_tool
PUBLIC_RC_EXCLUDE_REASON: Local visualisation tool; no signing, upload, or canonical mutation.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_INPUT = REPO_ROOT / "out/atlas_research/genesis_atlas_enriched_candidate_fix41a.json"
DEFAULT_OUTPUT = REPO_ROOT / "graphify-out/graph_3d.html"
DEFAULT_VIZ_EXPORT_DIR = REPO_ROOT / "out/viz_exports"

NODE0 = "artifact:genesis_intent_attestation_init_authority_map"

# ── colour palette by node prefix / kind ────────────────────────────────────
PREFIX_COLORS: dict[str, str] = {
    "genesis_authority_root": "#ffffff",   # white       — Node 0
    "truth_primitive":   "#ff4444",   # red         — genesis axioms
    "axiom":             "#ff2244",   # bright red  — axiom nodes
    "policy":            "#ff9900",   # amber       — governance policy
    "artifact":          "#ffcc00",   # gold        — genesis artifacts
    "material_manifest_root": "#d6b24a",   # brass       — unsigned repo candidate root
    "material_partition_root": "#9f8a4a",  # muted gold  — source/evidence partitions
    "package_material_root": "#ffd966",    # pale gold   — package material root
    "source_tree_overlay": "#7a7a55",       # olive       — candidate source-tree overlay
    "genesis_agent":     "#ff66ff",   # pink        — genesis agents
    "adr":               "#7d5cff",   # indigo      — ADRs
    "cdl":               "#00bfff",   # cyan-blue   — CDLs
    "ceremony":          "#ff88ff",   # light pink
    "invariant":         "#cc7722",   # amber-brown — protocol invariants
    "claim":             "#ff7733",   # orange      — epistemic claims
    "target":            "#66aa55",   # green       — planning targets
    "phase":             "#8888bb",   # muted blue  — phase tracking
    "sim":               "#44aacc",   # cyan-blue   — simulation results
    "command":           "#33bbaa",   # teal        — command nodes
    "executor_profile":  "#bb44bb",   # purple      — executor profiles
    "repo_dir":          "#555566",   # dark grey   — directory nodes
    "source":            "#44cc88",   # green       — source nodes
    "repo":              "#888888",   # grey        — repo file nodes
    "atlas":             "#aaaaaa",   # light grey  — atlas nodes
    "other":             "#cccccc",   # fallback
}

EDGE_COLORS: dict[str, str] = {
    "GOVERNS":              "#ff4444",
    "ATTESTATION":          "#ff9900",
    "IMPLEMENTS":           "#4499ff",
    "TESTS":                "#44aaff",
    "COVERS_SYMBOL":        "#33bbbb",
    "EVIDENCES":            "#44ff88",
    "REFERENCES_AUTHORITY": "#00cccc",
    "DERIVED_FROM":         "#cc88ff",
    "CLASSIFIED_BY":        "#ff88aa",
    "SAME_AUTHORITY":       "#ee88ff",
    "SAME_SOURCE":          "#44ff88",
    "OPENED_FOR":           "#88ddff",
    "PRELOCK_FOR":          "#88bbff",
    "RATIFICATION_EVIDENCE_FOR": "#88ffaa",
    "PROPOSES_CHANGE_TO":   "#ffaa88",
    "RESOLVED_BY":          "#aaff88",
    "CARRIES_FORWARD":      "#aa66cc",
    "SOURCE_TREE_MEMBER":   "#448844",
    "CONTAINS_FILE":        "#444444",
    "CONTAINS_GROUP":       "#444444",
    "CONTAINS_PARTITION":   "#444444",
    "IMPORTS_MODULE":       "#555555",
    "PROVENANCE":           "#888844",
    "PRIMITIVE_INVOCATION": "#ff6644",
    "CONSTRAINS":           "#886644",
}

AUTHORITY_PREFIXES = frozenset(
    [
        "truth_primitive",
        "axiom",
        "policy",
        "artifact",
        "genesis_authority_root",
        "genesis_agent",
        "adr",
        "cdl",
        "ceremony",
    ]
)

# Priority order for --max-nodes trimming (higher = kept first)
_GROUP_PRIORITY: dict[str, int] = {
    "genesis_authority_root": 120,
    "truth_primitive":  100,
    "axiom":            98,
    "genesis_agent":    90,
    "artifact":         80,
    "package_material_root": 78,
    "material_manifest_root": 74,
    "material_partition_root": 68,
    "source_tree_overlay": 18,
    "policy":           70,
    "cdl":              60,
    "adr":              55,
    "ceremony":         50,
    "invariant":        45,
    "claim":            40,
    "command":          35,
    "source":           30,
    "target":           25,
    "sim":              20,
    "phase":            15,
    "executor_profile": 12,
    "repo":             10,
    "repo_dir":         8,
    "atlas":            5,
    "other":            1,
}


def _prefix(node_id: str) -> str:
    return node_id.split(":", 1)[0]


def _node_id(node: dict) -> str:
    value = node.get("candidate_id") or node.get("id") or node.get("node_id")
    return value if isinstance(value, str) else ""


def _edge_source(edge: dict) -> str:
    value = edge.get("source_candidate_id") or edge.get("source") or edge.get("from")
    return value if isinstance(value, str) else ""


def _edge_target(edge: dict) -> str:
    value = edge.get("target_candidate_id") or edge.get("target") or edge.get("to")
    return value if isinstance(value, str) else ""


def _edge_type(edge: dict) -> str:
    value = edge.get("edge_type") or edge.get("type")
    return value if isinstance(value, str) else ""


def _node_size(node_id: str, _node: dict) -> int:
    exported = _node.get("size")
    if isinstance(exported, (int, float)) and exported > 0:
        return int(exported)
    p = _prefix(node_id)
    if node_id == NODE0:
        return 20
    if p == "truth_primitive":
        return 12
    if p in ("policy", "artifact", "genesis_agent"):
        return 10
    if p in ("adr", "cdl"):
        return 8
    if p == "ceremony":
        return 8
    return 4


def _node_color(node_id: str, _node: dict) -> str:
    exported = _node.get("color")
    if isinstance(exported, str) and exported:
        return exported
    if node_id == NODE0:
        return "#ffffff"
    p = _prefix(node_id)
    return PREFIX_COLORS.get(p, PREFIX_COLORS["other"])


def _short_label(node_id: str, node: dict) -> str:
    label = node.get("label") or node.get("source_path") or node_id
    if isinstance(label, str) and len(label) > 60:
        label = label[-60:]
    return label


def _build_graph_data(
    graph: dict,
    max_nodes: int | None = None,
) -> tuple[list, list]:
    """Emit ALL nodes and ALL edges from the candidate.

    Filtering is visual-only, done client-side via nodeVisibility /
    linkVisibility callbacks so physics runs on the true full-graph structure
    (spotlight model).  core_only is consumed by _html() only.
    """
    raw_nodes = graph.get("nodes", [])
    raw_edges = graph.get("edges", [])

    node_by_id: dict[str, dict] = {}
    nodes_out: list[dict] = []
    for n in raw_nodes:
        nid = _node_id(n)
        if not nid:
            continue
        node_by_id[nid] = n
        nodes_out.append({
            "id":    nid,
            "label": _short_label(nid, n),
            "color": _node_color(nid, n),
            "authority_class": str(n.get("authority_class") or ""),
            "degree_lmdb_total": n.get("degree_lmdb_total"),
            "directed_hop_from_root": n.get("directed_hop_from_root"),
            "size":  _node_size(nid, n),
            "group": str(n.get("visual_group") or n.get("group") or _prefix(nid)),
            "prefix": str(n.get("prefix") or _prefix(nid)),
            "tier":  str(n.get("tier", "")),
            "kind":  str(n.get("node_kind") or n.get("kind") or ""),
            "projection": str(n.get("graph_projection") or n.get("projection") or ""),
            "status": str(n.get("candidate_status") or n.get("status") or ""),
        })

    # --max-nodes: trim by group priority, always keep NODE0
    if max_nodes is not None and len(nodes_out) > max_nodes:
        nodes_out.sort(
            key=lambda n: (
                1 if n["id"] == NODE0 else 0,
                _GROUP_PRIORITY.get(n["group"], 0),
            ),
            reverse=True,
        )
        nodes_out = nodes_out[:max_nodes]

    node_ids = {n["id"] for n in nodes_out}
    links_out: list[dict] = []
    for e in raw_edges:
        src = _edge_source(e)
        tgt = _edge_target(e)
        etype = _edge_type(e)
        if not src or not tgt:
            continue
        if src not in node_ids or tgt not in node_ids:
            continue
        links_out.append({
            "source": src,
            "target": tgt,
            "type":   etype,
            "color":  EDGE_COLORS.get(etype, "#666666"),
        })

    return nodes_out, links_out


def _prefix_colors_js() -> str:
    """Emit the PREFIX_COLORS map as a JS const for dynamic legend building."""
    entries = ", ".join(f'"{k}": "{v}"' for k, v in PREFIX_COLORS.items())
    return f"const NODE_COLORS = {{{entries}}};"


def _html(
    nodes: list,
    links: list,
    title: str,
    sprite_manifest: dict | None = None,
    core_only: bool = False,
    metadata: dict | None = None,
) -> str:
    nodes_json = json.dumps(nodes, separators=(",", ":"))
    links_json = json.dumps(links, separators=(",", ":"))
    prefix_colors_js = _prefix_colors_js()
    node_count = len(nodes)
    link_count = len(links)
    metadata = metadata or {}
    lmdb_root_display = str(metadata.get("lmdb_root") or "unknown")
    lmdb_digest = str(metadata.get("lmdb_digest_sha256") or "")
    digest_short = lmdb_digest[:12] if lmdb_digest else "—"
    export_time = str(metadata.get("export_time_utc") or "—")

    # Sprite manifest injected as JS — empty dicts if none provided
    sm = sprite_manifest or {}
    sprite_by_group_json = json.dumps(sm.get("by_group", {}), separators=(",", ":"))
    sprite_by_id_json    = json.dumps(sm.get("by_id", {}),    separators=(",", ":"))

    # Build clustering JS as a plain string (not inside the f-string) so that
    # JS object literal braces { } don't need escaping as {{ }}.
    if core_only:
        cluster_js = """\
// ── core-only clustering force ─────────────────────────────────────────────
// Pull each authority group toward a fixed 3D cluster centre so the
// simulation settles into a meaningful layout instead of a sphere.
const _GROUP_CENTERS_3D = {
  "truth_primitive": {x:   0, y:   0, z:  0},
  "genesis_agent":   {x:   0, y:  70, z:  0},
  "artifact":        {x:   0, y: -70, z:  0},
  "policy":          {x:  90, y:   0, z:  0},
  "cdl":             {x: -130, y:  80, z: 40},
  "adr":             {x:  130, y:  80, z:-40},
  "ceremony":        {x:   0, y:-130, z:  0},
};
Graph.d3Force("cluster", function(alpha) {
  Graph.graphData().nodes.forEach(function(n) {
    const c = _GROUP_CENTERS_3D[n.group];
    if (!c) return;
    n.vx = (n.vx || 0) + (c.x - (n.x || 0)) * 0.04 * alpha;
    n.vy = (n.vy || 0) + (c.y - (n.y || 0)) * 0.04 * alpha;
    n.vz = (n.vz || 0) + (c.z - (n.z || 0)) * 0.04 * alpha;
  });
});
Graph.d3Force("charge").strength(-150);
Graph.d3Force("link").distance(60).strength(1.5);"""
    else:
        cluster_js = """\
// ── full-graph radial gravity force ──────────────────────────────────────────
// Pull each group toward a target radial distance from the origin so that
// authority nodes settle near centre and leaves drift to the outer shell.
// This overrides degree-centrality as the primary layout driver.
// Strength is kept gentle (0.015) so link topology still has influence.
const _RADIAL_TARGET = {
  "truth_primitive":  0,
  "genesis_agent":    0,
  "axiom":            20,
  "artifact":         80,
  "policy":           80,
  "cdl":              130,
  "adr":              130,
  "ceremony":         130,
  "invariant":        200,
  "claim":            220,
  "command":          230,
  "executor_profile": 240,
  "target":           260,
  "sim":              270,
  "phase":            280,
  "source":           300,
  "atlas":            310,
  "repo_dir":         320,
  "repo":             380,
  "other":            360,
};
Graph.d3Force("radial", function(alpha) {
  const str = 0.015 * alpha;
  Graph.graphData().nodes.forEach(function(n) {
    const r = _RADIAL_TARGET[n.group];
    if (r === undefined) return;
    const cx = n.x || 0, cy = n.y || 0, cz = n.z || 0;
    const dist = Math.sqrt(cx*cx + cy*cy + cz*cz) || 1;
    const delta = (r - dist) * str;
    n.vx = (n.vx || 0) + (cx / dist) * delta;
    n.vy = (n.vy || 0) + (cy / dist) * delta;
    n.vz = (n.vz || 0) + (cz / dist) * delta;
  });
});
Graph.d3Force("charge").strength(-25);"""

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0d0d1a; color: #eee; font-family: monospace; overflow: hidden; }}
  #graph {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; }}
  #lmdb-source-bar {{
    position: fixed; top: 0; left: 0; right: 0; z-index: 20;
    background: #111; color: #777; font-size: 10px; padding: 2px 8px;
    border-bottom: 1px solid #333; font-family: monospace;
  }}
  #panel {{
    position: fixed; top: 26px; left: 10px; z-index: 10;
    background: rgba(10,10,30,0.85); border: 1px solid #333;
    border-radius: 6px; padding: 12px; width: 220px;
    max-height: calc(100vh - 20px); overflow-y: auto;
  }}
  #panel h2 {{ font-size: 13px; color: #fff; margin-bottom: 8px; }}
  #panel .stat {{ font-size: 11px; color: #aaa; margin: 2px 0; }}
  #search {{
    width: 100%; background: #1a1a2e; border: 1px solid #444;
    color: #eee; padding: 5px 7px; border-radius: 4px;
    font-size: 11px; margin: 8px 0;
  }}
  #info {{
    position: fixed; bottom: 10px; left: 10px; z-index: 10;
    background: rgba(10,10,30,0.9); border: 1px solid #333;
    border-radius: 6px; padding: 10px; width: 320px;
    font-size: 11px; max-height: 200px; overflow-y: auto;
    display: none;
  }}
  #info h3 {{ color: #fff; margin-bottom: 6px; font-size: 12px; }}
  #info .field {{ color: #aaa; margin: 2px 0; word-break: break-all; }}
  #controls {{
    position: fixed; top: 26px; right: 10px; z-index: 10;
    background: rgba(10,10,30,0.85); border: 1px solid #333;
    border-radius: 6px; padding: 10px; font-size: 11px;
    width: 260px; box-sizing: border-box;
  }}
  #controls label {{ color: #aaa; display: block; margin: 4px 0; cursor: pointer; }}
  button {{
    background: #222244; border: 1px solid #444; color: #ccc;
    padding: 4px 8px; border-radius: 3px; cursor: pointer; font-size: 11px;
    margin: 3px 2px;
  }}
  button:hover {{ background: #333366; }}
</style>
</head>
<body>
<div id="graph"></div>
<div id="lmdb-source-bar">Source: {lmdb_root_display} | digest: {digest_short}… | exported: {export_time} | nodes: {node_count:,} | edges: {link_count:,}</div>

<div id="panel">
  <h2>ILC Genesis Atlas</h2>
  <div class="stat">Nodes: {node_count:,}</div>
  <div class="stat">Edges: {link_count:,}</div>
  <div class="stat" style="margin-top:4px;color:#888">Drag to rotate · Scroll to zoom · Click node for info</div>
  <input id="search" type="text" placeholder="Search node ID or label…">
  <div style="margin-top:8px;margin-bottom:4px;font-size:11px;color:#888">Node types</div>
  <div id="legend"></div>
</div>

<div id="controls">
  <div style="font-size:11px;color:#888;margin-bottom:4px">Node filters</div>
  <label><input type="checkbox" id="chk-spotlight"{"checked" if core_only else ""}> Spotlight authority</label>
  <label><input type="checkbox" id="chk-hide-generated" checked> Hide out/ (generated evidence)</label>
  <label><input type="checkbox" id="chk-hide-private-history" checked> Hide Z_Past_Chats (private history)</label>
  <div style="font-size:11px;color:#888;margin:6px 0 4px">Edge filters</div>
  <label><input type="checkbox" id="chk-governs" checked> GOVERNS edges</label>
  <label><input type="checkbox" id="chk-attestation" checked> ATTESTATION edges</label>
  <label><input type="checkbox" id="chk-refs" checked> REFERENCES_AUTHORITY</label>
  <label><input type="checkbox" id="chk-classified"> CLASSIFIED_BY</label>
  <label><input type="checkbox" id="chk-source-tree" checked> SOURCE_TREE_MEMBER</label>
  <label><input type="checkbox" id="chk-contains" checked> CONTAINS_* edges</label>
  <label><input type="checkbox" id="chk-imports" checked> IMPORTS_MODULE edges</label>
  <div id="node-count-display" style="font-size:11px;color:#aaa;margin-top:6px"></div>
  <div id="debug-log" style="font-size:9px;color:#666;margin-top:3px;word-break:break-all;overflow-wrap:break-word;white-space:normal"></div>
  <div style="margin-top:6px">
    <button id="btn-reset">Reset camera</button>
    <button id="btn-center">Centre on Node 0</button>
    <button id="btn-pause">Pause physics</button>
    <button id="btn-radial">Radial layout: ON</button>
  </div>
  <div style="margin-top:8px;border-top:1px solid #333;padding-top:8px">
    <div style="font-size:11px;color:#888;margin-bottom:4px">Genesis trace</div>
    <button id="btn-trace">Trace mode: OFF</button>
    <button id="btn-clear-trace">Clear trace</button>
    <div id="trace-info" style="font-size:10px;color:#ff6644;margin-top:4px"></div>
  </div>
  <div style="margin-top:8px;border-top:1px solid #333;padding-top:8px">
    <div style="font-size:11px;color:#888;margin-bottom:4px">Hops from Genesis</div>
    <div style="display:flex;align-items:center;gap:6px">
      <input type="range" id="hop-slider" min="0" max="30" value="0" style="flex:1;accent-color:#ff6644;">
      <span id="hop-label" style="font-size:11px;color:#ff9944;min-width:28px">All</span>
    </div>
    <div id="hop-stats" style="font-size:10px;color:#666;margin-top:3px"></div>
  </div>
</div>

<div id="info">
  <h3 id="info-title">Node info</h3>
  <div id="info-body"></div>
</div>

<script src="https://unpkg.com/3d-force-graph@1.73.0/dist/3d-force-graph.min.js"></script>
<script>
const RAW_NODES = {nodes_json};
const RAW_LINKS = {links_json};
const NODE0_ID  = "{NODE0}";

// ── node colour palette (mirrors Python PREFIX_COLORS) ────────────────────
{prefix_colors_js}

// ── sprite manifest ───────────────────────────────────────────────────────
const SPRITE_BY_ID    = {sprite_by_id_json};
const SPRITE_BY_GROUP = {sprite_by_group_json};

// ── build lookup ──────────────────────────────────────────────────────────
const nodeMap = {{}};
RAW_NODES.forEach(n => {{ nodeMap[n.id] = n; }});

// ── BFS hop depth from NODE0 (full graph, all links) ──────────────────────
// NODE_HOP[id] = distance in hops from NODE0.
// Nodes unreachable from NODE0 get Infinity.
const NODE_HOP = {{}};
(function computeHops() {{
  const adj = {{}};
  RAW_LINKS.forEach(l => {{
    const s = l.source, t = l.target;
    if (!adj[s]) adj[s] = [];
    if (!adj[t]) adj[t] = [];
    adj[s].push(t);
    adj[t].push(s);
  }});
  const queue = [NODE0_ID];
  NODE_HOP[NODE0_ID] = 0;
  while (queue.length) {{
    const curr = queue.shift();
    (adj[curr] || []).forEach(nb => {{
      if (NODE_HOP[nb] === undefined) {{
        NODE_HOP[nb] = NODE_HOP[curr] + 1;
        queue.push(nb);
      }}
    }});
  }}
  RAW_NODES.forEach(n => {{
    if (NODE_HOP[n.id] === undefined) NODE_HOP[n.id] = Infinity;
  }});
  const maxHop = Math.max(...Object.values(NODE_HOP).filter(v => isFinite(v)));
  document.getElementById("hop-slider").max = maxHop;
}})();

// ── BFS_ORDER: nodes sorted by hop depth, used by install-demo mode ───────
const BFS_ORDER = RAW_NODES
  .slice()
  .sort((a, b) => (NODE_HOP[a.id] ?? Infinity) - (NODE_HOP[b.id] ?? Infinity))
  .map(n => n.id);

// ── Genesis trace (BFS) ───────────────────────────────────────────────────
// Adjacency is rebuilt from the CURRENTLY VISIBLE links on every refresh so
// BFS only traverses nodes that are actually rendered.  This prevents the
// trace from silently routing through filtered-out nodes and looking broken.
let _visAdj = {{}};

function _rebuildVisAdj(links) {{
  _visAdj = {{}};
  links.forEach(l => {{
    // ForceGraph3D may have mutated source/target to objects; handle both.
    const s = (l.source && l.source.id) ? l.source.id : l.source;
    const t = (l.target && l.target.id) ? l.target.id : l.target;
    if (!s || !t) return;
    if (!_visAdj[s]) _visAdj[s] = new Set();
    if (!_visAdj[t]) _visAdj[t] = new Set();
    _visAdj[s].add(t);
    _visAdj[t].add(s);
  }});
}}

// ── Genesis trace state ───────────────────────────────────────────────────
let genesisTraceIds   = new Set(); // ordered set of node IDs on the path
let tracePathOrdered  = [];        // [selectedNode, ..., NODE0] ordered array
let traceOutwardIds   = new Set(); // nodes reachable FROM selected outward (not dimmed)
let selectedTraceNode = null;      // the node the user clicked
let pulseNodeId       = null;      // which node the pulse bead is currently on
let _pulseTimer       = null;
const PULSE_DWELL_MS  = 750;

// BFS outward from startId up to `depth` hops, excluding nodes already on
// the Genesis trace path.  Keeps those nodes at full brightness.
function _buildOutwardIds(startId, depth) {{
  const out     = new Set();
  const visited = new Set(genesisTraceIds);
  visited.add(startId);
  let frontier  = [startId];
  for (let d = 0; d < depth; d++) {{
    const next = [];
    for (const nid of frontier) {{
      for (const nb of (_visAdj[nid] || [])) {{
        if (visited.has(nb)) continue;
        visited.add(nb);
        out.add(nb);
        next.push(nb);
      }}
    }}
    frontier = next;
    if (!frontier.length) break;
  }}
  return out;
}}

function _startPulse(path) {{
  if (_pulseTimer) {{ clearTimeout(_pulseTimer); _pulseTimer = null; }}
  let idx = 0;
  function step() {{
    pulseNodeId = path[idx];
    // Only update color/size — no full refresh (avoids re-running visibility)
    Graph.nodeColor(nodeColor).nodeVal(nodeSize);
    idx = (idx + 1) % path.length;
    _pulseTimer = setTimeout(step, PULSE_DWELL_MS);
  }}
  step();
}}

function traceToGenesis(startId) {{
  if (_pulseTimer) {{ clearTimeout(_pulseTimer); _pulseTimer = null; }}
  pulseNodeId = null;

  if (startId === NODE0_ID) {{
    genesisTraceIds   = new Set([NODE0_ID]);
    tracePathOrdered  = [NODE0_ID];
    traceOutwardIds   = _buildOutwardIds(NODE0_ID, 2);
    selectedTraceNode = NODE0_ID;
    document.getElementById("trace-info").textContent = "You are at Genesis root.";
    refresh();
    return;
  }}

  const parent = {{ [startId]: null }};
  const queue  = [startId];
  let found    = false;
  while (queue.length && !found) {{
    const curr = queue.shift();
    for (const nb of (_visAdj[curr] || [])) {{
      if (nb in parent) continue;
      parent[nb] = curr;
      if (nb === NODE0_ID) {{ found = true; break; }}
      queue.push(nb);
    }}
  }}
  if (!found) {{
    genesisTraceIds   = new Set([startId]);
    tracePathOrdered  = [startId];
    traceOutwardIds   = _buildOutwardIds(startId, 2);
    selectedTraceNode = startId;
    document.getElementById("trace-info").textContent =
      "No path to Genesis in visible graph — try unchecking filters.";
    refresh();
    return;
  }}

  // Reconstruct ordered path: Genesis → selected, then reverse → selected → Genesis
  const pathArr = [];
  let node = NODE0_ID;
  while (node !== null) {{ pathArr.push(node); node = parent[node]; }}
  pathArr.reverse(); // now [startId, ..., NODE0]

  genesisTraceIds   = new Set(pathArr);
  tracePathOrdered  = pathArr;
  selectedTraceNode = startId;
  traceOutwardIds   = _buildOutwardIds(startId, 2);

  document.getElementById("trace-info").textContent =
    `Path: ${{pathArr.length - 1}} hop(s) to Genesis`;
  refresh();
  _startPulse(pathArr);
}}

function clearTrace() {{
  if (_pulseTimer) {{ clearTimeout(_pulseTimer); _pulseTimer = null; }}
  pulseNodeId       = null;
  genesisTraceIds   = new Set();
  tracePathOrdered  = [];
  traceOutwardIds   = new Set();
  selectedTraceNode = null;
  document.getElementById("trace-info").textContent = "";
  refresh();
}}

// ── filter state ─────────────────────────────────────────────────────────
// Filters are VISUAL ONLY — they never replace graphData or re-run physics.
// Every node keeps its position from the full-graph simulation.
// nodeVisibility / linkVisibility callbacks control what is rendered.
let searchTerm          = "";
// spotlightAuth: dims non-authority nodes to near-invisible; does NOT hide
// them so their edges to authority nodes remain visible (connected spine).
let spotlightAuth       = {"true" if core_only else "false"};
let hideGenerated       = true;
let hidePrivateHistory  = true;
let showGoverns         = true;
let showAttest          = true;
let showRefs            = true;
let showClassified      = false;
let showSourceTree      = true;
let showContains        = true;
let showImports         = true;
let hopDepth            = 0;  // 0 = all; N = show only nodes ≤ N hops from NODE0

// hiddenGroups: per-group toggle; nodes in this set are fully invisible.
const hiddenGroups = new Set();

const AUTHORITY_GROUPS = new Set([
  "truth_primitive","axiom","policy","artifact","genesis_authority_root","genesis_agent","adr","cdl","ceremony"
]);
const CONTAINS_TYPES = new Set([
  "CONTAINS_FILE","CONTAINS_GROUP","CONTAINS_PARTITION"
]);

function _isAuthority(n) {{
  return AUTHORITY_GROUPS.has(n.group);
}}

function nodeVisible(n) {{
  if (n.id === NODE0_ID) return true;
  // Per-group checkbox: fully hidden
  if (hiddenGroups.has(n.group)) return false;
  // Hop-depth filter: show only nodes within N hops of NODE0
  if (hopDepth > 0 && (NODE_HOP[n.id] ?? Infinity) > hopDepth) return false;
  // Tier-based hide filters
  if (hideGenerated && n.tier === "generated_evidence_material") return false;
  if (hidePrivateHistory && n.tier === "genesis_private_historical_material") return false;
  // Search: only matching nodes visible (overrides spotlight)
  if (searchTerm) {{
    const s = searchTerm.toLowerCase();
    return n.id.toLowerCase().includes(s) || n.label.toLowerCase().includes(s);
  }}
  return true;
}}

function linkVisible(l) {{
  const s = l.source?.id || l.source;
  const t = l.target?.id || l.target;
  const sm = nodeMap[s], tm = nodeMap[t];
  // Both endpoints must pass nodeVisible
  if (!sm || !nodeVisible(sm)) return false;
  if (!tm || !nodeVisible(tm)) return false;
  // Spotlight: hide edges where BOTH endpoints are non-authority (too noisy)
  if (spotlightAuth && !_isAuthority(sm) && !_isAuthority(tm)) return false;
  if (!showGoverns    && l.type === "GOVERNS") return false;
  if (!showAttest     && l.type === "ATTESTATION") return false;
  if (!showRefs       && l.type === "REFERENCES_AUTHORITY") return false;
  if (!showClassified && l.type === "CLASSIFIED_BY") return false;
  if (!showSourceTree && l.type === "SOURCE_TREE_MEMBER") return false;
  if (!showContains   && CONTAINS_TYPES.has(l.type)) return false;
  if (!showImports    && l.type === "IMPORTS_MODULE") return false;
  return true;
}}

function nodeColor(n) {{
  // Genesis root always white — visible in all modes
  if (n.id === NODE0_ID) return "#ffffff";
  if (genesisTraceIds.size > 0) {{
    if (n.id === pulseNodeId)      return "#ffee00"; // pulse bead: bright yellow
    if (n.id === selectedTraceNode) return "#ff7700"; // selected: orange
    if (genesisTraceIds.has(n.id)) return "#ff3300"; // trace path: red
    if (traceOutwardIds.has(n.id)) return n.color;   // outward context: normal
    return "#151520";                                  // unrelated: dim
  }}
  if (spotlightAuth && !_isAuthority(n)) return "#151528";
  return n.color;
}}

function nodeSize(n) {{
  // Genesis root always large and prominent
  if (n.id === NODE0_ID) return 22;
  if (genesisTraceIds.size > 0) {{
    if (n.id === pulseNodeId)       return n.size * 3.0; // pulse bead: biggest
    if (n.id === selectedTraceNode) return n.size * 2.2; // selected: large
    if (genesisTraceIds.has(n.id))  return n.size * 1.5; // trace path: bigger
    if (traceOutwardIds.has(n.id))  return n.size;       // outward: normal
    return n.size * 0.3;                                  // unrelated: tiny
  }}
  if (spotlightAuth && !_isAuthority(n)) return 0.5;
  return n.size;
}}

function _isTraceEdge(l) {{
  const s = l.source?.id || l.source;
  const t = l.target?.id || l.target;
  return genesisTraceIds.has(s) && genesisTraceIds.has(t);
}}
function _isPulseEdge(l) {{
  if (!pulseNodeId) return false;
  const s = l.source?.id || l.source;
  const t = l.target?.id || l.target;
  // Edge between pulse bead and its neighbour on the path
  const idx = tracePathOrdered.indexOf(pulseNodeId);
  if (idx < 0) return false;
  const prev = tracePathOrdered[idx - 1];
  const next = tracePathOrdered[idx + 1];
  return (s === pulseNodeId || t === pulseNodeId) &&
         (s === prev || t === prev || s === next || t === next);
}}

function linkColor(l) {{
  if (genesisTraceIds.size === 0) return l.color || "#555";
  if (_isPulseEdge(l))  return "#ffee00"; // pulse adjacency: yellow
  if (_isTraceEdge(l))  return "#ff3300"; // trace path: red
  const s = l.source?.id || l.source;
  const t = l.target?.id || l.target;
  const sm = nodeMap[s], tm = nodeMap[t];
  if (sm && tm && (traceOutwardIds.has(s) || traceOutwardIds.has(t) ||
                   s === selectedTraceNode || t === selectedTraceNode))
    return l.color || "#555"; // outward context: normal
  return "#151520"; // unrelated: dim
}}

function linkWidth(l) {{
  if (_isPulseEdge(l))  return 4;
  if (_isTraceEdge(l))  return 3;
  return (l.type === "GOVERNS" || l.type === "ATTESTATION") ? 1.5 : 0.5;
}}

function visibleNodeCount() {{
  return RAW_NODES.filter(nodeVisible).length;
}}
function visibleLinkCount() {{
  return RAW_LINKS.filter(linkVisible).length;
}}
function _edgeEndpointId(value) {{
  return value && value.id ? value.id : value;
}}
function exportDegree(nodeId) {{
  return RAW_LINKS.filter(l =>
    _edgeEndpointId(l.source) === nodeId || _edgeEndpointId(l.target) === nodeId
  ).length;
}}
function visibleDegree(nodeId) {{
  return RAW_LINKS.filter(l => linkVisible(l) && (
    _edgeEndpointId(l.source) === nodeId || _edgeEndpointId(l.target) === nodeId
  )).length;
}}
function hiddenEdges(nodeId) {{
  const exp = exportDegree(nodeId);
  const vis = visibleDegree(nodeId);
  const hidden = exp - vis;
  const node = RAW_NODES.find(n => n.id === nodeId);
  const lmdb = node && node.degree_lmdb_total !== undefined && node.degree_lmdb_total !== null
    ? node.degree_lmdb_total : "—";
  return `${{hidden}} hidden / ${{lmdb}} total LMDB`;
}}

// ── graph — load full graph once, never replace graphData ────────────────
let traceOnClick = false;

const Graph = ForceGraph3D()(document.getElementById("graph"))
  .backgroundColor("#0d0d1a")
  .nodeId("id")
  .nodeLabel(n => `${{n.id}}\\n${{n.kind || ""}}`)
  .nodeColor(nodeColor)
  .nodeVal(nodeSize)
  .nodeOpacity(0.9)
  .nodeVisibility(nodeVisible)
  .linkColor(linkColor)
  .linkOpacity(0.85)
  .linkWidth(linkWidth)
  .linkVisibility(linkVisible)
  .linkDirectionalArrowLength(l =>
    (l.type === "GOVERNS" || l.type === "ATTESTATION") ? 4 : 0
  )
  .linkDirectionalArrowRelPos(1)
  .onNodeClick(n => {{
    if (traceOnClick) {{
      traceToGenesis(n.id);
      refresh();
    }}
    showInfo(n);
  }})
  .graphData({{ nodes: RAW_NODES, links: RAW_LINKS }});

// seed node count display and initial visible adjacency
(function() {{
  const vn = visibleNodeCount(), vl = visibleLinkCount();
  document.getElementById("node-count-display").textContent =
    `Visible: ${{vn.toLocaleString()}}n / ${{vl.toLocaleString()}}e (total: {node_count:,}n / {link_count:,}e)`;
  _rebuildVisAdj(RAW_LINKS.filter(linkVisible));
}})();

// ── debug: log visible counts after physics settles ───────────────────────
Graph.onEngineStop(() => {{
  const vn = visibleNodeCount(), vl = visibleLinkCount();
  const byGroup = {{}};
  RAW_NODES.filter(nodeVisible).forEach(n => {{ byGroup[n.group] = (byGroup[n.group]||0)+1; }});
  const breakdown = Object.entries(byGroup)
    .sort((a,b)=>b[1]-a[1])
    .map(([g,c])=>`${{g}}:${{c}}`)
    .join(' | ');
  console.log(`[ILC graph] visible=${{vn}}n/${{vl}}e total={node_count:,}n/{link_count:,}e`);
  console.log(`[ILC graph] breakdown: ${{breakdown}}`);
  document.getElementById("debug-log").textContent =
    `${{vn}}n/${{vl}}e visible | ${{breakdown}}`;
}});

{cluster_js}


// ── info panel ────────────────────────────────────────────────────────────
function showInfo(n) {{
  const panel = document.getElementById("info");
  panel.style.display = "block";
  document.getElementById("info-title").textContent = n.id === NODE0_ID
    ? "⭐ Node 0 — Genesis Authority Root" : n.id;
  const customUrl = SPRITE_BY_ID[n.id] || SPRITE_BY_GROUP[n.group];
  const traceLen = tracePathOrdered.length > 1
    ? `${{tracePathOrdered.length - 1}} hop(s) to Genesis` : "";
    const fields = [
    ["id",            n.id],
    ["kind",          n.kind],
    ["tier",          n.tier],
    ["group",         n.group],
    ["prefix",        n.prefix],
    ["authority_class", n.authority_class],
    ["projection",    n.projection],
    ["status",        n.status],
    ["lmdb_degree",   n.degree_lmdb_total !== undefined && n.degree_lmdb_total !== null ? n.degree_lmdb_total : "—"],
    ["export_degree", exportDegree(n.id)],
    ["visible_degree", visibleDegree(n.id)],
    ["hidden_edges",  hiddenEdges(n.id)],
    ["directed_hop",  n.directed_hop_from_root !== null && n.directed_hop_from_root !== undefined
                        ? n.directed_hop_from_root : "unreachable"],
    ["label",         n.label],
    ["sprite",        customUrl || "(default circle)"],
    ...(traceLen ? [["trace", traceLen]] : []),
  ];
  document.getElementById("info-body").innerHTML =
    fields.map(([k,v]) =>
      `<div class="field"><b>${{k}}:</b> ${{v||"—"}}</div>`
    ).join("");
  if (traceLen) {{
    document.getElementById("trace-info").textContent =
      `Path: ${{traceLen}}`;
  }}
}}

// ── controls ─────────────────────────────────────────────────────────────
function refresh() {{
  // Re-evaluate visibility/color/width — does NOT replace graphData or re-run physics.
  Graph.nodeColor(nodeColor).nodeVal(nodeSize).nodeVisibility(nodeVisible)
       .linkVisibility(linkVisible)
       .linkColor(linkColor)
       .linkWidth(linkWidth);
  const vn = visibleNodeCount(), vl = visibleLinkCount();
  _rebuildVisAdj(RAW_LINKS.filter(linkVisible));
  document.getElementById("node-count-display").textContent =
    `Visible: ${{vn.toLocaleString()}}n / ${{vl.toLocaleString()}}e (total: {node_count:,}n / {link_count:,}e)`;
}}

document.getElementById("search").addEventListener("input", e => {{
  searchTerm = e.target.value.trim();
  refresh();
}});
document.getElementById("chk-spotlight").addEventListener("change", e => {{
  spotlightAuth = e.target.checked; refresh();
}});
document.getElementById("chk-hide-generated").addEventListener("change", e => {{
  hideGenerated = e.target.checked; refresh();
}});
document.getElementById("chk-hide-private-history").addEventListener("change", e => {{
  hidePrivateHistory = e.target.checked; refresh();
}});
document.getElementById("chk-governs").addEventListener("change", e => {{
  showGoverns = e.target.checked; refresh();
}});
document.getElementById("chk-attestation").addEventListener("change", e => {{
  showAttest = e.target.checked; refresh();
}});
document.getElementById("chk-refs").addEventListener("change", e => {{
  showRefs = e.target.checked; refresh();
}});
document.getElementById("chk-classified").addEventListener("change", e => {{
  showClassified = e.target.checked; refresh();
}});
document.getElementById("chk-source-tree").addEventListener("change", e => {{
  showSourceTree = e.target.checked; refresh();
}});
document.getElementById("chk-contains").addEventListener("change", e => {{
  showContains = e.target.checked; refresh();
}});
document.getElementById("chk-imports").addEventListener("change", e => {{
  showImports = e.target.checked; refresh();
}});

document.getElementById("hop-slider").addEventListener("input", e => {{
  hopDepth = parseInt(e.target.value, 10);
  const lbl = document.getElementById("hop-label");
  const stats = document.getElementById("hop-stats");
  if (hopDepth === 0) {{
    lbl.textContent = "All";
    stats.textContent = "";
  }} else {{
    lbl.textContent = hopDepth;
    // Count nodes at exactly this hop and cumulatively
    const atThisHop  = RAW_NODES.filter(n => NODE_HOP[n.id] === hopDepth).length;
    const cumulative = RAW_NODES.filter(n => (NODE_HOP[n.id] ?? Infinity) <= hopDepth).length;
    stats.textContent = `Layer ${{hopDepth}}: ${{atThisHop}} new · ${{cumulative}} total`;
  }}
  refresh();
}});

let paused = false;
document.getElementById("btn-pause").addEventListener("click", () => {{
  paused = !paused;
  paused ? Graph.pauseAnimation() : Graph.resumeAnimation();
  document.getElementById("btn-pause").textContent = paused ? "Resume physics" : "Pause physics";
}});
document.getElementById("btn-reset").addEventListener("click", () => {{
  Graph.cameraPosition({{ x: 0, y: 0, z: 800 }}, {{ x:0, y:0, z:0 }}, 1000);
}});
document.getElementById("btn-trace").addEventListener("click", () => {{
  traceOnClick = !traceOnClick;
  document.getElementById("btn-trace").textContent =
    traceOnClick ? "Trace mode: ON (click a node)" : "Trace mode: OFF";
  document.getElementById("btn-trace").style.color = traceOnClick ? "#ff6644" : "";
  if (!traceOnClick) {{ clearTrace(); }}
}});
document.getElementById("btn-clear-trace").addEventListener("click", () => {{
  clearTrace();
  document.getElementById("trace-info").textContent = "";
}});
document.getElementById("btn-center").addEventListener("click", () => {{
  const n = Graph.graphData().nodes.find(x => x.id === NODE0_ID);
  if (n) Graph.cameraPosition(
    {{ x: n.x, y: n.y, z: (n.z||0) + 200 }},
    {{ x: n.x, y: n.y, z: n.z||0 }},
    1000
  );
}});
let radialOn = true;
document.getElementById("btn-radial").addEventListener("click", () => {{
  radialOn = !radialOn;
  if (radialOn) {{
    // re-register the force (same function as injected by Python)
    Graph.d3Force("radial", function(alpha) {{
      const str = 0.015 * alpha;
      Graph.graphData().nodes.forEach(function(n) {{
        const r = _RADIAL_TARGET[n.group];
        if (r === undefined) return;
        const cx = n.x||0, cy = n.y||0, cz = n.z||0;
        const dist = Math.sqrt(cx*cx+cy*cy+cz*cz)||1;
        const delta = (r - dist)*str;
        n.vx = (n.vx||0) + (cx/dist)*delta;
        n.vy = (n.vy||0) + (cy/dist)*delta;
        n.vz = (n.vz||0) + (cz/dist)*delta;
      }});
    }});
  }} else {{
    Graph.d3Force("radial", null);
  }}
  Graph.numDimensions(3);  // reheat simulation
  document.getElementById("btn-radial").textContent =
    radialOn ? "Radial layout: ON" : "Radial layout: OFF";
}});

// ── dynamic legend: per-group checkboxes ─────────────────────────────────
(function buildLegend() {{
  const counts = {{}};
  RAW_NODES.forEach(n => {{ counts[n.group] = (counts[n.group] || 0) + 1; }});
  const sorted = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const legend = document.getElementById("legend");
  sorted.forEach(([g, cnt]) => {{
    const color = NODE_COLORS[g] || "#cccccc";
    const isFixedGroup = g === "genesis_authority_root";
    const row = document.createElement("div");
    row.style.cssText = "display:flex;align-items:center;margin:2px 0;";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = true;
    cb.disabled = isFixedGroup;
    cb.title = isFixedGroup ? "Genesis authority root is always visible" : "";
    cb.style.cssText = `margin-right:4px;flex-shrink:0;cursor:${{isFixedGroup ? "not-allowed" : "pointer"}};`;
    cb.addEventListener("change", () => {{
      if (isFixedGroup) {{ hiddenGroups.delete(g); cb.checked = true; return; }}
      if (cb.checked) hiddenGroups.delete(g);
      else hiddenGroups.add(g);
      refresh();
    }});
    const dot = document.createElement("div");
    dot.style.cssText = `width:10px;height:10px;border-radius:50%;background:${{color}};margin-right:5px;flex-shrink:0;`;
    const lbl = document.createElement("span");
    lbl.style.cssText = "font-size:10px;color:#aaa;";
    lbl.textContent = `${{g}}: ${{cnt.toLocaleString()}}${{isFixedGroup ? " (fixed)" : ""}}`;
    row.appendChild(cb);
    row.appendChild(dot);
    row.appendChild(lbl);
    legend.appendChild(row);
  }});
}})();
</script>
</body>
</html>
"""


def _install_html(nodes: list, links: list) -> str:
    """Homoiconic install demo — phased bootstrap with terminal + 3D graph + info panel."""
    nodes_json = json.dumps(nodes, separators=(",", ":"))
    links_json = json.dumps(links, separators=(",", ":"))
    prefix_colors_js = _prefix_colors_js()
    edge_colors_js = "const EDGE_COLORS = " + json.dumps(EDGE_COLORS, separators=(",", ":")) + ";"
    total_nodes = len(nodes)
    total_links = len(links)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>ILC — Homoiconic Install</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #000; color: #eee; font-family: monospace;
    overflow: hidden; display: flex; flex-direction: column; height: 100vh;
  }}

  /* ── header ────────────────────────────────────────────────────────────── */
  #header {{
    display: flex; align-items: center; gap: 14px;
    padding: 7px 14px; background: #060608;
    border-bottom: 1px solid #181828; flex-shrink: 0;
  }}
  #header h1 {{ font-size: 12px; color: #ff9944; letter-spacing: 2px;
                text-transform: uppercase; white-space: nowrap; }}
  #progress-wrap {{ flex: 1; }}
  #progress-bar-bg {{
    background: #0d0d18; border: 1px solid #222; border-radius: 3px;
    height: 7px; overflow: hidden;
  }}
  #progress-bar-fill {{
    background: linear-gradient(90deg, #ff2244, #ff9944);
    height: 100%; width: 0%; transition: width 0.1s linear;
  }}
  #progress-label {{ font-size: 10px; color: #666; margin-top: 3px; }}
  #header-stats {{ font-size: 10px; color: #444; white-space: nowrap; }}

  /* ── main row ───────────────────────────────────────────────────────────── */
  #main {{ display: flex; flex: 1; overflow: hidden; }}

  /* ── left column ────────────────────────────────────────────────────────── */
  #left-col {{
    width: 290px; flex-shrink: 0; display: flex; flex-direction: column;
    border-right: 1px solid #111;
  }}

  /* invite row */
  #invite-row {{
    padding: 8px; gap: 5px; display: flex; flex-shrink: 0;
    border-bottom: 1px solid #111; background: #030306;
  }}
  #invite-input {{
    flex: 1; background: #0a0a14; border: 1px solid #222;
    color: #00ff41; font-family: monospace; font-size: 11px;
    padding: 5px 7px; border-radius: 3px; outline: none;
  }}
  #invite-input::placeholder {{ color: #1a2a1a; }}
  #invite-input:focus {{ border-color: #ff6644; box-shadow: 0 0 0 1px #ff664433; }}
  #invite-btn {{
    background: #cc3333; border: none; color: #fff;
    font-family: monospace; font-size: 11px;
    padding: 5px 10px; border-radius: 3px; cursor: pointer;
  }}
  #invite-btn:hover {{ background: #ff4444; }}
  #invite-btn:disabled {{ background: #331111; color: #555; cursor: default; }}

  /* terminal — compact height */
  #terminal-log {{
    height: 200px; flex-shrink: 0; overflow-y: auto;
    padding: 6px 9px; font-size: 10px; line-height: 1.6;
    background: #010104; border-bottom: 1px solid #111;
  }}
  .tl-sys  {{ color: #3a3a4a; font-style: italic; }}
  .tl-h0   {{ color: #ffffff; font-weight: bold; }}
  .tl-h1   {{ color: #ff4444; }}
  .tl-h2   {{ color: #ff9900; }}
  .tl-h3   {{ color: #ffcc00; }}
  .tl-h4   {{ color: #44ff88; }}
  .tl-h5   {{ color: #44ccff; }}
  .tl-deep {{ color: #00aa55; }}
  .tl-done {{ color: #ff9944; font-weight: bold; }}
  .tl-bridge {{ color: #888866; }}

  /* speed / controls */
  #left-controls {{
    padding: 7px 10px; border-bottom: 1px solid #111;
    flex-shrink: 0; background: #020208;
    display: flex; flex-wrap: wrap; gap: 5px; align-items: center;
  }}
  .ctrl-btn {{
    background: #0d0d1a; border: 1px solid #222; color: #999;
    font-size: 10px; font-family: monospace; padding: 3px 8px;
    border-radius: 3px; cursor: pointer;
  }}
  .ctrl-btn:hover {{ background: #1a1a33; color: #fff; }}
  #speed-row {{ display: flex; align-items: center; gap: 5px;
                font-size: 10px; color: #555; }}
  #speed-slider {{ width: 72px; accent-color: #ff6644; }}

  /* phase-2 choice panel */
  #phase2-panel {{
    display: none; padding: 10px; flex-shrink: 0;
    background: #05050e; border-bottom: 1px solid #1a1a2a;
    animation: fadein 0.5s ease;
  }}
  @keyframes fadein {{ from {{ opacity:0 }} to {{ opacity:1 }} }}
  #phase2-panel h3 {{ font-size: 11px; color: #ff9944; margin-bottom: 6px; }}
  #phase2-panel p  {{ font-size: 10px; color: #555; margin-bottom: 8px; line-height: 1.5; }}
  .choice-btn {{
    display: block; width: 100%; background: #0a0a1e; border: 1px solid #2a2a3a;
    color: #bbb; font-family: monospace; font-size: 11px;
    padding: 7px 10px; border-radius: 4px; cursor: pointer;
    text-align: left; margin-bottom: 5px; transition: background 0.15s;
  }}
  .choice-btn:hover {{ background: #1a1a44; border-color: #ff6644; color: #fff; }}
  .choice-btn .sub {{ font-size: 9px; color: #444; display: block; margin-top: 2px; }}

  /* hop slider */
  #hop-section {{
    padding: 7px 10px; flex-shrink: 0;
    border-bottom: 1px solid #111; background: #020208;
  }}
  #hop-section label {{ font-size: 10px; color: #444; display: block; margin-bottom: 3px; }}
  #hop-row {{ display: flex; align-items: center; gap: 6px; }}
  #hop-slider {{ flex: 1; accent-color: #ff6644; }}
  #hop-label {{ font-size: 11px; color: #ff9944; min-width: 26px; }}
  #hop-stats {{ font-size: 9px; color: #333; margin-top: 2px; }}

  /* edge + view filters */
  #edge-filters {{
    flex: 1; overflow-y: auto; padding: 8px 10px;
    background: #010104; font-size: 10px;
  }}
  #edge-filters .section-hd {{ color: #333; margin: 6px 0 3px; letter-spacing: 1px; }}
  #edge-filters label {{
    display: flex; align-items: center; gap: 5px;
    color: #666; margin: 2px 0; cursor: pointer;
  }}
  #edge-filters label:hover {{ color: #aaa; }}

  /* ── graph ──────────────────────────────────────────────────────────────── */
  #graph-pane {{ flex: 1; position: relative; overflow: hidden; }}
  #graph {{ position: absolute; inset: 0; }}
  #vis-overlay {{
    position: absolute; bottom: 8px; right: 8px; z-index: 5;
    background: rgba(0,0,0,0.55); border: 1px solid #1a1a2a;
    border-radius: 3px; padding: 4px 8px; font-size: 10px; color: #444;
  }}

  /* ── right column ────────────────────────────────────────────────────────── */
  #right-col {{
    width: 240px; flex-shrink: 0; display: flex; flex-direction: column;
    border-left: 1px solid #111; background: #020208; overflow-y: auto;
  }}
  /* legend first */
  #legend-section {{ padding: 10px; border-bottom: 1px solid #111; flex-shrink: 0; }}
  #legend-section h3 {{ font-size: 10px; color: #444; margin-bottom: 6px;
                        letter-spacing: 1px; text-transform: uppercase; }}
  .leg-row {{
    display: flex; align-items: center; gap: 5px;
    margin: 2px 0; cursor: pointer; user-select: none;
  }}
  .leg-dot {{ width: 9px; height: 9px; border-radius: 50%; flex-shrink: 0; }}
  .leg-label {{ font-size: 10px; color: #666; flex: 1; }}
  .leg-count {{ font-size: 10px; color: #333; }}
  /* node info below legend */
  #node-info {{ padding: 10px; flex-shrink: 0; }}
  #node-info h3 {{ font-size: 10px; color: #444; margin-bottom: 6px;
                   letter-spacing: 1px; text-transform: uppercase; }}
  .nf {{ font-size: 10px; color: #444; margin: 3px 0; word-break: break-all; line-height: 1.4; }}
  .nf b {{ color: #666; }}
  .nf-id {{ color: #888; }}
</style>
</head>
<body>

<div id="header">
  <h1>ILC — Homoiconic Install</h1>
  <div id="progress-wrap">
    <div id="progress-bar-bg"><div id="progress-bar-fill"></div></div>
    <div id="progress-label">Paste your invite command and press ENTER</div>
  </div>
  <div id="header-stats">{total_nodes:,} nodes · {total_links:,} edges</div>
</div>

<div id="main">

  <!-- ── LEFT COLUMN ─────────────────────────────────────────────────────── -->
  <div id="left-col">

    <div id="invite-row">
      <input id="invite-input" type="text"
             placeholder="Paste your invite command and press ENTER">
      <button id="invite-btn">ENTER</button>
    </div>

    <div id="terminal-log">
      <div class="tl-sys">$ _ Waiting for invite command…</div>
    </div>

    <div id="left-controls">
      <button class="ctrl-btn" id="btn-pause">Pause</button>
      <button class="ctrl-btn" id="btn-restart">Restart</button>
      <div id="speed-row">
        Speed:
        <input type="range" id="speed-slider" min="1" max="300" value="50">
        <span id="speed-label">50/s</span>
      </div>
    </div>

    <div id="phase2-panel">
      <h3>Genesis core installed.</h3>
      <p>Choose how to expand your local graph:</p>
      <button class="choice-btn" id="btn-full-genesis">
        Load full Genesis graph
        <span class="sub">All {total_nodes:,} nodes — specs, runtime, evidence, tools.
For contributors, auditors, and developers.</span>
      </button>
      <button class="choice-btn" id="btn-invite-chain">
        Invite chain only
        <span class="sub">Genesis core + attestation path from your inviting agent.
Minimal footprint for participation.</span>
      </button>
    </div>

    <div id="hop-section">
      <label>Hops from Genesis (filter view)</label>
      <div id="hop-row">
        <input type="range" id="hop-slider" min="0" max="30" value="0">
        <span id="hop-label">All</span>
      </div>
      <div id="hop-stats"></div>
    </div>

    <div id="edge-filters">
      <div class="section-hd">Edge types</div>
      <label><input type="checkbox" id="chk-governs" checked> GOVERNS</label>
      <label><input type="checkbox" id="chk-attestation" checked> ATTESTATION</label>
      <label><input type="checkbox" id="chk-refs" checked> REFERENCES_AUTHORITY</label>
      <label><input type="checkbox" id="chk-implements" checked> IMPLEMENTS / TESTS</label>
      <label><input type="checkbox" id="chk-derived" checked> DERIVED_FROM / EVIDENCES</label>
      <label><input type="checkbox" id="chk-source-tree" checked> SOURCE_TREE_MEMBER</label>
      <label><input type="checkbox" id="chk-contains" checked> CONTAINS_*</label>
      <label><input type="checkbox" id="chk-imports" checked> IMPORTS_MODULE</label>
      <div class="section-hd" style="margin-top:8px">View</div>
      <label><input type="checkbox" id="chk-hide-private" checked> Hide private history</label>
      <label><input type="checkbox" id="chk-spotlight"> Spotlight authority</label>
    </div>

  </div>

  <!-- ── GRAPH ───────────────────────────────────────────────────────────── -->
  <div id="graph-pane">
    <div id="graph"></div>
    <div id="vis-overlay">
      <span id="vis-count">0</span>n / <span id="vis-edge-count">0</span>e visible
    </div>
  </div>

  <!-- ── RIGHT COLUMN ────────────────────────────────────────────────────── -->
  <div id="right-col">

    <!-- legend first -->
    <div id="legend-section">
      <h3>Node Types</h3>
      <div id="legend"></div>
    </div>

    <!-- node info below -->
    <div id="node-info">
      <h3>Node Info</h3>
      <div id="nf-body">
        <div class="nf" style="color:#222">Click any node to inspect it.</div>
      </div>
    </div>

  </div>

</div>

<script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
<script src="https://unpkg.com/3d-force-graph@1.73.0/dist/3d-force-graph.min.js"></script>
<script>
const ALL_NODES = {nodes_json};
const ALL_LINKS = {links_json};
const NODE0_ID  = "{NODE0}";

{prefix_colors_js}
{edge_colors_js}

// ── index ──────────────────────────────────────────────────────────────────
const nodeMap = {{}};
ALL_NODES.forEach(n => {{ nodeMap[n.id] = n; }});

// ── BFS hop depth + order (undirected, full graph) ─────────────────────────
const NODE_HOP = {{}};
const BFS_ORDER = [];

(function computeBFS() {{
  const adj = {{}};
  ALL_LINKS.forEach(l => {{
    if (!adj[l.source]) adj[l.source] = [];
    if (!adj[l.target]) adj[l.target] = [];
    adj[l.source].push(l.target);
    adj[l.target].push(l.source);
  }});
  const queue = [NODE0_ID];
  NODE_HOP[NODE0_ID] = 0;
  while (queue.length) {{
    const curr = queue.shift();
    BFS_ORDER.push(curr);
    (adj[curr] || []).forEach(nb => {{
      if (NODE_HOP[nb] === undefined) {{
        NODE_HOP[nb] = NODE_HOP[curr] + 1;
        queue.push(nb);
      }}
    }});
  }}
  ALL_NODES.forEach(n => {{
    if (NODE_HOP[n.id] === undefined) {{
      NODE_HOP[n.id] = Infinity;
      BFS_ORDER.push(n.id);
    }}
  }});
  const maxHop = Math.max(...Object.values(NODE_HOP).filter(v => isFinite(v)));
  document.getElementById("hop-slider").max = maxHop;
}})();

// ── Phase sets ─────────────────────────────────────────────────────────────
// Phase 1 = authority nodes + bridge nodes (connect ≥2 authority nodes).
// Adding bridges gives 6,500+ edges instead of 81 — visually rich from the start.
// Phase 2a = full graph. Phase 2b = invite chain only.

const AUTHORITY_GROUPS = new Set([
  "truth_primitive","axiom","policy","artifact","genesis_authority_root","genesis_agent",
  "adr","cdl","ceremony","invariant"
]);

const AUTH_IDS = new Set(ALL_NODES.filter(n => AUTHORITY_GROUPS.has(n.group)).map(n => n.id));

// Count how many authority neighbors each non-authority node has
const authNeighborCount = {{}};
ALL_LINKS.forEach(l => {{
  const s = l.source, t = l.target;
  if (AUTH_IDS.has(s) && !AUTH_IDS.has(t)) {{
    authNeighborCount[t] = (authNeighborCount[t]||0) + 1;
  }}
  if (AUTH_IDS.has(t) && !AUTH_IDS.has(s)) {{
    authNeighborCount[s] = (authNeighborCount[s]||0) + 1;
  }}
}});
const BRIDGE_IDS = new Set(
  Object.entries(authNeighborCount)
    .filter(([,cnt]) => cnt >= 2)
    .map(([id]) => id)
);
const PHASE1_IDS = new Set([...AUTH_IDS, ...BRIDGE_IDS]);

const CORE_BFS  = BFS_ORDER.filter(id => PHASE1_IDS.has(id));
const REST_BFS  = BFS_ORDER.filter(id => !PHASE1_IDS.has(id));

// Invite chain: authority nodes + BFS path to furthest genesis_agent
function buildInviteChain() {{
  const agentNodes = ALL_NODES.filter(n => n.group === "genesis_agent")
    .sort((a,b) => (NODE_HOP[b.id]||0) - (NODE_HOP[a.id]||0));
  if (!agentNodes.length) return CORE_BFS.slice();
  const target = agentNodes[0].id;
  const adj = {{}};
  ALL_LINKS.forEach(l => {{
    if (!adj[l.source]) adj[l.source] = [];
    if (!adj[l.target]) adj[l.target] = [];
    adj[l.source].push(l.target);
    adj[l.target].push(l.source);
  }});
  const parent = {{ [NODE0_ID]: null }};
  const queue = [NODE0_ID];
  let found = false;
  while (queue.length && !found) {{
    const curr = queue.shift();
    for (const nb of (adj[curr]||[])) {{
      if (nb in parent) continue;
      parent[nb] = curr;
      if (nb === target) {{ found = true; break; }}
      queue.push(nb);
    }}
  }}
  if (!found) return CORE_BFS.slice();
  const path = [];
  let node = target;
  while (node !== null) {{ path.push(node); node = parent[node]; }}
  path.reverse();
  const chain = new Set([...PHASE1_IDS, ...path]);
  return BFS_ORDER.filter(id => chain.has(id));
}}

// ── filter state ───────────────────────────────────────────────────────────
let installedIds  = new Set();
let hopDepth      = 0;
let spotlightAuth = false;
let hidePrivate   = true;
let showGoverns   = true;
let showAttest    = true;
let showRefs      = true;
let showImpl      = true;
let showDerived   = true;
let showSrcTree   = true;
let showContains  = true;
let showImports   = true;
const hiddenGroups = new Set(["repo"]);  // repo hidden by default

const CONTAINS_TYPES = new Set(["CONTAINS_FILE","CONTAINS_GROUP","CONTAINS_PARTITION"]);

function nodeVisible(n) {{
  if (n.id === NODE0_ID) return true;
  if (!installedIds.has(n.id)) return false;
  if (hiddenGroups.has(n.group)) return false;
  if (hopDepth > 0 && (NODE_HOP[n.id]??Infinity) > hopDepth) return false;
  if (hidePrivate && n.tier === "genesis_private_historical_material") return false;
  return true;
}}
function linkVisible(l) {{
  const s = l.source?.id||l.source, t = l.target?.id||l.target;
  if (!installedIds.has(s)||!installedIds.has(t)) return false;
  const sm = nodeMap[s], tm = nodeMap[t];
  if (!sm||!nodeVisible(sm)||!tm||!nodeVisible(tm)) return false;
  if (spotlightAuth && !AUTHORITY_GROUPS.has(sm.group) && !AUTHORITY_GROUPS.has(tm.group)) return false;
  if (!showGoverns && l.type==="GOVERNS") return false;
  if (!showAttest  && l.type==="ATTESTATION") return false;
  if (!showRefs    && l.type==="REFERENCES_AUTHORITY") return false;
  if (!showImpl    && (l.type==="IMPLEMENTS"||l.type==="TESTS")) return false;
  if (!showDerived && (l.type==="DERIVED_FROM"||l.type==="EVIDENCES")) return false;
  if (!showSrcTree && l.type==="SOURCE_TREE_MEMBER") return false;
  if (!showContains && CONTAINS_TYPES.has(l.type)) return false;
  if (!showImports && l.type==="IMPORTS_MODULE") return false;
  return true;
}}

// ── NODE0 "OG" canvas sprite ───────────────────────────────────────────────
// THREE is loaded explicitly above, so it is a guaranteed global here.
let _ogSprite = null;
function _makeOGSprite() {{
  if (_ogSprite) return _ogSprite.clone();
  const size = 128;
  const canvas = document.createElement("canvas");
  canvas.width = size; canvas.height = size;
  const ctx = canvas.getContext("2d");
  // soft glow ring
  const grad = ctx.createRadialGradient(size/2,size/2,10, size/2,size/2,size/2-2);
  grad.addColorStop(0, "rgba(255,255,255,0.22)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  ctx.fillStyle = grad;
  ctx.beginPath(); ctx.arc(size/2,size/2,size/2-2,0,Math.PI*2); ctx.fill();
  // "OG" text — 30% larger than default NODE0 size
  ctx.fillStyle = "#ffffff";
  ctx.font = "bold 44px monospace";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillText("OG", size/2, size/2);
  const tex = new THREE.CanvasTexture(canvas);
  const mat = new THREE.SpriteMaterial({{ map: tex, depthWrite: false }});
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(38, 38, 1);
  _ogSprite = sprite;
  return sprite;
}}

// ── graph ──────────────────────────────────────────────────────────────────
const Graph = ForceGraph3D()(document.getElementById("graph"))
  .backgroundColor("#000000")
  .nodeId("id")
  .nodeLabel(n => n.id)
  .nodeColor(n => {{
    if (n.id === NODE0_ID) return "#ffffff";
    if (spotlightAuth && !AUTHORITY_GROUPS.has(n.group)) return "#0a0a18";
    return n.color;
  }})
  .nodeVal(n => n.id === NODE0_ID ? 28 : n.size)
  .nodeOpacity(0.92)
  .nodeVisibility(nodeVisible)
  // Return undefined (not null) for non-NODE0 nodes — undefined = use default sphere.
  // null would suppress rendering entirely for that node.
  .nodeThreeObject(n => n.id === NODE0_ID ? _makeOGSprite() : undefined)
  .nodeThreeObjectExtend(false)
  .linkColor(l => EDGE_COLORS[l.type]||"#2a2a2a")
  .linkOpacity(0.65)
  .linkWidth(l => (l.type==="GOVERNS"||l.type==="ATTESTATION") ? 1.5 : 0.5)
  .linkVisibility(linkVisible)
  .linkDirectionalArrowLength(l => (l.type==="GOVERNS"||l.type==="ATTESTATION") ? 4 : 0)
  .linkDirectionalArrowRelPos(1)
  .onNodeClick(showNodeInfo)
  .graphData({{ nodes: ALL_NODES, links: ALL_LINKS }});

Graph.d3Force("charge").strength(-40);
Graph.d3Force("radial", function(alpha) {{
  const radial = {{
    "truth_primitive":0,"genesis_agent":5,"axiom":20,"artifact":60,
    "policy":80,"cdl":120,"adr":120,"ceremony":120,
    "invariant":180,"claim":220,"repo":320,"other":260
  }};
  const str = 0.025 * alpha;
  Graph.graphData().nodes.forEach(function(n) {{
    if (!installedIds.has(n.id)) return;
    const r = radial[n.group] ?? 220;
    const cx=n.x||0,cy=n.y||0,cz=n.z||0;
    const dist=Math.sqrt(cx*cx+cy*cy+cz*cz)||1;
    const delta=(r-dist)*str;
    n.vx=(n.vx||0)+(cx/dist)*delta;
    n.vy=(n.vy||0)+(cy/dist)*delta;
    n.vz=(n.vz||0)+(cz/dist)*delta;
  }});
}});

function refresh() {{
  Graph.nodeColor(n => {{
    if (n.id===NODE0_ID) return "#ffffff";
    if (spotlightAuth&&!AUTHORITY_GROUPS.has(n.group)) return "#0a0a18";
    return n.color;
  }})
  .nodeVal(n => n.id===NODE0_ID ? 0 : n.size)
  .nodeVisibility(nodeVisible)
  .linkVisibility(linkVisible)
  .linkColor(l=>EDGE_COLORS[l.type]||"#2a2a2a")
  .linkWidth(l=>(l.type==="GOVERNS"||l.type==="ATTESTATION")?1.5:0.5);
  const vn = ALL_NODES.filter(nodeVisible).length;
  const ve = ALL_LINKS.filter(linkVisible).length;
  document.getElementById("vis-count").textContent = vn.toLocaleString();
  document.getElementById("vis-edge-count").textContent = ve.toLocaleString();
}}

// ── node info panel ─────────────────────────────────────────────────────────
function showNodeInfo(n) {{
  const hop = NODE_HOP[n.id];
  const isAuth = AUTHORITY_GROUPS.has(n.group);
  const fields = [
    ["id",    n.id],
    ["group", n.group + (isAuth ? " ★" : "")],
    ["prefix", n.prefix||"—"],
    ["authority_class", n.authority_class||"—"],
    ["kind",  n.kind||"—"],
    ["tier",  n.tier||"—"],
    ["hops",  isFinite(hop) ? hop : "unreachable"],
    ["label", n.label && n.label !== n.id ? n.label : "—"],
  ];
  document.getElementById("nf-body").innerHTML =
    fields.map(([k,v]) =>
      `<div class="nf ${{k==="id"?"nf-id":""}}"><b>${{k}}:</b> ${{v}}</div>`
    ).join("");
}}

// ── install engine ──────────────────────────────────────────────────────────
const log          = document.getElementById("terminal-log");
const progressFill = document.getElementById("progress-bar-fill");
const progressLabel= document.getElementById("progress-label");

let installQueue = [];
let installTotal = 0;
let installDone  = 0;
let installTimer = null;
let paused       = false;
let speedNPS     = 50;
let started      = false;
let phase        = 0;

function hopCls(h) {{
  if (!isFinite(h)) return "tl-deep";
  if (h===0) return "tl-h0";
  if (h<=5) return `tl-h${{h}}`;
  return "tl-deep";
}}
function appendLog(text, cls) {{
  const d = document.createElement("div");
  d.className = cls||"tl-deep";
  d.textContent = text;
  log.appendChild(d);
  log.scrollTop = log.scrollHeight;
}}
function updateProgress(n, total, label) {{
  const pct = total > 0 ? (n/total*100).toFixed(1) : "0.0";
  progressFill.style.width = pct + "%";
  progressLabel.textContent = label || `${{n.toLocaleString()}} / ${{total.toLocaleString()}} nodes (${{pct}}%)`;
}}

function revealNext() {{
  if (!installQueue.length) {{
    clearInterval(installTimer); installTimer = null;
    if (phase === 1) {{
      const authCount = [...installedIds].filter(id => AUTH_IDS.has(id)).length;
      const bridgeCount = [...installedIds].filter(id => BRIDGE_IDS.has(id)).length;
      appendLog("", "tl-sys");
      appendLog(`✓ Genesis core installed.`, "tl-h0");
      appendLog(`  ${{authCount.toLocaleString()}} authority nodes · ${{bridgeCount.toLocaleString()}} connector nodes`, "tl-sys");
      updateProgress(CORE_BFS.length, CORE_BFS.length,
        "Genesis core complete — choose how to expand ↓");
      document.getElementById("phase2-panel").style.display = "block";
    }} else {{
      // Final completion message
      const n = installedIds.size;
      appendLog("", "tl-sys");
      appendLog("✓ Bootstrap complete.", "tl-done");
      appendLog(`  ${{n.toLocaleString()}} nodes now in your local graph.`, "tl-sys");
      appendLog("", "tl-sys");
      appendLog("  Welcome to ILC.", "tl-h0");
      appendLog("  We are building the future together.", "tl-h3");
      updateProgress(n, n, `Bootstrap complete — ${{n.toLocaleString()}} nodes installed.`);
    }}
    refresh();
    return;
  }}
  const nodeId = installQueue.shift();
  installedIds.add(nodeId);
  installDone++;
  const hop = NODE_HOP[nodeId]??Infinity;
  const isBridge = BRIDGE_IDS.has(nodeId) && !AUTH_IDS.has(nodeId);
  const cls = isBridge ? "tl-bridge" : hopCls(hop);
  const hopStr = isFinite(hop) ? `hop ${{hop}}` : "orphan";
  const tag = isBridge ? "[bridge]" : `[${{hopStr.padStart(6)}}]`;
  appendLog(`[${{String(installDone).padStart(6)}}] ${{tag.padStart(9)}} ${{nodeId}}`, cls);
  updateProgress(installDone, installTotal,
    `Phase ${{phase}} — ${{installDone.toLocaleString()}} / ${{installTotal.toLocaleString()}}`);
  // Batch refresh every 5 nodes for performance
  if (installDone % 5 === 0 || installQueue.length === 0) refresh();
}}

function scheduleInstall() {{
  if (installTimer) clearInterval(installTimer);
  installTimer = setInterval(revealNext, Math.max(3, Math.round(1000/speedNPS)));
}}

function startPhase1(inviteCmd) {{
  if (started) return;
  started = true; phase = 1;
  appendLog("", "tl-sys");
  appendLog("$ " + (inviteCmd||"ilc agent install"), "tl-sys");
  appendLog("Verifying invite token…", "tl-sys");
  appendLog("Resolving genesis anchors…", "tl-sys");
  appendLog(`Preparing ${{CORE_BFS.length.toLocaleString()}} nodes (${{AUTH_IDS.size.toLocaleString()}} authority + ${{BRIDGE_IDS.size.toLocaleString()}} connectors)…`, "tl-sys");
  appendLog("", "tl-sys");
  appendLog("Phase 1 — Genesis authority graph:", "tl-h0");
  appendLog("", "tl-sys");
  installQueue = CORE_BFS.slice();
  installTotal = CORE_BFS.length;
  installDone  = 0;
  scheduleInstall();
}}

function startPhase2Full() {{
  document.getElementById("phase2-panel").style.display = "none";
  phase = 2;
  appendLog("", "tl-sys");
  appendLog("Phase 2 — Full Genesis graph:", "tl-sys");
  appendLog(`  Loading ${{REST_BFS.length.toLocaleString()}} additional nodes…`, "tl-sys");
  installQueue = REST_BFS.slice();
  installTotal = CORE_BFS.length + REST_BFS.length;
  installDone  = CORE_BFS.length;
  scheduleInstall();
}}

function startPhase2InviteChain() {{
  document.getElementById("phase2-panel").style.display = "none";
  phase = 2;
  appendLog("", "tl-sys");
  appendLog("Phase 2 — Invite attestation chain:", "tl-sys");
  appendLog("  Tracing provenance from your inviting agent…", "tl-sys");
  const chain = buildInviteChain();
  const newNodes = chain.filter(id => !installedIds.has(id));
  installQueue = newNodes;
  installTotal = installedIds.size + newNodes.length;
  installDone  = installedIds.size;
  scheduleInstall();
}}

// ── invite handler ──────────────────────────────────────────────────────────
function handleInvite() {{
  const val = document.getElementById("invite-input").value.trim();
  if (!val) return;
  document.getElementById("invite-input").disabled = true;
  document.getElementById("invite-btn").disabled = true;
  startPhase1(val);
}}
document.getElementById("invite-btn").addEventListener("click", handleInvite);
document.getElementById("invite-input").addEventListener("keydown", e => {{
  if (e.key === "Enter") handleInvite();
}});

document.getElementById("btn-full-genesis").addEventListener("click", startPhase2Full);
document.getElementById("btn-invite-chain").addEventListener("click", startPhase2InviteChain);

// ── controls ────────────────────────────────────────────────────────────────
document.getElementById("btn-pause").addEventListener("click", () => {{
  if (!started) return;
  paused = !paused;
  if (paused) {{ clearInterval(installTimer); installTimer=null; }}
  else scheduleInstall();
  document.getElementById("btn-pause").textContent = paused ? "Resume" : "Pause";
}});
document.getElementById("btn-restart").addEventListener("click", () => {{
  clearInterval(installTimer); installTimer=null;
  installedIds.clear(); installQueue=[]; installDone=0; installTotal=0;
  started=false; paused=false; phase=0;
  refresh();
  document.getElementById("phase2-panel").style.display = "none";
  document.getElementById("invite-input").disabled = false;
  document.getElementById("invite-btn").disabled = false;
  document.getElementById("invite-input").value = "";
  document.getElementById("btn-pause").textContent = "Pause";
  log.innerHTML = '<div class="tl-sys">$ _ Restarted. Paste your invite command above.</div>';
  progressFill.style.width="0%";
  progressLabel.textContent="Paste your invite command and press ENTER";
}});

document.getElementById("speed-slider").addEventListener("input", e => {{
  speedNPS = parseInt(e.target.value,10);
  document.getElementById("speed-label").textContent = speedNPS+"/s";
  if (installTimer) scheduleInstall();
}});

// ── hop slider ──────────────────────────────────────────────────────────────
document.getElementById("hop-slider").addEventListener("input", e => {{
  hopDepth = parseInt(e.target.value,10);
  const lbl = document.getElementById("hop-label");
  const stats = document.getElementById("hop-stats");
  if (hopDepth===0) {{ lbl.textContent="All"; stats.textContent=""; }}
  else {{
    lbl.textContent = hopDepth;
    const atHop = ALL_NODES.filter(n=>installedIds.has(n.id)&&NODE_HOP[n.id]===hopDepth).length;
    const cum   = ALL_NODES.filter(n=>installedIds.has(n.id)&&(NODE_HOP[n.id]??Infinity)<=hopDepth).length;
    stats.textContent = `Layer ${{hopDepth}}: ${{atHop}} new · ${{cum}} total`;
  }}
  refresh();
}});

// ── edge / view filters ─────────────────────────────────────────────────────
document.getElementById("chk-governs").addEventListener("change",   e=>{{showGoverns=e.target.checked;refresh();}});
document.getElementById("chk-attestation").addEventListener("change",e=>{{showAttest=e.target.checked;refresh();}});
document.getElementById("chk-refs").addEventListener("change",       e=>{{showRefs=e.target.checked;refresh();}});
document.getElementById("chk-implements").addEventListener("change", e=>{{showImpl=e.target.checked;refresh();}});
document.getElementById("chk-derived").addEventListener("change",    e=>{{showDerived=e.target.checked;refresh();}});
document.getElementById("chk-source-tree").addEventListener("change",e=>{{showSrcTree=e.target.checked;refresh();}});
document.getElementById("chk-contains").addEventListener("change",   e=>{{showContains=e.target.checked;refresh();}});
document.getElementById("chk-imports").addEventListener("change",    e=>{{showImports=e.target.checked;refresh();}});
document.getElementById("chk-hide-private").addEventListener("change",e=>{{hidePrivate=e.target.checked;refresh();}});
document.getElementById("chk-spotlight").addEventListener("change",  e=>{{spotlightAuth=e.target.checked;refresh();}});

// ── legend with repo crossed out by default ─────────────────────────────────
(function buildLegend() {{
  const counts = {{}};
  ALL_NODES.forEach(n => {{ counts[n.group]=(counts[n.group]||0)+1; }});
  const sorted = Object.entries(counts).sort((a,b)=>b[1]-a[1]);
  const legend = document.getElementById("legend");
  sorted.forEach(([g, cnt]) => {{
    const color = NODE_COLORS[g]||"#ccc";
    const isHiddenByDefault = g === "repo";
    const isFixedGroup = g === "genesis_authority_root";
    if (isHiddenByDefault) hiddenGroups.add(g);  // already in set but explicit
    const row = document.createElement("div");
    row.className = "leg-row";
    row.title = isFixedGroup ? "Genesis authority root is always visible" : "";
    const dot = document.createElement("div");
    dot.className = "leg-dot";
    dot.style.background = color;
    const lbl = document.createElement("span");
    lbl.className = "leg-label";
    lbl.textContent = isFixedGroup ? `${{g}} (fixed)` : g;
    const cnt_el = document.createElement("span");
    cnt_el.className = "leg-count";
    cnt_el.textContent = cnt.toLocaleString();
    row.appendChild(dot); row.appendChild(lbl); row.appendChild(cnt_el);

    let hidden = isHiddenByDefault;
    // Apply initial crossed-out state
    if (hidden) {{
      lbl.style.textDecoration = "line-through";
      dot.style.opacity = "0.2";
    }}
    row.addEventListener("click", () => {{
      if (isFixedGroup) {{ hiddenGroups.delete(g); hidden = false; refresh(); return; }}
      hidden = !hidden;
      if (hidden) hiddenGroups.add(g); else hiddenGroups.delete(g);
      lbl.style.textDecoration = hidden ? "line-through" : "";
      dot.style.opacity = hidden ? "0.2" : "1";
      refresh();
    }});
    legend.appendChild(row);
  }});
}})();
</script>
</body>
</html>
"""

def _export_lmdb_view(view: str) -> Path:
    output_path = DEFAULT_VIZ_EXPORT_DIR / f"graph_view_{view}.json"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "tools/graph_viz_export.py"),
        "--view",
        view,
        "--output-dir",
        str(DEFAULT_VIZ_EXPORT_DIR),
        "--omit-export-time",
    ]
    subprocess.run(cmd, cwd=REPO_ROOT, check=True)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate 3D force-graph visualisation of a Genesis Atlas candidate.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input",      default=str(DEFAULT_INPUT),  help="Atlas JSON path")
    parser.add_argument("--output",     default=str(DEFAULT_OUTPUT), help="HTML output path")
    parser.add_argument("--open",       action="store_true",         help="Open in browser after writing")
    parser.add_argument("--lmdb",       action="store_true",         help="Export view JSON from Fix41 LMDB before rendering")
    parser.add_argument(
        "--view",
        default="public-material",
        choices=("all-local", "public-material", "private-local", "governance", "authority-core", "test-registry"),
        help="LMDB view to export when --lmdb is used",
    )
    parser.add_argument("--core-only",  action="store_true",         help="Pre-filter to authority nodes only")
    parser.add_argument("--max-nodes",  type=int, default=None,      help="Hard cap on node count")
    parser.add_argument("--sprites",      default=None,                help="JSON sprite manifest path")
    parser.add_argument(
        "--install-demo",
        action="store_true",
        help=(
            "Generate the homoiconic install demo: split terminal + live 3D graph "
            "that grows from NODE0 outward in BFS order. "
            "Output to graphify-out/graph_install_demo.html by default."
        ),
    )
    args = parser.parse_args()

    inp = _export_lmdb_view(args.view) if args.lmdb else Path(args.input)
    out = Path(args.output)

    if not inp.exists():
        print(f"ERROR: input not found: {inp}", file=sys.stderr)
        sys.exit(1)

    sprite_manifest: dict | None = None
    if args.sprites:
        sp = Path(args.sprites)
        if not sp.exists():
            print(f"ERROR: sprite manifest not found: {sp}", file=sys.stderr)
            sys.exit(1)
        sprite_manifest = json.loads(sp.read_text(encoding="utf-8"))
        print(f"Sprite manifest loaded: {sp}", file=sys.stderr)

    print(f"Loading {inp} …", file=sys.stderr)
    graph = json.loads(inp.read_text(encoding="utf-8"))

    print("Building graph data …", file=sys.stderr)
    nodes, links = _build_graph_data(graph, max_nodes=args.max_nodes)
    print(f"  {len(nodes):,} nodes, {len(links):,} links", file=sys.stderr)

    if args.install_demo:
        html = _install_html(nodes, links)
        out = out.parent / "graph_install_demo.html" if args.output == str(DEFAULT_OUTPUT) else out
    else:
        title = f"ILC Genesis Atlas ({len(nodes):,}n / {len(links):,}e)"
        html  = _html(
            nodes,
            links,
            title,
            sprite_manifest=sprite_manifest,
            core_only=args.core_only,
            metadata=graph.get("metadata") if isinstance(graph.get("metadata"), dict) else {},
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(out.parent), prefix=".graph_3d.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(html)
        os.replace(tmp, out)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise

    print(f"Written → {out}", file=sys.stderr)

    if args.open:
        subprocess.Popen(["open", str(out)])


if __name__ == "__main__":
    main()
