#!/usr/bin/env python3
"""
Deterministic Test Vector Generator for N-gram Route Index v1.

Uses core tooling from ilc_core.star_map.route_index.
See docs/specs/star.map.ngram.route_index.v1.md for spec details.

Usage:
    python3 tools/ngram_route_index_test_vectors.py
"""

from __future__ import annotations

import sys

# Add project root to path for import
sys.path.insert(0, str(__file__).rsplit("/tools/", 1)[0])

# Re-export core functions for backwards compatibility
from ilc_core.star_map.route_index import (
    canonicalize_text as canonicalize,
    tokenize_text as tokenize,
    extract_ngrams,
    compute_bucket_key_b64u as compute_bucket_key,
    TokenizationError,
    NGRAM_SEPARATOR,
)


# === Test Vectors (Section 16) ===

TEST_VECTORS = [
    {
        "name": "Vector 1: Simple sentence",
        "input": "Hello World Test",
    },
    {
        "name": "Vector 2: Whitespace normalization",
        "input": "  multiple   spaces   here  ",
    },
    {
        "name": "Vector 3: Case folding",
        "input": "MiXeD CaSe TeXt",
    },
    {
        "name": "Vector 4: Unicode NFKC",
        "input": "\ufb01le",  # U+FB01 LATIN SMALL LIGATURE FI + "le"
    },
    {
        "name": "Vector 5: Empty after normalization",
        "input": "   ",
    },
]


def process_vector(vector: dict) -> dict:
    """Process a test vector and return computed values."""
    name = vector["name"]
    input_text = vector["input"]
    
    canonical = canonicalize(input_text)
    tokens = tokenize(canonical)
    ngrams_2 = extract_ngrams(tokens, n=2)
    
    result = {
        "name": name,
        "input": repr(input_text),
        "canonical": canonical,
        "tokens": tokens,
        "ngrams_2": ngrams_2,
        "bucket_keys_head0": [],
    }
    
    for ngram in ngrams_2:
        result["bucket_keys_head0"].append({
            "ngram": ngram,
            "ngram_display": ngram.replace(b"\x1f", b"\\x1f").decode("utf-8"),
            "bucket_key_b64u": compute_bucket_key(ngram, head=0),
        })
    
    return result


def main() -> None:
    """Generate deterministic test vector outputs."""
    print("=" * 60)
    print("N-gram Route Index v1 - Test Vector Generator")
    print("=" * 60)
    print()
    
    for vector in TEST_VECTORS:
        result = process_vector(vector)
        
        print(f"### {result['name']}")
        print()
        print(f"Input: {result['input']}")
        print(f"Canonical: {repr(result['canonical'])}")
        print(f"Tokens: {result['tokens']}")
        print()
        
        if result["bucket_keys_head0"]:
            print("2-grams and bucket_key_b64u (head 0):")
            for entry in result["bucket_keys_head0"]:
                print(f"  {entry['ngram_display']!r} -> {entry['bucket_key_b64u']}")
        else:
            print("No 2-grams (token count < 2).")
        
        print()
        print("-" * 60)
        print()


if __name__ == "__main__":
    main()
