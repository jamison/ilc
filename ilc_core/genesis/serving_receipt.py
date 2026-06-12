# SPDX-License-Identifier: AGPL-3.0-only
"""Phase 1559 — HB-002 minimal known-peer serving receipts.

PUBLIC_RC_EXCLUDE: private_hb002_serving_receipt
PUBLIC_RC_EXCLUDE_REASON: Private pre-RC known-peer serving receipt surface. Does not activate public P2P discovery or public bundle serving.
"""

from __future__ import annotations

import hashlib
import json
import os
import ssl
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

from ilc_core.encoding.cidv1 import parse_nodeid_strict

from ilc_core.private_json_guardrails import (
    canonical_json,
    freeze_json_value,
    reject_float,
    require_sha256_hex,
    thaw_json_value,
)

SERVING_RECEIPT_SCHEMA_VERSION = "serving_receipt_1559.v0.1"
SERVING_RULE_VERSION = "hb002_known_peer_serving_rule_1559.v0.1"
GENESIS_SERVING_AGENT_ID = "genesis_agent:01"
SERVING_REQUEST_PATH = "/ilc/genesis/serve"
VERIFY_REQUEST_PATH = "/ilc/genesis/verify"
SERVING_HTTP_TIMEOUT_SECONDS = 30
MAX_SERVING_RESPONSE_BYTES = 1_048_576


class ServingReceiptError(ValueError):
    """Stable exception type for Phase 1559 serving receipt validation."""


@dataclass(frozen=True)
class ServingReceipt:
    serving_receipt_id: str
    serving_agent_id: str
    served_layer: str
    layer0_protocol_bundle_sha256: str
    serving_epoch: int
    serving_rule_version: str
    layer1_genesis_bundle_sha256: str = ""
    layer2_epoch_snapshot_sha256: str = ""
    layer3_wire_binding_sha256: str = ""
    layer0_protocol_bundle_cidv1: str = ""
    served_peer_url: str = ""
    co_attestation_receipt_ref: str = ""
    consent_decision_ref: str = ""
    canonical_json: str = ""

    def to_dict(self) -> dict[str, object]:
        return {
            "canonical_json": self.canonical_json,
            "co_attestation_receipt_ref": self.co_attestation_receipt_ref,
            "consent_decision_ref": self.consent_decision_ref,
            "layer0_protocol_bundle_cidv1": self.layer0_protocol_bundle_cidv1,
            "layer0_protocol_bundle_sha256": self.layer0_protocol_bundle_sha256,
            "layer1_genesis_bundle_sha256": self.layer1_genesis_bundle_sha256,
            "layer2_epoch_snapshot_sha256": self.layer2_epoch_snapshot_sha256,
            "layer3_wire_binding_sha256": self.layer3_wire_binding_sha256,
            "served_layer": self.served_layer,
            "served_peer_url": self.served_peer_url,
            "serving_agent_id": self.serving_agent_id,
            "serving_epoch": self.serving_epoch,
            "serving_receipt_id": self.serving_receipt_id,
            "serving_rule_version": self.serving_rule_version,
        }


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        _req: urllib.request.Request,
        _fp: object,
        _code: int,
        _msg: str,
        _headers: object,
        _newurl: str,
    ) -> None:
        raise urllib.error.HTTPError(_req.full_url, _code, "redirects_not_allowed", {}, None)


def build_serving_receipt(
    serving_agent_id: str,
    served_layer: str,
    *,
    layer0_protocol_bundle_sha256: str,
    serving_epoch: int,
    serving_rule_version: str = SERVING_RULE_VERSION,
    layer1_genesis_bundle_sha256: str = "",
    layer2_epoch_snapshot_sha256: str = "",
    layer3_wire_binding_sha256: str = "",
    layer0_protocol_bundle_cidv1: str = "",
    served_peer_url: str = "",
    co_attestation_receipt_ref: str = "",
    consent_decision_ref: str = "",
) -> ServingReceipt:
    payload = _receipt_payload(
        serving_agent_id=serving_agent_id,
        served_layer=served_layer,
        layer0_protocol_bundle_sha256=layer0_protocol_bundle_sha256,
        serving_epoch=serving_epoch,
        serving_rule_version=serving_rule_version,
        layer1_genesis_bundle_sha256=layer1_genesis_bundle_sha256,
        layer2_epoch_snapshot_sha256=layer2_epoch_snapshot_sha256,
        layer3_wire_binding_sha256=layer3_wire_binding_sha256,
        layer0_protocol_bundle_cidv1=layer0_protocol_bundle_cidv1,
        served_peer_url=served_peer_url,
        co_attestation_receipt_ref=co_attestation_receipt_ref,
        consent_decision_ref=consent_decision_ref,
    )
    body = canonical_json(payload, float_token="serving_receipt_float_not_allowed")
    receipt_id = "serving_receipt:" + hashlib.sha256(body.encode("utf-8")).hexdigest()
    return ServingReceipt(
        serving_receipt_id=receipt_id,
        serving_agent_id=serving_agent_id,
        served_layer=served_layer,
        layer0_protocol_bundle_sha256=layer0_protocol_bundle_sha256,
        layer1_genesis_bundle_sha256=layer1_genesis_bundle_sha256,
        layer2_epoch_snapshot_sha256=layer2_epoch_snapshot_sha256,
        layer3_wire_binding_sha256=layer3_wire_binding_sha256,
        layer0_protocol_bundle_cidv1=layer0_protocol_bundle_cidv1,
        serving_epoch=serving_epoch,
        serving_rule_version=serving_rule_version,
        served_peer_url=served_peer_url,
        co_attestation_receipt_ref=co_attestation_receipt_ref,
        consent_decision_ref=consent_decision_ref,
        canonical_json=body,
    )


def write_serving_receipt_json(receipt: ServingReceipt, path: str | Path) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    body = canonical_json(receipt.to_dict(), float_token="serving_receipt_float_not_allowed")
    fd, tmp_name = tempfile.mkstemp(
        dir=target.parent,
        prefix=f".{target.name}.",
        suffix=".tmp",
        text=True,
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(body)
            handle.write("\n")
        os.replace(tmp_path, target)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def serve_genesis_bundle(
    peer_tailscale_url: str,
    layer0: object,
    layer1: object | None = None,
    *,
    ca_file: str | Path | None = None,
) -> ServingReceipt:
    """Send Layer 0/1 bundle material to a known private peer.

    This function is implemented in Phase 1559 but first used against live
    Tailscale peers in Phase 1560. Tests must mock the outbound HTTP opener.
    """

    endpoint = _known_private_peer_endpoint(peer_tailscale_url)
    layer0_sha256 = _required_attr(layer0, "sha256")
    layer0_cidv1 = _optional_attr(layer0, "cidv1")
    layer1_sha256 = _optional_attr(layer1, "sha256") if layer1 is not None else ""
    receipt = build_serving_receipt(
        GENESIS_SERVING_AGENT_ID,
        "layer0+layer1" if layer1 is not None else "layer0",
        layer0_protocol_bundle_sha256=layer0_sha256,
        layer1_genesis_bundle_sha256=layer1_sha256,
        layer0_protocol_bundle_cidv1=layer0_cidv1,
        serving_epoch=0,
        served_peer_url=endpoint,
    )
    request_payload = {
        "layer0": _bundle_wire_payload(layer0),
        "layer1": _bundle_wire_payload(layer1) if layer1 is not None else None,
        "receipt": receipt.to_dict(),
        "schema_version": SERVING_RECEIPT_SCHEMA_VERSION,
    }
    response = _post_json(endpoint + SERVING_REQUEST_PATH, request_payload, ca_file=ca_file)
    if response and response.get("accepted") is False:
        raise ServingReceiptError("serving_receipt_peer_rejected_bundle")
    return receipt


def verify_received_bundle(
    peer_tailscale_url: str,
    expected_layer0_cid: str,
    *,
    ca_file: str | Path | None = None,
) -> bool:
    endpoint = _known_private_peer_endpoint(peer_tailscale_url)
    _require_cidv1(expected_layer0_cid, "serving_receipt_invalid_expected_layer0_cid")
    response = _post_json(
        endpoint + VERIFY_REQUEST_PATH,
        {
            "expected_layer0_cidv1": expected_layer0_cid,
            "schema_version": SERVING_RECEIPT_SCHEMA_VERSION,
        },
        ca_file=ca_file,
    )
    if not isinstance(response, dict):
        return False
    observed = response.get("layer0_cidv1", response.get("expected_layer0_cidv1", ""))
    return (
        response.get("verified") is True
        and isinstance(observed, str)
        and observed == expected_layer0_cid
    )


def _receipt_payload(
    *,
    serving_agent_id: str,
    served_layer: str,
    layer0_protocol_bundle_sha256: str,
    serving_epoch: int,
    serving_rule_version: str,
    layer1_genesis_bundle_sha256: str,
    layer2_epoch_snapshot_sha256: str,
    layer3_wire_binding_sha256: str,
    layer0_protocol_bundle_cidv1: str,
    served_peer_url: str,
    co_attestation_receipt_ref: str,
    consent_decision_ref: str,
) -> dict[str, object]:
    payload = {
        "co_attestation_receipt_ref": co_attestation_receipt_ref,
        "consent_decision_ref": consent_decision_ref,
        "layer0_protocol_bundle_cidv1": layer0_protocol_bundle_cidv1,
        "layer0_protocol_bundle_sha256": layer0_protocol_bundle_sha256,
        "layer1_genesis_bundle_sha256": layer1_genesis_bundle_sha256,
        "layer2_epoch_snapshot_sha256": layer2_epoch_snapshot_sha256,
        "layer3_wire_binding_sha256": layer3_wire_binding_sha256,
        "served_layer": served_layer,
        "served_peer_url": served_peer_url,
        "serving_agent_id": serving_agent_id,
        "serving_epoch": serving_epoch,
        "serving_rule_version": serving_rule_version,
    }
    try:
        reject_float(payload, "serving_receipt_float_not_allowed")
    except ValueError as exc:
        raise ServingReceiptError(str(exc)) from exc
    _require_non_empty_str(serving_agent_id, "serving_receipt_missing_serving_agent_id")
    _require_non_empty_str(served_layer, "serving_receipt_missing_served_layer")
    _require_non_empty_str(serving_rule_version, "serving_receipt_missing_rule_version")
    _require_protocol_epoch(serving_epoch)
    require_sha256_hex(
        layer0_protocol_bundle_sha256,
        "serving_receipt_invalid_layer0_sha256",
    )
    for value, token in (
        (layer1_genesis_bundle_sha256, "serving_receipt_invalid_layer1_sha256"),
        (layer2_epoch_snapshot_sha256, "serving_receipt_invalid_layer2_sha256"),
        (layer3_wire_binding_sha256, "serving_receipt_invalid_layer3_sha256"),
    ):
        if value != "":
            require_sha256_hex(value, token)
    if layer0_protocol_bundle_cidv1 != "":
        _require_cidv1(layer0_protocol_bundle_cidv1, "serving_receipt_invalid_layer0_cidv1")
    if served_peer_url != "":
        _known_private_peer_endpoint(served_peer_url)
    return payload


def _post_json(
    url: str,
    payload: Mapping[str, object],
    *,
    ca_file: str | Path | None = None,
) -> dict[str, object]:
    body = canonical_json(payload, float_token="serving_receipt_float_not_allowed").encode(
        "utf-8"
    )
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    opener = urllib.request.build_opener(
        _NoRedirectHandler,
        urllib.request.HTTPSHandler(context=_client_ssl_context(ca_file=ca_file)),
    )
    try:
        with opener.open(request, timeout=SERVING_HTTP_TIMEOUT_SECONDS) as response:
            raw = _read_bounded_response(response)
    except urllib.error.HTTPError as exc:
        raise ServingReceiptError("serving_receipt_http_error") from exc
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        raise ServingReceiptError("serving_receipt_transport_error") from exc
    if raw == b"":
        return {}
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ServingReceiptError("serving_receipt_response_invalid_json") from exc
    if not isinstance(parsed, dict):
        raise ServingReceiptError("serving_receipt_response_not_object")
    try:
        reject_float(parsed, "serving_receipt_float_not_allowed")
    except ValueError as exc:
        raise ServingReceiptError(str(exc)) from exc
    normalized = freeze_json_value(parsed)
    return thaw_json_value(normalized)  # type: ignore[return-value]


def _client_ssl_context(*, ca_file: str | Path | None = None) -> ssl.SSLContext:
    if ca_file is None:
        return ssl.create_default_context()
    return ssl.create_default_context(cafile=str(ca_file))


def _read_bounded_response(response: object) -> bytes:
    reader = getattr(response, "read", None)
    if reader is None:
        raise ServingReceiptError("serving_receipt_response_missing_read")
    raw = reader(MAX_SERVING_RESPONSE_BYTES + 1)
    if not isinstance(raw, bytes):
        raise ServingReceiptError("serving_receipt_response_not_bytes")
    if len(raw) > MAX_SERVING_RESPONSE_BYTES:
        raise ServingReceiptError("serving_receipt_response_too_large")
    return raw


def _known_private_peer_endpoint(endpoint: str) -> str:
    # Deferred import to break the circular dependency:
    # gossip_transport → centrality_delta_gossip_runtime → epistemic → genesis
    # → serving_receipt → gossip_peer_registry → gossip_transport
    from ilc_core.network.d2d.gossip_peer_registry import validate_peer_endpoint  # noqa: PLC0415
    return validate_peer_endpoint(endpoint, allow_private_address_literals=True)


def _bundle_wire_payload(bundle: object) -> dict[str, object]:
    return {
        "canonical_json": _optional_attr(bundle, "canonical_json"),
        "cidv1": _optional_attr(bundle, "cidv1"),
        "sha256": _required_attr(bundle, "sha256"),
    }


def _required_attr(value: object, name: str) -> str:
    attr = _optional_attr(value, name)
    _require_non_empty_str(attr, f"serving_receipt_missing_{name}")
    return attr


def _optional_attr(value: object, name: str) -> str:
    attr = getattr(value, name, "")
    if not isinstance(attr, str):
        raise ServingReceiptError(f"serving_receipt_invalid_{name}")
    return attr


def _require_non_empty_str(value: str, token: str) -> None:
    if not isinstance(value, str) or value == "":
        raise ServingReceiptError(token)


def _require_protocol_epoch(value: int) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ServingReceiptError("serving_receipt_invalid_protocol_epoch")


def _require_cidv1(value: str, token: str) -> None:
    try:
        parse_nodeid_strict(value)
    except ValueError as exc:
        raise ServingReceiptError(token) from exc


__all__ = [
    "GENESIS_SERVING_AGENT_ID",
    "MAX_SERVING_RESPONSE_BYTES",
    "SERVING_HTTP_TIMEOUT_SECONDS",
    "SERVING_RECEIPT_SCHEMA_VERSION",
    "SERVING_RULE_VERSION",
    "ServingReceipt",
    "ServingReceiptError",
    "build_serving_receipt",
    "serve_genesis_bundle",
    "verify_received_bundle",
    "write_serving_receipt_json",
]
