# ADR-0029: Spectral utility functions for hypergraph analytics.
#
# spectral_distance() is the routing metric used by spectral routing (SIM-ROUTING-01).
# It is defined here so it is always available as a primitive once the hyperedge
# substrate is in place, without waiting for the full beacon/routing implementation.
#
# compute_weight() is the deterministic weight function for HyperEdge.weight_params.
# w(e, t) = α(edge_type) × f(reuse_count) × decay(stake, epoch_created, t)
# PROVISIONAL: reuse_count functional form is log(n+1) pending SIM-REUSE-01 validation.
# CDL required before any of these parameters are constitutionally locked.
#
# Gate for full spectral pipeline: SIM-HYPEREDGE-01 -> SIM-SPECTRAL-01 -> CDL.
# Gate for spectral beacon emission: SIM-BEACON-01 (noise budget calibration).
# Gate for spectral routing: SIM-ROUTING-01 (convergence validation).
# Gate for weight parameterization: SIM-REUSE-01 + CDL (EdgeType coefficients).
from __future__ import annotations

import hashlib
import math
import os
import struct
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from ilc_core.types import WeightParams


SPECTRAL_HASH_V02_Q: int = 1_000_000
INT64_MIN: int = -(2**63)
INT64_MAX: int = 2**63 - 1


def spectral_distance(fingerprint_a: List[float], fingerprint_b: List[float]) -> float:
    """
    L2 distance between two spectral fingerprint vectors.

    ||lambda_A - lambda_B||_2

    This is the routing metric for greedy spectral descent: a hop toward the peer
    whose fingerprint minimises this distance moves toward the target epistemic
    neighbourhood. Vectors must be the same length; shorter vector is zero-padded.
    """
    len_a, len_b = len(fingerprint_a), len(fingerprint_b)
    if len_a < len_b:
        fingerprint_a = fingerprint_a + [0.0] * (len_b - len_a)
    elif len_b < len_a:
        fingerprint_b = fingerprint_b + [0.0] * (len_a - len_b)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(fingerprint_a, fingerprint_b)))


def compute_weight(
    params: "WeightParams",
    current_epoch: int,
    cdl_v1_decay_fn: Optional[Callable[[float, int], float]] = None,
) -> float:
    """Compute edge weight deterministically from WeightParams.

    w(e, t) = α(edge_type) × f(reuse_count) × decay(stake, t)

    Where:
      α(edge_type)   = params.edge_type_coefficient  (CDL-ratified per type)
      f(reuse_count) = log(reuse_count + 1)          (PROVISIONAL: SIM-REUSE-01 pending)
      decay(stake,t) = cdl_v1_decay_fn(float(stake), current_epoch) if supplied,
                       else float(stake) (no decay — for tests and analytics)

    IMPORTANT: The reuse_count functional form (log vs. linear vs. capped) and
    the edge_type_coefficient values are UNRATIFIED. SIM-REUSE-01 must validate
    stability and gaming resistance before any CDL locks these values.
    Do not use this output in any consensus-critical path until CDL ratified.

    Pure function — no side effects, no I/O, deterministic.
    """
    base_stake = float(params.stake)
    decayed_stake = (
        cdl_v1_decay_fn(base_stake, current_epoch)
        if cdl_v1_decay_fn is not None
        else base_stake
    )
    # Provisional reuse signal: log(n+1) so zero reuse → 0 additive, not multiplicative zero
    reuse_signal = math.log(params.reuse_count + 1)
    return params.edge_type_coefficient * decayed_stake * (1.0 + reuse_signal)


def quantize_spectral_eigenvalues_fixed_point(
    eigenvalues: List[float],
    *,
    q: int = SPECTRAL_HASH_V02_Q,
    k: Optional[int] = None,
) -> List[int]:
    """Return sorted fixed-point int64 eigenvalue encodings for v0.2 S(t).

    Merkle-Laplacian v0.2 commits to the smallest-k eigenvalue sequence after
    deterministic fixed-point quantization:

        mu_i = round(lambda_i * q)

    The returned integers are intended to be serialized as signed int64
    little-endian bytes before hashing. This helper is research/pre-CDL only;
    q must be ratified before any consensus commitment uses it.
    """
    if q <= 0:
        raise ValueError("spectral_hash_q_must_be_positive")

    sorted_values = sorted(float(value) for value in eigenvalues)
    if k is not None:
        if k <= 0:
            raise ValueError("spectral_hash_k_must_be_positive")
        sorted_values = sorted_values[:k]

    encoded: List[int] = []
    for value in sorted_values:
        if not math.isfinite(value):
            raise ValueError("spectral_hash_eigenvalue_non_finite")
        mu = int(round(value * q))
        if mu < INT64_MIN or mu > INT64_MAX:
            raise ValueError("spectral_hash_eigenvalue_int64_overflow")
        encoded.append(mu)
    return encoded


def spectral_hash_fixed_point_int64_le(
    eigenvalues: List[float],
    *,
    q: int = SPECTRAL_HASH_V02_Q,
    k: Optional[int] = None,
) -> str:
    """SHA-256 over v0.2 fixed-point int64 little-endian eigenvalue bytes.

    This is the Merkle-Laplacian v0.2 candidate encoding for S(t). It differs
    intentionally from the legacy spectral_hash() helper below, which remains
    available only for older beacon/routing tests that used IEEE double bytes.
    """
    encoded = quantize_spectral_eigenvalues_fixed_point(eigenvalues, q=q, k=k)
    packed = b"".join(value.to_bytes(8, "little", signed=True) for value in encoded)
    return hashlib.sha256(packed).hexdigest()


def spectral_hash(eigenvalues: List[float]) -> str:
    """Legacy SHA-256 over sorted eigenvalues.

    This helper is retained for H-013/H-015 beacon/routing compatibility. It is
    no longer the Merkle-Laplacian v0.2 epoch-commitment candidate because raw
    floating-point byte hashing is not reproducible enough for S(t).

    Use spectral_hash_fixed_point_int64_le() for v0.2 research vectors.
    """
    sorted_vals = sorted(float(value) for value in eigenvalues)
    for value in sorted_vals:
        if not math.isfinite(value):
            raise ValueError("spectral_hash_eigenvalue_non_finite")
    packed = b"".join(struct.pack(">d", value) for value in sorted_vals)
    return hashlib.sha256(packed).hexdigest()


def _csprng_gauss() -> float:
    """One standard-normal sample via Box-Muller transform over os.urandom.

    Uses os.urandom (CSPRNG) instead of random.gauss (PRNG). This is required
    by ILC coding security standards: no PRNG for cryptographic or noise
    generation in spectral beacon emission.

    Box-Muller: if U1, U2 ~ Uniform(0,1) then
        Z = sqrt(-2 ln U1) * cos(2π U2) ~ Normal(0,1)
    """
    # Draw two 64-bit uniform samples from os.urandom
    u1_raw = int.from_bytes(os.urandom(8), "big") / (2 ** 64)
    u2_raw = int.from_bytes(os.urandom(8), "big") / (2 ** 64)
    # Clamp away from 0 to avoid log(0); upper bound is fine (cos handles 2π)
    u1 = max(u1_raw, 1e-15)
    return math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2_raw)


def add_noise(eigenvalues: List[float], sigma: float) -> List[float]:
    """Add calibrated Gaussian noise to a spectral fingerprint before beacon emission.

    sigma is the noise standard deviation (differential privacy budget parameter).
    Calibrate sigma via SIM-BEACON-01 before production use.
    The H-013 spectral_beacon.py enforces MIN_NOISE_SIGMA=0.005 at the
    construction boundary — this function does not re-check the floor.

    Uses CSPRNG (os.urandom via Box-Muller), never random.gauss. This is a
    security requirement: noise for beacon privacy must not be predictable.
    """
    return [v + sigma * _csprng_gauss() for v in eigenvalues]
