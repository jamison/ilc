from __future__ import annotations

from dataclasses import dataclass
from statistics import median
from typing import Dict, List, Optional


@dataclass
class BacklogMetrics:
    """
    Local congestion metrics for a shard / cluster.

    This is intentionally minimal; richer versions can add:
    - auditor scarcity
    - refute rate
    - hotspot volatility
    """
    backlog_len: int               # number of pending tasks/claims
    finalized_last_epoch: int      # number of tasks finalized last epoch


class Governance:
    """
    ECU-anchored, congestion-aware governance surface for fees.

    Design goals
    ------------
    - Price work in ECU (epistemic contribution units), not directly in ILC.
    - Use congestion as *graph-local backlog pressure*, not block fullness.
    - Adjust for hardware capability via median benchmark potential.
    - Keep a tiny, explicit state that can later live on-chain or in a config
      registry without needing to track the full graph.

    Units
    -----
    All fee values returned here are in *ECU*, not ILC.
    Conversion ECU -> ILC should be handled by the epoch reward/issuance engine
    using the clearing price:

        P_e = B_e / max(epsilon, S_e)   (ILC per ECU)

    as described in the monetary design. This keeps fee logic decoupled from
    external token price movements.
    """

    def __init__(
        self,
        config: Optional[Dict] = None,
    ) -> None:
        cfg = config or {}

        # --- ECU base costs per task type -------------------------------
        ecu_cfg = cfg.get("ecu", {})
        # In the MVP config, ECU is currently defined as weights for reuse /
        # contra / refine. Here we allow explicit base ECU per task_type but
        # fall back to simple defaults if not provided.
        self.ecu_base_costs: Dict[str, float] = ecu_cfg.get("base_costs", {}) or {
            # Sensible MVP defaults; can be tuned via governance:
            "claim.submit": 0.05,
            "audit.panel": 0.02,
            "refute.attempt": 0.03,
            "contradiction.sweep": 0.10,
            "graph.compression": 0.04,
            "star.map.embedding": 0.02,
        }

        # --- Backlog / hotspot pricing parameters -----------------------
        backlog_cfg = cfg.get("backlog_hotspot_pricing", {}) or {}
        # Enable/disable congestion pricing at this layer.
        self.backlog_enabled: bool = bool(backlog_cfg.get("enabled", True))

        # How strongly backlog length increases price (per unit of normalized
        # backlog). This is a soft gain, not a hard cap.
        self.backlog_gain: float = float(backlog_cfg.get("backlog_gain", 0.05))

        # How strongly recent volume volatility affects price. Kept, but for
        # the MVP we treat this as a mild secondary factor.
        self.vol_price_gain: float = float(backlog_cfg.get("vol_price_gain", 0.2))

        # Maximum congestion multiplier (e.g. 1.5 = at most +50% over base).
        self.price_max: float = float(backlog_cfg.get("price_max", 1.5))

        # How quickly congestion decays per finalized task.
        self.decay_per_finalized: float = float(backlog_cfg.get("decay_per_finalized", 0.5))

        # --- Hardware capability baseline -------------------------------
        # "Genesis" median benchmark potential. This anchors the hardware
        # scaling factor. If the network becomes 10x faster, we *reduce* the
        # ECU-per-task baseline so that real-world cost stays roughly stable.
        self.genesis_median_potential: float = 0.1
        self.current_median_potential: float = 0.1

        # --- Internal state for congestion ------------------------------
        # We keep a smoothed congestion score per epoch.
        self._congestion_score: float = 0.0
        # Simple EMA smoothing factor for congestion.
        self._congestion_alpha: float = 0.5

    # ------------------------------------------------------------------
    # Hardware / benchmark updates
    # ------------------------------------------------------------------
    def update_hardware_potential(self, agent_potentials: List[float]) -> None:
        """
        Update the global median hardware potential from benchmark results.

        Parameters
        ----------
        agent_potentials : List[float]
            A list of benchmark scores (e.g., tokens/sec, FLOPs/sec
            normalized, or a composite "potential" metric) reported by agents.

        Behavior
        --------
        - If the median potential increases, we *lower* raw ECU base costs via
          a scaling factor, so that better hardware makes work cheaper in ECU.
        - We do NOT directly observe ILC price here.
        """
        if not agent_potentials:
            return

        m = median(agent_potentials)
        # Guard against pathological zeros.
        if m <= 0:
            return

        self.current_median_potential = float(m)

    @property
    def hardware_scale(self) -> float:
        """
        Returns a scaling factor in [0.25, 4.0] that adjusts ECU base cost
        downward when hardware improves.

        If the network becomes 4x faster (median_potential 4x genesis),
        hardware_scale will be ~1/4, making base ECU per task cheaper.
        """
        ratio = self.current_median_potential / max(1e-9, self.genesis_median_potential)
        # Invert: faster hardware -> smaller ECU cost.
        inv = 1.0 / max(ratio, 1e-9)
        # Clamp to avoid wild swings.
        return max(0.25, min(inv, 4.0))

    # ------------------------------------------------------------------
    # Backlog / congestion updates
    # ------------------------------------------------------------------
    def update_congestion(self, metrics: BacklogMetrics) -> None:
        """
        Update congestion score based on backlog and finalized work.

        This is a deliberately simple MVP function that can be replaced by a
        richer hotspot model later.

        Intuition
        ---------
        - Longer backlog => higher congestion.
        - More tasks finalized => reduces congestion.
        """
        backlog_term = float(metrics.backlog_len)
        relief_term = float(metrics.finalized_last_epoch) * self.decay_per_finalized

        raw_score = max(0.0, backlog_term - relief_term)

        # EMA smoothing.
        self._congestion_score = (
            self._congestion_alpha * raw_score
            + (1.0 - self._congestion_alpha) * self._congestion_score
        )

    @property
    def congestion_multiplier(self) -> float:
        """
        Convert internal congestion score into a multiplicative price factor.

        We normalize the congestion score by an implicit "target backlog" of 1,
        so score ~1 means mildly congested; score ~10 means heavily congested.

        The factor is:
            1 + backlog_gain * min(score, cap)
        capped at price_max.
        """
        score = self._congestion_score
        # Soft normalization: treat score directly, but cap it.
        normalized = min(score, 10.0)
        raw_factor = 1.0 + self.backlog_gain * normalized
        # Final cap.
        return max(1.0, min(raw_factor, self.price_max))

    # ------------------------------------------------------------------
    # Fee computation
    # ------------------------------------------------------------------
    def get_task_fee_ecu(self, task_type: str) -> float:
        """
        Return the current ECU fee for a given task type, including
        hardware scaling and congestion.

        Parameters
        ----------
        task_type : str
            Logical task type key, e.g.:
            - "claim.submit"
            - "audit.panel"
            - "refute.attempt"
            - "contradiction.sweep"
            - "graph.compression"
            - "star.map.embedding"

        Returns
        -------
        float
            Fee in ECU units.
        """
        base = float(self.ecu_base_costs.get(task_type, 0.01))

        # Apply hardware scaling: faster hardware => smaller base.
        scaled = base * self.hardware_scale

        # Apply congestion multiplier if enabled.
        if self.backlog_enabled:
            scaled *= self.congestion_multiplier

        # Round to a stable number of decimals for on-chain friendliness.
        return round(scaled, 8)
