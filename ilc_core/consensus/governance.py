# SPDX-License-Identifier: AGPL-3.0-only
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
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
        raw_base_costs = ecu_cfg.get("base_costs", {}) or {
            # Sensible MVP defaults; can be tuned via governance:
            "claim.submit": Decimal("0.05"),
            "audit.panel": Decimal("0.02"),
            "refute.attempt": Decimal("0.03"),
            "contradiction.sweep": Decimal("0.10"),
            "graph.compression": Decimal("0.04"),
            "star.map.embedding": Decimal("0.02"),
        }
        self.ecu_base_costs: Dict[str, Decimal] = {
            str(task_type): _to_decimal(cost, token="governance_ecu_base_cost_invalid")
            for task_type, cost in raw_base_costs.items()
        }

        # --- Backlog / hotspot pricing parameters -----------------------
        # MEDIUM-011 fix: all economic parameters stored as Decimal, not float.
        # Float intermediate arithmetic accumulates IEEE 754 drift before the
        # final Decimal conversion in fee computation; violates ILC §3 coding standard.
        backlog_cfg = cfg.get("backlog_hotspot_pricing", {}) or {}
        # Enable/disable congestion pricing at this layer.
        self.backlog_enabled: bool = bool(backlog_cfg.get("enabled", True))

        # How strongly backlog length increases price (per unit of normalized
        # backlog). This is a soft gain, not a hard cap.
        self.backlog_gain: Decimal = _to_decimal(
            backlog_cfg.get("backlog_gain", "0.05"), "governance_backlog_gain_invalid"
        )

        # How strongly recent volume volatility affects price.
        self.vol_price_gain: Decimal = _to_decimal(
            backlog_cfg.get("vol_price_gain", "0.2"), "governance_vol_price_gain_invalid"
        )

        # Maximum congestion multiplier (e.g. 1.5 = at most +50% over base).
        self.price_max: Decimal = _to_decimal(
            backlog_cfg.get("price_max", "1.5"), "governance_price_max_invalid"
        )

        # How quickly congestion decays per finalized task.
        self.decay_per_finalized: Decimal = _to_decimal(
            backlog_cfg.get("decay_per_finalized", "0.5"), "governance_decay_per_finalized_invalid"
        )

        # --- Hardware capability baseline -------------------------------
        hw_cfg = cfg.get("hardware", {})
        self.genesis_median_potential: Decimal = _to_decimal(
            hw_cfg.get("genesis_median_potential", "0.1"),
            "governance_genesis_median_potential_invalid",
        )
        self.current_median_potential: Decimal = self.genesis_median_potential

        # --- Internal state for congestion ------------------------------
        self._congestion_score: Decimal = Decimal("0")
        self._congestion_alpha: Decimal = Decimal("0.5")

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
            Callers must supply float values for potential here as this is an
            analysis surface; these values must NOT be used as direct ECU or
            settlement inputs without conversion to Decimal.

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

        self.current_median_potential = _to_decimal(str(m), "governance_median_potential_invalid")

    @property
    def hardware_scale(self) -> Decimal:
        """
        Returns a scaling factor in [0.25, 4.0] that adjusts ECU base cost
        downward when hardware improves.

        If the network becomes 4x faster (median_potential 4x genesis),
        hardware_scale will be ~1/4, making base ECU per task cheaper.
        """
        _epsilon = Decimal("1E-9")
        ratio = self.current_median_potential / max(_epsilon, self.genesis_median_potential)
        # Invert: faster hardware -> smaller ECU cost.
        inv = Decimal("1") / max(ratio, _epsilon)
        # Clamp to avoid wild swings.
        return max(Decimal("0.25"), min(inv, Decimal("4.0")))

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
        backlog_term = Decimal(metrics.backlog_len)
        relief_term = Decimal(metrics.finalized_last_epoch) * self.decay_per_finalized

        raw_score = max(Decimal("0"), backlog_term - relief_term)

        # EMA smoothing.
        self._congestion_score = (
            self._congestion_alpha * raw_score
            + (Decimal("1") - self._congestion_alpha) * self._congestion_score
        )

    @property
    def congestion_multiplier(self) -> Decimal:
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
        normalized = min(score, Decimal("10"))
        raw_factor = Decimal("1") + self.backlog_gain * normalized
        # Final cap.
        return max(Decimal("1"), min(raw_factor, self.price_max))

    # ------------------------------------------------------------------
    # Fee computation
    # ------------------------------------------------------------------
    def get_task_fee_ecu(self, task_type: str) -> Decimal:
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
        Decimal
            Fee in ECU units.
        """
        base = self.ecu_base_costs.get(task_type, Decimal("0.01"))

        # Apply hardware scaling: faster hardware => smaller base.
        # hardware_scale and congestion_multiplier now return Decimal directly.
        scaled = base * self.hardware_scale

        # Apply congestion multiplier if enabled.
        if self.backlog_enabled:
            scaled *= self.congestion_multiplier

        # Round to a stable number of decimals for on-chain friendliness.
        return scaled.quantize(Decimal("0.00000001"))


def _to_decimal(value: object, token: str) -> Decimal:
    if isinstance(value, bool):
        raise ValueError(token)
    if not isinstance(value, (Decimal, int, float, str)):
        raise ValueError(token)
    try:
        amount = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(token) from exc
    if not amount.is_finite():
        raise ValueError(f"{token}_non_finite")
    if amount < Decimal("0"):
        raise ValueError(f"{token}_negative")
    return amount
