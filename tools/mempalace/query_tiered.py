#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

DEFAULT_MANIFEST = Path("docs/tools/mempalace/ilc_mempalace_corpus_manifest_v0.1.json")
QUERY_CODE = r'''
import json
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
results = col.query(**kwargs)
docs = results["documents"][0]
metas = results["metadatas"][0]
dists = results["distances"][0]
payload = {
    "query": query,
    "wing": wing,
    "room": room,
    "distance_metric": distance_metric,
    "results": [
        {
            "text": doc,
            "source_file": meta.get("source_file", "?"),
            "wing": meta.get("wing", "unknown"),
            "room": meta.get("room", "unknown"),
            "distance": round(float(dist), 6),
            "relevance_score": round(1.0 / (1.0 + max(float(dist), 0.0)), 6),
        }
        for doc, meta, dist in zip(docs, metas, dists)
    ],
}
print(json.dumps(payload))
'''


def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


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
    if payload.get("source_filters"):
        lines.append(f'Source filters: {", ".join(payload["source_filters"])}')
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
            f'distance={item["distance"]} relevance_score={item["relevance_score"]}'
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
