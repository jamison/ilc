# ADR-0029: SpectralBeacon stub — sealed spectral fingerprint gossip message.
#
# A SpectralBeacon carries a privacy-noised local spectral fingerprint (top-k
# eigenvalues of the local Laplacian subgraph) over the D2d gossip layer with
# a sealed sender, enabling topology-guided discovery without revealing subgraph
# contents or agent identity to relay nodes.
#
# This stub defines the dataclass. Transmission is NOT implemented here.
# Transmission gates: SIM-BEACON-01 (noise budget epsilon calibration) must
# complete before any beacon emission is wired into gossip_transport.py.
# D2d sealed sender ADR (TBD) must also be accepted before the sealed: bool
# flag is added to the outbound gossip message.
#
# See: ADR-0029 §2, ilc_morphogenetic_hypergraph_planning_classification_v0.1.md §2.3
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class SpectralBeacon:
    """
    Sealed spectral fingerprint gossip message (stub — not yet transmitted).

    epoch:           validation epoch when the fingerprint was computed.
    lambda_local:    top-k eigenvalues of the local Laplacian subgraph.
                     Approx. neighbourhood shape; specific node IDs are NOT included.
    noise_sigma:     std-dev of Gaussian noise applied for differential privacy (ε-DP).
                     Calibrated value comes from SIM-BEACON-01; set to 0.0 until then.
    agent_id:        originating agent — concealed from relay nodes by sealed sender.
    """
    epoch: int
    lambda_local: List[float]
    noise_sigma: float
    agent_id: str
