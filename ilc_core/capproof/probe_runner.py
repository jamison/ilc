# SPDX-License-Identifier: AGPL-3.0-only
"""Deterministic epoch-salted CapProof v1 probe stubs."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from decimal import Decimal

from .capability_vector import CapProofValidationError

CAPPROOF_V1_NO_ILC_MINT = True
CAPPROOF_RUNTIME_VERSION = "capproof_v1_phase_1606.v0.1"

_EPOCH_SALT_RE = re.compile(r"^[0-9a-f]{64,128}$")


@dataclass(frozen=True)
class GEMMProbeResult:
    gemm_gops: Decimal
    reference_hash_matched: bool
    epoch_salt: str


@dataclass(frozen=True)
class InferProbeResult:
    infer_tps: Decimal
    logits_consensus_matched: bool
    epoch_salt: str


@dataclass(frozen=True)
class GraphProbeResult:
    graph_mteps: Decimal
    posk_commitment: str | None
    epoch_salt: str


@dataclass(frozen=True)
class BandwidthProbeResult:
    bw_gbps: Decimal
    epoch_salt: str


@dataclass(frozen=True)
class DeterminismProbeResult:
    det_pass: bool
    determinism_hash: str
    epoch_salt: str


class GEMMProbe:
    field_name = "gemm_gops"

    def run(self, epoch_salt: str) -> GEMMProbeResult:
        salt = _require_epoch_salt(epoch_salt)
        return GEMMProbeResult(
            gemm_gops=_derive_metric(salt, "gemm", Decimal("100000"), Decimal("1000")),
            reference_hash_matched=True,
            epoch_salt=salt,
        )


class InferProbe:
    field_name = "infer_tps"

    def run(self, epoch_salt: str) -> InferProbeResult:
        salt = _require_epoch_salt(epoch_salt)
        return InferProbeResult(
            infer_tps=_derive_metric(salt, "infer", Decimal("10000"), Decimal("100")),
            logits_consensus_matched=True,
            epoch_salt=salt,
        )


class GraphProbe:
    field_name = "graph_mteps"

    def run(self, epoch_salt: str) -> GraphProbeResult:
        salt = _require_epoch_salt(epoch_salt)
        return GraphProbeResult(
            graph_mteps=_derive_metric(salt, "graph", Decimal("10000"), Decimal("100")),
            posk_commitment=None,
            epoch_salt=salt,
        )


class BandwidthProbe:
    field_name = "bw_gbps"

    def run(self, epoch_salt: str) -> BandwidthProbeResult:
        salt = _require_epoch_salt(epoch_salt)
        return BandwidthProbeResult(
            bw_gbps=_derive_metric(salt, "bandwidth", Decimal("1000"), Decimal("10")),
            epoch_salt=salt,
        )


class DeterminismProbe:
    field_name = "det_pass"

    def run(self, epoch_salt: str) -> DeterminismProbeResult:
        salt = _require_epoch_salt(epoch_salt)
        digest = hashlib.sha256(
            f"ILC_CAPPROOF_DETERMINISM_V1:{salt}".encode("utf-8")
        ).hexdigest()
        return DeterminismProbeResult(
            det_pass=True,
            determinism_hash=digest,
            epoch_salt=salt,
        )


def _require_epoch_salt(epoch_salt: str) -> str:
    if not isinstance(epoch_salt, str):
        raise CapProofValidationError(
            "capproof_epoch_salt_must_be_string",
            "epoch_salt must be a lowercase hex string",
        )
    if epoch_salt != epoch_salt.strip() or epoch_salt != epoch_salt.lower():
        raise CapProofValidationError(
            "capproof_epoch_salt_must_be_lower_hex",
            "epoch_salt must be lowercase hex without surrounding whitespace",
        )
    if _EPOCH_SALT_RE.fullmatch(epoch_salt) is None:
        raise CapProofValidationError(
            "capproof_epoch_salt_must_be_64_to_128_lower_hex",
            "epoch_salt must be 64 to 128 lowercase hex characters",
        )
    return epoch_salt


def _derive_metric(epoch_salt: str, domain: str, scale: Decimal, quantum: Decimal) -> Decimal:
    digest = hashlib.sha256(
        f"ILC_CAPPROOF_PROBE_V1:{domain}:{epoch_salt}".encode("utf-8")
    ).hexdigest()
    raw = Decimal(int(digest[:16], 16) % 1000000)
    return (raw / quantum) + scale
