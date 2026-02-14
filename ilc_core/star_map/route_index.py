"""
Star Map N-gram Route Index v1 tooling.

Implements the spec from docs/specs/star.map.ngram.route_index.v1.md:
- Text canonicalization (Section 5)
- Tokenization with guardrails (Section 6)
- N-gram extraction (Section 7)
- Multi-head bucket key hashing (Section 8)
- Route index payload builder (Section 9)
- COSE Sign1 wrapper for signed payloads

All functions follow the spec exactly for determinism and interoperability.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from datetime import datetime, timezone
from typing import Any

from ..protocol.ndjson_bundle import b64u_encode
from ..encoding.dag_cbor import encode_dag_cbor
from ..encoding.cidv1 import node_id_from_bytes
from ..crypto.cose_sign1 import cose_sign1_sign
from ..exceptions import NgramExtractionError, TokenizationError

from cryptography.hazmat.primitives.asymmetric import ed25519


# === Constants (from spec) ===

DOMAIN_SEP = b"ilc.star.map.ngram.route_index.v1\0"
BUCKET_KEY_LEN = 8
MAX_TOKEN_BYTES = 64
MAX_TOKEN_COUNT = 1024
NGRAM_SEPARATOR = b"\x1f"
ALLOWED_NGRAM_ORDERS = frozenset({2, 3, 4})

SCHEMA_URI = "ilc.star.map.ngram.route_index@v1"
CANONICALIZER_URI = "ilc.text.canon@v1"


# === Canonicalization (Section 5) ===

def canonicalize_text(text: str) -> str:
    """
    Canonicalize input text per spec Section 5.
    
    Steps:
    1. Unicode NFKC normalization
    2. Case folding via casefold()
    3. Trim leading/trailing whitespace
    4. Collapse all internal whitespace runs to single ASCII space
    
    Args:
        text: Raw input text.
        
    Returns:
        Canonical form of the text.
    """
    # NFKC normalization (compatibility decomposition + canonical composition)
    normalized = unicodedata.normalize("NFKC", text)
    # Case folding (locale-independent lowercase)
    folded = normalized.casefold()
    # Trim and collapse whitespace to single ASCII space
    collapsed = re.sub(r"\s+", " ", folded).strip()
    return collapsed


# === Tokenization (Section 6) ===

def tokenize_text(canonical_text: str) -> list[str]:
    """
    Tokenize canonical text per spec Section 6.
    
    Steps:
    1. Split on ASCII space (0x20)
    2. Discard empty tokens
    3. Reject tokens containing byte 0x1F (n-gram separator)
    4. Reject tokens > 64 bytes (UTF-8 encoded)
    5. Reject inputs with > 1024 tokens
    
    Args:
        canonical_text: Canonical (normalized) text.
        
    Returns:
        List of token strings.
        
    Raises:
        TokenizationError: If any guardrail is violated.
    """
    if not canonical_text:
        return []
    
    tokens = [t for t in canonical_text.split(" ") if t]
    
    # Validate each token
    for token in tokens:
        token_bytes = token.encode("utf-8")
        # Reject tokens containing n-gram separator byte
        if b"\x1f" in token_bytes:
            raise TokenizationError(
                f"Token contains forbidden byte 0x1F: {token!r}"
            )
        # Reject oversized tokens
        if len(token_bytes) > MAX_TOKEN_BYTES:
            raise TokenizationError(
                f"Token exceeds {MAX_TOKEN_BYTES} bytes: {token[:20]}..."
            )
    
    # Reject inputs with too many tokens
    if len(tokens) > MAX_TOKEN_COUNT:
        raise TokenizationError(
            f"Token count {len(tokens)} exceeds limit {MAX_TOKEN_COUNT}"
        )
    
    return tokens


# === N-gram Extraction (Section 7) ===

def extract_ngrams(tokens: list[str], n: int = 2) -> list[bytes]:
    """
    Extract n-grams from token list per spec Section 7.
    
    Joins consecutive tokens with byte 0x1F separator.
    
    Args:
        tokens: List of token strings.
        n: N-gram order (must be in {2, 3, 4}).
        
    Returns:
        List of n-gram byte sequences.
        
    Raises:
        NgramExtractionError: If n is not in allowed set.
    """
    if n not in ALLOWED_NGRAM_ORDERS:
        raise NgramExtractionError(
            f"N-gram order {n} not in allowed set {sorted(ALLOWED_NGRAM_ORDERS)}"
        )
    
    if len(tokens) < n:
        return []
    
    ngrams = []
    for i in range(len(tokens) - n + 1):
        token_group = tokens[i:i + n]
        ngram_bytes = NGRAM_SEPARATOR.join(
            t.encode("utf-8") for t in token_group
        )
        ngrams.append(ngram_bytes)
    
    return ngrams


# === Hashing (Section 8) ===

def compute_bucket_key_b64u(ngram: bytes, head: int = 0) -> str:
    """
    Compute bucket key for an n-gram per spec Section 8.
    
    Hash construction:
        H = SHA256(domain_sep + head_id + b"\\0" + ngram)
        bucket_key = H[0:8]
        
    Output is base64url encoded without padding.
    
    Args:
        ngram: N-gram byte sequence (tokens joined with 0x1F).
        head: Head index (0-based, encoded as ASCII digits).
        
    Returns:
        Base64url-encoded bucket key (11 characters for 8 bytes).
    """
    head_id = str(head).encode("ascii")
    digest = hashlib.sha256(DOMAIN_SEP + head_id + b"\0" + ngram).digest()
    return b64u_encode(digest[:BUCKET_KEY_LEN])


# === Payload Builder (Section 9) ===

def build_route_index_payload(
    routes: list[dict],
    ngram_orders: list[int],
    heads: int,
    created_at: datetime | None = None,
    epoch: str | None = None,
    producer: str | None = None,
    chunk_id: int | None = None,
    chunk_total: int | None = None,
    chunk_range_hint: str | None = None,
) -> dict:
    """
    Build a route index payload dict per spec Section 9.
    
    The payload follows ILC canonical object rules (str-only keys).
    Routes and targets are sorted deterministically.
    
    Args:
        routes: List of route dicts, each with keys:
            - "n": int (n-gram order)
            - "head": int (head index)
            - "k": str (bucket key b64u)
            - "targets": list of {"route": str, "w": int}
        ngram_orders: List of n-gram orders used (e.g., [2, 3]).
        heads: Number of hash heads.
        created_at: Creation timestamp (default: now UTC).
        epoch: Optional epoch identifier.
        producer: Optional producer identifier.
        chunk_id: Optional chunk index (0-based).
        chunk_total: Optional total chunk count.
        chunk_range_hint: Optional range hint for chunking.
        
    Returns:
        Payload dict ready for DAG-CBOR encoding.
    """
    if created_at is None:
        created_at = datetime.now(timezone.utc)
    
    # Deep copy routes to avoid mutating caller's data
    copied_routes = []
    for r in routes:
        r_copy = dict(r)
        if "targets" in r_copy:
            r_copy["targets"] = list(r_copy["targets"])
        copied_routes.append(r_copy)
    
    # Sort routes by (n, head, k) for determinism
    sorted_routes = sorted(
        copied_routes,
        key=lambda r: (r["n"], r["head"], r["k"])
    )
    
    # Sort targets within each route by route key for determinism
    for route in sorted_routes:
        if "targets" in route:
            route["targets"] = sorted(
                route["targets"],
                key=lambda t: t["route"]
            )
    
    # Build payload with required fields
    payload: dict[str, Any] = {
        "schema": SCHEMA_URI,
        "created_at": created_at.isoformat().replace("+00:00", "Z"),
        "canonicalizer": CANONICALIZER_URI,
        "ngram_orders": sorted(ngram_orders),
        "heads": heads,
        "bucket_key_len": BUCKET_KEY_LEN,
        "routes": sorted_routes,
    }
    
    # Add optional fields if provided
    if epoch is not None:
        payload["epoch"] = epoch
    if producer is not None:
        payload["producer"] = producer
    if chunk_id is not None:
        payload["chunk_id"] = chunk_id
    if chunk_total is not None:
        payload["chunk_total"] = chunk_total
    if chunk_range_hint is not None:
        payload["chunk_range_hint"] = chunk_range_hint
    
    return payload


# === Node ID Helper ===

def node_id_from_payload(payload: dict) -> str:
    """
    Compute NodeID from a route index payload.
    
    Encodes the payload as DAG-CBOR and computes CIDv1 hash.
    
    Args:
        payload: Route index payload dict.
        
    Returns:
        NodeID string (base32-encoded CIDv1).
    """
    dag_cbor_bytes = encode_dag_cbor(payload)
    return node_id_from_bytes(dag_cbor_bytes)


# === COSE Signing ===

def build_route_index_cose_sign1(
    payload: dict,
    private_key: ed25519.Ed25519PrivateKey,
    kid: bytes | None = None,
) -> bytes:
    """
    Build a COSE Sign1 attestation for a route index payload.
    
    Encodes the payload as DAG-CBOR and signs with Ed25519.
    
    Args:
        payload: Route index payload dict.
        private_key: Ed25519 private key for signing.
        kid: Optional key identifier bytes.
        
    Returns:
        COSE_Sign1 encoded bytes.
    """
    dag_cbor_bytes = encode_dag_cbor(payload)
    return cose_sign1_sign(dag_cbor_bytes, private_key, kid=kid)
