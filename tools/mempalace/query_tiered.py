#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

DEFAULT_MANIFEST = Path("docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json")
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TMPDIR = REPO_ROOT / "out" / "mempalace_tmp"
BM25_INDEX_NAME = ".ilc_bm25_index.pkl"

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


# ---------------------------------------------------------------------------
# BM25 query (runs in-process — rank_bm25 is lightweight)
# ---------------------------------------------------------------------------

def _bm25_tokenize(text: str) -> list[str]:
    # Same pattern as build_tiered_corpus.py — preserves CDL-044, ADR-0029, v5.0
    return re.findall(r"[a-z0-9][a-z0-9\-_.]*", text.lower())


def _query_bm25(
    palace_path: Path,
    query: str,
    tier: str | None,
    n_results: int,
) -> list[dict]:
    """Return BM25-ranked results from the palace's .ilc_bm25_index.pkl.

    Returns [] if the index doesn't exist or rank_bm25 is not installed.
    Each result: {text, source_file, wing, room, distance, relevance_score, _bm25_score}
    """
    index_path = palace_path / BM25_INDEX_NAME
    if not index_path.exists():
        return []
    try:
        import pickle  # noqa: PLC0415
        from rank_bm25 import BM25Okapi  # type: ignore  # noqa: PLC0415
    except ImportError:
        return []

    try:
        with index_path.open("rb") as fh:
            data = pickle.load(fh)  # noqa: S301
    except Exception:
        return []

    bm25: BM25Okapi = data["bm25"]
    meta: list[dict] = data["meta"]

    tokens = _bm25_tokenize(query)
    if not tokens:
        return []

    scores = bm25.get_scores(tokens)
    max_score = float(max(scores)) if scores.any() else 0.0
    if max_score <= 0.0:
        return []

    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    results = []
    for idx, raw_score in ranked:
        if len(results) >= n_results:
            break
        m = meta[idx]
        if tier and m.get("wing") != tier:
            continue
        norm_score = round(float(raw_score) / max_score, 6)
        results.append({
            "text": m["snippet"],
            "source_file": m["source_file"],
            "wing": m.get("wing", "unknown"),
            "room": "general",
            "distance": None,
            "relevance_score": norm_score,
            "_bm25_score": norm_score,
        })
    return results


def _merge_results(
    semantic: list[dict],
    bm25: list[dict],
    n_results: int,
) -> tuple[list[dict], str]:
    """Merge semantic + BM25 results. Deduplicate by source_file.

    Files appearing in both get a 25% relevance boost. BM25-only results are
    appended. Returns (merged_list, query_mode_label).
    """
    if not bm25:
        return semantic[:n_results], "semantic"
    if not semantic:
        return bm25[:n_results], "bm25"

    bm25_by_source = {r["source_file"]: r for r in bm25}
    seen: set[str] = set()
    merged: list[dict] = []

    for r in semantic:
        sf = r["source_file"]
        seen.add(sf)
        if sf in bm25_by_source:
            boosted = dict(r)
            boosted["relevance_score"] = round(min(1.0, r["relevance_score"] * 1.25), 6)
            boosted["_bm25_score"] = bm25_by_source[sf]["_bm25_score"]
            merged.append(boosted)
        else:
            merged.append(r)

    for r in bm25:
        if r["source_file"] not in seen:
            seen.add(r["source_file"])
            merged.append(r)

    merged.sort(key=lambda x: x["relevance_score"], reverse=True)
    return merged[:n_results], "hybrid"


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
        bm25_tag = f' bm25={item["_bm25_score"]}' if item.get("_bm25_score") else ""
        lines.append(f'[{idx}] {item["source_file"]}')
        lines.append(
            '  '
            f'wing={item["wing"]} room={item["room"]} '
            f'distance={item.get("distance")} relevance_score={item["relevance_score"]}'
            f'{bm25_tag}'
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
    parser.add_argument("--no-bm25", action="store_true",
                        help="Disable BM25 hybrid retrieval even if index exists.")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    manifest = load_manifest(args.manifest)
    if args.tier and args.tier not in manifest["tiers"]:
        raise SystemExit(f"unknown_tier:{args.tier}")

    # Run semantic (ChromaDB) and BM25 in parallel conceptually; merge results.
    # Fetch extra semantic results to allow for source_filter pruning + merging headroom.
    fetch_n = args.results * 3

    payload = query_memories(
        args.python_bin,
        palace_path=args.palace,
        query=args.query,
        tier=args.tier,
        room=args.room,
        results=fetch_n,
        source_filters=args.source_filters,
    )
    semantic_results = payload.get("results", [])[:fetch_n]

    bm25_results: list[dict] = []
    if not args.no_bm25:
        bm25_results = _query_bm25(args.palace, args.query, args.tier, fetch_n)

    merged, query_mode = _merge_results(semantic_results, bm25_results, args.results)
    payload["results"] = merged
    payload["query_mode"] = query_mode
    payload["bm25_hits"] = len(bm25_results)

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(render_text(payload))
    return 0


if __name__ == "__main__":
    sys.exit(main())
