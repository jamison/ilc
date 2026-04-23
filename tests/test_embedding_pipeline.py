"""
H-010 gate tests: type-aware epoch-stamped embedding pipeline.

Tests cover the policy layer (select_payload_family, select_model,
prepare_text_payload, is_embedding_stale) and the embed_node API using
an injected fake encoder so that no ML dependencies are required.
"""

from __future__ import annotations

import asyncio
import json

import numpy as np
import pytest

from ilc_core.analysis.embedding_pipeline import (
    EMBEDDING_PIPELINE_VERSION,
    EmbeddingSidecarStore,
    FAMILY_APPLICATION_JSON,
    FAMILY_IMAGE,
    FAMILY_TEXT_MARKDOWN,
    FAMILY_TEXT_PLAIN,
    MODEL_CLIP,
    MODEL_MINILM,
    STALENESS_EPOCHS,
    EmbeddingPipelineError,
    embed_and_store_node,
    embed_and_store_node_async,
    embed_node,
    embed_node_async,
    is_embedding_stale,
    prepare_text_payload,
    select_model,
    select_payload_family,
)
from ilc_core.types import Node


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_node(**kwargs) -> Node:
    defaults: dict = {
        "id": "test-id",
        "type": "claim",
        "content": "a test claim",
        "agent_id": "agent_0",
        "signature": "sig",
    }
    defaults.update(kwargs)
    return Node(**defaults)


def _fake_encoder(payloads) -> np.ndarray:
    """Returns L2-normalized unit vectors of fixed dim=4 for testing."""
    n = len(list(payloads))
    vecs = np.ones((n, 4), dtype=float)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    return vecs / norms


# ---------------------------------------------------------------------------
# Version token
# ---------------------------------------------------------------------------

def test_version_token_identifies_h010() -> None:
    assert "embedding_pipeline_h010" in EMBEDDING_PIPELINE_VERSION


# ---------------------------------------------------------------------------
# select_payload_family
# ---------------------------------------------------------------------------

def test_select_payload_family_none_returns_text_plain() -> None:
    assert select_payload_family(None) == FAMILY_TEXT_PLAIN


def test_select_payload_family_semantic_claim() -> None:
    assert select_payload_family("claim") == FAMILY_TEXT_PLAIN


def test_select_payload_family_semantic_evidence() -> None:
    assert select_payload_family("evidence") == FAMILY_TEXT_PLAIN


def test_select_payload_family_semantic_task_result() -> None:
    assert select_payload_family("task_result") == FAMILY_TEXT_PLAIN


def test_select_payload_family_semantic_task_returns_markdown() -> None:
    assert select_payload_family("task") == FAMILY_TEXT_MARKDOWN


def test_select_payload_family_semantic_route_index() -> None:
    assert select_payload_family("route_index") == FAMILY_APPLICATION_JSON


def test_select_payload_family_semantic_hyperedge_entity() -> None:
    assert select_payload_family("hyperedge_entity") == FAMILY_APPLICATION_JSON


def test_select_payload_family_semantic_star_map() -> None:
    assert select_payload_family("star_map") == FAMILY_APPLICATION_JSON


def test_select_payload_family_semantic_genesis() -> None:
    assert select_payload_family("genesis") == FAMILY_TEXT_PLAIN


def test_select_payload_family_mime_passthrough() -> None:
    # MIME-style families pass through unchanged.
    assert select_payload_family("text/plain") == FAMILY_TEXT_PLAIN
    assert select_payload_family("text/markdown") == FAMILY_TEXT_MARKDOWN
    assert select_payload_family("application/json") == FAMILY_APPLICATION_JSON
    assert select_payload_family("image/*") == FAMILY_IMAGE


def test_select_payload_family_specific_image_mime_maps_to_image_family() -> None:
    assert select_payload_family("image/png") == FAMILY_IMAGE
    assert select_payload_family("image/jpeg") == FAMILY_IMAGE


def test_select_payload_family_unknown_falls_back_to_text_plain() -> None:
    assert select_payload_family("totally_unknown_type") == FAMILY_TEXT_PLAIN


# ---------------------------------------------------------------------------
# select_model
# ---------------------------------------------------------------------------

def test_select_model_text_families_return_minilm() -> None:
    assert select_model(FAMILY_TEXT_PLAIN) == MODEL_MINILM
    assert select_model(FAMILY_TEXT_MARKDOWN) == MODEL_MINILM
    assert select_model(FAMILY_APPLICATION_JSON) == MODEL_MINILM


def test_select_model_image_returns_clip() -> None:
    assert select_model(FAMILY_IMAGE) == MODEL_CLIP


# ---------------------------------------------------------------------------
# STALENESS_EPOCHS sanity (locked to SIM-EMBED-01 results §6)
# ---------------------------------------------------------------------------

def test_staleness_thresholds_match_sim_embed_01() -> None:
    assert STALENESS_EPOCHS[FAMILY_TEXT_PLAIN] == 32
    assert STALENESS_EPOCHS[FAMILY_TEXT_MARKDOWN] == 16
    assert STALENESS_EPOCHS[FAMILY_APPLICATION_JSON] == 48
    assert STALENESS_EPOCHS[FAMILY_IMAGE] == 4


# ---------------------------------------------------------------------------
# prepare_text_payload
# ---------------------------------------------------------------------------

def test_prepare_text_payload_plain_string_content() -> None:
    node = _make_node(content="hello world", content_type="claim")
    assert prepare_text_payload(node, FAMILY_TEXT_PLAIN) == "hello world"


def test_prepare_text_payload_dict_content_for_text_family_stringifies() -> None:
    node = _make_node(content={"key": "val"}, content_type="claim")
    result = prepare_text_payload(node, FAMILY_TEXT_PLAIN)
    assert "key" in result


def test_prepare_text_payload_json_dict_produces_canonical_json() -> None:
    # Keys are out of alphabetical order; canonical output must sort them.
    node = _make_node(content={"z": 1, "a": 2}, content_type="route_index")
    result = prepare_text_payload(node, FAMILY_APPLICATION_JSON)
    parsed = json.loads(result)
    assert parsed == {"z": 1, "a": 2}
    assert result == json.dumps({"a": 2, "z": 1}, sort_keys=True)


def test_prepare_text_payload_json_string_gets_canonicalized() -> None:
    # Provide a JSON string with unsorted keys; must be re-serialized sorted.
    raw = '{"z": 1, "a": 2}'
    node = _make_node(content=raw, content_type="star_map")
    result = prepare_text_payload(node, FAMILY_APPLICATION_JSON)
    assert result == json.dumps({"a": 2, "z": 1}, sort_keys=True)


def test_prepare_text_payload_non_json_string_falls_back_for_json_family() -> None:
    node = _make_node(content="not json at all", content_type="route_index")
    result = prepare_text_payload(node, FAMILY_APPLICATION_JSON)
    assert result == "not json at all"


# ---------------------------------------------------------------------------
# is_embedding_stale
# ---------------------------------------------------------------------------

def test_is_embedding_stale_when_no_embedding() -> None:
    node = _make_node()
    assert is_embedding_stale(node, current_epoch=1)


def test_is_embedding_stale_when_embedding_epoch_none() -> None:
    node = _make_node(embedding=[0.1, 0.2], embedding_model=MODEL_MINILM)
    assert is_embedding_stale(node, current_epoch=1)


def test_is_embedding_stale_fresh_at_same_epoch() -> None:
    node = _make_node(
        content_type="claim",
        embedding=[0.1],
        embedding_model=MODEL_MINILM,
        embedding_epoch=10,
    )
    assert not is_embedding_stale(node, current_epoch=10)


def test_is_embedding_stale_fresh_within_text_plain_threshold() -> None:
    # text/plain threshold = 32; 42 - 10 = 32, not stale.
    node = _make_node(
        content_type="claim",
        embedding=[0.1],
        embedding_model=MODEL_MINILM,
        embedding_epoch=10,
    )
    assert not is_embedding_stale(node, current_epoch=42)


def test_is_embedding_stale_beyond_text_plain_threshold() -> None:
    # 43 - 10 = 33 > 32, stale.
    node = _make_node(
        content_type="claim",
        embedding=[0.1],
        embedding_model=MODEL_MINILM,
        embedding_epoch=10,
    )
    assert is_embedding_stale(node, current_epoch=43)


def test_is_embedding_stale_json_threshold_boundary() -> None:
    # application/json threshold = 48.
    node = _make_node(
        content_type="route_index",
        embedding=[0.1],
        embedding_model=MODEL_MINILM,
        embedding_epoch=0,
    )
    assert not is_embedding_stale(node, current_epoch=48)   # exactly at threshold
    assert is_embedding_stale(node, current_epoch=49)        # one over


# ---------------------------------------------------------------------------
# embed_node
# ---------------------------------------------------------------------------

def test_embed_node_populates_all_three_fields() -> None:
    node = _make_node(content_type="claim")
    result = embed_node(node, epoch=5, encoder=_fake_encoder)
    assert result.embedding is not None
    assert len(result.embedding) == 4
    assert result.embedding_model == MODEL_MINILM
    assert result.embedding_epoch == 5


def test_embed_node_returns_new_node_instance() -> None:
    node = _make_node(content_type="claim")
    result = embed_node(node, epoch=5, encoder=_fake_encoder)
    assert result is not node


def test_embed_node_preserves_non_embedding_fields() -> None:
    node = _make_node(content_type="claim", content="preserved content")
    result = embed_node(node, epoch=5, encoder=_fake_encoder)
    assert result.content == "preserved content"
    assert result.agent_id == node.agent_id
    assert result.type == node.type


def test_embed_node_skips_when_embedding_fresh() -> None:
    existing = [0.1, 0.2, 0.3, 0.4]
    node = _make_node(
        content_type="claim",
        embedding=existing,
        embedding_model=MODEL_MINILM,
        embedding_epoch=10,
    )
    # epoch=20: 20-10=10 < 32 threshold; embedding is fresh.
    result = embed_node(node, epoch=20, encoder=_fake_encoder)
    assert result is node  # identical object — no copy was made


def test_embed_node_force_overwrites_fresh_embedding() -> None:
    existing = [0.1, 0.2, 0.3, 0.4]
    node = _make_node(
        content_type="claim",
        embedding=existing,
        embedding_model=MODEL_MINILM,
        embedding_epoch=10,
    )
    result = embed_node(node, epoch=20, encoder=_fake_encoder, force=True)
    assert result is not node
    assert result.embedding_epoch == 20


def test_embed_node_re_embeds_when_model_would_change() -> None:
    # Node was embedded with CLIP (wrong model for text/plain).
    node = _make_node(
        content_type="claim",
        embedding=[0.1, 0.2, 0.3, 0.4],
        embedding_model=MODEL_CLIP,
        embedding_epoch=10,
    )
    # Epoch 20 is within threshold, but model mismatch forces re-embed.
    result = embed_node(node, epoch=20, encoder=_fake_encoder)
    assert result is not node
    assert result.embedding_model == MODEL_MINILM


def test_embed_node_image_uses_clip_when_encoder_is_injected() -> None:
    node = _make_node(content_type="image/*", content="dummy image bytes")
    result = embed_node(node, epoch=1, encoder=_fake_encoder)
    assert result.embedding_model == MODEL_CLIP
    assert result.embedding_epoch == 1
    assert result.embedding is not None


def test_embed_node_image_without_encoder_has_explicit_gate() -> None:
    node = _make_node(content_type="image/*", content="dummy image bytes")
    with pytest.raises(EmbeddingPipelineError, match="image_encoder_requires_explicit_encoder"):
        embed_node(node, epoch=1)


def test_embed_node_result_is_unit_vector() -> None:
    # _fake_encoder already L2-normalizes; verify embed_node passes vectors through.
    node = _make_node(content_type="claim")
    result = embed_node(node, epoch=1, encoder=_fake_encoder)
    v = np.array(result.embedding)
    assert abs(np.linalg.norm(v) - 1.0) < 1e-6


def test_embed_node_canonical_json_route_index() -> None:
    # Verify dict content with route_index type goes through canonical JSON.
    node = _make_node(
        content_type="route_index",
        content={"z": 1, "a": 2},
    )
    # If prepare_text_payload is working, encoder receives '{"a": 2, "z": 1}'.
    received: list[str] = []

    def capturing_encoder(payloads):
        received.extend(payloads)
        return _fake_encoder(payloads)

    embed_node(node, epoch=1, encoder=capturing_encoder)
    assert len(received) == 1
    assert received[0] == json.dumps({"a": 2, "z": 1}, sort_keys=True)


def test_embed_node_stale_embedding_is_regenerated() -> None:
    node = _make_node(
        content_type="claim",
        embedding=[0.9, 0.9, 0.9, 0.9],
        embedding_model=MODEL_MINILM,
        embedding_epoch=0,
    )
    # epoch=50: 50-0=50 > 32 threshold, stale → must regenerate.
    result = embed_node(node, epoch=50, encoder=_fake_encoder)
    assert result is not node
    assert result.embedding_epoch == 50


def test_is_embedding_stale_empty_list_is_stale() -> None:
    # An empty embedding vector must be treated as stale, not as a valid embedding.
    # Without this guard, embed_node would return a node with embedding=[] unchanged,
    # making it permanently ineligible for vector similarity queries.
    node = _make_node(
        content_type="claim",
        embedding=[],
        embedding_model=MODEL_MINILM,
        embedding_epoch=10,
    )
    assert is_embedding_stale(node, current_epoch=10)


def test_embed_node_re_embeds_empty_embedding() -> None:
    # embed_node must not skip a node with embedding=[] even if the epoch is fresh.
    node = _make_node(
        content_type="claim",
        embedding=[],
        embedding_model=MODEL_MINILM,
        embedding_epoch=10,
    )
    result = embed_node(node, epoch=10, encoder=_fake_encoder)
    assert result is not node
    assert len(result.embedding) == 4   # _fake_encoder returns 4-dim vectors
    assert result.embedding_epoch == 10


def test_embed_node_content_type_none_uses_minilm() -> None:
    # Nodes with content_type=None (legacy untyped nodes) must embed via the
    # text/plain → MiniLM path.  This is the default for all nodes that predate
    # ADR-0030 content_type declaration.
    node = _make_node(content_type=None)
    result = embed_node(node, epoch=3, encoder=_fake_encoder)
    assert result.embedding_model == MODEL_MINILM
    assert result.embedding_epoch == 3
    assert result.embedding is not None and len(result.embedding) > 0


def test_embed_node_unknown_content_type_falls_back_without_crash() -> None:
    node = _make_node(content_type="unknown/custom")
    result = embed_node(node, epoch=4, encoder=_fake_encoder)
    assert result.embedding_model == MODEL_MINILM
    assert result.embedding_epoch == 4
    assert result.embedding is not None


def test_embed_node_async_stamps_epoch_off_hot_path() -> None:
    node = _make_node(content_type="claim")
    result = asyncio.run(embed_node_async(node, epoch=12, encoder=_fake_encoder))
    assert result.embedding_epoch == 12
    assert result.embedding_model == MODEL_MINILM
    assert result.embedding is not None


def test_embedding_sidecar_store_round_trip(tmp_path) -> None:
    node = _make_node(content_type="claim")
    with EmbeddingSidecarStore(tmp_path / "embeddings") as store:
        embedded = embed_and_store_node(node, epoch=7, store=store, encoder=_fake_encoder)
        record = store.get_node_embedding(node.id)
    assert record is not None
    assert record["node_id"] == node.id
    assert record["embedding_model"] == MODEL_MINILM
    assert record["embedding_epoch"] == 7
    assert record["embedding"] == embedded.embedding


def test_embedding_sidecar_rejects_unembedded_node(tmp_path) -> None:
    node = _make_node(content_type="claim")
    with EmbeddingSidecarStore(tmp_path / "embeddings") as store:
        with pytest.raises(EmbeddingPipelineError, match="node_embedding_missing"):
            store.put_node_embedding(node)


def test_embed_and_store_node_async_round_trip(tmp_path) -> None:
    node = _make_node(content_type="claim")
    with EmbeddingSidecarStore(tmp_path / "embeddings") as store:
        embedded = asyncio.run(
            embed_and_store_node_async(node, epoch=8, store=store, encoder=_fake_encoder)
        )
        record = store.get_node_embedding(node.id)
    assert embedded.embedding_epoch == 8
    assert record is not None
    assert record["embedding_epoch"] == 8
