from __future__ import annotations

import collections
import io
from pathlib import Path

import pytest

from ilc_core.encoding.cidv1 import node_id_from_obj
from ilc_core.network.d2d import gossip_transport
from ilc_core.network.d2d.truth_primitive_fetch_runtime import FetchRateLimiter
from ilc_core.protocol.ndjson_bundle import (
    make_bundle_header,
    make_bundle_record,
    read_bundle,
    write_bundle,
)


ROOT = Path(__file__).resolve().parents[1]
SPEC_DOC = ROOT / "docs/specs/ilc_phase_1331_fix3_network_dos_hardening_v0.1.md"
WALKTHROUGH_DOC = ROOT / "docs/phases/phase_1331_fix3_network_dos_hardening_walkthrough.md"
STATUS_DOC = ROOT / "docs/phases/STATUS.md"
PLANNING_INDEX = ROOT / "docs/PLANNING_INDEX.md"

REQUIRED_TOKENS = (
    "phase_1331_fix3_network_dos_hardening.v0.1",
    "fetch_rate_limiter_bucket_cap_phase_1331_fix3",
    "http_gossip_chunked_transfer_rejected_phase_1331_fix3",
    "ndjson_read_bundle_materialization_cap_phase_1331_fix3",
    "gossip_type_header_length_bound_phase_1331_fix3",
    "phase_1332_final_deterministic_code_security_audit_still_next_after_fix3",
    "public_rc_remains_blocked_after_phase_1331_fix3",
)


def test_fetch_rate_limiter_uses_bounded_ordered_buckets() -> None:
    limiter = FetchRateLimiter(limit_per_minute=1, max_buckets=2)
    assert isinstance(limiter._buckets, collections.OrderedDict)
    assert limiter.check_and_consume("agent-a") is True
    assert limiter.check_and_consume("agent-b") is True
    assert limiter.check_and_consume("agent-c") is True
    assert list(limiter._buckets) == ["agent-b", "agent-c"]


def test_ndjson_read_bundle_materialization_cap_is_separate_from_streaming_cap() -> None:
    records = [
        make_bundle_record(seq=1, node_id=node_id_from_obj({"record": 1}), cose_bytes=b"a"),
        make_bundle_record(seq=2, node_id=node_id_from_obj({"record": 2}), cose_bytes=b"b"),
    ]
    buf = io.StringIO()
    write_bundle(buf, header=make_bundle_header(), records=records)
    buf.seek(0)

    with pytest.raises(ValueError, match="max_materialized_records"):
        read_bundle(buf, max_records=10, max_materialized_records=1)


def test_gossip_type_length_bound_applies_to_path_builder_and_headers() -> None:
    oversized = "g" * (gossip_transport.MAX_GOSSIP_TYPE_BYTES + 1)
    with pytest.raises(ValueError, match="gossip_message_type_too_long"):
        gossip_transport.gossip_request_path(oversized)

    headers = gossip_transport.build_gossip_headers(
        gossip_type="centrality_delta",
        channel="cid:9f7a8c42bb11ddee99aa22cc33ff44aa",
        epoch=7,
        hop_count=1,
        signature="sig-abc",
    )
    headers["ILC-Gossip-Type"] = oversized
    with pytest.raises(ValueError, match="gossip_message_type_too_long"):
        gossip_transport.validate_gossip_headers(headers)


@pytest.mark.parametrize(
    "path",
    (SPEC_DOC, WALKTHROUGH_DOC, STATUS_DOC, PLANNING_INDEX),
)
def test_phase_1331_fix3_tokens_are_recorded(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    for token in REQUIRED_TOKENS:
        assert token in text
