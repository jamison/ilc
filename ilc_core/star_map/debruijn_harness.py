# SPDX-License-Identifier: AGPL-3.0-or-later
"""
de Bruijn Harness for Route Index Evaluation.

Provides synthetic coverage testing using de Bruijn sequences to generate
token streams with guaranteed combinatorial properties for bucket key
hash distribution analysis.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .route_index import extract_ngrams, compute_bucket_key_b64u


def generate_debruijn_sequence(alphabet: list[str], n: int) -> list[str]:
    """
    Generate a de Bruijn sequence over the given alphabet.
    
    A de Bruijn sequence B(k,n) contains every possible subsequence of
    length n exactly once when viewed cyclically.
    
    Uses the standard FKM algorithm (lexicographically smallest).
    
    Args:
        alphabet: List of distinct token strings.
        n: Subsequence length (n-gram order).
        
    Returns:
        List of tokens forming the de Bruijn sequence.
        Length is len(alphabet) ** n (cyclic, not including wrap-around).
        
    Raises:
        ValueError: If alphabet is empty or n < 1.
    """
    if not alphabet:
        raise ValueError("Alphabet must not be empty")
    if n < 1:
        raise ValueError("n must be at least 1")
    
    k = len(alphabet)
    
    # Build index mapping for alphabet
    idx_to_token = {i: tok for i, tok in enumerate(alphabet)}
    
    # FKM algorithm: generate de Bruijn sequence as indices
    sequence_indices: list[int] = []
    a = [0] * (k * n)
    
    def db(t: int, p: int) -> None:
        if t > n:
            if n % p == 0:
                sequence_indices.extend(a[1:p + 1])
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)
    
    db(1, 1)
    
    # Convert indices to tokens
    return [idx_to_token[i] for i in sequence_indices]


def build_token_stream(seq: list[str], length: int) -> list[str]:
    """
    Build a token stream of exact length by repeating the sequence.
    
    Args:
        seq: Base sequence (typically a de Bruijn sequence).
        length: Desired output length.
        
    Returns:
        Token list of exactly `length` tokens.
        
    Raises:
        ValueError: If seq is empty and length > 0.
    """
    if length <= 0:
        return []
    if not seq:
        raise ValueError("Cannot build stream from empty sequence")
    
    # Tile the sequence to reach desired length
    full_repeats = length // len(seq)
    remainder = length % len(seq)
    
    result = seq * full_repeats + seq[:remainder]
    return result


def compute_bucket_histogram(
    tokens: list[str],
    n: int,
    heads: int,
    cyclic: bool = False,
) -> dict[str, Any]:
    """
    Compute bucket key histogram for n-grams over multiple heads.
    
    Args:
        tokens: Token stream.
        n: N-gram order (must be in {2, 3, 4}).
        heads: Number of hash heads (must be >= 1).
        cyclic: If True, extend tokens by first n-1 for wrap-around coverage.
        
    Returns:
        Dict with:
        - total_ngrams: int
        - heads: int
        - cyclic: bool
        - per_head: list of dicts, each with:
            - head: int
            - unique_buckets: int
            - max_bucket_load: int
            - collisions: int (n-grams beyond first in any bucket)
            - bucket_counts: dict[str, int]
            
    Raises:
        ValueError: If n not in {2,3,4} or heads < 1.
    """
    if n not in {2, 3, 4}:
        raise ValueError(f"n must be in {{2, 3, 4}}, got {n}")
    if heads < 1:
        raise ValueError(f"heads must be >= 1, got {heads}")
    
    if len(tokens) < n:
        return {
            "total_ngrams": 0,
            "heads": heads,
            "cyclic": cyclic,
            "per_head": [
                {
                    "head": h,
                    "unique_buckets": 0,
                    "max_bucket_load": 0,
                    "collisions": 0,
                    "bucket_counts": {},
                }
                for h in range(heads)
            ],
        }
    
    # Apply cyclic wrap-around if requested
    if cyclic and len(tokens) >= n:
        tokens = tokens + tokens[:n - 1]
    
    # Extract n-grams
    ngrams = extract_ngrams(tokens, n=n)
    total_ngrams = len(ngrams)
    
    per_head_stats = []
    for h in range(heads):
        bucket_counts: dict[str, int] = defaultdict(int)
        
        for ngram in ngrams:
            bucket_key = compute_bucket_key_b64u(ngram, head=h)
            bucket_counts[bucket_key] += 1
        
        unique_buckets = len(bucket_counts)
        max_load = max(bucket_counts.values()) if bucket_counts else 0
        # Collisions = total - unique (items beyond first per bucket)
        collisions = total_ngrams - unique_buckets
        
        per_head_stats.append({
            "head": h,
            "unique_buckets": unique_buckets,
            "max_bucket_load": max_load,
            "collisions": collisions,
            "bucket_counts": dict(bucket_counts),
        })
    
    return {
        "total_ngrams": total_ngrams,
        "heads": heads,
        "cyclic": cyclic,
        "per_head": per_head_stats,
    }


def summarize_stats(stats: dict[str, Any]) -> str:
    """
    Generate human-readable summary of bucket histogram stats.
    
    Args:
        stats: Output from compute_bucket_histogram.
        
    Returns:
        Multi-line summary string.
    """
    lines = [
        f"Total n-grams: {stats['total_ngrams']}",
        f"Heads: {stats['heads']}",
    ]
    
    for ph in stats["per_head"]:
        lines.append(
            f"  Head {ph['head']}: "
            f"unique={ph['unique_buckets']}, "
            f"max_load={ph['max_bucket_load']}, "
            f"collisions={ph['collisions']}"
        )
    
    return "\n".join(lines)
