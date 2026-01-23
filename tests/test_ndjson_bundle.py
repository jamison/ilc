"""
Tests for NDJSON Bundle Transport.

Phase 66C: Comprehensive tests for streaming NDJSON bundles with
ordering, size limits, footer digest, and transport-to-commitment binding.
"""

import io
import pytest

from cryptography.hazmat.primitives.asymmetric import ed25519

from ilc_core.encoding.dag_cbor import encode_dag_cbor
from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.crypto.cose_sign1 import cose_sign1_sign
from ilc_core.crypto.cbor_canonical import cbor_dumps_canonical

from ilc_core.protocol.ndjson_bundle import (
    # Constants
    DEFAULT_MAX_LINE_BYTES,
    TYPE_HEADER,
    TYPE_RECORD,
    TYPE_FOOTER,
    # Base64url
    b64u_encode,
    b64u_decode,
    # JSON
    dumps_ndjson,
    loads_ndjson,
    # Validators
    validate_bundle_header,
    validate_bundle_record,
    validate_bundle_footer,
    # Factory
    make_bundle_header,
    make_bundle_record,
    # Writer/Reader
    write_bundle,
    iter_bundle,
    read_bundle,
)

from ilc_core.protocol.bundle_verify import verify_bundle_record


# Fixed test keys
TEST_PRIVATE_KEY_BYTES = bytes.fromhex(
    "9d61b19deffd5a60ba844af492ec2cc44449c5697b326919703bac031cae7f60"
)
TEST_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(TEST_PRIVATE_KEY_BYTES)
TEST_PUBLIC_KEY = TEST_PRIVATE_KEY.public_key()


def make_signed_record(payload_obj: dict, seq: int) -> tuple[dict, bytes]:
    """Create a signed bundle record from payload object."""
    payload_bytes = encode_dag_cbor(payload_obj)
    node_id = node_id_from_obj(payload_obj)
    cose_bytes = cose_sign1_sign(payload_bytes, TEST_PRIVATE_KEY)
    record = make_bundle_record(seq=seq, node_id=node_id, cose_bytes=cose_bytes)
    return record, cose_bytes


class TestBase64url:
    """Tests for base64url encoding/decoding."""

    def test_encode_decode_roundtrip(self):
        """Base64url roundtrip preserves data."""
        data = b"\x00\xff\x10\x20test"
        encoded = b64u_encode(data)
        decoded = b64u_decode(encoded)
        assert decoded == data

    def test_no_padding_in_output(self):
        """Encoder produces no '=' padding."""
        # Length not multiple of 3
        data = b"ab"
        encoded = b64u_encode(data)
        assert "=" not in encoded

    def test_decode_rejects_invalid_chars(self):
        """Decoder rejects invalid base64url characters."""
        with pytest.raises(ValueError, match="Invalid base64url"):
            b64u_decode("abc!def")

    def test_urlsafe_alphabet(self):
        """Uses URL-safe alphabet (- and _ instead of + and /)."""
        # Data that produces + and / in standard base64
        data = bytes([0xfb, 0xef])
        encoded = b64u_encode(data)
        assert "+" not in encoded
        assert "/" not in encoded


class TestNdjsonSerialization:
    """Tests for deterministic JSON line serialization."""

    def test_dumps_ends_with_newline(self):
        """dumps_ndjson output ends with newline."""
        line = dumps_ndjson({"a": 1})
        assert line.endswith("\n")

    def test_dumps_sorted_keys(self):
        """Keys are sorted for determinism."""
        line = dumps_ndjson({"z": 1, "a": 2, "m": 3})
        assert line == '{"a":2,"m":3,"z":1}\n'

    def test_dumps_compact(self):
        """No extra whitespace in output."""
        line = dumps_ndjson({"key": "value"})
        assert " " not in line.strip()

    def test_loads_strips_newlines(self):
        """loads_ndjson handles various line endings."""
        obj1 = loads_ndjson('{"a":1}\n')
        obj2 = loads_ndjson('{"a":1}\r\n')
        obj3 = loads_ndjson('{"a":1}')
        assert obj1 == obj2 == obj3 == {"a": 1}

    def test_loads_rejects_empty(self):
        """Empty lines are rejected."""
        with pytest.raises(ValueError, match="Empty"):
            loads_ndjson("")
        with pytest.raises(ValueError, match="Empty"):
            loads_ndjson("   \n")

    def test_loads_rejects_non_dict(self):
        """Non-dict JSON is rejected."""
        with pytest.raises(ValueError, match="must be a JSON object"):
            loads_ndjson("[1, 2, 3]")
        with pytest.raises(ValueError, match="must be a JSON object"):
            loads_ndjson('"string"')


class TestBundleRoundtrip:
    """Tests for bundle write/read roundtrip."""

    def test_happy_path_with_footer(self):
        """Full roundtrip with 3 records and footer."""
        payloads = [
            {"message": "first", "n": 1},
            {"message": "second", "n": 2},
            {"message": "third", "n": 3},
        ]
        
        records = []
        for i, payload in enumerate(payloads, 1):
            record, _ = make_signed_record(payload, seq=i)
            records.append(record)
        
        # Write
        buf = io.StringIO()
        header = make_bundle_header(notes="test bundle")
        result = write_bundle(buf, header=header, records=records, include_footer=True)
        
        assert result["record_count"] == 3
        assert "sha256_b64u" in result
        
        # Read
        buf.seek(0)
        bundle = read_bundle(buf, validate_footer=True)
        
        assert bundle["header"]["type"] == TYPE_HEADER
        assert len(bundle["records"]) == 3
        assert bundle["footer"] is not None
        assert bundle["footer"]["record_count"] == 3

    def test_verify_all_records(self):
        """verify_bundle_record succeeds for all records."""
        payloads = [{"key": f"value{i}"} for i in range(3)]
        
        records = []
        for i, payload in enumerate(payloads, 1):
            record, _ = make_signed_record(payload, seq=i)
            records.append(record)
        
        buf = io.StringIO()
        write_bundle(buf, header=make_bundle_header(), records=records)
        
        buf.seek(0)
        bundle = read_bundle(buf)
        
        for i, record in enumerate(bundle["records"]):
            verified = verify_bundle_record(record, public_key=TEST_PUBLIC_KEY)
            assert verified["seq"] == i + 1
            assert verified["node_id"] == record["node_id"]
            assert verified["payload_obj"] == payloads[i]


class TestDeterminism:
    """Tests for deterministic output."""

    def test_same_input_same_output(self):
        """Writing same bundle twice produces identical bytes."""
        payload = {"test": "determinism", "seq": 42}
        record, _ = make_signed_record(payload, seq=1)
        
        def write_once():
            buf = io.StringIO()
            header = make_bundle_header(
                bundle_id="fixed-id",
                created_at="2026-01-24T00:00:00Z",
            )
            write_bundle(buf, header=header, records=[record])
            return buf.getvalue()
        
        output1 = write_once()
        output2 = write_once()
        
        assert output1 == output2


class TestStreamingLarge:
    """Tests for streaming behavior with large record counts."""

    def test_large_generator_streaming(self):
        """Writer consumes generator once, reader counts correctly."""
        record_count = 2000
        
        # Track generator consumption
        consumed = []
        
        def gen_records():
            for i in range(1, record_count + 1):
                payload = {"i": i}
                record, _ = make_signed_record(payload, seq=i)
                consumed.append(i)
                yield record
        
        buf = io.StringIO()
        write_bundle(buf, header=make_bundle_header(), records=gen_records())
        
        # Generator was fully consumed once
        assert len(consumed) == record_count
        
        # Reader counts correctly
        buf.seek(0)
        read_count = 0
        for event_type, _ in iter_bundle(buf):
            if event_type == "record":
                read_count += 1
        
        assert read_count == record_count


class TestOrderingViolations:
    """Tests for ordering enforcement."""

    def test_record_before_header_rejected(self):
        """Record before header is rejected."""
        lines = '{"type":"ilc.bundle.record","seq":1,"node_id":"bafabc","cose_sign1_b64u":"AA"}\n'
        buf = io.StringIO(lines)
        
        with pytest.raises(ValueError, match="record before header"):
            list(iter_bundle(buf))

    def test_duplicate_header_rejected(self):
        """Second header is rejected."""
        header = make_bundle_header()
        lines = dumps_ndjson(header) + dumps_ndjson(header)
        buf = io.StringIO(lines)
        
        with pytest.raises(ValueError, match="duplicate header"):
            list(iter_bundle(buf))

    def test_record_after_footer_rejected(self):
        """Record after footer is rejected."""
        header = make_bundle_header()
        record, _ = make_signed_record({"a": 1}, seq=1)
        footer = {"type": TYPE_FOOTER, "record_count": 1, "sha256_b64u": "AA"}
        
        lines = dumps_ndjson(header) + dumps_ndjson(record) + dumps_ndjson(footer) + dumps_ndjson(record)
        buf = io.StringIO(lines)
        
        with pytest.raises(ValueError, match="record after footer"):
            list(iter_bundle(buf))

    def test_unknown_type_rejected(self):
        """Unknown line type is rejected."""
        header = make_bundle_header()
        unknown = {"type": "ilc.bundle.unknown"}
        lines = dumps_ndjson(header) + dumps_ndjson(unknown)
        buf = io.StringIO(lines)
        
        with pytest.raises(ValueError, match="unknown type"):
            list(iter_bundle(buf))

    def test_seq_not_increasing_rejected(self):
        """Non-increasing seq is rejected."""
        header = make_bundle_header()
        record1, _ = make_signed_record({"a": 1}, seq=5)
        record2, _ = make_signed_record({"a": 2}, seq=3)  # Out of order
        
        lines = dumps_ndjson(header) + dumps_ndjson(record1) + dumps_ndjson(record2)
        buf = io.StringIO(lines)
        
        with pytest.raises(ValueError, match="not greater than previous"):
            list(iter_bundle(buf))


class TestLineSizeLimit:
    """Tests for line size enforcement."""

    def test_line_too_large_rejected(self):
        """Line exceeding limit is rejected with sizes in error."""
        # Create a record with large metadata
        payload = {"a": 1}
        record, _ = make_signed_record(payload, seq=1)
        record["meta"] = {"big": "x" * 1000}
        
        buf = io.StringIO()
        header = make_bundle_header()
        
        with pytest.raises(ValueError, match=r"line too large.*bytes.*limit"):
            write_bundle(buf, header=header, records=[record], max_line_bytes=500)


class TestFooterMismatch:
    """Tests for footer validation."""

    def test_wrong_record_count_rejected(self):
        """Footer with wrong record_count is rejected."""
        header = make_bundle_header()
        record, _ = make_signed_record({"a": 1}, seq=1)
        
        # Write manually with wrong footer
        lines = dumps_ndjson(header) + dumps_ndjson(record)
        
        # Compute correct digest for one record
        import hashlib
        hasher = hashlib.sha256()
        record_line = dumps_ndjson(record)
        hasher.update(record_line.encode("utf-8"))
        digest = b64u_encode(hasher.digest())
        
        footer = {"type": TYPE_FOOTER, "record_count": 999, "sha256_b64u": digest}
        lines += dumps_ndjson(footer)
        
        buf = io.StringIO(lines)
        with pytest.raises(ValueError, match="record_count mismatch"):
            list(iter_bundle(buf, validate_footer=True))

    def test_wrong_sha256_rejected(self):
        """Footer with wrong sha256 is rejected."""
        header = make_bundle_header()
        record, _ = make_signed_record({"a": 1}, seq=1)
        
        lines = dumps_ndjson(header) + dumps_ndjson(record)
        footer = {"type": TYPE_FOOTER, "record_count": 1, "sha256_b64u": "AAAA"}
        lines += dumps_ndjson(footer)
        
        buf = io.StringIO(lines)
        with pytest.raises(ValueError, match="sha256 digest mismatch"):
            list(iter_bundle(buf, validate_footer=True))


class TestNodeIdMismatch:
    """Tests for NodeID verification."""

    def test_wrong_node_id_rejected(self):
        """Record with wrong node_id fails verification."""
        payload = {"test": "data"}
        record, _ = make_signed_record(payload, seq=1)
        
        # Tamper with node_id
        record["node_id"] = "bafkreihdwdcefgh4dqkjv67uzcmw7ojee6xedzdetojuzjevtenxquvyku"
        
        with pytest.raises(ValueError, match="NodeID mismatch"):
            verify_bundle_record(record, public_key=TEST_PUBLIC_KEY)


class TestInvalidBase64:
    """Tests for base64url validation."""

    def test_invalid_chars_rejected(self):
        """Invalid base64url characters are rejected."""
        # Create a valid NodeID first
        payload = {"test": "base64"}
        valid_node_id = node_id_from_obj(payload)
        
        header = make_bundle_header()
        record = {
            "type": TYPE_RECORD,
            "seq": 1,
            "node_id": valid_node_id,
            "cose_sign1_b64u": "invalid!@#chars",  # Invalid base64url
        }
        
        lines = dumps_ndjson(header) + dumps_ndjson(record)
        buf = io.StringIO(lines)
        
        with pytest.raises(ValueError, match="invalid cose_sign1_b64u"):
            list(iter_bundle(buf))


class TestCoseGuardrails:
    """Tests for COSE guardrail invocation."""

    def test_nonempty_unprotected_rejected(self):
        """COSE with non-empty unprotected header fails verification."""
        from cbor2 import CBORTag
        from ilc_core.crypto.cose_sign1 import COSE_TAG_SIGN1, COSE_ALG_EDDSA, COSE_HDR_ALG
        
        payload_obj = {"test": "data"}
        payload = encode_dag_cbor(payload_obj)
        node_id = node_id_from_obj(payload_obj)
        
        # Build COSE with non-empty unprotected
        protected = cbor_dumps_canonical({COSE_HDR_ALG: COSE_ALG_EDDSA})
        unprotected = {99: b"extra"}  # Non-empty!
        cose_array = [protected, unprotected, payload, b"\x00" * 64]
        bad_cose = cbor_dumps_canonical(CBORTag(COSE_TAG_SIGN1, cose_array))
        
        record = make_bundle_record(seq=1, node_id=node_id, cose_bytes=bad_cose)
        
        with pytest.raises(ValueError, match="unprotected"):
            verify_bundle_record(record, public_key=TEST_PUBLIC_KEY)

    def test_non_canonical_cose_rejected(self):
        """Non-canonical COSE bytes fail verification."""
        payload_obj = {"test": "data"}
        record, cose_bytes = make_signed_record(payload_obj, seq=1)
        
        # Make non-canonical by appending trailing bytes
        bad_cose = cose_bytes + b"\x00"
        record["cose_sign1_b64u"] = b64u_encode(bad_cose)
        
        with pytest.raises(ValueError, match="[Nn]on-canonical|Invalid"):
            verify_bundle_record(record, public_key=TEST_PUBLIC_KEY)


class TestRequireFooter:
    """Tests for require_footer option."""

    def test_require_footer_when_missing(self):
        """require_footer=True fails when footer absent."""
        header = make_bundle_header()
        record, _ = make_signed_record({"a": 1}, seq=1)
        
        lines = dumps_ndjson(header) + dumps_ndjson(record)
        buf = io.StringIO(lines)
        
        with pytest.raises(ValueError, match="footer required"):
            list(iter_bundle(buf, require_footer=True))
