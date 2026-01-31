#!/usr/bin/env python3
"""
de Bruijn Route Index Harness CLI.

Phase 66C: Synthetic coverage testing for bucket key hash distribution.

Usage:
    python3 tools/route_index_debruijn_harness.py --alphabet-size 4 --n 3 --sequence-length 256 --heads 4
"""

import argparse
import json
import os
import sys

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ilc_core.star_map.debruijn_harness import (
    generate_debruijn_sequence,
    build_token_stream,
    compute_bucket_histogram,
    summarize_stats,
)


def main() -> int:
    """Run de Bruijn harness with CLI arguments."""
    parser = argparse.ArgumentParser(
        description="de Bruijn synthetic coverage harness for route index bucket keys"
    )
    parser.add_argument(
        "--alphabet-size",
        type=int,
        default=4,
        help="Number of distinct tokens (default: 4)",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=3,
        help="N-gram order (2, 3, or 4) (default: 3)",
    )
    parser.add_argument(
        "--sequence-length",
        type=int,
        default=256,
        help="Length of token stream to analyze (default: 256)",
    )
    parser.add_argument(
        "--heads",
        type=int,
        default=4,
        help="Number of hash heads (default: 4)",
    )
    parser.add_argument(
        "--out-json",
        type=str,
        default=None,
        help="Path to write full stats JSON (optional)",
    )
    parser.add_argument(
        "--cyclic",
        action="store_true",
        help="Enable cyclic wrap-around for full de Bruijn coverage",
    )
    
    args = parser.parse_args()
    
    # Validate n
    if args.n not in {2, 3, 4}:
        print(f"Error: --n must be 2, 3, or 4, got {args.n}", file=sys.stderr)
        return 1
    
    if args.alphabet_size < 1:
        print(f"Error: --alphabet-size must be >= 1, got {args.alphabet_size}", file=sys.stderr)
        return 1
    
    if args.heads < 1:
        print(f"Error: --heads must be >= 1, got {args.heads}", file=sys.stderr)
        return 1
    
    # Build alphabet
    alphabet = [f"a{i}" for i in range(args.alphabet_size)]
    
    print("=== de Bruijn Route Index Harness ===\n")
    print(f"Alphabet size: {args.alphabet_size}")
    print(f"N-gram order: {args.n}")
    print(f"Sequence length: {args.sequence_length}")
    print(f"Heads: {args.heads}")
    print(f"Cyclic mode: {args.cyclic}")
    print()
    
    # Generate de Bruijn sequence
    debruijn_seq = generate_debruijn_sequence(alphabet, args.n)
    print(f"de Bruijn B({args.alphabet_size},{args.n}) length: {len(debruijn_seq)}")
    
    # Build token stream
    tokens = build_token_stream(debruijn_seq, args.sequence_length)
    print(f"Token stream length: {len(tokens)}")
    print()
    
    # Compute bucket histogram
    stats = compute_bucket_histogram(tokens, n=args.n, heads=args.heads, cyclic=args.cyclic)
    
    # Print summary
    print("=== Bucket Distribution ===\n")
    print(summarize_stats(stats))
    print()
    
    # Per-head detail
    print("=== Per-Head Detail ===")
    for ph in stats["per_head"]:
        unique = ph["unique_buckets"]
        total = stats["total_ngrams"]
        collision_rate = (ph["collisions"] / total * 100) if total > 0 else 0.0
        print(f"  Head {ph['head']}: {unique} unique buckets, collision rate={collision_rate:.1f}%")
    
    # Write JSON if requested
    if args.out_json:
        # Remove bucket_counts for cleaner JSON (can be very large)
        stats_for_json = {
            "alphabet_size": args.alphabet_size,
            "n": args.n,
            "sequence_length": args.sequence_length,
            "debruijn_length": len(debruijn_seq),
            "total_ngrams": stats["total_ngrams"],
            "heads": stats["heads"],
            "per_head": [
                {
                    "head": ph["head"],
                    "unique_buckets": ph["unique_buckets"],
                    "max_bucket_load": ph["max_bucket_load"],
                    "collisions": ph["collisions"],
                }
                for ph in stats["per_head"]
            ],
        }
        
        with open(args.out_json, "w", encoding="utf-8") as f:
            json.dump(stats_for_json, f, indent=2)
        print(f"\nStats written to: {args.out_json}")
    
    print("\nHarness complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
