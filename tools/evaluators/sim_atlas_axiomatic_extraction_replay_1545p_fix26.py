#!/usr/bin/env python3
"""Whole-repo Atlas axiomatic extraction replay for Phase 1545p-Fix26.

PUBLIC_RC_EXCLUDE: atlas_axiomatic_extraction_replay_research_only
PUBLIC_RC_EXCLUDE_REASON: Research-only atom-candidate extraction over unsigned Atlas substrate; no canonical graph mutation, Genesis signing, public RC activation, or runtime activation.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import sys
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evaluators.sim_atlas_axiomatic_calibration_1545p_fix19 import (  # noqa: E402
    RECIPE_LIBRARY,
    TRUTH_PRIMITIVES,
)
from tools.evaluators.sim_atlas_precision_replay_1545p_fix20 import (  # noqa: E402
    _evaluate_golden,
    _evaluate_manual_spot_checks,
    _evaluate_negative_controls,
    extract_atoms as extract_fix20_atoms,
)


PHASE = "1545p-Fix26"
SIM_ID = "SIM-ATLAS-AXIOMATIC-EXTRACTION-REPLAY-01"
SCHEMA_VERSION = "sim_atlas_axiomatic_extraction_replay_1545p_fix26.v0.1"

NODE0 = "artifact:genesis_intent_attestation_init_authority_map"
FIX22_GRAPH = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
FIX22_PREIMAGES = REPO_ROOT / "out/genesis_atlas_full_repo_node_preimages_1545p_fix22.jsonl"
FIX25_JSON = REPO_ROOT / "out/sim_atlas_whole_graph_baseline_diagnostic_1545p_fix25.json"

ATOM_QUEUE_OUT = REPO_ROOT / "out/atlas_research/genesis_atlas_atom_candidates_1545p_fix26.jsonl"
JSON_OUT = REPO_ROOT / "out/sim_atlas_axiomatic_extraction_replay_1545p_fix26.json"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_atlas_axiomatic_extraction_replay_1545p_fix26_v0.1.md"
REVIEW_OUT = REPO_ROOT / "docs/specs/ilc_atlas_axiomatic_extraction_replay_review_1545p_fix26_v0.1.md"

TEXT_ANALYSIS_NODE_KINDS = {
    "adr_document_node",
    "genesis_private_material_node",
    "repo_material_node",
    "runtime_source_file_node",
    "sidecar_material_node",
    "sim_evidence_node",
    "spec_document_node",
    "test_evidence_node",
    "tooling_source_file_node",
}

SUPPORTED_TRACE_ROLES = {
    "ATTESTATION",
    "CLASSIFIED_BY",
    "DERIVED_FROM",
    "EVIDENCES",
    "GOVERNS",
    "IMPLEMENTS",
    "REFERENCES_AUTHORITY",
    "TESTS",
    "undeclared",
}

NEGATION_PATTERNS = (
    r"\bnot authority\b",
    r"\bnot .*authority\b",
    r"\bdoes not .*authori[sz]e\b",
    r"\bnot canonical\b",
    r"\bnot promoted\b",
    r"\bnot signed\b",
    r"\bnot activated\b",
    r"\bnot live\b",
    r"\bno public\b",
    r"\bnot public\b",
)

RECIPE_EDGE_HINTS = {
    "activation_refutation": "EVIDENCES",
    "authority_assertion": "REFERENCES_AUTHORITY",
    "canonicalization_validation": "IMPLEMENTS",
    "candidate_revision": "EVIDENCES",
    "contradiction_guard": "EVIDENCES",
    "phase_token_commitment": "EVIDENCES",
    "schema_validation": "IMPLEMENTS",
}

PUBLIC_ROOT = "artifact:public_release_candidate_material_root_1545p_fix22"
PRIVATE_ROOT = "artifact:genesis_private_local_material_root_1545p_fix22"
GENERATED_ROOT = "artifact:generated_evidence_material_root_1545p_fix22"


def _canonical_dumps(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        dir=str(path.parent),
        prefix=f".{path.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(text)
        os.replace(tmp_path, path)
        path.chmod(0o644)
    except Exception:
        try:
            tmp_path.unlink()
        finally:
            raise


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_object_required:{path}")
    return payload


def _read_preimages(path: Path) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"preimage_object_required:{line_no}")
        node_id = row.get("node_id")
        if not isinstance(node_id, str) or not node_id:
            raise ValueError(f"preimage_node_id_required:{line_no}")
        rows[node_id] = row
    return rows


def _sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _short_hash(payload: Any) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()[:20]


def _slug(value: str, limit: int = 120) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:limit] or "root"


def _has_any(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL) for pattern in patterns)


def _node_id(node: dict[str, Any]) -> str:
    node_id = node.get("candidate_id")
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("candidate_id_required")
    return node_id


def _build_terminal_maps(nodes: list[dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for node in nodes:
        node_id = _node_id(node)
        label = str(node.get("label", ""))
        haystack = f"{node_id} {label}"

        if node_id.startswith("adr:"):
            match = re.search(r"ADR[-_ ]?(\d{4})|adr:(?:adr_)?(\d{4})", haystack, re.IGNORECASE)
            if match:
                mapping[f"ADR-{match.group(1) or match.group(2)}"] = node_id

        if node_id.startswith("cdl:"):
            vmatch = re.search(r"CDL[-_ ]?(V\d+)|cdl:(?:cdl_)?(v\d+)", haystack, re.IGNORECASE)
            nmatch = re.search(r"CDL[-_ ]?0*(\d{1,3})|cdl:(?:cdl_)?0*(\d{1,3})", haystack, re.IGNORECASE)
            if vmatch:
                mapping[f"CDL-{(vmatch.group(1) or vmatch.group(2)).upper()}"] = node_id
            if nmatch:
                mapping[f"CDL-{int(nmatch.group(1) or nmatch.group(2)):03d}"] = node_id

        if node_id.startswith("policy:"):
            mapping.setdefault(f"POLICY:{_slug(label or node_id)}", node_id)
        if node_id == NODE0:
            mapping[node_id] = node_id
    return mapping


def _authority_refs_from_path(path: str) -> list[str]:
    refs: list[str] = []
    adr_match = re.search(r"ADR[_-](\d{4})", path, re.IGNORECASE)
    if adr_match:
        refs.append(f"ADR-{adr_match.group(1)}")
    cdl_match = re.search(r"cdl[_-](v\d+|\d{1,3})", path, re.IGNORECASE)
    if cdl_match:
        raw = cdl_match.group(1).upper()
        refs.append(f"CDL-{raw if raw.startswith('V') else f'{int(raw):03d}'}")
    return refs


def _authority_refs_from_text(text: str) -> list[str]:
    refs: list[str] = []
    for match in re.finditer(r"\bADR[-_ ]?(\d{4})\b", text, re.IGNORECASE):
        refs.append(f"ADR-{match.group(1)}")
    for match in re.finditer(r"\bCDL[-_ ]?(V\d+|\d{1,3})\b", text, re.IGNORECASE):
        raw = match.group(1).upper()
        refs.append(f"CDL-{raw if raw.startswith('V') else f'{int(raw):03d}'}")
    for match in re.finditer(r"\bCDL_(V\d+|\d{3})_[A-Z0-9_]*DEPENDENCY\b", text):
        raw = match.group(1).upper()
        refs.append(f"CDL-{raw if raw.startswith('V') else f'{int(raw):03d}'}")
    deduped: list[str] = []
    for ref in refs:
        if ref not in deduped:
            deduped.append(ref)
    return deduped


def _python_semantic_text(path: Path) -> tuple[str, str]:
    source = path.read_text(encoding="utf-8", errors="replace")
    pieces: list[str] = []
    try:
        module = ast.parse(source)
    except SyntaxError:
        return source, "python_ast_parse_failed_regex_fallback"

    module_doc = ast.get_docstring(module)
    if module_doc:
        pieces.append(module_doc)

    for node in ast.walk(module):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            pieces.append(node.name)
            doc = ast.get_docstring(node)
            if doc:
                pieces.append(doc)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    pieces.append(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            pieces.append(node.target.id)

    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            pieces.append(stripped.lstrip("#").strip())

    semantic_text = "\n".join(piece for piece in pieces if piece)
    if not semantic_text:
        semantic_text = "\n".join(line.strip() for line in source.splitlines() if re.match(r"^\s*(class|def|[A-Z0-9_]{3,}\s*=)", line))
    return semantic_text, "python_ast_symbols_docstrings_comments"


def _text_for_node(path: str) -> tuple[str, str]:
    resolved = REPO_ROOT / path
    if not resolved.exists() or not resolved.is_file():
        raise FileNotFoundError(path)
    if resolved.suffix == ".py":
        return _python_semantic_text(resolved)
    return resolved.read_text(encoding="utf-8", errors="replace"), "direct_text"


def _evidence_hint(recipe_id: str, text: str) -> tuple[str, str]:
    patterns = {
        "activation_refutation": r"PUBLIC_RC_EXCLUDE|support-only|not canonical|not authority|no public|not public|blocked|not activated|does not mutate|not minting|not live|not signed|unsigned|does not activate|deferred|reserved|excluded",
        "authority_assertion": r"\bCDL-\d+|\bADR-\d+|\bCDL_[0-9A-Z_]+_DEPENDENCY\b|RATIFICATION_TOKEN|ratified|governs|authority basis|authority ref|assert\.truth",
        "canonicalization_validation": r"canonical JSON|sort_keys=True|allow_nan=False|dag-cbor|DAG-CBOR|os\.replace|atomic write|canonical_json",
        "candidate_revision": r"Selected v0\.4 Additions|Deferred Candidate Queue|must_include_genesis_node|candidate_common_node|sidecar_recipe_node|Option [ABC]|selected|deferred per ADR-\d+|later CDL opening|candidate",
        "contradiction_guard": r"anti-gaming|reject|rejected|fail[- ]?closed|fail-safe|must not|cannot|prohibition|violates|overclaim|not promote|does not promote",
        "phase_token_commitment": r"\b[a-z0-9]+(?:_[a-z0-9]+){2,}_phase_[0-9p]+(?:_fix\d+)?\b|VERSION|SCHEMA_VERSION|schema_version|Token:",
        "schema_validation": r"\bschema\b|validate|validation|verifier|field|contract|reject_float|type_definition|edge_type_definition|hydrated_nodes|hydrated_edges|objective|requirements",
    }
    pattern = patterns.get(recipe_id, r".+")
    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        if re.search(pattern, line, re.IGNORECASE):
            evidence = line.strip()[:300] or recipe_id
            return evidence, f"line:{line_no}"
    return recipe_id, "line:unknown"


def _trace_role(node: dict[str, Any], recipe_id: str, terminal: str | None) -> str:
    if terminal is None:
        return "undeclared"
    kind = str(node.get("node_kind", ""))
    path = str(node.get("source_path", ""))
    if kind == "runtime_source_file_node" or path.startswith("ilc_core/"):
        return "IMPLEMENTS"
    if kind == "test_evidence_node" or path.startswith("tests/"):
        return "TESTS"
    if kind == "sim_evidence_node" or path.startswith("docs/sims/"):
        return "EVIDENCES"
    if kind in {"generated_evidence_node", "genesis_private_material_node", "sidecar_material_node"}:
        if terminal in {PRIVATE_ROOT, GENERATED_ROOT, PUBLIC_ROOT}:
            return "CLASSIFIED_BY"
        return "EVIDENCES"
    if kind in {"adr_document_node", "spec_document_node"} or path.startswith(("docs/adr/", "docs/specs/")):
        return "REFERENCES_AUTHORITY"
    return RECIPE_EDGE_HINTS.get(recipe_id, "REFERENCES_AUTHORITY")


def _privacy_class(node: dict[str, Any]) -> str:
    combined = " ".join(
        str(node.get(key, ""))
        for key in ("authority_tier", "tier", "public_release_status", "node_kind", "source_path")
    ).lower()
    if "private" in combined:
        return "genesis_private_or_local"
    if "generated" in combined or "/out/" in combined or str(node.get("source_path", "")).startswith("out/"):
        return "generated_evidence"
    if "public_release" in combined or "publishable" in combined:
        return "public_release_candidate_material"
    return "unspecified_or_support_material"


def _classification_terminal(node: dict[str, Any], node_ids: set[str]) -> str | None:
    """Return a Genesis-rooted classification rule terminal if one is known.

    Fix22 material roots are containment buckets, not classification rules. A
    private/generated/public bucket alone is therefore not a valid CLASSIFIED_BY
    terminal under the Fix24/Fix25 typed-trace standard. Until a policy/rule
    terminal exists for these classifications, these candidates must stay
    deferred.
    """
    _ = (node, node_ids)
    return None


def _terminal_for_candidate(
    *,
    node: dict[str, Any],
    text: str,
    terminal_map: dict[str, str],
    node_ids: set[str],
) -> tuple[str | None, list[str]]:
    source_path = str(node.get("source_path", ""))
    refs = _authority_refs_from_path(source_path) + _authority_refs_from_text(text)
    deduped_refs: list[str] = []
    for ref in refs:
        if ref not in deduped_refs:
            deduped_refs.append(ref)
        if ref in terminal_map:
            return terminal_map[ref], deduped_refs

    terminal = _classification_terminal(node, node_ids)
    if terminal:
        return terminal, deduped_refs
    return None, deduped_refs


def _queue_class(recipe_id: str, role: str, terminal: str | None, text: str) -> tuple[str, str]:
    if role == "undeclared" or terminal is None:
        return "deferred_low_confidence", "typed_trace_terminal_missing_or_role_undeclared"
    if recipe_id in {"authority_assertion", "candidate_revision"} and _has_any(NEGATION_PATTERNS, text) and not _authority_refs_from_text(text):
        return "rejected_overclaim_or_noisy", "negated_authority_or_promotion_language_without_authority_terminal"
    return "accepted_atom_candidates_for_review", "accepted_for_review_not_promoted"


def _authority_class(node: dict[str, Any], terminal: str | None) -> str:
    kind = str(node.get("node_kind", ""))
    if kind in {"adr_document_node", "spec_document_node"}:
        return "authority_document_file_trace_candidate"
    if terminal and terminal.startswith(("adr:", "cdl:", "policy:", "truth_primitive:", "artifact:")):
        return "source_to_genesis_rooted_terminal_trace_candidate"
    return "source_support_trace_candidate"


def _candidate_record(
    *,
    node: dict[str, Any],
    recipe_id: str,
    text: str,
    analysis_method: str,
    terminal: str | None,
    refs: list[str],
) -> dict[str, Any]:
    source_node_id = _node_id(node)
    source_path = str(node.get("source_path", ""))
    evidence, span = _evidence_hint(recipe_id, text)
    evidence_hash = _sha256_text(evidence)
    role = _trace_role(node, recipe_id, terminal)
    queue_class, reason = _queue_class(recipe_id, role, terminal, text)
    seed = {
        "evidence_text_hash": evidence_hash,
        "recipe_id": recipe_id,
        "source_node_id": source_node_id,
        "terminal": terminal or "undeclared",
        "trace_role": role,
    }
    record = {
        "analysis_method": analysis_method,
        "atom_candidate_id": f"atlas-atom:{_short_hash(seed)}",
        "authority_class": _authority_class(node, terminal),
        "confidence_class": "medium" if queue_class == "accepted_atom_candidates_for_review" else "low",
        "evidence_authority_refs": refs,
        "evidence_span_hint": span,
        "evidence_text_hash": evidence_hash,
        "nonclaim_boundary": "candidate_atom_for_review_only_no_promotion_no_authority_claim",
        "privacy_class": _privacy_class(node),
        "queue_class": queue_class,
        "recipe_id": recipe_id,
        "rejection_reason": reason if queue_class != "accepted_atom_candidates_for_review" else "",
        "source_node_id": source_node_id,
        "source_path": source_path,
        "traversal_direction": "verification_backtrace" if role not in {"GOVERNS", "ATTESTATION"} else "authority_forward",
        "truth_primitive_recipe": list(RECIPE_LIBRARY[recipe_id]),
        "typed_trace_edge_role": role,
        "typed_trace_terminal_node_id": terminal or "undeclared",
    }
    if role not in SUPPORTED_TRACE_ROLES:
        raise ValueError(f"unsupported_trace_role:{role}")
    return record


def _iter_text_nodes(graph: dict[str, Any], preimages: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for node in graph["nodes"]:
        if not isinstance(node, dict):
            continue
        node_id = _node_id(node)
        source_path = node.get("source_path")
        if not isinstance(source_path, str) or not source_path:
            continue
        node_kind = str(node.get("node_kind", ""))
        text_status = str(node.get("text_analysis_status", preimages.get(node_id, {}).get("text_analysis_status", "")))
        if node_kind not in TEXT_ANALYSIS_NODE_KINDS:
            continue
        if text_status != "analyzed":
            continue
        if not (REPO_ROOT / source_path).is_file():
            continue
        rows.append(node)
    return sorted(rows, key=lambda row: (str(row.get("source_path", "")), _node_id(row)))


def _extract_full_repo_candidates(graph: dict[str, Any], preimages: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    nodes = graph["nodes"]
    node_ids = {_node_id(node) for node in nodes}
    terminal_map = _build_terminal_maps(nodes)
    records: list[dict[str, Any]] = []
    file_errors: list[dict[str, str]] = []
    analyzed_files = 0

    for node in _iter_text_nodes(graph, preimages):
        source_path = str(node.get("source_path", ""))
        try:
            text, method = _text_for_node(source_path)
        except (OSError, UnicodeDecodeError) as exc:
            file_errors.append({"error": type(exc).__name__, "source_path": source_path})
            continue
        analyzed_files += 1
        if not text.strip():
            continue
        terminal, refs = _terminal_for_candidate(
            node=node,
            text=text,
            terminal_map=terminal_map,
            node_ids=node_ids,
        )
        atoms = extract_fix20_atoms(text)
        for recipe_id in sorted({atom.recipe_id for atom in atoms}):
            records.append(
                _candidate_record(
                    node=node,
                    recipe_id=recipe_id,
                    text=text,
                    analysis_method=method,
                    terminal=terminal,
                    refs=refs,
                )
            )

    records.sort(key=lambda row: row["atom_candidate_id"])
    return records, {
        "analyzed_file_count": analyzed_files,
        "file_error_count": len(file_errors),
        "file_errors_sample": file_errors[:20],
        "terminal_map_count": len(terminal_map),
        "text_node_count": len(_iter_text_nodes(graph, preimages)),
    }


def _write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    text = "".join(
        json.dumps(record, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n"
        for record in records
    )
    _atomic_write(path, text)


def _queue_counts(records: list[dict[str, Any]]) -> dict[str, int]:
    counts = Counter(str(record["queue_class"]) for record in records)
    for queue in (
        "accepted_atom_candidates_for_review",
        "deferred_low_confidence",
        "rejected_overclaim_or_noisy",
    ):
        counts.setdefault(queue, 0)
    return dict(sorted(counts.items()))


def _record_samples(records: list[dict[str, Any]], queue: str, limit: int = 12) -> list[dict[str, Any]]:
    sample: list[dict[str, Any]] = []
    for record in records:
        if record["queue_class"] != queue:
            continue
        sample.append(
            {
                "atom_candidate_id": record["atom_candidate_id"],
                "recipe_id": record["recipe_id"],
                "source_path": record["source_path"],
                "typed_trace_edge_role": record["typed_trace_edge_role"],
                "typed_trace_terminal_node_id": record["typed_trace_terminal_node_id"],
            }
        )
        if len(sample) >= limit:
            break
    return sample


def _build_payload() -> dict[str, Any]:
    graph = _read_json(FIX22_GRAPH)
    preimages = _read_preimages(FIX22_PREIMAGES)
    fix25 = _read_json(FIX25_JSON)

    records, extraction_meta = _extract_full_repo_candidates(graph, preimages)
    _write_jsonl(ATOM_QUEUE_OUT, records)

    golden = _evaluate_golden()
    negative = _evaluate_negative_controls()
    manual = _evaluate_manual_spot_checks()
    forbidden_hit_count = sum(len(row["forbidden_hits"]) for row in negative["controls"])
    queue_counts = _queue_counts(records)
    role_counts = Counter(str(record["typed_trace_edge_role"]) for record in records)
    recipe_counts = Counter(str(record["recipe_id"]) for record in records)
    authority_counts = Counter(str(record["authority_class"]) for record in records)
    privacy_counts = Counter(str(record["privacy_class"]) for record in records)
    analysis_method_counts = Counter(str(record["analysis_method"]) for record in records)
    undeclared_role_count = role_counts.get("undeclared", 0)

    status = (
        "committed_research_only_axiomatic_replay"
        if golden["missing_atom_count"] == 0
        and negative["failed_count"] == 0
        and manual["failed_count"] == 0
        else "needs_review_calibration_gate_failed"
    )

    return {
        "analysis_method_counts": dict(sorted(analysis_method_counts.items())),
        "atom_candidate_jsonl": str(ATOM_QUEUE_OUT.relative_to(REPO_ROOT)),
        "atom_candidate_record_count": len(records),
        "authority_bearing_denominator_lock": {
            "fix25_authority_bearing_node_count": fix25["authority_bearing_node_count"],
            "phase26_denominator_action": "unchanged_no_node_metadata_reclassification",
        },
        "authority_class_counts": dict(sorted(authority_counts.items())),
        "calibration_gates": {
            "fix19_golden_replay": golden,
            "fix20_manual_spot_checks": manual,
            "fix20_negative_controls": negative,
            "held_out_validation_non_claim": "Fix19/Fix20 corpora were used as held-out validation gates only; no threshold tuning occurred in this run.",
        },
        "deferred_carry_forward": [
            "semantic_authority_bearing_node_count deferred to Fix29/Fix31.",
            "authority_document_file_node_count deferred to Fix29/Fix31.",
            "Support-edge backtrace orientation remains source_node_to_authority_terminal; support edges were not reversed.",
        ],
        "extraction_confusion_matrix": {
            "FN": golden["missing_atom_count"],
            "FP": forbidden_hit_count,
            "TP": golden["covered_atom_count"],
            "Uncertain": queue_counts["deferred_low_confidence"],
            "matrix_scope": "TP/FN/FP derive from held-out Fix19/Fix20 gates; Uncertain derives from full-repo deferred queue.",
        },
        "extraction_meta": extraction_meta,
        "fix25_baseline_inputs": {
            "authority_bearing_node_count": fix25["authority_bearing_node_count"],
            "directed_view_not_yet_contractualized_count": fix25["directed_view_not_yet_contractualized_count"],
            "source_derived_node_count": fix25["source_derived_node_count"],
        },
        "negative_controls": {
            "atom_candidates_not_promoted": True,
            "no_canonical_graph_mutation": True,
            "no_public_path_authorization": True,
            "undeclared_role_candidates_deferred": undeclared_role_count,
        },
        "non_claims": [
            "No atom candidate was promoted.",
            "No edge rewrite occurred.",
            "No canonical Genesis graph mutation occurred.",
            "No Genesis signing occurred.",
            "No node upload occurred.",
            "No public RC activation occurred.",
            "No runtime activation occurred.",
            "No ADR or CDL mutation occurred.",
            "Fix19/Fix20 golden corpus was treated as held-out validation and was not used to tune thresholds.",
            "Candidate queue acceptance means accepted for review only, not accepted into Genesis authority.",
        ],
        "phase": PHASE,
        "privacy_class_counts": dict(sorted(privacy_counts.items())),
        "queue_counts": queue_counts,
        "queue_samples": {
            "accepted_atom_candidates_for_review": _record_samples(records, "accepted_atom_candidates_for_review"),
            "deferred_low_confidence_atom_candidates": _record_samples(records, "deferred_low_confidence"),
            "rejected_overclaim_or_noisy_atom_candidates": _record_samples(records, "rejected_overclaim_or_noisy"),
        },
        "recipe_counts": dict(sorted(recipe_counts.items())),
        "schema_version": SCHEMA_VERSION,
        "sim_id": SIM_ID,
        "source_graph": str(FIX22_GRAPH.relative_to(REPO_ROOT)),
        "source_preimages": str(FIX22_PREIMAGES.relative_to(REPO_ROOT)),
        "status": status,
        "tokens": [
            "whole_graph_axiomatic_extraction_replay_committed_phase_1545p_fix26",
            "truth_primitive_recipe_replay_full_repo_phase_1545p_fix26",
            "atlas_atom_candidate_queue_generated_phase_1545p_fix26",
            "atlas_axiomatic_negative_controls_retained_phase_1545p_fix26",
            "atlas_atoms_not_promoted_phase_1545p_fix26",
            "public_path_remains_blocked_phase_1545p_fix26",
        ],
        "trace_role_counts": dict(sorted(role_counts.items())),
        "truth_primitives": list(TRUTH_PRIMITIVES),
        "typed_trace_contract": {
            "candidate_edge_orientation": "source_node_to_authority_or_classification_terminal",
            "supported_trace_roles": sorted(SUPPORTED_TRACE_ROLES),
            "traversal_direction_rule": "support traces use verification_backtrace; GOVERNS/ATTESTATION would use authority_forward",
        },
    }


def _counts_table(counts: dict[str, int]) -> list[str]:
    lines = ["| Class | Count |", "|---|---:|"]
    for key, value in sorted(counts.items()):
        lines.append(f"| `{key}` | `{value}` |")
    return lines


def _samples_table(samples: list[dict[str, Any]]) -> list[str]:
    lines = ["| Candidate | Recipe | Source | Role | Terminal |", "|---|---|---|---|---|"]
    for sample in samples:
        lines.append(
            f"| `{sample['atom_candidate_id']}` | `{sample['recipe_id']}` | `{sample['source_path']}` | "
            f"`{sample['typed_trace_edge_role']}` | `{sample['typed_trace_terminal_node_id']}` |"
        )
    return lines


def _report(payload: dict[str, Any]) -> str:
    lines = [
        "# SIM-ATLAS-AXIOMATIC-EXTRACTION-REPLAY-01",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: atlas_axiomatic_extraction_replay_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: research-only full-repo atom-candidate extraction; no canonical graph mutation, Genesis signing, public RC activation, or runtime activation -->",
        "",
        f"**Phase:** {PHASE}",
        f"**Status:** {payload['status']}",
        "**Sensitivity:** NON-SENSITIVE",
        "",
        "## Scope",
        "",
        "This SIM replays the Fix19/Fix20 recipe extractor over text-analyzable",
        "Fix22 whole-repo Atlas file nodes. It emits atom candidates for review",
        "only. It does not promote atoms, rewrite edges, mutate the canonical",
        "Genesis graph, sign nodes, upload nodes, or activate any public/runtime",
        "surface.",
        "",
        "## Extraction Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Text nodes in scope | `{payload['extraction_meta']['text_node_count']}` |",
        f"| Files analyzed | `{payload['extraction_meta']['analyzed_file_count']}` |",
        f"| Atom candidate records | `{payload['atom_candidate_record_count']}` |",
        f"| File read errors | `{payload['extraction_meta']['file_error_count']}` |",
        "",
        "## Queue Counts",
        "",
        *_counts_table(payload["queue_counts"]),
        "",
        "## Trace Role Counts",
        "",
        *_counts_table(payload["trace_role_counts"]),
        "",
        "## Recipe Counts",
        "",
        *_counts_table(payload["recipe_counts"]),
        "",
        "## Confusion Matrix",
        "",
        "| Class | Count | Scope |",
        "|---|---:|---|",
        f"| TP | `{payload['extraction_confusion_matrix']['TP']}` | Fix19/Fix20 held-out gates |",
        f"| FP | `{payload['extraction_confusion_matrix']['FP']}` | Fix20 negative controls |",
        f"| FN | `{payload['extraction_confusion_matrix']['FN']}` | Fix19 golden corpus |",
        f"| Uncertain | `{payload['extraction_confusion_matrix']['Uncertain']}` | Full-repo deferred queue |",
        "",
        "## Accepted For Review Samples",
        "",
        *_samples_table(payload["queue_samples"]["accepted_atom_candidates_for_review"]),
        "",
        "## Deferred Samples",
        "",
        *_samples_table(payload["queue_samples"]["deferred_low_confidence_atom_candidates"]),
        "",
        "## Known Limitations And Future Metric Refinements",
        "",
        "- Fix26 does not change the Fix25 authority-bearing denominator.",
        "- `semantic_authority_bearing_node_count` is deferred to Fix29/Fix31.",
        "- `authority_document_file_node_count` is deferred to Fix29/Fix31.",
        "- Support edges are emitted source to terminal; they are not reversed.",
        "- Accepted candidates are accepted for review only, not promoted.",
        "",
        "## Output Tokens",
        "",
    ]
    for token in payload["tokens"]:
        lines.append(f"- `{token}`")
    lines.extend(["", "## Non-Claims", ""])
    for non_claim in payload["non_claims"]:
        lines.append(f"- {non_claim}")
    lines.append("")
    return "\n".join(lines)


def _review(payload: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# ILC Atlas Axiomatic Extraction Replay Review - Phase 1545p-Fix26",
            "",
            "<!-- PUBLIC_RC_EXCLUDE: atlas_axiomatic_extraction_replay_review_research_only -->",
            "<!-- PUBLIC_RC_EXCLUDE_REASON: research-only review packet for unsigned atom-candidate queue; no public RC activation or canonical graph mutation -->",
            "",
            "## Verdict",
            "",
            "`PASS` for research-only extraction replay if calibration gates pass and",
            "candidate queues remain non-promotional.",
            "",
            "## Contract Findings",
            "",
            f"- Full-repo atom candidate queue: `{payload['atom_candidate_record_count']}` records.",
            f"- Accepted for review: `{payload['queue_counts']['accepted_atom_candidates_for_review']}`.",
            f"- Deferred low confidence: `{payload['queue_counts']['deferred_low_confidence']}`.",
            f"- Rejected overclaim/noisy: `{payload['queue_counts']['rejected_overclaim_or_noisy']}`.",
            f"- Fix25 authority-bearing denominator retained: `{payload['authority_bearing_denominator_lock']['fix25_authority_bearing_node_count']}`.",
            "- Python files use AST-derived symbol/docstring/comment text before recipe extraction.",
            "- Support trace candidates use source-node to terminal orientation for Fix25 mixed backtrace compatibility.",
            "",
            "## Carry-Forward",
            "",
            "- Fix27 may consume accepted review candidates as rewrite hypotheses, not as promoted edges.",
            "- Fix30 must treat proof-class erasure as a hard failure.",
            "- Fix31 must not classify candidates as Atlas signing-batch-ready without typed trace role, terminal, traversal direction, and governing condition record.",
            "",
            "## Non-Claims",
            "",
            "- No canonical Genesis graph mutation occurred.",
            "- No candidate atom was promoted.",
            "- No Genesis signing or node upload occurred.",
            "- No public path authorization occurred.",
            "",
        ]
    )


def main() -> None:
    payload = _build_payload()
    _atomic_write(JSON_OUT, _canonical_dumps(payload))
    _atomic_write(REPORT_OUT, _report(payload))
    _atomic_write(REVIEW_OUT, _review(payload))
    print(
        json.dumps(
            {
                "atom_candidate_record_count": payload["atom_candidate_record_count"],
                "json_out": str(JSON_OUT),
                "queue_counts": payload["queue_counts"],
                "status": payload["status"],
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
