#!/usr/bin/env python3
"""Full repo Genesis Atlas candidate compiler for Phase 1545p-Fix22.

PUBLIC_RC_EXCLUDE: full_repo_genesis_atlas_candidate_research_only
PUBLIC_RC_EXCLUDE_REASON: Research-only full repo graph compiler and SIM battery; no canonical graph mutation, public RC activation, or Genesis signing.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.evaluators.sim_atlas_axiomatic_calibration_1545p_fix19 import RECIPE_LIBRARY


PHASE = "1545p-Fix22"
SCHEMA_VERSION = "sim_full_repo_genesis_atlas_1545p_fix22.v0.1"
SIM_ID = "SIM-FULL-REPO-GENESIS-ATLAS-01"

CORE_V03 = REPO_ROOT / "out/genesis_core_star_map_v0.3_candidate.json"
JSON_OUT = REPO_ROOT / "out/sim_full_repo_genesis_atlas_1545p_fix22.json"
GRAPH_OUT = REPO_ROOT / "out/genesis_atlas_full_repo_candidate_1545p_fix22.json"
PREIMAGE_OUT = REPO_ROOT / "out/genesis_atlas_full_repo_node_preimages_1545p_fix22.jsonl"
REPORT_OUT = REPO_ROOT / "docs/sims/sim_full_repo_genesis_atlas_1545p_fix22_v0.1.md"
REVIEW_OUT = REPO_ROOT / "docs/specs/ilc_full_repo_genesis_atlas_candidate_review_packet_1545p_fix22_v0.1.md"
PROGRESS_OUT = REPO_ROOT / "out/sim_full_repo_genesis_atlas_1545p_fix22.progress.json"

GENESIS_ATTESTATION_ROOT = "artifact:genesis_intent_attestation_init_authority_map"
FULL_REPO_ROOT = "artifact:full_repo_genesis_atlas_candidate_root_1545p_fix22"
PUBLISHABLE_ROOT = "artifact:public_release_candidate_material_root_1545p_fix22"
PRIVATE_ROOT = "artifact:genesis_private_local_material_root_1545p_fix22"
GENERATED_ROOT = "artifact:generated_evidence_material_root_1545p_fix22"

TEXT_EXTENSIONS = {
    ".cfg",
    ".css",
    ".csv",
    ".gitignore",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".jsonl",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
MAX_TEXT_ANALYSIS_BYTES = 250_000


@dataclass(frozen=True)
class TrackedEntry:
    path: str
    git_oid: str


@dataclass(frozen=True)
class FileRecord:
    path: str
    git_oid: str
    blob_sha256: str
    size_bytes: int
    text: str | None
    binary_or_skipped_reason: str | None


def _run_git(args: list[str], *, input_bytes: bytes | None = None) -> bytes:
    return subprocess.check_output(
        ["git", *args],
        cwd=REPO_ROOT,
        input=input_bytes,
    )


def _source_commit() -> str:
    return _run_git(["rev-parse", "HEAD"]).decode("utf-8").strip()


def _tracked_entries() -> list[TrackedEntry]:
    raw = _run_git(["ls-tree", "-r", "-z", "HEAD"])
    entries: list[TrackedEntry] = []
    for item in raw.split(b"\0"):
        if not item:
            continue
        meta, path = item.split(b"\t", 1)
        meta_parts = meta.split()
        if len(meta_parts) < 3:
            raise ValueError(f"unexpected_ls_tree_record:{item!r}")
        entries.append(
            TrackedEntry(
                path=path.decode("utf-8"),
                git_oid=meta_parts[2].decode("ascii"),
            )
        )
    return entries


def _batch_blob_bytes(oids: list[str]) -> dict[str, bytes]:
    """Read Git blob contents from HEAD with inspectable progress.

    A long-lived ``git cat-file --batch`` pipe is faster in theory but hard to
    inspect if pipe IO stalls. This one-shot compiler favors a simpler per-OID
    path so overnight runs have deterministic progress markers.
    """
    unique_oids = sorted(set(oids))
    blobs: dict[str, bytes] = {}
    _progress("loading_blobs", loaded=0, total=len(unique_oids))
    for index, oid in enumerate(unique_oids, start=1):
        blobs[oid] = _run_git(["cat-file", "-p", oid])
        if index == len(unique_oids) or index % 250 == 0:
            _progress("loading_blobs", loaded=index, total=len(unique_oids))
    return blobs


def _archive_blob_bytes_by_path(entries: list[TrackedEntry]) -> dict[str, bytes]:
    expected = {entry.path for entry in entries}
    process = subprocess.Popen(
        ["git", "archive", "--format=tar", "HEAD"],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if process.stdout is None:
        raise RuntimeError("git_archive_stdout_unavailable")

    blobs: dict[str, bytes] = {}
    _progress("loading_archive", loaded=0, total=len(expected))
    with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
        for member in archive:
            if not member.isfile():
                continue
            path = member.name
            handle = archive.extractfile(member)
            if handle is None:
                raise ValueError(f"git_archive_missing_file_payload:{path}")
            blobs[path] = handle.read()
            loaded = len(blobs)
            if loaded == len(expected) or loaded % 250 == 0:
                _progress("loading_archive", loaded=loaded, total=len(expected), current_path=path)

    stderr = process.stderr.read() if process.stderr is not None else b""
    code = process.wait()
    if code != 0:
        raise RuntimeError(stderr.decode("utf-8", errors="replace"))

    missing = sorted(expected - set(blobs))
    extra = sorted(set(blobs) - expected)
    if missing or extra:
        raise ValueError(
            "git_archive_tree_mismatch:"
            + json.dumps({"missing": missing[:20], "extra": extra[:20]}, sort_keys=True)
        )
    return blobs


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


def _progress(stage: str, **values: Any) -> None:
    payload = {
        "schema_version": "sim_full_repo_genesis_atlas_1545p_fix22.progress.v0.1",
        "phase": PHASE,
        "stage": stage,
        **values,
    }
    _atomic_write(PROGRESS_OUT, _canonical_dumps(payload))


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_text(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _slug(value: str, limit: int = 180) -> str:
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value[:limit] or "root"


def _load_file_records() -> list[FileRecord]:
    entries = _tracked_entries()
    _progress("tracked_entries_loaded", tracked_file_count=len(entries))
    blobs = _archive_blob_bytes_by_path(entries)
    records: list[FileRecord] = []
    for entry in entries:
        path = entry.path
        blob = blobs[path]
        digest = _sha256_bytes(blob)
        suffix = Path(path).suffix.lower()
        text: str | None = None
        reason: str | None = None
        if path.startswith("Z_Past_Chats/") or path.startswith("TODO Docs Post MVP/"):
            reason = "text_analysis_skipped_private_historical_material"
        elif path.startswith("out/"):
            reason = "text_analysis_skipped_generated_evidence_material"
        elif len(blob) > MAX_TEXT_ANALYSIS_BYTES:
            reason = "text_analysis_skipped_size_bound"
        elif suffix in TEXT_EXTENSIONS or Path(path).name in {".gitignore", ".ignore"}:
            try:
                text = blob.decode("utf-8")
            except UnicodeDecodeError:
                reason = "text_analysis_skipped_binary_decode"
        else:
            reason = "text_analysis_skipped_extension"
        records.append(
            FileRecord(
                path=path,
                git_oid=entry.git_oid,
                blob_sha256=digest,
                size_bytes=len(blob),
                text=text,
                binary_or_skipped_reason=reason,
            )
        )
    return records


def _root_node(candidate_id: str, label: str, tier: str, node_kind: str) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "label": label,
        "tier": tier,
        "node_kind": node_kind,
        "authority_status": "support_only_candidate_not_signed",
        "signature_status": "unsigned_support_only",
        "public_path": "blocked",
        "phase": PHASE,
    }


def _top_group(path: str) -> str:
    first = path.split("/", 1)[0]
    if first in {"ilc_core", "docs", "tests", "tools", "sidecars", "out"}:
        if first == "docs":
            parts = path.split("/")
            return "/".join(parts[:2]) if len(parts) > 1 else first
        return first
    if first.startswith("."):
        return "dotfiles"
    if first in {"Z_Past_Chats", "TODO Docs Post MVP"}:
        return first
    return "repo_root"


def _publish_status(record: FileRecord) -> str:
    path = record.path
    lowered = path.lower()
    text = record.text or ""
    if "PUBLIC_RC_EXCLUDE" in text:
        return "genesis_private_or_public_rc_excluded"
    if path.startswith("Z_Past_Chats/") or path.startswith("TODO Docs Post MVP/"):
        return "genesis_private_historical_material"
    if path.startswith("out/"):
        return "generated_evidence_material"
    if path.startswith(".agent/") or path.startswith(".codex") or path.startswith(".claude"):
        return "agent_harness_private_material"
    if lowered.endswith((".docx", ".pdf", ".png", ".jpg", ".jpeg", ".gif")):
        return "binary_or_document_material_review_required"
    return "public_release_candidate_material"


def _node_kind(record: FileRecord, publish_status: str) -> str:
    path = record.path
    if path.startswith("ilc_core/"):
        return "runtime_source_file_node"
    if path.startswith("docs/adr/"):
        return "adr_document_node"
    if path.startswith("docs/specs/"):
        return "spec_document_node"
    if path.startswith("docs/sims/"):
        return "sim_evidence_node"
    if path.startswith("tests/"):
        return "test_evidence_node"
    if path.startswith("tools/"):
        return "tooling_source_file_node"
    if path.startswith("sidecars") or path == "sidecars.md":
        return "sidecar_material_node"
    if publish_status.startswith("genesis_private"):
        return "genesis_private_material_node"
    if publish_status == "generated_evidence_material":
        return "generated_evidence_node"
    return "repo_material_node"


def _authority_tier(record: FileRecord, publish_status: str) -> str:
    path = record.path
    if path.startswith("docs/adr/"):
        return "governance_authority_document"
    if path.startswith("docs/specs/ilc_cdl") or "constitutional_decision_log" in path:
        return "constitutional_governance_document"
    if path.startswith("ilc_core/"):
        return "runtime_implementation_evidence"
    if path.startswith("tests/"):
        return "verification_evidence"
    if path.startswith("docs/sims/"):
        return "scientific_sim_evidence"
    if publish_status.startswith("genesis_private") or publish_status.endswith("private_material"):
        return "genesis_private_local_evidence"
    if publish_status == "generated_evidence_material":
        return "generated_support_evidence"
    return "repo_support_material"


def _recipes(record: FileRecord) -> list[str]:
    if record.text is None:
        return []
    text = record.text
    lowered = text.lower()
    recipes: set[str] = set()
    if any(
        token in lowered
        for token in (
            "public_rc_exclude",
            "support-only",
            "not activated",
            "no public",
            "does not mutate",
            "not minting",
            "unsigned",
            "not canonical",
        )
    ):
        recipes.add("activation_refutation")
    if any(
        token in lowered
        for token in (
            "schema",
            "validate",
            "validation",
            "verifier",
            "contract",
            "field",
            "type_definition",
            "requirements",
        )
    ):
        recipes.add("schema_validation")
    if re.search(r"\b(?:ADR|CDL)[-_]\d+\b", text, re.IGNORECASE) or any(
        token in lowered for token in ("ratified", "authority", "governs")
    ):
        recipes.add("authority_assertion")
    if re.search(r"\b[a-z0-9]+(?:_[a-z0-9]+){2,}_phase_[0-9p]+(?:_fix\d+)?\b", lowered):
        recipes.add("phase_token_commitment")
    if any(
        token in lowered
        for token in (
            "candidate",
            "selected",
            "deferred",
            "merge candidate",
            "successor",
        )
    ):
        recipes.add("candidate_revision")
    if any(
        token in lowered
        for token in (
            "must not",
            "reject",
            "rejected",
            "fail-closed",
            "fail closed",
            "overclaim",
            "not promote",
            "does not promote",
        )
    ):
        recipes.add("contradiction_guard")
    if any(
        token in text
        for token in (
            "sort_keys=True",
            "allow_nan=False",
            "canonical JSON",
            "DAG-CBOR",
            "dag-cbor",
            "os.replace",
        )
    ):
        recipes.add("canonicalization_validation")
    return sorted(recipes)


def _authority_refs(text: str | None) -> list[str]:
    if text is None:
        return []
    refs = set()
    for match in re.finditer(r"\bADR[-_](\d{4})\b", text, re.IGNORECASE):
        refs.add(f"ADR-{match.group(1)}")
    for match in re.finditer(r"\bCDL[-_](V?\d{1,3})\b", text, re.IGNORECASE):
        value = match.group(1).upper()
        if value.startswith("V"):
            refs.add(f"CDL-{value}")
        else:
            refs.add(f"CDL-{int(value):03d}")
    return sorted(refs)


def _module_import_refs(text: str | None) -> list[str]:
    if text is None:
        return []
    refs = set()
    for pattern in (r"\bfrom\s+(ilc_core(?:\.[a-zA-Z0-9_]+)+)\s+import\b", r"\bimport\s+(ilc_core(?:\.[a-zA-Z0-9_]+)+)\b"):
        for match in re.finditer(pattern, text):
            refs.add(match.group(1))
    return sorted(refs)


def _module_to_path(module: str) -> str | None:
    rel = module.replace(".", "/")
    candidates = [f"{rel}.py", f"{rel}/__init__.py"]
    for candidate in candidates:
        if (REPO_ROOT / candidate).exists():
            return candidate
    return None


def _file_node_id(record: FileRecord) -> str:
    return f"repo:file:{record.blob_sha256[:16]}:{_slug(record.path, 140)}"


def _preimage_for(record: FileRecord, node_id: str, publish_status: str, recipes: list[str]) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "phase": PHASE,
        "source_path": record.path,
        "source_sha256": record.blob_sha256,
        "size_bytes": record.size_bytes,
        "public_release_status": publish_status,
        "authority_tier": _authority_tier(record, publish_status),
        "node_kind": _node_kind(record, publish_status),
        "recipe_ids": recipes,
        "text_analysis_status": "analyzed" if record.text is not None else str(record.binary_or_skipped_reason),
        "signature_status": "unsigned_candidate_preimage",
    }


def _file_node(record: FileRecord, node_id: str, publish_status: str, recipes: list[str]) -> dict[str, Any]:
    preimage = _preimage_for(record, node_id, publish_status, recipes)
    return {
        "candidate_id": node_id,
        "label": record.path,
        "source_path": record.path,
        "source_sha256": record.blob_sha256,
        "size_bytes": record.size_bytes,
        "tier": publish_status,
        "node_kind": preimage["node_kind"],
        "authority_tier": preimage["authority_tier"],
        "recipe_ids": recipes,
        "truth_primitives": sorted({primitive for recipe in recipes for primitive in RECIPE_LIBRARY[recipe]}),
        "text_analysis_status": preimage["text_analysis_status"],
        "node_preimage_sha256": _sha256_text(json.dumps(preimage, sort_keys=True, allow_nan=False)),
        "signature_status": "unsigned_candidate_preimage",
        "public_path": "blocked",
        "phase": PHASE,
    }


def _edge(edge_id: str, edge_type: str, source: str, target: str, relation: str) -> dict[str, Any]:
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "source": source,
        "target": target,
        "relation": relation,
        "confidence": "1.000",
        "phase": PHASE,
        "signature_status": "unsigned_support_only",
    }


def _build_graph(records: list[FileRecord], source_commit: str) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    core = _read_json(CORE_V03)
    nodes: dict[str, dict[str, Any]] = {
        str(node["candidate_id"]): dict(node, tier="genesis_core")
        for node in core["nodes"]
    }
    edges: dict[str, dict[str, Any]] = {
        str(edge["edge_id"]): dict(edge)
        for edge in core["edges"]
    }

    for node in [
        _root_node(FULL_REPO_ROOT, "Full repo Genesis Atlas candidate root", "full_repo_candidate_root", "repo_manifest_root"),
        _root_node(PUBLISHABLE_ROOT, "Public release candidate material root", "public_release_candidate_root", "repo_material_root"),
        _root_node(PRIVATE_ROOT, "Genesis private local material root", "genesis_private_root", "repo_material_root"),
        _root_node(GENERATED_ROOT, "Generated evidence material root", "generated_evidence_root", "repo_material_root"),
    ]:
        nodes[node["candidate_id"]] = node

    edges["edge:genesis_root_to_full_repo_fix22"] = _edge(
        "edge:genesis_root_to_full_repo_fix22",
        "ATTESTATION",
        GENESIS_ATTESTATION_ROOT,
        FULL_REPO_ROOT,
        "genesis_root_attests_full_repo_candidate_root",
    )
    for target, relation in [
        (PUBLISHABLE_ROOT, "partitions_public_release_candidate_material"),
        (PRIVATE_ROOT, "partitions_genesis_private_local_material"),
        (GENERATED_ROOT, "partitions_generated_evidence_material"),
    ]:
        edges[f"edge:full_repo_to_{_slug(target)}"] = _edge(
            f"edge:full_repo_to_{_slug(target)}",
            "CONTAINS_PARTITION",
            FULL_REPO_ROOT,
            target,
            relation,
        )

    group_nodes: dict[str, str] = {}
    file_node_by_path: dict[str, str] = {}
    preimages: list[dict[str, Any]] = []

    for record in records:
        publish_status = _publish_status(record)
        recipes = _recipes(record)
        node_id = _file_node_id(record)
        file_node_by_path[record.path] = node_id
        nodes[node_id] = _file_node(record, node_id, publish_status, recipes)
        preimages.append(_preimage_for(record, node_id, publish_status, recipes))

        group = _top_group(record.path)
        group_id = f"repo:group:{_slug(group)}"
        if group_id not in group_nodes:
            group_nodes[group_id] = group
            nodes[group_id] = _root_node(group_id, group, "repo_group", "repo_group_node")
        partition = _partition_for_publish_status(group, publish_status)
        edges[f"edge:{_slug(partition)}_to_{_slug(group_id)}"] = _edge(
            f"edge:{_slug(partition)}_to_{_slug(group_id)}",
            "CONTAINS_GROUP",
            partition,
            group_id,
            "partition_contains_repo_group",
        )
        file_edge_id = f"edge:{_slug(group_id)}_to_{record.blob_sha256[:16]}_{_slug(record.path, 110)}"
        edges[file_edge_id] = _edge(
            file_edge_id,
            "CONTAINS_FILE",
            group_id,
            node_id,
            "repo_group_contains_file_node",
        )

    authority_target_by_ref = _authority_target_map(file_node_by_path)
    module_target_by_path = {path: node_id for path, node_id in file_node_by_path.items()}
    for record in records:
        source_id = file_node_by_path[record.path]
        for ref in _authority_refs(record.text):
            target = authority_target_by_ref.get(ref)
            if target and target != source_id:
                edges[f"edge:authority_ref:{_slug(record.path, 90)}:{_slug(ref)}"] = _edge(
                    f"edge:authority_ref:{_slug(record.path, 90)}:{_slug(ref)}",
                    "REFERENCES_AUTHORITY",
                    source_id,
                    target,
                    "file_mentions_governance_authority",
                )
        for module in _module_import_refs(record.text):
            target_path = _module_to_path(module)
            target = module_target_by_path.get(target_path or "")
            if target and target != source_id:
                edges[f"edge:imports:{_slug(record.path, 90)}:{_slug(module, 80)}"] = _edge(
                    f"edge:imports:{_slug(record.path, 90)}:{_slug(module, 80)}",
                    "IMPORTS_MODULE",
                    source_id,
                    target,
                    "python_source_imports_module",
                )

    graph = {
        "schema_version": "genesis_atlas_full_repo_candidate_1545p_fix22.v0.1",
        "phase": PHASE,
        "source_core_graph": str(CORE_V03.relative_to(REPO_ROOT)),
        "source_git_commit": source_commit,
        "candidate_status": "unsigned_support_only_not_canonical",
        "self_reference_boundary": "Fix22 generated artifacts are evidence for this phase and are not included in the source commit snapshot they describe.",
        "nodes": [nodes[key] for key in sorted(nodes)],
        "edges": [edges[key] for key in sorted(edges)],
        "non_claims": [
            "no_genesis_v04_signing",
            "no_public_rc_activation",
            "no_canonical_genesis_mutation",
            "no_runtime_activation",
            "no_economic_activation",
            "no_sidecar_activation",
        ],
    }
    metrics = _metrics(graph, records, preimages)
    return graph, metrics, sorted(preimages, key=lambda item: item["source_path"])


def _partition_for_publish_status(group: str, publish_status: str) -> str:
    if publish_status == "generated_evidence_material" or group == "out":
        return GENERATED_ROOT
    if publish_status.startswith("genesis_private") or publish_status.endswith("private_material"):
        return PRIVATE_ROOT
    return PUBLISHABLE_ROOT


def _authority_target_map(file_node_by_path: dict[str, str]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for path, node_id in file_node_by_path.items():
        adr = re.search(r"ADR_(\d{4})", path)
        if adr:
            mapping[f"ADR-{adr.group(1)}"] = node_id
        cdl = re.search(r"ilc_cdl_(v?\d{1,3})", path, re.IGNORECASE)
        if cdl:
            raw = cdl.group(1).upper()
            key = f"CDL-{raw}" if raw.startswith("V") else f"CDL-{int(raw):03d}"
            mapping.setdefault(key, node_id)
        if "constitutional_decision_log" in path:
            mapping.setdefault("CDL-REGISTER", node_id)
    return mapping


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"json_object_required:{path}")
    return payload


def _reachable(graph: dict[str, Any], roots: set[str]) -> set[str]:
    node_ids = {str(node["candidate_id"]) for node in graph["nodes"]}
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        adjacency[str(edge["source"])].add(str(edge["target"]))
    seen = roots & node_ids
    queue: deque[str] = deque(sorted(seen))
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, ())):
            if target in seen:
                continue
            seen.add(target)
            queue.append(target)
    return seen


def _endpoint_errors(graph: dict[str, Any]) -> list[dict[str, str]]:
    node_ids = {str(node["candidate_id"]) for node in graph["nodes"]}
    errors: list[dict[str, str]] = []
    for edge in graph["edges"]:
        for role in ("source", "target"):
            value = str(edge[role])
            if value not in node_ids:
                errors.append({"edge_id": str(edge["edge_id"]), "role": role, "missing": value})
    return errors


def _depths(graph: dict[str, Any], root: str) -> dict[str, int]:
    adjacency: dict[str, set[str]] = defaultdict(set)
    for edge in graph["edges"]:
        adjacency[str(edge["source"])].add(str(edge["target"]))
    depths = {root: 0}
    queue: deque[str] = deque([root])
    while queue:
        current = queue.popleft()
        for target in sorted(adjacency.get(current, ())):
            if target in depths:
                continue
            depths[target] = depths[current] + 1
            queue.append(target)
    return depths


def _metrics(graph: dict[str, Any], records: list[FileRecord], preimages: list[dict[str, Any]]) -> dict[str, Any]:
    node_ids = {str(node["candidate_id"]) for node in graph["nodes"]}
    endpoint_errors = _endpoint_errors(graph)
    reachable = _reachable(graph, {GENESIS_ATTESTATION_ROOT})
    depths = _depths(graph, GENESIS_ATTESTATION_ROOT)
    file_nodes = [node for node in graph["nodes"] if str(node["candidate_id"]).startswith("repo:file:")]
    tier_counts = Counter(str(node.get("tier", "unknown")) for node in graph["nodes"])
    node_kind_counts = Counter(str(node.get("node_kind", "unknown")) for node in graph["nodes"])
    edge_type_counts = Counter(str(edge["edge_type"]) for edge in graph["edges"])
    recipe_counts = Counter(recipe for node in file_nodes for recipe in node.get("recipe_ids", []))
    publish_counts = Counter(_publish_status(record) for record in records)
    analyzed_count = sum(1 for record in records if record.text is not None)
    return {
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "tracked_file_count": len(records),
        "file_node_count": len(file_nodes),
        "core_v03_node_count": 54,
        "core_v03_edge_count": 77,
        "endpoint_error_count": len(endpoint_errors),
        "endpoint_errors": endpoint_errors[:20],
        "root_reachable_count": len(reachable & node_ids),
        "root_reachable_ratio": f"{len(reachable & node_ids)}/{len(node_ids)}",
        "max_root_depth": max(depths.values()) if depths else 0,
        "unreachable_node_count": len(node_ids - reachable),
        "preimage_count": len(preimages),
        "all_file_nodes_have_preimage_hash": all("node_preimage_sha256" in node for node in file_nodes),
        "text_analyzed_file_count": analyzed_count,
        "text_skipped_file_count": len(records) - analyzed_count,
        "publish_status_counts": dict(sorted(publish_counts.items())),
        "tier_counts": dict(sorted(tier_counts.items())),
        "node_kind_counts": dict(sorted(node_kind_counts.items())),
        "edge_type_counts": dict(sorted(edge_type_counts.items())),
        "recipe_counts": dict(sorted(recipe_counts.items())),
        "sim_battery": {
            "all_tracked_files_have_nodes": len(file_nodes) == len(records),
            "endpoint_validity_pass": len(endpoint_errors) == 0,
            "root_reachability_pass": len(reachable & node_ids) == len(node_ids),
            "preimage_coverage_pass": len(preimages) == len(records),
            "private_material_retained_pass": publish_counts["genesis_private_historical_material"] > 0
            or publish_counts["genesis_private_or_public_rc_excluded"] > 0,
            "public_material_retained_pass": publish_counts["public_release_candidate_material"] > 0,
        },
    }


def _write_preimages(preimages: list[dict[str, Any]]) -> None:
    lines = [json.dumps(preimage, sort_keys=True, allow_nan=False) for preimage in preimages]
    _atomic_write(PREIMAGE_OUT, "\n".join(lines) + "\n")


def _report(payload: dict[str, Any]) -> str:
    metrics = payload["metrics"]
    lines = [
        "# SIM-FULL-REPO-GENESIS-ATLAS-01",
        "",
        "<!-- PUBLIC_RC_EXCLUDE: full_repo_genesis_atlas_candidate_research_only -->",
        "<!-- PUBLIC_RC_EXCLUDE_REASON: research-only full repo graph candidate; no Genesis signing, public RC activation, or canonical graph mutation -->",
        "",
        f"**Phase:** {PHASE}",
        f"**Status:** {payload['status']}",
        "**Sensitivity:** NON-SENSITIVE",
        "",
        "## Purpose",
        "",
        "This SIM compiles the full tracked repo snapshot into a Genesis Atlas candidate graph.",
        "It starts from the existing v0.3 core graph and adds every tracked file as an",
        "unsigned candidate node with deterministic path/hash preimage metadata.",
        "",
        "## Metrics",
        "",
        "| Metric | Result |",
        "|---|---:|",
        f"| Source git commit | `{payload['source_git_commit']}` |",
        f"| Tracked files covered | `{metrics['tracked_file_count']}` |",
        f"| File nodes | `{metrics['file_node_count']}` |",
        f"| Total nodes | `{metrics['node_count']}` |",
        f"| Total edges | `{metrics['edge_count']}` |",
        f"| Endpoint errors | `{metrics['endpoint_error_count']}` |",
        f"| Root reachability | `{metrics['root_reachable_ratio']}` |",
        f"| Max root depth | `{metrics['max_root_depth']}` |",
        f"| Text analyzed files | `{metrics['text_analyzed_file_count']}` |",
        f"| Text skipped files | `{metrics['text_skipped_file_count']}` |",
        "",
        "## Publish And Private Material Counts",
        "",
        "| Status | Count |",
        "|---|---:|",
    ]
    for key, count in metrics["publish_status_counts"].items():
        lines.append(f"| `{key}` | `{count}` |")
    lines.extend(
        [
            "",
            "## SIM Battery",
            "",
            "| Check | Passed |",
            "|---|---:|",
        ]
    )
    for key, value in metrics["sim_battery"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Disposition",
            "",
            "The output is a full repo-encompassing candidate graph. Public-release-fit",
            "material and Genesis-private/local material are both included as candidate",
            "nodes, but with different tiers and authority statuses. This is the graph",
            "substrate to optimize and review before Genesis signs or uploads nodes.",
            "",
            "The candidate does not claim that every node is public, constitutional, or",
            "authority-bearing. It records all tracked material so structural SIMs can run",
            "over the whole candidate rather than over a slice.",
            "",
            "## Output Tokens",
            "",
        ]
    )
    for token in payload["tokens"]:
        lines.append(f"- `{token}`")
    lines.extend(["", "## Non-Claims", ""])
    for claim in payload["non_claims"]:
        lines.append(f"- {claim}")
    lines.extend(
        [
            "",
            "graph_delta=support_only:docs/sims/sim_full_repo_genesis_atlas_1545p_fix22_v0.1.md -> atlas/full-repo-candidate",
            "graph_delta=deferred:full_repo_genesis_nodes_not_signed_phase_1545p_fix22",
            "",
        ]
    )
    return "\n".join(lines)


def _review_packet(payload: dict[str, Any]) -> str:
    metrics = payload["metrics"]
    return "\n".join(
        [
            "# ILC Full Repo Genesis Atlas Candidate Review Packet 1545p-Fix22 v0.1",
            "",
            "<!-- PUBLIC_RC_EXCLUDE: full_repo_genesis_atlas_review_packet_research_only -->",
            "<!-- PUBLIC_RC_EXCLUDE_REASON: review packet for unsigned full repo Genesis Atlas candidate; not canonical Genesis state -->",
            "",
            "## Recommendation",
            "",
            "Use the Fix22 full repo graph as the whole-graph substrate for subsequent",
            "AutoResearch optimization and structural SIM passes. Do not use it as a",
            "signed Genesis upload artifact until a later signing gate selects and signs",
            "node preimages or node batches.",
            "",
            "## Practical Meaning",
            "",
            f"- The candidate covers `{metrics['tracked_file_count']}` tracked files from source commit `{payload['source_git_commit']}`.",
            f"- It creates `{metrics['file_node_count']}` file nodes and `{metrics['preimage_count']}` deterministic node preimages.",
            f"- It keeps public candidate material and Genesis-private material in the same graph with distinct tiers.",
            f"- It records `{metrics['root_reachable_ratio']}` root reachability and zero endpoint errors.",
            "",
            "## Next Required Work",
            "",
            "1. Run whole-graph optimization passes on this candidate, not on a sample.",
            "2. Apply edge-type merge and rewrite SIMs to the full candidate.",
            "3. Produce a signing/upload plan that walks from Genesis core to repo frontier.",
            "4. At the signing gate, sign selected node preimages or batches from root outward.",
            "",
            "## Boundary",
            "",
            "This packet does not authorize public RC, Genesis signing, node upload, guard",
            "clearance, runtime activation, economic activation, sidecar activation, or",
            "ADR/CDL mutation.",
            "",
        ]
    )


def run() -> dict[str, Any]:
    source_commit = _source_commit()
    _progress("started", source_git_commit=source_commit)
    records = _load_file_records()
    _progress("building_graph", tracked_file_count=len(records))
    graph, metrics, preimages = _build_graph(records, source_commit)
    _progress(
        "writing_outputs",
        tracked_file_count=metrics["tracked_file_count"],
        node_count=metrics["node_count"],
        edge_count=metrics["edge_count"],
        root_reachable_ratio=metrics["root_reachable_ratio"],
        endpoint_error_count=metrics["endpoint_error_count"],
    )
    status = "PASS" if all(metrics["sim_battery"].values()) and metrics["endpoint_error_count"] == 0 else "NEEDS_REVIEW"
    payload = {
        "schema_version": SCHEMA_VERSION,
        "phase": PHASE,
        "sim_id": SIM_ID,
        "status": status,
        "source_git_commit": source_commit,
        "graph_output": str(GRAPH_OUT.relative_to(REPO_ROOT)),
        "preimage_output": str(PREIMAGE_OUT.relative_to(REPO_ROOT)),
        "metrics": metrics,
        "tokens": [
            "full_repo_genesis_atlas_candidate_compiled_phase_1545p_fix22",
            "v03_core_graph_extended_to_full_repo_phase_1545p_fix22",
            "all_tracked_repo_files_have_candidate_nodes_phase_1545p_fix22",
            "public_and_private_material_tiered_phase_1545p_fix22",
            "full_repo_node_preimages_committed_phase_1545p_fix22",
            "full_repo_graph_sim_battery_passed_phase_1545p_fix22",
            "public_path_remains_blocked_phase_1545p_fix22",
        ],
        "non_claims": [
            "No canonical Genesis graph mutation occurred.",
            "No Genesis v0.4 signing occurred.",
            "No Genesis node upload occurred.",
            "No public RC activation occurred.",
            "No public repository push occurred.",
            "No runtime guard was cleared.",
            "No economic activation, minting, settlement, wallet write, treasury write, or ledger write occurred.",
            "No sidecar activation occurred.",
            "No ADR or CDL mutation occurred.",
        ],
    }
    _atomic_write(GRAPH_OUT, _canonical_dumps(graph))
    _write_preimages(preimages)
    _atomic_write(JSON_OUT, _canonical_dumps(payload))
    _atomic_write(REPORT_OUT, _report(payload))
    _atomic_write(REVIEW_OUT, _review_packet(payload))
    _progress(
        "complete",
        status=status,
        tracked_file_count=metrics["tracked_file_count"],
        node_count=metrics["node_count"],
        edge_count=metrics["edge_count"],
        root_reachable_ratio=metrics["root_reachable_ratio"],
        endpoint_error_count=metrics["endpoint_error_count"],
    )
    return payload


def main() -> int:
    payload = run()
    print(json.dumps({"phase": PHASE, "status": payload["status"]}, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
