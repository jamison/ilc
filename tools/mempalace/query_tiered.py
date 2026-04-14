#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

DEFAULT_MANIFEST = Path("docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TMPDIR = REPO_ROOT / "out" / "mempalace_tmp"
QUERY_CODE = r'''
import json
import re
import sys
import chromadb

query = sys.argv[1]
palace_path = sys.argv[2]
wing = sys.argv[3] or None
room = sys.argv[4] or None
n_results = int(sys.argv[5])
client = chromadb.PersistentClient(path=palace_path)
col = client.get_collection("mempalace_drawers")
collection_metadata = getattr(col, "metadata", None) or {}
distance_metric = collection_metadata.get("hnsw:space", "unknown")
kwargs = {
    "query_texts": [query],
    "n_results": n_results,
    "include": ["documents", "metadatas", "distances"],
}
if wing and room:
    kwargs["where"] = {"$and": [{"wing": wing}, {"room": room}]}
elif wing:
    kwargs["where"] = {"wing": wing}
elif room:
    kwargs["where"] = {"room": room}


def tokenize(text):
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def lexical_fallback():
    get_kwargs = {
        "include": ["documents", "metadatas"],
        "limit": col.count(),
    }
    if "where" in kwargs:
        get_kwargs["where"] = kwargs["where"]
    rows = col.get(**get_kwargs)
    docs = rows.get("documents", []) or []
    metas = rows.get("metadatas", []) or []
    query_tokens = set(tokenize(query))
    query_phrase = (query or "").strip().lower()
    ranked = []
    for idx, (doc, meta) in enumerate(zip(docs, metas)):
        source_file = meta.get("source_file", "?")
        source_tokens = set(tokenize(source_file))
        doc_tokens = set(tokenize(doc))
        overlap = len(query_tokens & doc_tokens)
        source_overlap = len(query_tokens & source_tokens)
        coverage = overlap / len(query_tokens) if query_tokens else 0.0
        phrase_bonus = 1.0 if query_phrase and query_phrase in (doc or "").lower() else 0.0
        source_bonus = 0.25 if source_overlap else 0.0
        lexical_score = round((phrase_bonus * 2.0) + coverage + source_bonus, 6)
        if lexical_score <= 0.0:
            continue
        ranked.append(
            (
                -lexical_score,
                source_file,
                idx,
                {
                    "text": doc,
                    "source_file": source_file,
                    "wing": meta.get("wing", "unknown"),
                    "room": meta.get("room", "unknown"),
                    "distance": None,
                    "relevance_score": lexical_score,
                },
            )
        )
    ranked.sort()
    return [item[-1] for item in ranked[:n_results]]


query_mode = "semantic"
semantic_error = None
try:
    results = col.query(**kwargs)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    rows = [
        {
            "text": doc,
            "source_file": meta.get("source_file", "?"),
            "wing": meta.get("wing", "unknown"),
            "room": meta.get("room", "unknown"),
            "distance": round(float(dist), 6),
            "relevance_score": round(1.0 / (1.0 + max(float(dist), 0.0)), 6),
        }
        for doc, meta, dist in zip(docs, metas, dists)
    ]
except Exception as exc:
    query_mode = "lexical_fallback"
    semantic_error = f"{type(exc).__name__}: {exc}"
    rows = lexical_fallback()

payload = {
    "query": query,
    "wing": wing,
    "room": room,
    "distance_metric": distance_metric,
    "query_mode": query_mode,
    "semantic_error": semantic_error,
    "results": rows,
}
print(json.dumps(payload))
'''


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def query_env() -> dict[str, str]:
    env = os.environ.copy()
    env["TMPDIR"] = env.get("ILC_MEMPALACE_TMPDIR", env.get("TMPDIR", str(DEFAULT_TMPDIR)))
    Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)
    return env


def query_memories(
    python_bin: str,
    *,
    palace_path: Path,
    query: str,
    tier: str | None,
    room: str | None,
    results: int,
    source_filters: list[str] | None = None,
) -> dict:
    requested_results = results
    fetch_results = max(results, requested_results * 10 if source_filters else results)
    proc = subprocess.run(
        [python_bin, "-c", QUERY_CODE, query, str(palace_path), tier or "", room or "", str(fetch_results)],
        check=True,
        capture_output=True,
        text=True,
        env=query_env(),
    )
    payload = json.loads(proc.stdout)
    if source_filters:
        payload["results"] = [
            item for item in payload.get("results", [])
            if any(fragment in item.get("source_file", "") for fragment in source_filters)
        ][:requested_results]
    else:
        payload["results"] = payload.get("results", [])[:requested_results]
    payload["source_filters"] = source_filters or []
    return payload


def render_text(payload: dict) -> str:
    lines = [f'Query: {payload["query"]}']
    if payload.get("wing"):
        lines.append(f'Tier: {payload["wing"]}')
    if payload.get("room"):
        lines.append(f'Room: {payload["room"]}')
    if payload.get("distance_metric"):
        lines.append(f'Distance metric: {payload["distance_metric"]}')
    if payload.get("query_mode"):
        lines.append(f'Query mode: {payload["query_mode"]}')
    if payload.get("source_filters"):
        lines.append(f'Source filters: {", ".join(payload["source_filters"])}')
    lines.append(f'TMPDIR: {query_env()["TMPDIR"]}')
    if payload.get("semantic_error"):
        lines.append(f'Semantic fallback reason: {payload["semantic_error"]}')
    lines.append("")
    results = payload.get("results", [])
    if not results:
        lines.append("No results.")
        return "\n".join(lines)
    for idx, item in enumerate(results, start=1):
        lines.append(f'[{idx}] {item["source_file"]}')
        lines.append(
            '  '
            f'wing={item["wing"]} room={item["room"]} '
            f'distance={item.get("distance")} relevance_score={item["relevance_score"]}'
        )
        text = item["text"].strip().replace("\n", " ")
        lines.append(f'  text={text[:240]}')
        lines.append("")
    return "\n".join(lines).rstrip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a tier-filtered MemPalace query.")
    parser.add_argument("query")
    parser.add_argument("--tier")
    parser.add_argument("--room")
    parser.add_argument("--results", type=int, default=5)
    parser.add_argument("--palace", type=Path, required=True)
    parser.add_argument("--python", dest="python_bin", default="python")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--source-contains", action="append", dest="source_filters")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    if args.tier and args.tier not in manifest["tiers"]:
        raise SystemExit(f"unknown_tier:{args.tier}")

    payload = query_memories(
        args.python_bin,
        palace_path=args.palace,
        query=args.query,
        tier=args.tier,
        room=args.room,
        results=args.results,
        source_filters=args.source_filters,
    )
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
