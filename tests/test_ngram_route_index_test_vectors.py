"""
Unit tests for N-gram Route Index v1 test vector determinism.

Validates that the computed bucket_key_b64u values match the spec.
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from core tooling
from ilc_core.star_map.route_index import (
    canonicalize_text,
    tokenize_text,
    extract_ngrams,
    compute_bucket_key_b64u,
    TokenizationError,
)


class TestNgramRouteIndexTestVectors:
    """Test that computed hashes match spec values."""

    def test_vector1_hello_world(self) -> None:
        """Vector 1: Simple sentence - hello\\x1fworld."""
        canonical = canonicalize_text("Hello World Test")
        assert canonical == "hello world test"
        
        tokens = tokenize_text(canonical)
        assert tokens == ["hello", "world", "test"]
        
        ngrams = extract_ngrams(tokens, n=2)
        assert len(ngrams) == 2
        assert ngrams[0] == b"hello\x1fworld"
        assert ngrams[1] == b"world\x1ftest"
        
        # Spec values from docs/specs/star.map.ngram.route_index.v1.md
        assert compute_bucket_key_b64u(ngrams[0], head=0) == "HJa6H7nn6qk"
        assert compute_bucket_key_b64u(ngrams[1], head=0) == "sMfke74adZo"

    def test_vector2_whitespace_normalization(self) -> None:
        """Vector 2: Whitespace normalization - multiple\\x1fspaces."""
        canonical = canonicalize_text("  multiple   spaces   here  ")
        assert canonical == "multiple spaces here"
        
        tokens = tokenize_text(canonical)
        assert tokens == ["multiple", "spaces", "here"]
        
        ngrams = extract_ngrams(tokens, n=2)
        assert len(ngrams) == 2
        
        # Spec values
        assert compute_bucket_key_b64u(ngrams[0], head=0) == "dD6R9C-F-20"
        assert compute_bucket_key_b64u(ngrams[1], head=0) == "26YEXyLuwRo"

    def test_vector3_case_folding(self) -> None:
        """Vector 3: Case folding - mixed\\x1fcase."""
        canonical = canonicalize_text("MiXeD CaSe TeXt")
        assert canonical == "mixed case text"
        
        tokens = tokenize_text(canonical)
        assert tokens == ["mixed", "case", "text"]
        
        ngrams = extract_ngrams(tokens, n=2)
        assert len(ngrams) == 2
        
        # Spec values
        assert compute_bucket_key_b64u(ngrams[0], head=0) == "b5dh6DvrBoU"
        assert compute_bucket_key_b64u(ngrams[1], head=0) == "Pu772CIvePw"

    def test_vector4_unicode_nfkc(self) -> None:
        """Vector 4: Unicode NFKC - single token, no 2-grams."""
        canonical = canonicalize_text("\ufb01le")  # U+FB01 ligature fi + "le"
        assert canonical == "file"
        
        tokens = tokenize_text(canonical)
        assert tokens == ["file"]
        
        ngrams = extract_ngrams(tokens, n=2)
        assert ngrams == []  # No 2-grams

    def test_vector5_empty_after_normalization(self) -> None:
        """Vector 5: Empty after normalization - no tokens, no 2-grams."""
        canonical = canonicalize_text("   ")
        assert canonical == ""
        
        tokens = tokenize_text(canonical)
        assert tokens == []
        
        ngrams = extract_ngrams(tokens, n=2)
        assert ngrams == []  # No 2-grams


class TestTokenizationGuardrails:
    """Test tokenization guardrail enforcement."""

    def test_token_contains_unit_separator_rejected(self) -> None:
        """Tokens containing 0x1F must be rejected unconditionally."""
        with pytest.raises(TokenizationError):
            tokenize_text("bad\x1ftoken")

    def test_single_token_with_unit_separator_rejected(self) -> None:
        """Single token with 0x1F rejected even though no 2-grams would be produced."""
        with pytest.raises(TokenizationError):
            tokenize_text("a\x1fb")
