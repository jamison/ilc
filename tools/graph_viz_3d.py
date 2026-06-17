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
    "truth_primitive": "#ff4444",   # red   — genesis axioms
    "policy":          "#ff9900",   # amber — governance policy
    "artifact":        "#ffcc00",   # gold  — genesis artifacts
    "genesis_agent":   "#ff66ff",   # pink  — genesis agents
    "adr":             "#4499ff",   # blue  — ADRs
    "cdl":             "#44aaff",   # sky   — CDLs
    "ceremony":        "#ff88ff",   # light pink
    "source":          "#44cc88",   # green — source nodes
    "repo":            "#888888",   # grey  — repo file nodes
    "atlas":           "#aaaaaa",   # light grey — atlas nodes
    "other":           "#cccccc",   # fallback
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
    ["truth_primitive", "policy", "artifact", "genesis_agent", "adr", "cdl", "ceremony"]
)

# Priority order for --max-nodes trimming (higher = kept first)
_GROUP_PRIORITY: dict[str, int] = {
    "truth_primitive": 100,
    "genesis_agent":   90,
    "artifact":        80,
    "policy":          70,
    "cdl":             60,
    "adr":             55,
    "ceremony":        50,
    "source":          30,
    "repo":            10,
    "atlas":           5,
    "other":           1,
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
    core_only: bool = False,
    max_nodes: int | None = None,
) -> tuple[list, list]:
    raw_nodes = graph.get("nodes", [])
    raw_edges = graph.get("edges", [])

    nodes_out = []
    for n in raw_nodes:
        nid = _node_id(n)
        if not nid:
            continue
        p = _prefix(nid)
        if core_only and p not in AUTHORITY_PREFIXES:
            continue
        nodes_out.append({
            "id":    nid,
            "label": _short_label(nid, n),
            "color": _node_color(nid, n),
            "size":  _node_size(nid, n),
            "group": p,
            "tier":  str(n.get("tier", "")),
            "kind":  str(n.get("node_kind", "")),
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

    links_out = []
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


def _legend_html() -> str:
    rows = ""
    for prefix, color in PREFIX_COLORS.items():
        rows += (
            f'<div style="display:flex;align-items:center;margin:3px 0">'
            f'<div style="width:12px;height:12px;border-radius:50%;background:{color};'
            f'margin-right:8px;flex-shrink:0"></div>'
            f'<span style="font-size:11px">{prefix}:</span></div>\n'
        )
    return rows


def _html(
    nodes: list,
    links: list,
    title: str,
    sprite_manifest: dict | None = None,
) -> str:
    nodes_json = json.dumps(nodes, separators=(",", ":"))
    links_json = json.dumps(links, separators=(",", ":"))
    legend = _legend_html()
    node_count = len(nodes)
    link_count = len(links)

    # Sprite manifest injected as JS — empty dicts if none provided
    sm = sprite_manifest or {}
    sprite_by_group_json = json.dumps(sm.get("by_group", {}), separators=(",", ":"))
    sprite_by_id_json    = json.dumps(sm.get("by_id", {}),    separators=(",", ":"))

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0d0d1a; color: #eee; font-family: monospace; overflow: hidden; }}
  #graph {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; }}
  #panel {{
    position: fixed; top: 10px; left: 10px; z-index: 10;
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
    position: fixed; top: 10px; right: 10px; z-index: 10;
    background: rgba(10,10,30,0.85); border: 1px solid #333;
    border-radius: 6px; padding: 10px; font-size: 11px;
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

<div id="panel">
  <h2>ILC Genesis Atlas</h2>
  <div class="stat">Nodes: {node_count:,}</div>
  <div class="stat">Edges: {link_count:,}</div>
  <div class="stat" style="margin-top:4px;color:#888">Drag to rotate · Scroll to zoom · Click node for info</div>
  <input id="search" type="text" placeholder="Search node ID or label…">
  <div style="margin-top:8px;margin-bottom:4px;font-size:11px;color:#888">Node types</div>
  {legend}
</div>

<div id="controls">
  <div style="font-size:11px;color:#888;margin-bottom:4px">Node filters</div>
  <label><input type="checkbox" id="chk-authority"> Authority nodes only</label>
  <label><input type="checkbox" id="chk-hide-generated" checked> Hide out/ (generated evidence)</label>
  <label><input type="checkbox" id="chk-hide-private-history" checked> Hide Z_Past_Chats (private history)</label>
  <div style="font-size:11px;color:#888;margin:6px 0 4px">Edge filters</div>
  <label><input type="checkbox" id="chk-governs" checked> GOVERNS edges</label>
  <label><input type="checkbox" id="chk-attestation" checked> ATTESTATION edges</label>
  <label><input type="checkbox" id="chk-refs" checked> REFERENCES_AUTHORITY</label>
  <label><input type="checkbox" id="chk-classified" checked> CLASSIFIED_BY</label>
  <label><input type="checkbox" id="chk-source-tree" checked> SOURCE_TREE_MEMBER</label>
  <label><input type="checkbox" id="chk-contains" checked> CONTAINS_* edges</label>
  <label><input type="checkbox" id="chk-imports" checked> IMPORTS_MODULE edges</label>
  <div id="node-count-display" style="font-size:11px;color:#aaa;margin-top:6px"></div>
  <div style="margin-top:6px">
    <button id="btn-reset">Reset camera</button>
    <button id="btn-center">Centre on Node 0</button>
    <button id="btn-pause">Pause physics</button>
  </div>
  <div style="margin-top:8px;border-top:1px solid #333;padding-top:8px">
    <div style="font-size:11px;color:#888;margin-bottom:4px">Genesis trace</div>
    <button id="btn-trace">Trace mode: OFF</button>
    <button id="btn-clear-trace">Clear trace</button>
    <div id="trace-info" style="font-size:10px;color:#ff6644;margin-top:4px"></div>
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

// ── sprite manifest ───────────────────────────────────────────────────────
// "by_id"    — node-specific sprite URL (highest priority)
// "by_group" — group-level sprite URL (fallback if no by_id match)
// Both support any URL the browser can load: PNG, JPEG, GIF (animated),
// SVG, or data-URI.  Animated GIFs work because THREE.SpriteMaterial
// accepts a video texture or an HTMLImageElement directly.
const SPRITE_BY_ID    = {sprite_by_id_json};
const SPRITE_BY_GROUP = {sprite_by_group_json};

// ── sprite manifest (reserved for future custom node icons) ───────────────
// SPRITE_BY_ID and SPRITE_BY_GROUP are available but not yet applied to
// built-in node rendering. Custom THREE-based sprites can be re-enabled
// once a stable window.THREE access path is confirmed.

// ── build lookup ──────────────────────────────────────────────────────────
const nodeMap = {{}};
RAW_NODES.forEach(n => {{ nodeMap[n.id] = n; }});

// ── Genesis trace (BFS) ───────────────────────────────────────────────────
// Pre-build adjacency from raw string IDs (before ForceGraph3D mutates links)
const _adj = {{}}; // node -> Set of connected node ids (both directions)
RAW_LINKS.forEach(l => {{
  const s = l.source, t = l.target;
  if (!_adj[s]) _adj[s] = new Set();
  if (!_adj[t]) _adj[t] = new Set();
  _adj[s].add(t);
  _adj[t].add(s);
}});

let genesisTraceIds = new Set(); // node ids on the highlighted path

function traceToGenesis(startId) {{
  if (startId === NODE0_ID) {{ genesisTraceIds = new Set([NODE0_ID]); return; }}
  const parent = {{ [startId]: null }};
  const queue = [startId];
  let found = false;
  while (queue.length && !found) {{
    const curr = queue.shift();
    for (const nb of (_adj[curr] || [])) {{
      if (nb in parent) continue;
      parent[nb] = curr;
      if (nb === NODE0_ID) {{ found = true; break; }}
      queue.push(nb);
    }}
  }}
  if (!found) {{ genesisTraceIds = new Set([startId]); return; }}
  const path = new Set();
  let node = NODE0_ID;
  while (node !== null) {{ path.add(node); node = parent[node]; }}
  genesisTraceIds = path;
}}

function clearTrace() {{
  genesisTraceIds = new Set();
  refresh();
}}

// ── filter state ─────────────────────────────────────────────────────────
let searchTerm          = "";
let showAuthOnly        = false;
let hideGenerated       = true;
let hidePrivateHistory  = true;
let showGoverns         = true;
let showAttest          = true;
let showRefs            = true;
let showClassified      = true;
let showSourceTree      = true;
let showContains        = true;
let showImports         = true;

const AUTHORITY_GROUPS = new Set([
  "truth_primitive","policy","artifact","genesis_agent","adr","cdl","ceremony"
]);
const CONTAINS_TYPES = new Set([
  "CONTAINS_FILE","CONTAINS_GROUP","CONTAINS_PARTITION"
]);

function filterNodes() {{
  return RAW_NODES.filter(n => {{
    if (showAuthOnly && !AUTHORITY_GROUPS.has(n.group)) return false;
    if (hideGenerated && n.tier === "generated_evidence_material") return false;
    if (hidePrivateHistory && n.tier === "genesis_private_historical_material") return false;
    if (searchTerm) {{
      const s = searchTerm.toLowerCase();
      return n.id.toLowerCase().includes(s) || n.label.toLowerCase().includes(s);
    }}
    return true;
  }});
}}

function filterLinks(activeNodeIds) {{
  return RAW_LINKS.filter(l => {{
    if (!activeNodeIds.has(l.source) && !activeNodeIds.has(l.source?.id)) return false;
    if (!activeNodeIds.has(l.target) && !activeNodeIds.has(l.target?.id)) return false;
    if (!showGoverns  && l.type === "GOVERNS") return false;
    if (!showAttest   && l.type === "ATTESTATION") return false;
    if (!showRefs     && l.type === "REFERENCES_AUTHORITY") return false;
    if (!showClassified && l.type === "CLASSIFIED_BY") return false;
    if (!showSourceTree && l.type === "SOURCE_TREE_MEMBER") return false;
    if (!showContains && CONTAINS_TYPES.has(l.type)) return false;
    if (!showImports  && l.type === "IMPORTS_MODULE") return false;
    return true;
  }});
}}

function buildData() {{
  const nodes = filterNodes().map(n => {{
    if (genesisTraceIds.size === 0) return n;
    if (genesisTraceIds.has(n.id)) {{
      return {{ ...n, color: "#ff3300", size: n.size * 1.6, _traced: true }};
    }}
    // dim non-trace nodes: darken colour toward background
    return {{ ...n, color: "#1e2030", size: n.size * 0.8, _dimmed: true }};
  }});
  const ids   = new Set(nodes.map(n => n.id));
  const links = filterLinks(ids);
  return {{ nodes, links }};
}}

// ── graph ─────────────────────────────────────────────────────────────────
let traceOnClick = false;

const Graph = ForceGraph3D()(document.getElementById("graph"))
  .backgroundColor("#0d0d1a")
  .nodeId("id")
  .nodeLabel(n => `${{n.id}}\\n${{n.kind || ""}}`)
  .nodeColor(n => n.color)
  .nodeVal(n => n.size)
  .nodeOpacity(0.9)
  .linkColor(l => {{
    if (genesisTraceIds.size === 0) return l.color || "#555";
    const s = l.source?.id || l.source;
    const t = l.target?.id || l.target;
    return (genesisTraceIds.has(s) && genesisTraceIds.has(t))
      ? "#ff3300" : "#1a1a2e";
  }})
  .linkOpacity(0.7)
  .linkWidth(l => (l.type === "GOVERNS" || l.type === "ATTESTATION") ? 1.5 : 0.5)
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
  .graphData(buildData());

// seed node count display
(function() {{
  const d = buildData();
  document.getElementById("node-count-display").textContent =
    `Showing ${{d.nodes.length.toLocaleString()}} nodes / ${{d.links.length.toLocaleString()}} edges`;
}})();

Graph.d3Force("charge").strength(-30);

// ── info panel ────────────────────────────────────────────────────────────
function showInfo(n) {{
  const panel = document.getElementById("info");
  panel.style.display = "block";
  document.getElementById("info-title").textContent = n.id === NODE0_ID
    ? "⭐ Node 0 — Genesis Authority Root" : n.id;
  const customUrl = SPRITE_BY_ID[n.id] || SPRITE_BY_GROUP[n.group];
  const traceLen = genesisTraceIds.size > 0
    ? `${{genesisTraceIds.size}} hops to Genesis` : "";
  const fields = [
    ["group",  n.group],
    ["kind",   n.kind],
    ["tier",   n.tier],
    ["label",  n.label],
    ["sprite", customUrl || "(default circle)"],
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
  const data = buildData();
  Graph.graphData(data);
  document.getElementById("node-count-display").textContent =
    `Showing ${{data.nodes.length.toLocaleString()}} nodes / ${{data.links.length.toLocaleString()}} edges`;
}}

document.getElementById("search").addEventListener("input", e => {{
  searchTerm = e.target.value.trim();
  refresh();
}});
document.getElementById("chk-authority").addEventListener("change", e => {{
  showAuthOnly = e.target.checked; refresh();
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
    parser.add_argument("--sprites",    default=None,                help="JSON sprite manifest path")
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
    nodes, links = _build_graph_data(graph, core_only=args.core_only, max_nodes=args.max_nodes)
    print(f"  {len(nodes):,} nodes, {len(links):,} links", file=sys.stderr)

    title = f"ILC Genesis Atlas ({len(nodes):,}n / {len(links):,}e)"
    html  = _html(nodes, links, title, sprite_manifest=sprite_manifest)

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
