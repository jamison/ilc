"""
Tests for de Bruijn harness module.

Validates sequence generation, coverage properties, and histogram accounting.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ilc_core.star_map.debruijn_harness import (
    generate_debruijn_sequence,
    build_token_stream,
    compute_bucket_histogram,
    summarize_stats,
)


class TestGenerateDebruijnSequence:
    """Test de Bruijn sequence generation."""

    def test_sequence_length_binary_n3(self) -> None:
        """B(2,3) should have length 2^3 = 8."""
        alphabet = ["0", "1"]
        seq = generate_debruijn_sequence(alphabet, n=3)
        assert len(seq) == 8

    def test_sequence_length_quaternary_n2(self) -> None:
        """B(4,2) should have length 4^2 = 16."""
        alphabet = ["a", "b", "c", "d"]
        seq = generate_debruijn_sequence(alphabet, n=2)
        assert len(seq) == 16

    def test_sequence_length_ternary_n3(self) -> None:
        """B(3,3) should have length 3^3 = 27."""
        alphabet = ["x", "y", "z"]
        seq = generate_debruijn_sequence(alphabet, n=3)
        assert len(seq) == 27

    def test_all_bigrams_appear_once_cyclic(self) -> None:
        """B(2,2) cyclic should contain all 4 bigrams exactly once."""
        alphabet = ["0", "1"]
        seq = generate_debruijn_sequence(alphabet, n=2)
        
        # Length should be 4
        assert len(seq) == 4
        
        # Extract all cyclic bigrams
        bigrams = set()
        for i in range(len(seq)):
            bigram = (seq[i], seq[(i + 1) % len(seq)])
            bigrams.add(bigram)
        
        # Should have all 4 possible bigrams
        expected = {("0", "0"), ("0", "1"), ("1", "0"), ("1", "1")}
        assert bigrams == expected

    def test_empty_alphabet_raises(self) -> None:
        """Empty alphabet should raise ValueError."""
        with pytest.raises(ValueError):
            generate_debruijn_sequence([], n=2)

    def test_n_less_than_one_raises(self) -> None:
        """n < 1 should raise ValueError."""
        with pytest.raises(ValueError):
            generate_debruijn_sequence(["a", "b"], n=0)


class TestBuildTokenStream:
    """Test token stream building."""

    def test_exact_length_match(self) -> None:
        """Output has exactly the requested length."""
        seq = ["a", "b", "c"]
        stream = build_token_stream(seq, 10)
        assert len(stream) == 10

    def test_shorter_than_sequence(self) -> None:
        """Can request length shorter than sequence."""
        seq = ["a", "b", "c", "d", "e"]
        stream = build_token_stream(seq, 3)
        assert len(stream) == 3
        assert stream == ["a", "b", "c"]

    def test_zero_length(self) -> None:
        """Zero length returns empty list."""
        seq = ["a", "b", "c"]
        stream = build_token_stream(seq, 0)
        assert stream == []

    def test_empty_sequence_raises(self) -> None:
        """Empty sequence with positive length raises."""
        with pytest.raises(ValueError):
            build_token_stream([], 5)


class TestComputeBucketHistogram:
    """Test bucket histogram computation."""

    def test_total_ngrams_count(self) -> None:
        """Total n-grams equals tokens - n + 1."""
        tokens = ["a0", "a1", "a2", "a3", "a0"]
        stats = compute_bucket_histogram(tokens, n=2, heads=2)
        # 5 tokens, n=2 -> 4 bigrams
        assert stats["total_ngrams"] == 4

    def test_unique_buckets_bounded(self) -> None:
        """Unique buckets <= total n-grams."""
        tokens = ["a0", "a1", "a2", "a3"]
        stats = compute_bucket_histogram(tokens, n=2, heads=1)
        assert stats["per_head"][0]["unique_buckets"] <= stats["total_ngrams"]

    def test_max_bucket_load_at_least_one(self) -> None:
        """Max bucket load >= 1 when n-grams exist."""
        tokens = ["a0", "a1", "a2"]
        stats = compute_bucket_histogram(tokens, n=2, heads=1)
        assert stats["per_head"][0]["max_bucket_load"] >= 1

    def test_insufficient_tokens_empty_stats(self) -> None:
        """Fewer tokens than n produces zero counts."""
        tokens = ["a0"]
        stats = compute_bucket_histogram(tokens, n=2, heads=2)
        assert stats["total_ngrams"] == 0
        assert stats["per_head"][0]["unique_buckets"] == 0

    def test_invalid_n_raises(self) -> None:
        """n not in {2,3,4} should raise."""
        with pytest.raises(ValueError):
            compute_bucket_histogram(["a", "b", "c", "d", "e"], n=5, heads=1)

    def test_zero_heads_raises(self) -> None:
        """heads < 1 should raise."""
        with pytest.raises(ValueError):
            compute_bucket_histogram(["a", "b", "c"], n=2, heads=0)

    def test_cyclic_coverage_count(self) -> None:
        """Cyclic mode produces seq_len n-grams for de Bruijn sequence."""
        # B(2,2) = ["0", "0", "1", "1"] (length 4)
        # With cyclic=True, 4 tokens + 1 wrap = 5 effective, so 4 bigrams
        tokens = ["0", "0", "1", "1"]
        stats = compute_bucket_histogram(tokens, n=2, heads=1, cyclic=True)
        assert stats["total_ngrams"] == 4
        assert stats["cyclic"] is True

    def test_non_cyclic_count_unchanged(self) -> None:
        """Non-cyclic mode produces seq_len - n + 1 n-grams."""
        # Same 4 tokens without cyclic -> 3 bigrams
        tokens = ["0", "0", "1", "1"]
        stats = compute_bucket_histogram(tokens, n=2, heads=1, cyclic=False)
        assert stats["total_ngrams"] == 3
        assert stats["cyclic"] is False


class TestSummarizeStats:
    """Test stats summary generation."""

    def test_summary_contains_total(self) -> None:
        """Summary includes total n-gram count."""
        stats = {
            "total_ngrams": 42,
            "heads": 2,
            "per_head": [
                {"head": 0, "unique_buckets": 40, "max_bucket_load": 2, "collisions": 2},
                {"head": 1, "unique_buckets": 41, "max_bucket_load": 2, "collisions": 1},
            ],
        }
        summary = summarize_stats(stats)
        assert "42" in summary
        assert "Head 0" in summary
        assert "Head 1" in summary
