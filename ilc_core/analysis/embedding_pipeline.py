# H-010: Type-aware, epoch-stamped node embedding pipeline.
#
# Gate history:
#   H-002 positive → SIM-EMBED-01 verdict=pass; model recommendations locked:
#     text/plain, text/markdown, application/json → sentence-transformers/all-MiniLM-L6-v2
#     image/* → openai/clip-vit-base-patch32 (not yet implemented — no image corpus at testnet)
#   H-010 → this implementation
#
# Authority:
#   docs/adr/ADR_0030_Node_Embedding_Substrate_and_Content_Typing.md
#   docs/research/ilc_sim_embed_01_results_v0.1.md
#
# Two-level mapping (per SIM-EMBED-01 §2 scope correction):
#   ADR-0030 semantic content_type → payload-modality family → embedding model
#
# Design constraints:
#   - Off the hot path: no embedding generation during node submission
#   - Lazy model loading: torch/transformers not imported until first real encode call
#   - Testnet scale: LMDB sidecar storage is adequate; no FAISS index required
#   - image/* not implemented in this phase (no PIL Image corpus at testnet scale)
#   - embed_node accepts an optional encoder callable so tests work without ML deps
#
# `run_h010_embedding_pipeline_verdict=pass`

from __future__ import annotations

import json
from typing import Callable, List, Optional, Sequence

import numpy as np

from ilc_core.types import Node


EMBEDDING_PIPELINE_VERSION = "embedding_pipeline_h010.v0.1"


# ---------------------------------------------------------------------------
# Payload-modality families (SIM-EMBED-01 taxonomy)
# ---------------------------------------------------------------------------

FAMILY_TEXT_PLAIN = "text/plain"
FAMILY_TEXT_MARKDOWN = "text/markdown"
FAMILY_APPLICATION_JSON = "application/json"
FAMILY_IMAGE = "image/*"

_ALL_FAMILIES = frozenset({
    FAMILY_TEXT_PLAIN,
    FAMILY_TEXT_MARKDOWN,
    FAMILY_APPLICATION_JSON,
    FAMILY_IMAGE,
})


# ---------------------------------------------------------------------------
# Model identifiers (SIM-EMBED-01 results §7)
# ---------------------------------------------------------------------------

MODEL_MINILM = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_CLIP = "openai/clip-vit-base-patch32"


# ---------------------------------------------------------------------------
# Staleness thresholds per family (SIM-EMBED-01 results §6)
# ---------------------------------------------------------------------------
# text/plain TTL=32: conservative conventional choice; all drift variants
#   returned cosine=1.0 in simulation, so any TTL is compatible with the evidence.
# text/markdown TTL=16: measured formatting-change drift (cos ≈ 0.994 per variant).
# application/json TTL=48: epoch-field semantic drift after canonicalization.
#   The simulation measures how much the embedding changes as the "epoch" metadata
#   field increments; key-ordering differences are erased by canonicalization.
# image/* TTL=4: measured render and GaussianBlur drift on CLIP.

STALENESS_EPOCHS: dict[str, int] = {
    FAMILY_TEXT_PLAIN: 32,
    FAMILY_TEXT_MARKDOWN: 16,
    FAMILY_APPLICATION_JSON: 48,
    FAMILY_IMAGE: 4,
}


# ---------------------------------------------------------------------------
# ADR-0030 semantic content_type → payload-modality family
# ---------------------------------------------------------------------------
# claim, evidence, task_result: natural-language prose → text/plain
# task: structured markdown specifications → text/markdown
# route_index, hyperedge_entity, star_map: JSON structures → application/json
# genesis: immutable axiomatic text → text/plain
# Unrecognized semantic tokens default to text/plain (conservative fallback).

_SEMANTIC_TYPE_TO_FAMILY: dict[str, str] = {
    "claim": FAMILY_TEXT_PLAIN,
    "evidence": FAMILY_TEXT_PLAIN,
    "task": FAMILY_TEXT_MARKDOWN,
    "task_result": FAMILY_TEXT_PLAIN,
    "route_index": FAMILY_APPLICATION_JSON,
    "hyperedge_entity": FAMILY_APPLICATION_JSON,
    "genesis": FAMILY_TEXT_PLAIN,
    "star_map": FAMILY_APPLICATION_JSON,
}


# ---------------------------------------------------------------------------
# Errors and types
# ---------------------------------------------------------------------------

class EmbeddingPipelineError(ValueError):
    """Raised for unrecoverable embedding pipeline errors."""


# Encoder type: accepts a sequence of text payloads, returns L2-normalized matrix.
Encoder = Callable[[Sequence[str]], np.ndarray]


# ---------------------------------------------------------------------------
# Policy functions (no ML dependencies)
# ---------------------------------------------------------------------------

def select_payload_family(content_type: Optional[str]) -> str:
    """Map ADR-0030 semantic content_type (or MIME family) to payload-modality family.

    Accepts both ADR-0030 semantic tokens ("claim", "evidence", "route_index", ...)
    and MIME-style families ("text/plain", "application/json", ...) for compatibility
    with both node creation conventions.

    None and unrecognized types fall back to text/plain.
    """
    if content_type is None:
        return FAMILY_TEXT_PLAIN
    if content_type in _ALL_FAMILIES:
        # Already a modality family — pass through directly.
        return content_type
    return _SEMANTIC_TYPE_TO_FAMILY.get(content_type, FAMILY_TEXT_PLAIN)


def select_model(family: str) -> str:
    """Map payload-modality family to recommended embedding model identifier."""
    if family == FAMILY_IMAGE:
        return MODEL_CLIP
    return MODEL_MINILM


def prepare_text_payload(node: Node, family: str) -> str:
    """Extract and normalize the text payload from a node for embedding.

    For application/json: applies canonical JSON (sort_keys=True) before embedding,
    per SIM-EMBED-01 §4.3 and §6.3.  Canonicalization removes key-ordering drift so
    that two nodes with equivalent JSON content receive identical embeddings.

    For text families (text/plain, text/markdown): returns content as a string.
    Dict-typed content is JSON-serialized with sorted keys as a safe fallback.
    """
    if family == FAMILY_APPLICATION_JSON:
        if isinstance(node.content, dict):
            return json.dumps(node.content, sort_keys=True)
        try:
            parsed = json.loads(str(node.content))
            return json.dumps(parsed, sort_keys=True)
        except (json.JSONDecodeError, TypeError, ValueError):
            # Content is not valid JSON — fall back to string representation.
            return str(node.content)
    else:
        if isinstance(node.content, dict):
            return json.dumps(node.content, sort_keys=True)
        return str(node.content)


def is_embedding_stale(node: Node, current_epoch: int) -> bool:
    """Return True if the node's embedding is absent or past its staleness threshold.

    Thresholds are per-family values from SIM-EMBED-01 results §6.
    A node with no embedding, an empty embedding vector, or no embedding_epoch
    is always stale.
    A node is stale when (current_epoch - embedding_epoch) > threshold.
    Exactly at the threshold the embedding is still considered fresh.

    Architectural note: nodes are content-addressed (node.id derives from
    type + content + agent_id).  Changing a node's content produces a new node
    with a new ID and embedding=None, so content-change invalidation is handled
    automatically at node creation — not by this function.  This function only
    measures time-based staleness for the same unchanged node across epochs.
    """
    if not node.embedding or node.embedding_epoch is None:
        # Covers: embedding is None, embedding is [], or embedding_epoch absent.
        return True
    family = select_payload_family(node.content_type)
    threshold = STALENESS_EPOCHS.get(family, 32)
    return (current_epoch - node.embedding_epoch) > threshold


# ---------------------------------------------------------------------------
# Module-level lazy model cache
# ---------------------------------------------------------------------------
# Not thread-safe; intended for the single-threaded analytics loop at testnet scale.
# Mainnet scale requires an explicit cache eviction policy and thread synchronisation.

_encoder_cache: dict[str, Encoder] = {}


def _build_text_encoder(model_id: str) -> Encoder:
    """Load a sentence-transformers model and return an L2-normalizing encoder.

    Requires transformers and torch; imported lazily so that modules importing
    embedding_pipeline for policy functions only do not pull in ML dependencies.

    trust_remote_code is enabled for nomic-embed-text, which requires custom
    pooling layers not available in the standard AutoModel dispatch path.
    """
    import torch
    from transformers import AutoModel, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(
        model_id, trust_remote_code="nomic" in model_id
    )
    model = AutoModel.from_pretrained(
        model_id, trust_remote_code="nomic" in model_id
    )

    @torch.no_grad()
    def encode(payloads: Sequence[str]) -> np.ndarray:
        texts = [str(p) for p in payloads]
        batch = tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        output = model(**batch)
        mask = (
            batch["attention_mask"]
            .unsqueeze(-1)
            .expand(output.last_hidden_state.size())
            .float()
        )
        summed = torch.sum(output.last_hidden_state * mask, dim=1)
        counts = torch.clamp(mask.sum(dim=1), min=1e-9)
        pooled = (summed / counts).detach().cpu().numpy()
        norms = np.linalg.norm(pooled, axis=1, keepdims=True)
        return pooled / np.clip(norms, 1e-12, None)

    return encode


def _get_encoder(model_id: str) -> Encoder:
    """Return a cached encoder for model_id, loading it on the first call."""
    if model_id not in _encoder_cache:
        _encoder_cache[model_id] = _build_text_encoder(model_id)
    return _encoder_cache[model_id]


# ---------------------------------------------------------------------------
# Main API
# ---------------------------------------------------------------------------

def embed_node(
    node: Node,
    epoch: int,
    *,
    encoder: Optional[Encoder] = None,
    force: bool = False,
) -> Node:
    """Generate and return a new Node with embedding fields populated.

    The embedding is regenerated when any of the following is true:
      - node.embedding is None or node.embedding_epoch is None (not yet embedded)
      - the embedding is past its staleness threshold (is_embedding_stale)
      - the selected model differs from node.embedding_model (content_type changed)
      - force=True

    Otherwise the original node is returned unchanged (no copy, no allocation).

    image/* content_type raises EmbeddingPipelineError — CLIP image embedding is
    not implemented in this phase; there is no image corpus at testnet scale.

    Args:
        node:    The node to embed.
        epoch:   The current epoch; written to embedding_epoch on the result.
        encoder: Optional encoder callable (Sequence[str] -> np.ndarray of L2-normalized
                 row vectors).  If None, the production text encoder is loaded lazily
                 from the module-level cache.  Pass a callable in tests to avoid
                 loading ML dependencies.
        force:   If True, regenerate even if the embedding is not stale.

    Returns:
        A new Node instance with embedding, embedding_model, embedding_epoch set,
        or the original node if the embedding is still fresh and force=False.

    Raises:
        EmbeddingPipelineError: for image/* content_type or if encoding fails.
    """
    family = select_payload_family(node.content_type)

    if family == FAMILY_IMAGE:
        raise EmbeddingPipelineError(
            f"image/* embedding is not implemented in H-010; "
            f"node id={node.id!r} has content_type='image/*'. "
            "Implement a CLIP image encoder in a future H-series phase."
        )

    current_model = select_model(family)

    # Re-embed if stale, if the model changed (content_type was updated since last
    # embedding), or if force=True.
    model_mismatch = (
        node.embedding is not None and node.embedding_model != current_model
    )
    if not force and not is_embedding_stale(node, epoch) and not model_mismatch:
        return node

    text = prepare_text_payload(node, family)
    _encoder = encoder if encoder is not None else _get_encoder(current_model)

    try:
        matrix = _encoder([text])
    except Exception as exc:
        raise EmbeddingPipelineError(
            f"encoder failed for node id={node.id!r}: {exc}"
        ) from exc

    vector: List[float] = matrix[0].tolist()

    return node.model_copy(update={
        "embedding": vector,
        "embedding_model": current_model,
        "embedding_epoch": epoch,
    })
