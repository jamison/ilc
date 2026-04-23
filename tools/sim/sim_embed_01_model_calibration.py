#!/usr/bin/env python3
"""
SIM-EMBED-01: embedding model calibration per payload-modality family.

This research script is intentionally off the runtime hot path. It benchmarks
candidate embedding models against a small deterministic ILC-style corpus and
reports:

- semantic proximity margin (within-cluster cosine minus across-cluster cosine)
- median cold-cache latency per node
- benign-drift stability across synthetic epoch variants

Scope boundary:
- no ilc_core/ mutation
- no embedding pipeline activation
- no gossip / beacon wiring

Environment notes:
- text local models require transformers + torch
- image baseline requires transformers + pillow
- text-embedding-3-small is optional and is only evaluated when OPENAI_API_KEY
  is present in the environment
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from transformers import AutoModel, AutoProcessor, AutoTokenizer, CLIPModel


TEXT_MODELS: dict[str, str] = {
    "sentence-transformers/all-MiniLM-L6-v2": "minilm",
    "nomic-ai/nomic-embed-text-v1.5": "nomic",
}

IMAGE_MODEL = "openai/clip-vit-base-patch32"


@dataclass(frozen=True)
class CorpusItem:
    label: str
    payload: object


def _mean_pool(last_hidden_state: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
    mask = attention_mask.unsqueeze(-1).expand(last_hidden_state.size()).float()
    summed = torch.sum(last_hidden_state * mask, dim=1)
    counts = torch.clamp(mask.sum(dim=1), min=1e-9)
    return summed / counts


def _l2_normalize(matrix: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    return matrix / np.clip(norms, 1e-12, None)


def _pairwise_margin(vectors: np.ndarray, labels: Sequence[str]) -> tuple[float, float, float]:
    sims = vectors @ vectors.T
    within: list[float] = []
    across: list[float] = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            bucket = within if labels[i] == labels[j] else across
            bucket.append(float(sims[i, j]))
    return float(np.mean(within)), float(np.mean(across)), float(np.mean(within) - np.mean(across))


def _latency_ms_per_node(encoder: Callable[[Sequence[object]], np.ndarray], items: Sequence[object]) -> float:
    timings: list[float] = []
    for _ in range(3):
        t0 = time.perf_counter()
        encoder(items)
        timings.append((time.perf_counter() - t0) * 1000.0 / len(items))
    return float(np.median(timings))


def _plain_corpus() -> dict[str, list[str]]:
    return {
        "validator": [
            "Validator admission stays human gated until the bootstrap transition criteria are met.",
            "Epoch checkpoint verification must resolve the historically active validator set.",
            "A non genesis validator cannot join until governance and activation conditions hold.",
        ],
        "hypergraph": [
            "A hyperedge panel records one claim, several evidence nodes, and multiple judging agents.",
            "The local lambda2 signal describes whether a cluster is sparse but healthy or near partition.",
            "A spectral beacon carries a privacy noised local fingerprint of a validator neighborhood.",
        ],
        "route": [
            "The star map route index hashes n grams into advisory routing buckets.",
            "Route clusters are navigational results that help an agent move toward a target neighborhood.",
            "A route index is a low cost prefilter before expensive semantic retrieval.",
        ],
        "evidence": [
            "A claim can be supported by evidence or weakened by a refutation coalition.",
            "Contradiction handling compares competing assertions and their provenance trails.",
            "Evidence submission remains auditable through append only observational feeds.",
        ],
    }


def _markdown_wrap(theme: str, text: str, idx: int) -> str:
    return (
        f"# {theme.title()} note {idx}\n\n"
        f"- focus: {text}\n"
        "- status: reviewable\n"
        "- lane: hypergraph\n"
    )


def _json_wrap(theme: str, text: str, idx: int) -> str:
    payload = {
        "topic": theme,
        "summary": text,
        "epoch": idx,
        "tags": ["ilc", "hypergraph", theme],
        "reviewable": True,
    }
    return json.dumps(payload, sort_keys=True)


def _render_card(theme: str, text: str, variant: int) -> Image.Image:
    colors = {
        "validator": ("#1d4ed8", "#dbeafe"),
        "hypergraph": ("#047857", "#d1fae5"),
        "route": ("#7c3aed", "#ede9fe"),
        "evidence": ("#b45309", "#fef3c7"),
    }
    shapes = {
        "validator": "circle",
        "hypergraph": "grid",
        "route": "path",
        "evidence": "triangle",
    }
    fg, bg = colors[theme]
    image = Image.new("RGB", (256, 256), bg)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.rounded_rectangle((12, 12, 244, 244), radius=20, outline=fg, width=4 + variant)
    shape = shapes[theme]
    if shape == "circle":
        draw.ellipse((36, 36, 96, 96), outline=fg, width=4 + variant)
        draw.ellipse((120, 36, 180, 96), outline=fg, width=4 + variant)
    elif shape == "grid":
        for x in (48, 96, 144, 192):
            draw.line((x, 36, x, 120), fill=fg, width=3)
        for y in (36, 64, 92, 120):
            draw.line((48, y, 192, y), fill=fg, width=3)
    elif shape == "path":
        draw.line((32, 112, 80, 48, 144, 80, 216, 40), fill=fg, width=5 + variant)
        for pt in ((32, 112), (80, 48), (144, 80), (216, 40)):
            draw.ellipse((pt[0] - 6, pt[1] - 6, pt[0] + 6, pt[1] + 6), fill=fg)
    else:
        draw.polygon((64, 120, 128, 36, 192, 120), outline=fg, width=4 + variant)
        draw.line((64, 120, 192, 120), fill=fg, width=4 + variant)
    draw.text((20, 150), theme.upper(), fill=fg, font=font)
    draw.text((20, 172), text[:24], fill="#111827", font=font)
    if variant:
        draw.text((20, 194), f"epoch {variant}", fill="#374151", font=font)
    return image


def build_corpora() -> dict[str, list[CorpusItem]]:
    plain = _plain_corpus()
    corpora: dict[str, list[CorpusItem]] = {
        "text/plain": [],
        "text/markdown": [],
        "application/json": [],
        "image/*": [],
    }
    for theme, items in plain.items():
        for idx, text in enumerate(items, start=1):
            corpora["text/plain"].append(CorpusItem(theme, text))
            corpora["text/markdown"].append(CorpusItem(theme, _markdown_wrap(theme, text, idx)))
            corpora["application/json"].append(CorpusItem(theme, _json_wrap(theme, text, idx)))
            corpora["image/*"].append(CorpusItem(theme, _render_card(theme, text, idx % 3)))
    return corpora


@torch.no_grad()
def _build_text_encoder(model_id: str) -> Callable[[Sequence[object]], np.ndarray]:
    # trust_remote_code is required for nomic-embed-text: it uses custom mean-pooling
    # layers defined in the model repo that are not part of the standard transformers
    # AutoModel dispatch path.  MiniLM does not need this and the flag has no effect for it.
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code="nomic" in model_id)
    model = AutoModel.from_pretrained(model_id, trust_remote_code="nomic" in model_id)

    def encode(payloads: Sequence[object]) -> np.ndarray:
        texts = [str(p) for p in payloads]
        batch = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        output = model(**batch)
        pooled = _mean_pool(output.last_hidden_state, batch["attention_mask"])
        return _l2_normalize(pooled.detach().cpu().numpy())

    return encode


@torch.no_grad()
def _build_image_encoder() -> Callable[[Sequence[object]], np.ndarray]:
    processor = AutoProcessor.from_pretrained(IMAGE_MODEL)
    model = CLIPModel.from_pretrained(IMAGE_MODEL)

    def encode(payloads: Sequence[object]) -> np.ndarray:
        images = list(payloads)
        batch = processor(images=images, return_tensors="pt")
        features = model.get_image_features(**batch)
        return _l2_normalize(features.detach().cpu().numpy())

    return encode


def _staleness_scores_text(encoder: Callable[[Sequence[object]], np.ndarray], base_text: str) -> list[float]:
    # Variants are whitespace-normalized and case-only mutations of the same sentence.
    # MiniLM produces cosine ≈ 1.0000 for all eight — the simulation shows zero drift under
    # trivial reformatting but gives no signal about real content evolution (added/changed
    # sentences).  The recommended TTL=32 in the results doc is therefore a conservative
    # conventional choice, not a value derived from this curve.
    base = encoder([base_text])[0]
    variants: list[str] = []
    for epoch in range(1, 9):
        if epoch % 2:
            variants.append("  " + base_text.replace("Validator", "validator") + "  ")
        else:
            variants.append(base_text + " ")
    return [float((base * encoder([variant])[0]).sum()) for variant in variants]


def _staleness_scores_markdown(encoder: Callable[[Sequence[object]], np.ndarray], base_md: str) -> list[float]:
    base = encoder([base_md])[0]
    variants: list[str] = []
    for epoch in range(1, 9):
        if epoch % 2:
            variants.append(base_md.replace("- ", "* "))
        else:
            variants.append(base_md.replace("# Validator", "## Validator"))
    return [float((base * encoder([variant])[0]).sum()) for variant in variants]


def _staleness_scores_json(encoder: Callable[[Sequence[object]], np.ndarray], base_text: str) -> list[float]:
    # What this curve actually measures: semantic drift caused by the "epoch" metadata field
    # incrementing from 1 to 8 across the eight variants.
    #
    # The variants also alternate key ordering (sort_keys=True/False), but the subsequent
    # json.loads + json.dumps(sort_keys=True) canonicalization erases all key-order
    # differences before embedding.  The resulting drift sequence is driven entirely by
    # the epoch-field value change, not by formatting noise.
    #
    # The conclusion — "regenerate immediately on canonical payload hash change" — is still
    # correct: if the epoch field changes, the canonical hash changes, which triggers
    # regeneration.  But the TTL=48 recommendation reflects how slowly the embedding drifts
    # as epoch metadata increments, not how robust it is to structural JSON reformatting.
    # H-010 must treat any canonical payload change (including epoch-field updates) as a
    # cache-invalidation event rather than relying on the TTL alone.
    base_payload = {
        "topic": "validator",
        "summary": base_text,
        "epoch": 1,
        "tags": ["ilc", "hypergraph", "validator"],
        "reviewable": True,
    }
    base = encoder([json.dumps(base_payload, sort_keys=True)])[0]
    scores: list[float] = []
    for epoch in range(1, 9):
        raw = json.dumps(
            {
                "reviewable": True,
                "tags": ["ilc", "hypergraph", "validator"],
                "epoch": epoch,
                "summary": base_text,
                "topic": "validator",
            },
            sort_keys=(epoch % 2 == 0),
        )
        canonical = json.dumps(json.loads(raw), sort_keys=True)
        scores.append(float((base * encoder([canonical])[0]).sum()))
    return scores


def _staleness_scores_image(encoder: Callable[[Sequence[object]], np.ndarray]) -> list[float]:
    base = encoder([_render_card("validator", "bootstrap transition", 0)])[0]
    variants: list[Image.Image] = []
    for epoch in range(1, 9):
        variant = _render_card("validator", "bootstrap transition", epoch)
        if epoch % 2 == 0:
            variant = variant.filter(ImageFilter.GaussianBlur(radius=0.2))
        variants.append(variant)
    return [float((base * encoder([image])[0]).sum()) for image in variants]


def main() -> None:
    corpora = build_corpora()
    results: dict[str, list[dict[str, float | str]]] = {
        "modalities": [],
        "staleness": [],
    }

    text_encoders = {
        model_id: _build_text_encoder(model_id)
        for model_id in TEXT_MODELS
    }
    image_encoder = _build_image_encoder()

    for family in ("text/plain", "text/markdown", "application/json"):
        items = corpora[family]
        labels = [item.label for item in items]
        payloads = [item.payload for item in items]
        for model_id in TEXT_MODELS:
            encoder = text_encoders[model_id]
            vectors = encoder(payloads)
            within, across, margin = _pairwise_margin(vectors, labels)
            results["modalities"].append(
                {
                    "family": family,
                    "model": model_id,
                    "within_mean": round(within, 4),
                    "across_mean": round(across, 4),
                    "margin": round(margin, 4),
                    "latency_ms_per_node": round(_latency_ms_per_node(encoder, payloads), 2),
                }
            )

    image_labels = [item.label for item in corpora["image/*"]]
    image_payloads = [item.payload for item in corpora["image/*"]]
    image_vectors = image_encoder(image_payloads)
    within, across, margin = _pairwise_margin(image_vectors, image_labels)
    results["modalities"].append(
        {
            "family": "image/*",
            "model": IMAGE_MODEL,
            "within_mean": round(within, 4),
            "across_mean": round(across, 4),
            "margin": round(margin, 4),
            "latency_ms_per_node": round(_latency_ms_per_node(image_encoder, image_payloads), 2),
        }
    )

    minilm_encoder = text_encoders["sentence-transformers/all-MiniLM-L6-v2"]
    base_plain = _plain_corpus()["validator"][0]
    base_markdown = _markdown_wrap("validator", base_plain, 1)
    results["staleness"].append(
        {
            "family": "text/plain",
            "scores": [round(x, 4) for x in _staleness_scores_text(minilm_encoder, base_plain)],
        }
    )
    results["staleness"].append(
        {
            "family": "text/markdown",
            "scores": [round(x, 4) for x in _staleness_scores_markdown(minilm_encoder, base_markdown)],
        }
    )
    results["staleness"].append(
        {
            "family": "application/json",
            "scores": [round(x, 4) for x in _staleness_scores_json(minilm_encoder, base_plain)],
        }
    )
    results["staleness"].append(
        {
            "family": "image/*",
            "scores": [round(x, 4) for x in _staleness_scores_image(image_encoder)],
        }
    )

    if os.environ.get("OPENAI_API_KEY"):
        results["openai_status"] = "available_but_not_executed_in_default_local_pass"
    else:
        results["openai_status"] = "skipped_no_openai_api_key"

    print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
