"""
NDJSON Bundle Transport for COSE-Signed ILC Artifacts.

Phase 66C: Streaming NDJSON format for moving COSE_Sign1 attestations between
agents/nodes with ordering guarantees, size limits, and optional footer digest.

This module provides:
- Deterministic JSON line serialization
- Streaming bundle writer with size guardrails
- Streaming bundle reader/iterator with strict ordering
- Line validators for header/record/footer schemas
- Base64url encoding (no padding) for COSE bytes

Transport vs Commitment:
- This is a TRANSPORT format (untrusted until verified)
- Commitment layer is strict DAG-CBOR + CIDv1 NodeID + COSE_Sign1
- Use verify_bundle_record() to bind transport records to commitment
"""

from __future__ import annotations

import hashlib
import json
import base64
import binascii
import uuid
from datetime import datetime, timezone
from typing import Any, Iterator, TextIO, Iterable

from ..encoding.cidv1 import parse_nodeid_strict


# === Constants ===

DEFAULT_MAX_LINE_BYTES = 1_048_576  # 1 MiB
DEFAULT_MAX_RECORDS_PER_BUNDLE = 100_000
DEFAULT_MAX_TOTAL_BYTES_PER_BUNDLE = 64 * 1024 * 1024  # 64 MiB

BUNDLE_VERSION = 1
RECORD_KIND_COSE_SIGN1 = "cose_sign1"
COSE_ENCODING_BASE64URL = "base64url"

TYPE_HEADER = "ilc.bundle.header"
TYPE_RECORD = "ilc.bundle.record"
TYPE_FOOTER = "ilc.bundle.footer"


# === Base64url Helpers (NO padding) ===

def b64u_encode(data: bytes) -> str:
    """Encode bytes to base64url without '=' padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


# Base64url alphabet (RFC 4648)
_B64U_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_")


def b64u_decode(s: str) -> bytes:
    """Decode base64url without '=' padding.
    
    Raises:
        ValueError: If input contains invalid characters.
    """
    # Validate charset first
    for i, c in enumerate(s):
        if c not in _B64U_CHARS:
            raise ValueError(f"Invalid base64url encoding: invalid character '{c}' at position {i}")
    
    # Add padding back
    padding = 4 - (len(s) % 4)
    if padding != 4:
        s = s + "=" * padding
    try:
        return base64.urlsafe_b64decode(s)
    except (binascii.Error, ValueError) as e:
        raise ValueError(f"Invalid base64url encoding: {e}")


# === Deterministic JSON Serialization ===

def dumps_ndjson(obj: dict) -> str:
    """Serialize dict to deterministic JSON line ending with '\\n'.
    
    Uses sorted keys and compact separators for reproducibility.
    Rejects NaN/Infinity for cross-language compatibility.
    """
    line = json.dumps(
        obj,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,  # Strict JSON: reject NaN/Infinity
    )
    return line + "\n"


def _reject_nan_infinity(constant: str):
    """Raise error for NaN/Infinity in JSON parsing."""
    raise ValueError(f"Non-JSON constant not allowed: {constant}")


def loads_ndjson(line: str) -> dict:
    """Parse one NDJSON line into a dict.
    
    Strips trailing newlines, rejects non-dict results.
    Rejects NaN/Infinity for cross-language compatibility.
    
    Raises:
        ValueError: If line is empty, doesn't parse to dict, or contains NaN/Infinity.
    """
    # Normalize line endings
    line = line.rstrip("\r\n")
    if not line or line.isspace():
        raise ValueError("Empty or whitespace-only NDJSON line")
    
    try:
        obj = json.loads(line, parse_constant=_reject_nan_infinity)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")
    
    if not isinstance(obj, dict):
        raise ValueError(f"NDJSON line must be a JSON object, got {type(obj).__name__}")
    
    return obj


# === Line Validators ===

def validate_bundle_header(obj: dict, *, line_num: int = 1) -> None:
    """Validate bundle header line.
    
    Raises:
        ValueError: If header is invalid with actionable message.
    """
    prefix = f"NDJSON bundle line {line_num}"
    
    if obj.get("type") != TYPE_HEADER:
        raise ValueError(f"{prefix}: expected type '{TYPE_HEADER}', got '{obj.get('type')}'")
    
    # Required fields
    required = ["bundle_version", "bundle_id", "created_at", "record_kind", "cose_encoding"]
    for key in required:
        if key not in obj:
            raise ValueError(f"{prefix}: header missing required field '{key}'")
    
    # Version check
    if obj["bundle_version"] != BUNDLE_VERSION:
        raise ValueError(f"{prefix}: unsupported bundle_version {obj['bundle_version']}, expected {BUNDLE_VERSION}")
    
    # Record kind
    if obj["record_kind"] != RECORD_KIND_COSE_SIGN1:
        raise ValueError(f"{prefix}: unsupported record_kind '{obj['record_kind']}', expected '{RECORD_KIND_COSE_SIGN1}'")
    
    # COSE encoding
    if obj["cose_encoding"] != COSE_ENCODING_BASE64URL:
        raise ValueError(f"{prefix}: unsupported cose_encoding '{obj['cose_encoding']}', expected '{COSE_ENCODING_BASE64URL}'")
    
    # bundle_id should be string
    if not isinstance(obj["bundle_id"], str):
        raise ValueError(f"{prefix}: bundle_id must be string")
    
    # created_at should be string
    if not isinstance(obj["created_at"], str):
        raise ValueError(f"{prefix}: created_at must be string")


def validate_bundle_record(obj: dict, *, line_num: int, prev_seq: int | None = None) -> None:
    """Validate bundle record line.
    
    Args:
        obj: Parsed record dict.
        line_num: Line number for error messages.
        prev_seq: Previous sequence number for ordering check (None if first record).
    
    Raises:
        ValueError: If record is invalid with actionable message.
    """
    prefix = f"NDJSON bundle line {line_num}"
    
    if obj.get("type") != TYPE_RECORD:
        raise ValueError(f"{prefix}: expected type '{TYPE_RECORD}', got '{obj.get('type')}'")
    
    # Required fields
    required = ["seq", "node_id", "cose_sign1_b64u"]
    for key in required:
        if key not in obj:
            raise ValueError(f"{prefix}: record missing required field '{key}'")
    
    # seq must be integer >= 1
    seq = obj["seq"]
    if not isinstance(seq, int) or seq < 1:
        raise ValueError(f"{prefix}: seq must be integer >= 1, got {seq!r}")
    
    # Strict ordering: seq must be strictly increasing
    if prev_seq is not None and seq <= prev_seq:
        raise ValueError(f"{prefix}: seq {seq} not greater than previous {prev_seq} (strict ordering required)")
    
    # node_id must be valid CIDv1
    node_id = obj["node_id"]
    if not isinstance(node_id, str):
        raise ValueError(f"{prefix}: node_id must be string")
    try:
        parse_nodeid_strict(node_id)
    except ValueError as e:
        raise ValueError(f"{prefix}: invalid node_id: {e}")
    
    # cose_sign1_b64u must be string
    cose_b64 = obj["cose_sign1_b64u"]
    if not isinstance(cose_b64, str):
        raise ValueError(f"{prefix}: cose_sign1_b64u must be string")
    
    # Validate base64url decodes
    try:
        b64u_decode(cose_b64)
    except ValueError as e:
        raise ValueError(f"{prefix}: invalid cose_sign1_b64u: {e}")
    
    # meta is optional, but if present must be dict
    if "meta" in obj and not isinstance(obj["meta"], dict):
        raise ValueError(f"{prefix}: meta must be object if present")


def validate_bundle_footer(obj: dict, *, line_num: int) -> None:
    """Validate bundle footer line structure (not digest).
    
    Raises:
        ValueError: If footer structure is invalid.
    """
    prefix = f"NDJSON bundle line {line_num}"
    
    if obj.get("type") != TYPE_FOOTER:
        raise ValueError(f"{prefix}: expected type '{TYPE_FOOTER}', got '{obj.get('type')}'")
    
    # Required fields
    required = ["record_count", "sha256_b64u"]
    for key in required:
        if key not in obj:
            raise ValueError(f"{prefix}: footer missing required field '{key}'")
    
    # record_count must be non-negative integer
    count = obj["record_count"]
    if not isinstance(count, int) or count < 0:
        raise ValueError(f"{prefix}: record_count must be non-negative integer, got {count!r}")
    
    # sha256_b64u must be string
    if not isinstance(obj["sha256_b64u"], str):
        raise ValueError(f"{prefix}: sha256_b64u must be string")


# === Bundle Writer ===

def make_bundle_header(
    *,
    bundle_id: str | None = None,
    created_at: str | None = None,
    ilc_phase: str = "66C",
    notes: str | None = None,
) -> dict:
    """Create a valid bundle header dict."""
    header = {
        "type": TYPE_HEADER,
        "bundle_version": BUNDLE_VERSION,
        "bundle_id": bundle_id or str(uuid.uuid4()),
        "created_at": created_at or datetime.now(timezone.utc).isoformat(),
        "ilc_phase": ilc_phase,
        "record_kind": RECORD_KIND_COSE_SIGN1,
        "cose_encoding": COSE_ENCODING_BASE64URL,
    }
    if notes is not None:
        header["notes"] = notes
    return header


def make_bundle_record(
    *,
    seq: int,
    node_id: str,
    cose_bytes: bytes,
    meta: dict | None = None,
) -> dict:
    """Create a valid bundle record dict."""
    record = {
        "type": TYPE_RECORD,
        "seq": seq,
        "node_id": node_id,
        "cose_sign1_b64u": b64u_encode(cose_bytes),
    }
    if meta is not None:
        record["meta"] = meta
    return record


def write_bundle(
    fp: TextIO,
    *,
    header: dict,
    records: Iterable[dict],
    include_footer: bool = True,
    max_line_bytes: int = DEFAULT_MAX_LINE_BYTES,
) -> dict:
    """Write NDJSON bundle to file-like object.
    
    Args:
        fp: File-like object open for text writing.
        header: Bundle header dict.
        records: Iterable of record dicts.
        include_footer: Whether to emit footer with digest.
        max_line_bytes: Maximum line size in UTF-8 bytes.
    
    Returns:
        Summary dict with record_count and footer_digest (if footer emitted).
    
    Raises:
        ValueError: If validation fails or line too large.
    """
    line_num = 0
    
    def emit_line(obj: dict) -> bytes:
        """Emit one line, return UTF-8 bytes for digest."""
        nonlocal line_num
        line_num += 1
        line = dumps_ndjson(obj)
        line_bytes = line.encode("utf-8")
        if len(line_bytes) > max_line_bytes:
            raise ValueError(
                f"NDJSON bundle line {line_num}: line too large "
                f"({len(line_bytes)} bytes > {max_line_bytes} limit)"
            )
        fp.write(line)
        return line_bytes
    
    # Emit header
    validate_bundle_header(header, line_num=1)
    emit_line(header)
    
    # Emit records, compute digest
    record_count = 0
    hasher = hashlib.sha256() if include_footer else None
    prev_seq = None
    
    for record in records:
        record_count += 1
        line_num_for_record = line_num + 1
        validate_bundle_record(record, line_num=line_num_for_record, prev_seq=prev_seq)
        prev_seq = record["seq"]
        
        line_bytes = emit_line(record)
        if hasher is not None:
            hasher.update(line_bytes)
    
    # Emit footer
    result = {"record_count": record_count}
    
    if include_footer:
        digest = hasher.digest()
        footer = {
            "type": TYPE_FOOTER,
            "record_count": record_count,
            "sha256_b64u": b64u_encode(digest),
        }
        validate_bundle_footer(footer, line_num=line_num + 1)
        emit_line(footer)
        result["sha256_b64u"] = footer["sha256_b64u"]
    
    return result


# === Bundle Reader / Iterator ===

def _parse_bundle_line(
    raw_line: str,
    *,
    line_num: int,
    max_line_bytes: int,
) -> dict | None:
    line_bytes = raw_line.encode("utf-8")
    if len(line_bytes) > max_line_bytes:
        raise ValueError(
            f"NDJSON bundle line {line_num}: line too large "
            f"({len(line_bytes)} bytes > {max_line_bytes} limit)"
        )
    stripped = raw_line.rstrip("\r\n")
    if not stripped or stripped.isspace():
        return None
    try:
        return loads_ndjson(raw_line)
    except ValueError as e:
        raise ValueError(f"NDJSON bundle line {line_num}: {e}")

def _bundle_check_header_state(line_num: int, header_seen: bool, record_count: int, footer_seen: bool) -> None:
    if header_seen:
        raise ValueError(f"NDJSON bundle line {line_num}: duplicate header")
    if record_count > 0 or footer_seen:
        raise ValueError(f"NDJSON bundle line {line_num}: header must be first line")

def _bundle_check_record_state(line_num: int, header_seen: bool, footer_seen: bool) -> None:
    if not header_seen:
        raise ValueError(f"NDJSON bundle line {line_num}: record before header")
    if footer_seen:
        raise ValueError(f"NDJSON bundle line {line_num}: record after footer")

def _bundle_check_footer_state(line_num: int, header_seen: bool, footer_seen: bool) -> None:
    if not header_seen:
        raise ValueError(f"NDJSON bundle line {line_num}: footer before header")
    if footer_seen:
        raise ValueError(f"NDJSON bundle line {line_num}: duplicate footer")

def _bundle_validate_footer_content(
    pending_footer: dict,
    record_count: int,
    hasher: Any  # hashlib object
) -> None:
    if pending_footer["record_count"] != record_count:
        raise ValueError(
            f"NDJSON bundle footer: record_count mismatch "
            f"(footer says {pending_footer['record_count']}, actual {record_count})"
        )
    
    computed_digest = b64u_encode(hasher.digest())
    if pending_footer["sha256_b64u"] != computed_digest:
        raise ValueError(
            f"NDJSON bundle footer: sha256 digest mismatch "
            f"(footer: {pending_footer['sha256_b64u']}, computed: {computed_digest})"
        )

def iter_bundle(
    fp: TextIO,
    *,
    require_footer: bool = False,
    validate_footer: bool = True,
    max_line_bytes: int = DEFAULT_MAX_LINE_BYTES,
    max_records: int = DEFAULT_MAX_RECORDS_PER_BUNDLE,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES_PER_BUNDLE,
) -> Iterator[tuple[str, dict]]:
    """Iterate over bundle lines, yielding (type, obj) tuples.
    
    Yields:
        ("header", header_dict) - exactly once, first
        ("record", record_dict) - zero or more times
        ("footer", footer_dict) - at most once, last
    
    Args:
        fp: File-like object open for text reading.
        require_footer: If True, error if footer absent.
        validate_footer: If True, validate footer digest.
        max_line_bytes: Maximum line size in UTF-8 bytes.
    
    Raises:
        ValueError: On validation errors with line number context.
    """
    line_num = 0
    header_seen = False
    footer_seen = False
    prev_seq = None
    record_count = 0
    hasher = hashlib.sha256()
    total_bytes = 0
    
    pending_footer: dict | None = None
    
    for raw_line in fp:
        line_num += 1
        line_bytes = raw_line.encode("utf-8")
        total_bytes += len(line_bytes)
        if total_bytes > max_total_bytes:
            raise ValueError(
                "NDJSON bundle exceeded max_total_bytes "
                f"({total_bytes} bytes > {max_total_bytes} limit)"
            )
        obj = _parse_bundle_line(
            raw_line,
            line_num=line_num,
            max_line_bytes=max_line_bytes,
        )
        if obj is None:
            continue

        obj_type = obj.get("type")
        
        if obj_type == TYPE_HEADER:
            _bundle_check_header_state(line_num, header_seen, record_count, footer_seen)
            validate_bundle_header(obj, line_num=line_num)
            header_seen = True
            yield ("header", obj)
        
        elif obj_type == TYPE_RECORD:
            _bundle_check_record_state(line_num, header_seen, footer_seen)
            validate_bundle_record(obj, line_num=line_num, prev_seq=prev_seq)
            prev_seq = obj["seq"]
            record_count += 1
            if record_count > max_records:
                raise ValueError(
                    "NDJSON bundle exceeded max_records "
                    f"({record_count} records > {max_records} limit)"
                )
            
            # Hash using normalized line (ending with \n)
            normalized = raw_line.rstrip("\r\n") + "\n"
            hasher.update(normalized.encode("utf-8"))
            
            yield ("record", obj)
        
        elif obj_type == TYPE_FOOTER:
            _bundle_check_footer_state(line_num, header_seen, footer_seen)
            validate_bundle_footer(obj, line_num=line_num)
            footer_seen = True
            pending_footer = obj
            # Don't yield yet - need to check it's actually last
        
        else:
            raise ValueError(f"NDJSON bundle line {line_num}: unknown type '{obj_type}'")
    
    # Post-iteration checks
    if not header_seen:
        raise ValueError("NDJSON bundle: no header found")
    
    if pending_footer is not None:
        # Validate footer content
        if validate_footer:
            _bundle_validate_footer_content(pending_footer, record_count, hasher)
        
        yield ("footer", pending_footer)
    
    elif require_footer:
        raise ValueError("NDJSON bundle: footer required but not found")


def read_bundle(
    fp: TextIO,
    *,
    require_footer: bool = False,
    validate_footer: bool = True,
    max_line_bytes: int = DEFAULT_MAX_LINE_BYTES,
    max_records: int = DEFAULT_MAX_RECORDS_PER_BUNDLE,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES_PER_BUNDLE,
) -> dict:
    """Read entire bundle into memory.
    
    Returns:
        {
            "header": header_dict,
            "records": [record_dict, ...],
            "footer": footer_dict or None
        }
    """
    result: dict[str, Any] = {"header": None, "records": [], "footer": None}
    
    for event_type, obj in iter_bundle(
        fp,
        require_footer=require_footer,
        validate_footer=validate_footer,
        max_line_bytes=max_line_bytes,
        max_records=max_records,
        max_total_bytes=max_total_bytes,
    ):
        if event_type == "header":
            result["header"] = obj
        elif event_type == "record":
            result["records"].append(obj)
        elif event_type == "footer":
            result["footer"] = obj
    
    return result
