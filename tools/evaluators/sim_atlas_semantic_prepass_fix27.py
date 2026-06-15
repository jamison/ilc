#!/usr/bin/env python3
"""Fix27 semantic pre-pass classifier.

Implements discovered patterns P1-P29 over the Fix26 deferred queue.
Skips files already marked `manually_annotated=True` in the Fix22 graph.

Pattern inventory:
  P1  — Python import / Rust use statements → IMPORTS_MODULE
  P2  — CDL_NNN_DEPENDENCY / CDL_VN_DEPENDENCY AST assignments → REFERENCES_AUTHORITY
  P3  — Anchor: <path> declarations in markdown → REFERENCES_AUTHORITY
  P4  — Phase prompt "Inputs to read first" / "Required inputs" → REFERENCES_AUTHORITY
  P5  — Test file path constants (ROOT / "...") → TESTS / REFERENCES_AUTHORITY
  P6  — Phase number → window sequence lock deterministic mapping → REFERENCES_AUTHORITY
  P7  — Sim notes referencing tool scripts → EVIDENCES
  P8  — Walkthrough "Files touched" / "Main implementation commit" → REFERENCES_AUTHORITY
  P9  — graph_delta= annotations → REFERENCES_AUTHORITY / EVIDENCES
  P10 — Walkthrough claim audit table (confirmed rows) → REFERENCES_AUTHORITY
  P11 — Walkthrough "Files Changed" table (markdown links + plain paths) → REFERENCES_AUTHORITY
  P12 — Numbered ingestion order / required reading lists → REFERENCES_AUTHORITY
  P13 — Spec front-matter Related artifacts / Primary roadmap anchor → REFERENCES_AUTHORITY
  P14 — "Inputs Verified" / "Read and consumed" bullet sections → REFERENCES_AUTHORITY
  P15 — JSON structural keys (source_ref, governing_adr, evidence_refs, …) → REFERENCES_AUTHORITY / EVIDENCES
  P16 — Shell script pytest / validate_phase_prompt / path variable assignments → TESTS / REFERENCES_AUTHORITY
  P17 — CDL ratification evidence docs → EVIDENCES (CDL register)
  P18 — Non-phase-doc global bullet list backtick paths → REFERENCES_AUTHORITY
  P19 — Table cell backtick docs/ paths in any markdown → REFERENCES_AUTHORITY
  P20 — git diff/show/log -- path commands → REFERENCES_AUTHORITY
  P21 — Phase prompt deliverables fenced block paths → REFERENCES_AUTHORITY
  P22 — "In scope" / "Scope" section paths in phase prompts → REFERENCES_AUTHORITY
  P23 — Prose CDL-NNN / ADR-NNNN mentions resolved to CDL/ADR nodes → REFERENCES_AUTHORITY
  P24 — Multi-line bash array pytest (python3 -m pytest then indented paths) → TESTS
  P25 — Shell scripts calling tools/*.py runners → REFERENCES_AUTHORITY
  P26 — Pytest in fenced code blocks + test paths in section headings → TESTS
  P27 — Phase→seqlock mapping variant for alternate filename formats → REFERENCES_AUTHORITY
  P28 — Inline backtick-wrapped relative file paths in MD prose → REFERENCES_AUTHORITY / TESTS
  P29 — Absolute filesystem paths in MD markdown links (Atlas turn logs) → REFERENCES_AUTHORITY / TESTS

BOUNDARY NOTE: This script was originally used to write edges directly into
out/genesis_atlas_full_repo_candidate_1545p_fix22.json. That was incorrect —
Fix22 is the signing-preimage baseline and must not be mutated. The correct
output for pre-pass edge candidates is a separate JSONL artifact:
  out/atlas_research/genesis_atlas_semantic_prepass_fix27.jsonl
The enriched graph (Fix22 + pre-pass + manual annotations) lives at:
  out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json

Run:
    python3 tools/evaluators/sim_atlas_semantic_prepass_fix27.py \
        --annotation-graph out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json \
        [--batch N] [--compare-manual]

Without --annotation-graph the script operates against the restored Fix22 baseline,
which has no manually_annotated / prepass_annotated flags. All deferred files will
be treated as unannotated and processed again. Use --annotation-graph to reproduce
the original pre-pass skip behaviour.

Outputs:
    out/atlas_research/genesis_atlas_semantic_prepass_fix27.jsonl
    out/sim_atlas_semantic_prepass_fix27.json
"""

from __future__ import annotations

import ast
import json
import os
import re
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FIX22_GRAPH = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
FIX26_QUEUE = REPO_ROOT / "out/atlas_research/genesis_atlas_atom_candidates_1545p_fix26.jsonl"
EDGE_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_semantic_prepass_fix27.jsonl"
JSON_OUT = REPO_ROOT / "out/sim_atlas_semantic_prepass_fix27.json"

CDL_REGISTER = "docs/specs/ilc_constitutional_decision_log_v0.1.md"

# ── P1 helpers ────────────────────────────────────────────────────────────────

def _module_to_path(
    module: str,
    label_to_id: dict[str, str],
    src_dir: str = "",
) -> str | None:
    """Resolve a Python dotted module to the most likely repo path.

    src_dir: directory of the source file (e.g. "ilc_core/epoch") used to
    resolve unqualified relative imports like `from epoch_emission_runtime import`.
    """
    as_path = module.replace(".", "/") + ".py"
    if as_path in label_to_id:
        return as_path
    # Try __init__.py
    init = module.replace(".", "/") + "/__init__.py"
    if init in label_to_id:
        return init
    # Unqualified name (no dots) in ilc_core/ — try same-directory resolution
    if "." not in module and src_dir:
        sibling = src_dir.rstrip("/") + "/" + module + ".py"
        if sibling in label_to_id:
            return sibling
    return None


def _rust_module_to_path(use_path: str, label_to_id: dict[str, str]) -> str | None:
    """Resolve a `use ilc_consensus::a::b` path to a source file."""
    parts = use_path.replace("ilc_consensus::", "").split("::")
    base = "ilc_consensus/src/" + "/".join(parts)
    for candidate in [base + ".rs", base + "/mod.rs"]:
        if candidate in label_to_id:
            return candidate
    return None


def _p1_edge_type(src_path: str) -> str:
    """Choose edge type for import based on source file location."""
    if src_path.startswith("tests/"):
        return "TESTS"
    if src_path.startswith("tools/") or src_path.startswith("simulations/"):
        return "IMPLEMENTS"
    return "IMPORTS_MODULE"


def _p1_py(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P1: Python imports → TESTS (test files), IMPLEMENTS (tools/sims), IMPORTS_MODULE (ilc_core)."""
    edges = []
    etype = _p1_edge_type(src_path)
    src_dir = str(Path(src_path).parent)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return edges
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            resolved = _module_to_path(node.module, label_to_id, src_dir)
            if resolved and resolved != src_path:
                edges.append((resolved, etype, f"P1:from {node.module} import ..."))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                resolved = _module_to_path(alias.name, label_to_id, src_dir)
                if resolved and resolved != src_path:
                    edges.append((resolved, etype, f"P1:import {alias.name}"))
    return edges


def _p1_rs(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P1: Rust use statements → IMPORTS_MODULE."""
    edges = []
    for m in re.finditer(r"use\s+(ilc_consensus::[^\s;{]+)", text):
        resolved = _rust_module_to_path(m.group(1), label_to_id)
        if resolved and resolved != src_path:
            edges.append((resolved, "IMPORTS_MODULE", f"P1:use {m.group(1)}"))
    return edges


def _p2_py(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P2: CDL_NNN_DEPENDENCY / CDL_VN_DEPENDENCY constants → REFERENCES_AUTHORITY."""
    edges = []
    if CDL_REGISTER in label_to_id:
        for m in re.finditer(r'CDL_(?:0*(\d+)|V(\d+))_DEPENDENCY\s*=', text):
            edges.append((CDL_REGISTER, "REFERENCES_AUTHORITY",
                          f"P2:CDL_{m.group(1) or 'V'+m.group(2)}_DEPENDENCY constant"))
    return edges


def _p3_md(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P3: Markdown Anchor: declarations → REFERENCES_AUTHORITY."""
    edges = []
    for m in re.finditer(r"^Anchor:\s+(\S+)", text, re.MULTILINE | re.IGNORECASE):
        tgt = m.group(1).strip("`")
        if tgt in label_to_id and tgt != src_path:
            edges.append((tgt, "REFERENCES_AUTHORITY", "P3:Anchor: declaration"))
    return edges


def _p4_md(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P4: Phase prompt 'Inputs to read first' / 'Required inputs' → REFERENCES_AUTHORITY."""
    edges = []
    in_section = False
    for line in text.splitlines():
        if re.match(r"^#{1,3}\s*(Inputs to read first|Required inputs)", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and re.match(r"^#", line):
            in_section = False
        if not in_section:
            continue
        m = re.search(r"`((?:docs|ilc_core|tests|tools|simulations|out)/[^`]+)`", line)
        if m:
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P4:Inputs to read first"))
    return edges


_PATH_RHS = re.compile(
    r'(?:ROOT\s*/\s*|Path\s*\(\s*)'
    r'"((?:docs|ilc_core|tests|tools|out|simulations)[^"]+)"'
)

_AUTHORITY_VAR_TOKENS = ("SOURCE", "AUTHORITY", "CANON", "CDL_", "ADR_", "_REFS", "ANCHOR")

def _p5_target_edge_type(tgt: str, var_name: str = "") -> str:
    """Choose edge type for a path constant target in a test/tool file.

    ADRs are always REFERENCES_AUTHORITY (governing decisions).
    When a SET/LIST variable name signals an authority-citation collection
    (SOURCE_PATHS, AUTHORITY_DOCS, CANON_PATHS, etc.), ALL its members become
    REFERENCES_AUTHORITY regardless of whether they are docs/ or ilc_core/.
    Otherwise: ilc_core/, tests/, docs/phases/ → TESTS.
    """
    if tgt.startswith("docs/adr/"):
        return "REFERENCES_AUTHORITY"
    name_up = var_name.upper()
    if any(tok in name_up for tok in _AUTHORITY_VAR_TOKENS):
        return "REFERENCES_AUTHORITY"
    if tgt.startswith("docs/specs/") or tgt.startswith("docs/antigravity_tasks/"):
        return "TESTS"
    return "TESTS"


def _p5_py(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P5: Test file path constants → TESTS or REFERENCES_AUTHORITY.

    Individual Path() / ROOT / "..." assignments → TESTS (verifying artifact exists).
    Set/list/tuple literals → pass variable name to _p5_target_edge_type so that
    SOURCE_PATHS-style authority-citation sets get REFERENCES_AUTHORITY for docs/.
    """
    edges = []
    if not (src_path.startswith("tests/") or src_path.startswith("tools/")):
        return edges
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return edges
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        # Infer variable name from assignment target
        var_name = ""
        if node.targets and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id

        if isinstance(node.value, (ast.Set, ast.List, ast.Tuple)):
            # Set/list/tuple of string literals — pass var_name for authority detection
            for elt in ast.walk(node.value):
                if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                    tgt = elt.value.lstrip("/")
                    if tgt in label_to_id and tgt != src_path:
                        etype = _p5_target_edge_type(tgt, var_name)
                        edges.append((tgt, etype, "P5:set/list path constant"))
        else:
            # Individual constant within an expression (Path(), ROOT /)
            for sub in ast.walk(node.value):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    tgt = sub.value.lstrip("/")
                    if tgt in label_to_id and tgt != src_path:
                        edges.append((tgt, _p5_target_edge_type(tgt, ""), "P5:path constant"))
    return edges


_SECTION_TRIGGERS = re.compile(
    r"Files (?:Changed|Touched|touched|changed|Modified|modified|Updated|updated)"
    r"|(?:Touched|Changed|Modified|Updated) files"
    r"|Deliverables?"
    r"|Delivery Summary"
    r"|Artifacts? (?:added|changed|created)"
    r"|Mutation scope"
    r"|Changes made"
    r"|\bChanges\b"          # bare "## Changes" heading common in early walkthroughs
    r"|\bImplementation\b"   # "## Implementation" sections that list files modified
    r"|\bFiles\b",           # bare "## Files" section
    re.IGNORECASE,
)

# Bare label variant: "Files touched:" without a heading marker (common in early walkthroughs)
_BARE_SECTION_TRIGGERS = re.compile(
    r"^(?:Files (?:touched|changed|modified|updated)|Deliverables?|Files added):\s*$",
    re.IGNORECASE,
)

def _p8_walkthrough_md(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P8: Walkthrough Files-Changed / Deliverables / Delivery-Summary table → REFERENCES_AUTHORITY.

    Triggers on both `## Files Changed` (headed) and bare `Files touched:` labels.
    Handles nested sub-headings: once a section trigger fires, sub-headings (deeper
    than the trigger level) are allowed through; only same-level or shallower headings
    close the section.
    """
    edges = []
    in_section = False
    trigger_level = 0
    for line in text.splitlines():
        headed = _SECTION_TRIGGERS.search(line) and re.match(r"^#{1,4}", line)
        bare   = _BARE_SECTION_TRIGGERS.match(line)
        if headed or bare:
            in_section = True
            # Determine heading depth for nested-section handling
            m = re.match(r"^(#{1,4})", line)
            trigger_level = len(m.group(1)) if m else 0
            continue
        if in_section:
            m = re.match(r"^(#{1,4})", line)
            if m:
                depth = len(m.group(1))
                # Same level or shallower closes the section; deeper levels are sub-sections and stay in
                if depth <= trigger_level or trigger_level == 0:
                    in_section = False
                    trigger_level = 0
        if not in_section:
            continue
        # table row with backtick path
        m = re.search(r"\|\s*`((?:docs|ilc_core|tests|tools|simulations|out)/[^`]+)`", line)
        if m:
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P8:deliverable table"))
        # plain path in table
        m2 = re.search(r"\|\s*((?:docs|ilc_core|tests|tools)/[^\s|`]+)\s*\|", line)
        if m2:
            tgt = m2.group(1).strip()
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P8:plain path table"))
        # markdown link: [name](../../path)
        m3 = re.search(r"\[([^\]]+)\]\(\.\.\/\.\.\/([^)]+)\)", line)
        if m3:
            tgt = m3.group(2)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P8:md link in table"))
        # bullet item with backtick path (e.g. "- `docs/specs/foo.md`: description")
        m4 = re.search(r"^\s*[-*]\s+`((?:docs|ilc_core|tests|tools|simulations)/[^`]+)`", line)
        if m4:
            tgt = m4.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P8:section bullet"))
    return edges


def _p9_graph_delta(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P9: graph_delta= lines → REFERENCES_AUTHORITY / EVIDENCES."""
    edges = []
    for m in re.finditer(
        r"graph_delta=([a-z_]+):([^->\s]+)\s*->\s*(\S+)", text
    ):
        relation = m.group(1)
        path = m.group(2).strip()
        if path in label_to_id and path != src_path:
            etype = "REFERENCES_AUTHORITY" if "load_bearing" in relation else "EVIDENCES"
            edges.append((path, etype, f"P9:graph_delta={relation}"))
    return edges


def _p10_claim_table(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P10: Claim Audit / Claim Verification table → REFERENCES_AUTHORITY."""
    edges = []
    for line in text.splitlines():
        if "confirmed" not in line.lower():
            continue
        m = re.search(r"\|\s*`((?:docs|ilc_core|tests|tools)[^`]+)`", line)
        if m:
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P10:Claim table confirmed"))
    return edges


# P11 shares the same triggers as P8 — don't duplicate
_P11_TRIGGERS = _SECTION_TRIGGERS

# Also match bare "Touched files:" / "Files touched:" labels without a heading prefix
_BARE_SECTION_TRIGGERS_EXT = re.compile(
    r"^(?:Files (?:touched|changed|modified|updated)|Touched files|Deliverables?):\s*$",
    re.IGNORECASE,
)

def _p11_files_changed_plain(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P11: Bullet lists INSIDE Files-Changed/Deliverables sections → REFERENCES_AUTHORITY.

    Triggers on both `## Files Changed` (headed) and bare `Files touched:` labels.
    Uses nested-heading-aware exit: sub-headings deeper than the trigger level stay
    inside the section; same-level or shallower headings close it.
    """
    edges = []
    in_section = False
    trigger_level = 0
    for line in text.splitlines():
        headed = _P11_TRIGGERS.search(line) and re.match(r"^#{1,4}", line)
        bare   = _BARE_SECTION_TRIGGERS.match(line) or _BARE_SECTION_TRIGGERS_EXT.match(line)
        if headed or bare:
            in_section = True
            hm = re.match(r"^(#{1,4})", line)
            trigger_level = len(hm.group(1)) if hm else 0
            continue
        if in_section:
            hm = re.match(r"^(#{1,4})", line)
            if hm:
                depth = len(hm.group(1))
                if depth <= trigger_level or trigger_level == 0:
                    in_section = False
                    trigger_level = 0
        if not in_section:
            continue
        m = re.search(r"^\s*[-*]\s+`((?:docs|ilc_core|tests|tools|simulations)/[^`]+)`", line)
        if m:
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P11:section bullet"))
    return edges


_P12_TRIGGERS = re.compile(
    r"ingestion order|required reading|deterministic ingestion"
    r"|Baseline Inputs|Required inputs|Inputs And Canon"
    r"|Guidance consumed",
    re.IGNORECASE,
)

def _p12_ingestion_order(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P12: Numbered lists AND baseline-inputs tables → REFERENCES_AUTHORITY."""
    edges = []
    in_section = False
    for line in text.splitlines():
        if _P12_TRIGGERS.search(line):
            in_section = True
            continue
        if in_section and re.match(r"^#{1,4}", line):
            in_section = False
        if not in_section:
            continue
        # Numbered list item
        m = re.search(r"\d+\.\s+`((?:docs|ilc_core|tests|tools|simulations)[^`]+)`", line)
        if m:
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P12:ingestion order"))
        # Table row (Baseline Inputs / Guidance consumed tables)
        m2 = re.search(r"\|\s*`((?:docs|ilc_core|tests|tools|simulations)[^`]+)`", line)
        if m2:
            tgt = m2.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P12:baseline inputs table"))
        # Bullet with backtick path
        m3 = re.search(r"^[-*]\s+`((?:docs|ilc_core|tests|tools|simulations)[^`]+)`", line)
        if m3:
            tgt = m3.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P12:guidance consumed bullet"))
    return edges


_P13_FIELDS = re.compile(
    r"^(?:\*{0,2})?(?:Related artifacts?|Primary roadmap anchor|Related documents?|Code|Tests?|Simulation):\s*",
    re.IGNORECASE,
)

def _p13_related_artifacts(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P13: Metadata field lines → REFERENCES_AUTHORITY / TESTS.

    Covers:
    - 'Related artifacts:', 'Primary roadmap anchor:', 'Related documents:'
    - 'Code:', 'Tests:' / 'Test:' — used in research briefs to cite simulation script and test file
    - 'Simulation:' — alternate key for the code target in some briefs
    """
    edges = []
    for line in text.splitlines()[:35]:
        if not _P13_FIELDS.match(line):
            continue
        key = _P13_FIELDS.match(line).group(0).strip().rstrip(":").lower().strip("*")
        for m in re.finditer(r"`((?:docs|ilc_core|tests|tools|simulations)/[^`]+)`", line):
            tgt = m.group(1)
            if tgt not in label_to_id or tgt == src_path:
                continue
            if key in ("tests", "test"):
                edges.append((tgt, "TESTS", "P13:Tests: metadata field"))
            else:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P13:metadata field"))
    return edges


def _p14_inputs_verified(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P14: 'Inputs Verified' / 'Read and consumed' bullet list → REFERENCES_AUTHORITY."""
    edges = []
    in_section = False
    for line in text.splitlines():
        if re.search(r"(inputs verified|read and consumed|inputs read)", line, re.IGNORECASE):
            in_section = True
            continue
        if in_section and re.match(r"^#", line):
            in_section = False
        if not in_section:
            continue
        m = re.search(r"`((?:docs|ilc_core|tests|tools|simulations)/[^`]+)`", line)
        if m:
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P14:inputs verified bullet"))
    return edges


def _p15_json_source_refs(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P15: JSON files with source_ref / evidence_refs / source_anchors / governing_adr → REFERENCES_AUTHORITY."""
    edges = []
    try:
        data = json.loads(text)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return edges

    def _collect(obj: object) -> None:
        if isinstance(obj, dict):
            for key, val in obj.items():
                if key in ("source_ref", "governing_adr") and isinstance(val, str):
                    if val in label_to_id and val != src_path:
                        edges.append((val, "REFERENCES_AUTHORITY", f"P15:{key} field"))
                elif key in ("evidence_refs", "source_anchors") and isinstance(val, list):
                    for item in val:
                        if isinstance(item, str) and item in label_to_id and item != src_path:
                            edges.append((item, "REFERENCES_AUTHORITY", f"P15:{key} list item"))
                elif key == "first_pass_results" and isinstance(val, str):
                    if val in label_to_id and val != src_path:
                        edges.append((val, "EVIDENCES", "P15:first_pass_results field"))
                else:
                    _collect(val)
        elif isinstance(obj, list):
            for item in obj:
                _collect(item)

    _collect(data)
    return edges


_RATIFICATION_EVIDENCE_RE = re.compile(
    r"docs/specs/ilc_cdl_\d+_.*_ratification_evidence.*\.md$"
)
_STATUS_DOC = "docs/phases/STATUS.md"

def _p17_ratification_evidence(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P17: CDL ratification evidence docs → EVIDENCES to CDL_REGISTER."""
    edges = []
    if not _RATIFICATION_EVIDENCE_RE.match(src_path):
        return edges
    if CDL_REGISTER in label_to_id:
        edges.append((CDL_REGISTER, "EVIDENCES", "P17:ratification evidence doc"))
    return edges


_P18_SKIP_SRC = re.compile(r"^docs/phases/")
_P18_DOC_TARGETS = re.compile(r"^(?:docs/specs/|docs/adr/|docs/antigravity_tasks/|docs/architecture/|docs/research/)")
_P18_ANY_TARGETS = re.compile(r"^(?:ilc_core/|tests/|tools/)")
_P18_SPEC_SOURCES = re.compile(r"^(?:docs/specs/|docs/architecture/|docs/research/)")
_P18_SKIP_TGTS = {_STATUS_DOC, "docs/phases/README.md"}

def _p18_global_bullet_paths(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P18: Bullet list items in non-phase markdown docs → REFERENCES_AUTHORITY.

    Catches paths in window handoff docs, ratification evidence docs, and spec
    docs that use bullet lists outside of the Files-Changed/Deliverables sections
    already covered by P11.

    Restrictions:
    - Does NOT fire in docs/phases/ (walkthrough docs handled separately by P8/P11/P20).
    - docs/antigravity_tasks/ sources: emit for docs/ AND ilc_core/tests/ targets
      (phase prompt "Fix A/B/C — Update:" bullets reference implementation files).
    - docs/specs/ and docs/architecture/ sources: emit for docs/ AND ilc_core/tests/
      targets (companion-file migration lists, numeric cleanup specs, etc.).
    - All other sources: docs/ targets only.
    """
    edges = []
    if _P18_SKIP_SRC.match(src_path):
        return edges
    is_prompt = src_path.startswith("docs/antigravity_tasks/")
    is_spec = _P18_SPEC_SOURCES.match(src_path)
    for line in text.splitlines():
        if not re.match(r"^\s*[-*]\s", line):
            continue
        for m in re.finditer(r"`((?:docs|ilc_core|tests|tools|simulations)/[^`]+)`", line):
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path and tgt not in _P18_SKIP_TGTS:
                if _P18_DOC_TARGETS.match(tgt):
                    edges.append((tgt, "REFERENCES_AUTHORITY", "P18:global bullet backtick path"))
                elif (is_prompt or is_spec) and _P18_ANY_TARGETS.match(tgt):
                    edges.append((tgt, "REFERENCES_AUTHORITY", "P18:global bullet backtick path"))
    return edges


def _p19_global_table_paths(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P19: Markdown table cells with backtick docs/ paths → REFERENCES_AUTHORITY.

    Catches CDL evidence tables, ratification tables, and spec tables.
    Restriction: only emits for docs/ targets (not tools/, tests/, ilc_core/
    which are non-authority artifacts).
    """
    edges = []
    for line in text.splitlines():
        if "|" not in line:
            continue
        for m in re.finditer(r"\|\s*`((?:docs)/[^`]+)`", line):
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path and tgt != _STATUS_DOC:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P19:global table backtick path"))
    return edges


_GIT_DIFF_PATH = re.compile(
    r"git\s+(?:diff|show|log)\s+[^\n]*?--\s+((?:ilc_core|docs|tests|tools|simulations)/\S+)"
)

_P22_TRIGGERS = re.compile(
    r"In[- ]?scope|Scope|Files in scope|Targeted files|Files to (?:update|modify|change)",
    re.IGNORECASE,
)

def _p22_scope_section(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P22: Phase prompt 'Scope / In-scope' section → REFERENCES_AUTHORITY.

    Code-health and refactor batch prompts list files under '## Scope > ### In-scope'
    rather than under '## Inputs to read first'.  Extract backtick paths from these
    sections and emit REFERENCES_AUTHORITY.
    """
    edges = []
    in_section = False
    trigger_level = 0
    for line in text.splitlines():
        if _P22_TRIGGERS.search(line) and re.match(r"^#{1,4}", line):
            in_section = True
            m = re.match(r"^(#{1,4})", line)
            trigger_level = len(m.group(1)) if m else 0
            continue
        if in_section:
            m = re.match(r"^(#{1,4})", line)
            if m and len(m.group(1)) <= trigger_level:
                in_section = False
                trigger_level = 0
        if not in_section:
            continue
        for mm in re.finditer(r"`((?:ilc_core|docs|tests|tools|simulations)/[^`]+)`", line):
            tgt = mm.group(1)
            if tgt in label_to_id and tgt != src_path:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P22:Scope/In-scope section"))
    return edges


_CDL_PROSE_RE = re.compile(r"\bCDL-(\d+)\b")

def _p23_prose_cdl_refs(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P23: Prose CDL-NNN mentions in spec/walkthrough docs → REFERENCES_AUTHORITY to CDL register.

    Many spec docs (TLA+ shells, architecture notes, research briefs) reference CDL
    numbers in prose (e.g. 'CDL-051 semantics') without citing the file path.
    Emit a single REFERENCES_AUTHORITY edge to the CDL register when any CDL mention
    is found.  Deduplicated — only one edge per file regardless of CDL mention count.
    """
    edges = []
    if CDL_REGISTER not in label_to_id:
        return edges
    if _CDL_PROSE_RE.search(text):
        edges.append((CDL_REGISTER, "REFERENCES_AUTHORITY", "P23:prose CDL-NNN reference"))
    return edges


_P21_SECTION_TRIGGERS = re.compile(
    r"Deliverables?|Files (?:touched|changed|modified|updated)|(?:Touched|Changed) files",
    re.IGNORECASE,
)
_PLAIN_PATH_RE = re.compile(
    r"^((?:docs|ilc_core|tests|tools|simulations|out)/[^\s]+)\s*$"
)

def _p21_deliverables_fenced_block(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P21: Plain file paths inside fenced code blocks under Deliverables/Files-Changed sections.

    Closure-gate walkthroughs list deliverables as plain paths (no backticks) inside
    a ```text``` fenced block under ## 3. Deliverables or similar sections.
    """
    edges = []
    in_section = False
    in_fence = False
    for line in text.splitlines():
        # Enter section on heading match
        if re.match(r"^#{1,4}", line) and _P21_SECTION_TRIGGERS.search(line):
            in_section = True
            in_fence = False
            continue
        # Leave section on next heading
        if in_section and re.match(r"^#{1,4}", line):
            in_section = False
            in_fence = False
            continue
        if not in_section:
            continue
        # Toggle fence
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            continue
        # Plain path line inside fence
        m = _PLAIN_PATH_RE.match(line.strip())
        if m:
            tgt = m.group(1)
            if tgt in label_to_id and tgt != src_path and tgt != _STATUS_DOC:
                edges.append((tgt, "REFERENCES_AUTHORITY", "P21:deliverables fenced block"))
    return edges


def _p20_git_diff_paths(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P20: `git diff HEAD -- <path>` lines → REFERENCES_AUTHORITY.

    Walkthrough and spec docs include git diff verification commands that
    explicitly name the files being tracked/verified. The doc references those
    files as the subject of the verification.
    """
    edges = []
    for m in _GIT_DIFF_PATH.finditer(text):
        tgt = m.group(1).strip()
        if tgt in label_to_id and tgt != src_path:
            edges.append((tgt, "REFERENCES_AUTHORITY", "P20:git diff path"))
    return edges


def _p16_sh_commands(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P16: Shell scripts — pytest tests → TESTS; validate_phase_prompt → REFERENCES_AUTHORITY; path vars → REFERENCES_AUTHORITY/TESTS."""
    edges = []

    # pytest: only extract individual test file paths (stop at flags or non-path tokens)
    for m in re.finditer(r"\bpytest\b([^'\"\n\\]*)", text):
        segment = m.group(1)
        for part in segment.split():
            part = part.strip("'\"\\")
            if part.startswith("tests/") and part.endswith(".py") and part in label_to_id:
                edges.append((part, "TESTS", "P16:pytest command"))

    # validate_phase_prompt: one path per command occurrence
    for m in re.finditer(r"validate_phase_prompt\.py\s+(docs/\S+\.md)", text):
        tgt = m.group(1).strip("'\"")
        if tgt in label_to_id and tgt != src_path:
            edges.append((tgt, "REFERENCES_AUTHORITY", "P16:validate_phase_prompt"))

    # Shell variable assignments
    for m in re.finditer(
        r'(?:PROMPT_PATH|GATE_PATH|HANDOFF_PATH|SNAPSHOT_PATH|SEQUENCE_LOCK_PATH)'
        r'\s*=\s*["\']?(docs/[^\s\'"]+|out/[^\s\'"]+|tools/[^\s\'"]+)["\']?',
        text
    ):
        tgt = m.group(1).strip("'\"")
        if tgt in label_to_id and tgt != src_path:
            etype = "REFERENCES_AUTHORITY" if tgt.startswith("docs/") else "TESTS"
            edges.append((tgt, etype, "P16:shell path var"))

    # P24: Bash array multi-line pytest — python3 -m pytest on its own line inside (...)
    # followed by test file paths on subsequent lines.
    _P24_PYTEST_SOLO = re.compile(r"^\s*python3\s+-m\s+pytest\s*$")
    _P24_TEST_LINE = re.compile(r"^\s*(tests/[^\s]+\.py)\s*\\?\s*$")
    _P24_STOP = re.compile(r"^\s*(?:-[a-zA-Z]|--|\)|$)")
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if _P24_PYTEST_SOLO.match(line):
            for j in range(i + 1, len(lines)):
                next_line = lines[j]
                m = _P24_TEST_LINE.match(next_line)
                if m:
                    tgt = m.group(1)
                    if tgt in label_to_id:
                        edges.append((tgt, "TESTS", "P24:multiline pytest array"))
                elif _P24_STOP.match(next_line):
                    break
                else:
                    break

    # P25: Shell scripts that call other tools/ scripts or Python runner scripts
    # "bash tools/some_gate.sh" or "python3 tools/run_something.py"
    for m in re.finditer(
        r'\b(?:bash|sh)\s+(tools/[^\s\'"]+\.sh)',
        text
    ):
        tgt = m.group(1).strip("'\"")
        if tgt in label_to_id and tgt != src_path:
            edges.append((tgt, "IMPLEMENTS", "P25:shell calls shell"))
    for m in re.finditer(
        r'\bpython3?\s+(tools/[^\s\'"]+\.py)',
        text
    ):
        tgt = m.group(1).strip("'\"")
        if tgt in label_to_id and tgt != src_path:
            edges.append((tgt, "IMPLEMENTS", "P25:shell calls python runner"))

    return edges


_P26_PYTEST_IN_FENCE = re.compile(
    r"^\s*(?:\$\s+)?\S*pytest\S*\s+(tests/[^\s]+\.py)"
)
_P26_HEADING_PATH = re.compile(
    r"^#{2,4}\s+.*`((?:ilc_core|tests|tools|simulations|docs)/[^`]+\."
    r"(?:py|md|rs|sh|json|toml))`"
)

# P28: inline backtick paths anywhere in MD prose
_P28_INLINE_BT = re.compile(
    r"`((?:ilc_core|tests|tools|simulations|docs)/[^`\s]+\.\w+)`"
)

# P29: absolute filesystem paths in markdown links (Atlas turn logs use /Users/.../repo/path)
_P29_ABS_REPO_PREFIX = re.compile(
    r"/Users/[^/]+/(?:\w+/)*ILC[^/]*/[^/]+/"  # matches up to and including the repo root dir
)
_P29_MD_LINK_ABS = re.compile(
    r"\]\(/Users/[^\)]+\)"
)


def _p29_md_absolute_path_links(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P29: Markdown links with absolute filesystem paths → REFERENCES_AUTHORITY / TESTS.

    Atlas turn logs and Codex turn logs use absolute paths like:
    [name](/Users/jamison/Documents/ILC_Main/01_Current/docs/specs/...)
    Strip the repo root prefix to get the relative path.
    """
    edges = []
    repo_root_str = str(REPO_ROOT) + "/"
    for m in _P29_MD_LINK_ABS.finditer(text):
        abs_path = m.group()[2:-1]  # strip "](" and ")"
        # Try stripping known repo root prefix
        if abs_path.startswith(repo_root_str):
            rel = abs_path[len(repo_root_str):]
        else:
            # Try regex-based strip
            rest = _P29_ABS_REPO_PREFIX.sub("", abs_path)
            rel = rest if "/" in rest else ""
        if not rel:
            continue
        # Strip fragment (#line-N)
        rel = rel.split("#")[0]
        if rel in label_to_id and rel != src_path:
            etype = "TESTS" if rel.startswith("tests/") else "REFERENCES_AUTHORITY"
            edges.append((rel, etype, "P29:absolute path md link"))
    return edges


def _p28_md_inline_backtick_paths(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P28: Backtick-wrapped file paths anywhere in MD prose → REFERENCES_AUTHORITY / TESTS.

    Catches paths like `ilc_core/some/module.py` embedded in prose sentences,
    verification tables, spec bodies, etc. that aren't captured by P8/P18/P19/P26.
    """
    edges = []
    for m in _P28_INLINE_BT.finditer(text):
        tgt = m.group(1)
        if tgt not in label_to_id or tgt == src_path:
            continue
        etype = "TESTS" if tgt.startswith("tests/") else "REFERENCES_AUTHORITY"
        edges.append((tgt, etype, "P28:inline backtick path"))
    return edges


def _p26_md_code_block_pytest(src_path: str, text: str, label_to_id: dict) -> list[tuple]:
    """P26: `pytest tests/path.py` lines inside fenced code blocks in MD files → TESTS.

    Also extracts file paths embedded in heading lines like:
    ### 1. New Module: `ilc_core/sim/module.py`
    """
    edges = []
    in_fence = False
    for line in text.splitlines():
        stripped = line.strip()
        # Toggle fence on ``` or ~~~
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            continue
        # pytest inside fence
        if in_fence:
            m = _P26_PYTEST_IN_FENCE.match(line)
            if m:
                tgt = m.group(1)
                if tgt in label_to_id and tgt != src_path:
                    edges.append((tgt, "TESTS", "P26:pytest in fenced block"))
        # Heading-embedded path (works outside fence too)
        mh = _P26_HEADING_PATH.match(line)
        if mh:
            tgt = mh.group(1)
            if tgt in label_to_id and tgt != src_path:
                etype = "TESTS" if tgt.startswith("tests/") else "REFERENCES_AUTHORITY"
                edges.append((tgt, etype, "P26:path in heading"))
    return edges


# ── Per-file classifier ───────────────────────────────────────────────────────

def classify_file(
    src_path: str,
    label_to_id: dict[str, str],
) -> list[dict]:
    """Return list of edge dicts {target, edge_type, rationale, pattern}."""
    full = REPO_ROOT / src_path
    try:
        text = full.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []

    ext = Path(src_path).suffix.lower()
    raw_edges: list[tuple] = []  # (target_path, edge_type, rationale)

    if ext == ".py":
        raw_edges += _p1_py(src_path, text, label_to_id)
        raw_edges += _p2_py(src_path, text, label_to_id)
        raw_edges += _p5_py(src_path, text, label_to_id)

    elif ext == ".rs":
        raw_edges += _p1_rs(src_path, text, label_to_id)

    elif ext == ".md":
        raw_edges += _p3_md(src_path, text, label_to_id)
        raw_edges += _p4_md(src_path, text, label_to_id)
        raw_edges += _p8_walkthrough_md(src_path, text, label_to_id)
        raw_edges += _p9_graph_delta(src_path, text, label_to_id)
        raw_edges += _p10_claim_table(src_path, text, label_to_id)
        raw_edges += _p11_files_changed_plain(src_path, text, label_to_id)
        raw_edges += _p12_ingestion_order(src_path, text, label_to_id)
        raw_edges += _p13_related_artifacts(src_path, text, label_to_id)
        raw_edges += _p14_inputs_verified(src_path, text, label_to_id)
        raw_edges += _p17_ratification_evidence(src_path, text, label_to_id)
        raw_edges += _p18_global_bullet_paths(src_path, text, label_to_id)
        raw_edges += _p19_global_table_paths(src_path, text, label_to_id)
        raw_edges += _p20_git_diff_paths(src_path, text, label_to_id)
        raw_edges += _p21_deliverables_fenced_block(src_path, text, label_to_id)
        raw_edges += _p22_scope_section(src_path, text, label_to_id)
        raw_edges += _p23_prose_cdl_refs(src_path, text, label_to_id)
        raw_edges += _p26_md_code_block_pytest(src_path, text, label_to_id)
        raw_edges += _p28_md_inline_backtick_paths(src_path, text, label_to_id)
        raw_edges += _p29_md_absolute_path_links(src_path, text, label_to_id)

    elif ext == ".json":
        raw_edges += _p15_json_source_refs(src_path, text, label_to_id)

    elif ext == ".sh":
        raw_edges += _p16_sh_commands(src_path, text, label_to_id)

    # Deduplicate
    seen: set[tuple] = set()
    result = []
    for (tgt, etype, rationale) in raw_edges:
        key = (tgt, etype)
        if key not in seen:
            seen.add(key)
            result.append({"target": tgt, "edge_type": etype, "rationale": rationale})
    return result


# ── Comparison vs manual ground truth ────────────────────────────────────────

def compare_to_manual(
    src_path: str,
    script_edges: list[dict],
    manual_edges: list[dict],
) -> dict:
    """Return precision/recall comparison between script and manual edges."""
    script_set = {(e["target"], e["edge_type"]) for e in script_edges}
    manual_set = {(e["target"], e["edge_type"]) for e in manual_edges}

    tp = script_set & manual_set
    fp = script_set - manual_set  # script found but manual didn't
    fn = manual_set - script_set  # manual found but script missed

    return {
        "source_path": src_path,
        "script_edge_count": len(script_set),
        "manual_edge_count": len(manual_set),
        "tp": len(tp),
        "fp": len(fp),
        "fn": len(fn),
        "precision": len(tp) / len(script_set) if script_set else 1.0,
        "recall": len(tp) / len(manual_set) if manual_set else 1.0,
        "fp_edges": [{"target": t, "edge_type": et} for t, et in sorted(fp)],
        "fn_edges": [{"target": t, "edge_type": et} for t, et in sorted(fn)],
    }


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Fix27 semantic pre-pass classifier")
    parser.add_argument("--batch", type=int, default=0,
                        help="Limit to first N unannotated files (0 = all)")
    parser.add_argument("--compare-manual", action="store_true",
                        help="Compare script output to manual edges in graph")
    parser.add_argument(
        "--annotation-graph",
        type=str,
        default=None,
        help=(
            "Path to enriched graph JSON that carries manually_annotated / "
            "prepass_annotated node flags (e.g. "
            "out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json). "
            "When omitted the script falls back to the Fix22 baseline, which has no "
            "annotation flags — all deferred files will be treated as unannotated."
        ),
    )
    args = parser.parse_args()

    # Load Fix22 for label-to-id mapping and edge structure (read-only baseline)
    print("Loading Fix22 graph (read-only baseline)...")
    g = json.loads(FIX22_GRAPH.read_text(encoding="utf-8"))
    label_to_id = {n["label"]: n["candidate_id"] for n in g["nodes"]}
    id_to_node = {n["candidate_id"]: n for n in g["nodes"]}

    # Load annotation flags from the enriched artifact if provided; fall back to Fix22
    if args.annotation_graph:
        ann_graph_path = Path(args.annotation_graph)
        if not ann_graph_path.is_absolute():
            ann_graph_path = REPO_ROOT / ann_graph_path
        print(f"Loading annotation flags from enriched graph: {ann_graph_path}")
        g_ann = json.loads(ann_graph_path.read_text(encoding="utf-8"))
        annotated_ids = {
            n["candidate_id"] for n in g_ann["nodes"]
            if n.get("manually_annotated") or n.get("prepass_annotated")
        }
        # Also extend graph lookup maps with any nodes only in the enriched artifact.
        for n in g_ann["nodes"]:
            if n.get("label") and n["label"] not in label_to_id:
                label_to_id[n["label"]] = n["candidate_id"]
            if n.get("candidate_id") and n["candidate_id"] not in id_to_node:
                id_to_node[n["candidate_id"]] = n
        print(f"  Annotation flags loaded: {len(annotated_ids)} annotated node IDs")
    else:
        annotated_ids = {n["candidate_id"] for n in g["nodes"] if n.get("manually_annotated")}
        print(
            "WARNING: --annotation-graph not provided. Fix22 has no manually_annotated / "
            "prepass_annotated flags (it was restored to committed baseline). All deferred "
            "files will be treated as unannotated. To reproduce original pre-pass skip "
            "behaviour, pass: --annotation-graph "
            "out/atlas_research/genesis_atlas_enriched_candidate_1545p_fix27_prepass.json"
        )

    # Manual edges: those with manual provenance keyed by source (from whichever graph)
    g_for_manual = g_ann if args.annotation_graph else g  # g_ann defined above when flag set
    manual_by_src: dict[str, list[dict]] = defaultdict(list)
    for e in g_for_manual["edges"]:
        provenance = e.get("provenance")
        if isinstance(provenance, str) and provenance.startswith("manual_bucket_analysis_fix27"):
            src_label = id_to_node.get(e["source"], {}).get("label", "")
            tgt_label = id_to_node.get(e["target"], {}).get("label", "")
            if src_label and tgt_label:
                manual_by_src[src_label].append({
                    "target": tgt_label,
                    "edge_type": e["edge_type"],
                })

    print("Loading Fix26 deferred queue...")
    deferred_paths: list[str] = []
    for line in FIX26_QUEUE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            r = json.loads(line)
            if r.get("queue_class") == "deferred_low_confidence":
                deferred_paths.append(r["source_path"])
    unique_deferred = list(dict.fromkeys(deferred_paths))

    # Decide which files to process
    if args.compare_manual:
        # Only run on files that have manual edges (to measure efficacy)
        targets = [p for p in unique_deferred if p in manual_by_src]
        print(f"Comparing script vs manual on {len(targets)} manually-annotated files")
    else:
        # Skip already-annotated files
        targets = [
            p for p in unique_deferred
            if label_to_id.get(p) not in annotated_ids
        ]
        print(f"Processing {len(targets)} unannotated deferred files")

    if args.batch and args.batch > 0:
        targets = targets[:args.batch]
        print(f"Limiting to first {args.batch} files")

    results = []
    comparison_rows = []
    edge_count = 0
    pattern_counts: Counter = Counter()

    for src_path in targets:
        script_edges = classify_file(src_path, label_to_id)
        edge_count += len(script_edges)
        for e in script_edges:
            pattern_counts[e["rationale"].split(":")[0]] += 1

        row = {
            "source_path": src_path,
            "script_edges": script_edges,
        }

        if args.compare_manual and src_path in manual_by_src:
            comp = compare_to_manual(src_path, script_edges, manual_by_src[src_path])
            row["comparison"] = comp
            comparison_rows.append(comp)

        results.append(row)

    # Write edge JSONL
    EDGE_OUT.parent.mkdir(parents=True, exist_ok=True)
    with EDGE_OUT.open("w", encoding="utf-8") as f:
        for row in results:
            for e in row["script_edges"]:
                f.write(json.dumps({
                    "source_path": row["source_path"],
                    "target_path": e["target"],
                    "edge_type": e["edge_type"],
                    "rationale": e["rationale"],
                    "provenance": "semantic_prepass_fix27",
                }, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n")

    # Aggregate comparison stats
    agg = {}
    if comparison_rows:
        total_tp = sum(r["tp"] for r in comparison_rows)
        total_fp = sum(r["fp"] for r in comparison_rows)
        total_fn = sum(r["fn"] for r in comparison_rows)
        total_manual = sum(r["manual_edge_count"] for r in comparison_rows)
        total_script = sum(r["script_edge_count"] for r in comparison_rows)
        agg = {
            "files_compared": len(comparison_rows),
            "total_manual_edges": total_manual,
            "total_script_edges": total_script,
            "aggregate_tp": total_tp,
            "aggregate_fp": total_fp,
            "aggregate_fn": total_fn,
            "aggregate_precision": total_tp / total_script if total_script else 1.0,
            "aggregate_recall": total_tp / total_manual if total_manual else 1.0,
            "worst_fn_files": sorted(
                comparison_rows, key=lambda r: r["fn"], reverse=True
            )[:10],
        }

    summary = {
        "phase": "1545p-Fix27-semantic-prepass",
        "files_processed": len(targets),
        "script_edges_found": edge_count,
        "pattern_counts": dict(pattern_counts),
        "comparison_aggregate": agg,
    }

    fd, tmp = tempfile.mkstemp(prefix=".prepass_fix27.", suffix=".json", dir=str(JSON_OUT.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, sort_keys=True)
            f.write("\n")
        os.replace(tmp, str(JSON_OUT))
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise

    print(f"\nFiles processed: {len(targets)}")
    print(f"Script edges found: {edge_count}")
    print(f"Pattern breakdown: {dict(pattern_counts)}")
    if agg:
        print(f"\n=== Efficacy vs manual ===")
        print(f"  Files compared:    {agg['files_compared']}")
        print(f"  Manual edges:      {agg['total_manual_edges']}")
        print(f"  Script edges:      {agg['total_script_edges']}")
        print(f"  TP: {agg['aggregate_tp']}  FP: {agg['aggregate_fp']}  FN: {agg['aggregate_fn']}")
        print(f"  Precision: {agg['aggregate_precision']:.3f}")
        print(f"  Recall:    {agg['aggregate_recall']:.3f}")
        if agg["worst_fn_files"]:
            print(f"\n  Worst recall files (most FN):")
            for r in agg["worst_fn_files"][:5]:
                print(f"    {r['fn']} FN  {r['source_path']}")
                for e in r["fn_edges"][:3]:
                    print(f"      MISSED: {e['edge_type']} -> {e['target']}")


if __name__ == "__main__":
    main()
