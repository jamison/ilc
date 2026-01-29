"""
Unit tests for Star Map Route Index core tooling.

Tests the functions in ilc_core.star_map.route_index for:
- Canonicalization correctness
- Tokenization guardrails
- N-gram extraction determinism
- Bucket key hash verification against spec
- Payload ordering determinism
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ilc_core.star_map.route_index import (
    canonicalize_text,
    tokenize_text,
    extract_ngrams,
    compute_bucket_key_b64u,
    build_route_index_payload,
    node_id_from_payload,
    TokenizationError,
    NgramExtractionError,
)


class TestCanonicalizeText:
    """Test canonicalization function."""

    def test_mixed_case_folding(self) -> None:
        """MiXeD CaSe should become lowercase."""
        assert canonicalize_text("MiXeD CaSe") == "mixed case"

    def test_whitespace_collapse(self) -> None:
        """Multiple spaces and leading/trailing whitespace collapsed."""
        assert canonicalize_text("  hello   world  ") == "hello world"

    def test_ligature_normalization(self) -> None:
        """U+FB01 ligature fi should normalize to 'fi'."""
        assert canonicalize_text("\ufb01le") == "file"

    def test_empty_string(self) -> None:
        """Empty string remains empty."""
        assert canonicalize_text("") == ""

    def test_whitespace_only(self) -> None:
        """Whitespace-only string becomes empty."""
        assert canonicalize_text("   ") == ""


class TestTokenizeText:
    """Test tokenization function and guardrails."""

    def test_basic_tokenization(self) -> None:
        """Simple sentence tokenizes correctly."""
        tokens = tokenize_text("hello world test")
        assert tokens == ["hello", "world", "test"]

    def test_empty_string(self) -> None:
        """Empty string produces empty token list."""
        assert tokenize_text("") == []

    def test_reject_token_with_0x1f(self) -> None:
        """Token containing 0x1F is rejected."""
        with pytest.raises(TokenizationError) as exc_info:
            tokenize_text("bad\x1ftoken")
        assert "0x1F" in str(exc_info.value)

    def test_reject_oversized_token(self) -> None:
        """Token exceeding 64 bytes is rejected."""
        oversized = "a" * 65
        with pytest.raises(TokenizationError) as exc_info:
            tokenize_text(oversized)
        assert "64 bytes" in str(exc_info.value)

    def test_reject_too_many_tokens(self) -> None:
        """Input with > 1024 tokens is rejected."""
        too_many = " ".join(["word"] * 1025)
        with pytest.raises(TokenizationError) as exc_info:
            tokenize_text(too_many)
        assert "1024" in str(exc_info.value)


class TestExtractNgrams:
    """Test n-gram extraction."""

    def test_bigrams_extraction(self) -> None:
        """Three tokens produce two bigrams."""
        tokens = ["a", "b", "c"]
        ngrams = extract_ngrams(tokens, n=2)
        assert ngrams == [b"a\x1fb", b"b\x1fc"]

    def test_trigrams_extraction(self) -> None:
        """Four tokens produce two trigrams."""
        tokens = ["a", "b", "c", "d"]
        ngrams = extract_ngrams(tokens, n=3)
        assert ngrams == [b"a\x1fb\x1fc", b"b\x1fc\x1fd"]

    def test_insufficient_tokens(self) -> None:
        """Fewer tokens than n produces empty list."""
        tokens = ["only"]
        ngrams = extract_ngrams(tokens, n=2)
        assert ngrams == []

    def test_invalid_n_rejected(self) -> None:
        """N-gram order not in {2,3,4} is rejected."""
        with pytest.raises(NgramExtractionError):
            extract_ngrams(["a", "b"], n=5)


class TestComputeBucketKey:
    """Test bucket key hash computation against spec values."""

    def test_vector1_hello_world(self) -> None:
        """Verify spec value for hello\\x1fworld."""
        ngram = b"hello\x1fworld"
        assert compute_bucket_key_b64u(ngram, head=0) == "HJa6H7nn6qk"

    def test_vector1_world_test(self) -> None:
        """Verify spec value for world\\x1ftest."""
        ngram = b"world\x1ftest"
        assert compute_bucket_key_b64u(ngram, head=0) == "sMfke74adZo"

    def test_vector2_multiple_spaces(self) -> None:
        """Verify spec value for multiple\\x1fspaces."""
        ngram = b"multiple\x1fspaces"
        assert compute_bucket_key_b64u(ngram, head=0) == "dD6R9C-F-20"

    def test_vector3_mixed_case(self) -> None:
        """Verify spec value for mixed\\x1fcase."""
        ngram = b"mixed\x1fcase"
        assert compute_bucket_key_b64u(ngram, head=0) == "b5dh6DvrBoU"

    def test_different_heads_produce_different_keys(self) -> None:
        """Different head indices produce different bucket keys."""
        ngram = b"hello\x1fworld"
        key_head0 = compute_bucket_key_b64u(ngram, head=0)
        key_head1 = compute_bucket_key_b64u(ngram, head=1)
        assert key_head0 != key_head1


class TestBuildRouteIndexPayload:
    """Test payload builder ordering and structure."""

    def test_routes_sorted_by_n_head_k(self) -> None:
        """Routes are sorted by (n, head, k) tuple."""
        routes = [
            {"n": 3, "head": 0, "k": "zzz", "targets": []},
            {"n": 2, "head": 1, "k": "aaa", "targets": []},
            {"n": 2, "head": 0, "k": "bbb", "targets": []},
        ]
        payload = build_route_index_payload(
            routes=routes,
            ngram_orders=[2, 3],
            heads=2,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
        )
        sorted_keys = [(r["n"], r["head"], r["k"]) for r in payload["routes"]]
        assert sorted_keys == [(2, 0, "bbb"), (2, 1, "aaa"), (3, 0, "zzz")]

    def test_targets_sorted_by_route(self) -> None:
        """Targets within a route are sorted by route key."""
        routes = [
            {
                "n": 2,
                "head": 0,
                "k": "test",
                "targets": [
                    {"route": "shard-003", "w": 1},
                    {"route": "shard-001", "w": 5},
                    {"route": "shard-002", "w": 3},
                ],
            }
        ]
        payload = build_route_index_payload(
            routes=routes,
            ngram_orders=[2],
            heads=1,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
        )
        target_routes = [t["route"] for t in payload["routes"][0]["targets"]]
        assert target_routes == ["shard-001", "shard-002", "shard-003"]

    def test_required_fields_present(self) -> None:
        """Payload contains all required fields."""
        payload = build_route_index_payload(
            routes=[],
            ngram_orders=[2],
            heads=4,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
        )
        assert payload["schema"] == "ilc.star.map.ngram.route_index@v1"
        assert payload["canonicalizer"] == "ilc.text.canon@v1"
        assert payload["bucket_key_len"] == 8
        assert payload["heads"] == 4
        assert payload["ngram_orders"] == [2]

    def test_optional_fields_included(self) -> None:
        """Optional fields appear when provided."""
        payload = build_route_index_payload(
            routes=[],
            ngram_orders=[2],
            heads=1,
            epoch="2026-W05",
            producer="test-producer",
        )
        assert payload["epoch"] == "2026-W05"
        assert payload["producer"] == "test-producer"

    def test_does_not_mutate_input_routes(self) -> None:
        """Input routes remain unchanged after payload build."""
        original_targets = [
            {"route": "shard-003", "w": 1},
            {"route": "shard-001", "w": 5},
            {"route": "shard-002", "w": 3},
        ]
        routes = [
            {"n": 2, "head": 0, "k": "test", "targets": original_targets},
        ]
        # Capture original order
        original_order = [t["route"] for t in original_targets]
        
        build_route_index_payload(
            routes=routes,
            ngram_orders=[2],
            heads=1,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
        )
        
        # Verify original order is preserved
        current_order = [t["route"] for t in original_targets]
        assert current_order == original_order
        assert current_order == ["shard-003", "shard-001", "shard-002"]


class TestNodeIdFromPayload:
    """Test NodeID computation from payload."""

    def test_deterministic_node_id(self) -> None:
        """Same payload produces same NodeID."""
        payload = build_route_index_payload(
            routes=[],
            ngram_orders=[2],
            heads=1,
            created_at=datetime(2026, 1, 30, tzinfo=timezone.utc),
        )
        node_id_1 = node_id_from_payload(payload)
        node_id_2 = node_id_from_payload(payload)
        assert node_id_1 == node_id_2
        assert node_id_1.startswith("b")  # CIDv1 base32 prefix

