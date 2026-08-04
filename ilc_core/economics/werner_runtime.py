"""
Werner Credit Pressure-Signal Runtime

Computes Werner credit as a dimensionless topology-pressure flow signal per
CDL-096 and CDL-053. This module is a FLOW GOVERNOR, not an ECU issuance path.

Werner credit is NOT ECU, NOT ILC, NOT claimable, NOT wallet-visible, and
NOT transferable. The output of this module is a dimensionless scalar that
represents topology-pressure priority for flow-governor policy decisions only.

CDL authority: CDL-096 (ratified Phase 1553p), CDL-053 (ratified Phase 1407_fix2)

Ratified constants (CDL-096 §2):
  topology_pressure_model = "werner_v1"
  heat_threshold = 100  (smoothed pressure >= 100 triggers heat signal)
  spectral_trust: K=2, N=3, beta_floor=0.5, pulse_floor=0.5
  candidate_priority = smoothed_pressure * beta_signal
  flow_budget = min(runtime_policy_cap, candidate_priority)
  output_unit = dimensionless (not ECU, not ILC)

GAP-WERNER-02b cleared the guard only for CDL-109 bounded reweighting of
CDL-108 backward attribution raw path scores. This module still exposes no
amount-producing or balance-mutating API.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation, localcontext
from typing import Mapping, Sequence

# ---------------------------------------------------------------------------
# Production activation guard
# Cleared by GAP-WERNER-02b for CDL-109 bounded bridge scope only.
# ---------------------------------------------------------------------------
WERNER_CREDIT_WIRING_NOT_ACTIVATED = False

WERNER_RUNTIME_VERSION = "werner_credit_pressure_signal_gap_werner_01.v0.1"

# ---------------------------------------------------------------------------
# CDL-096 ratified constants
# ---------------------------------------------------------------------------
TOPOLOGY_PRESSURE_MODEL = "werner_v1"
WERNER_HEAT_THRESHOLD = Decimal("100")

# Spectral trust rule (CDL-096 §2)
SPECTRAL_TRUST_K = 2          # minimum epochs above threshold in window
SPECTRAL_TRUST_N = 3          # epoch window size
SPECTRAL_TRUST_BETA_FLOOR = Decimal("0.5")
SPECTRAL_TRUST_PULSE_FLOOR = Decimal("0.5")

# Default smoothing alpha for exponential moving average (from SIM evidence)
DEFAULT_SMOOTHING_ALPHA = Decimal("0.50")

# Precision context
_TWELVE_PLACES = Decimal("0.000000000001")
MAX_WERNER_ADJACENCY_NODES = 10_000
MAX_WERNER_ADJACENCY_EDGES = 50_000

# Non-activation token — embedded in runtime output to assert guard state
WERNER_WIRING_NOT_ACTIVATED_TOKEN = "werner_credit_wiring_not_activated_gap_werner_01"


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------

def _require_finite(d: Decimal, name: str) -> Decimal:
    """Reject non-finite Decimal values at input boundaries.

    Per CLAUDE.md §3: Decimal("NaN") and Decimal("Infinity") must be explicitly
    rejected at every ledger/numeric input boundary.
    """
    if not d.is_finite():
        raise ValueError(f"non_finite_decimal_{name}")
    return d


def _coerce_decimal(value: object, name: str) -> Decimal:
    """Coerce a value to Decimal and reject non-finite results.

    Raises ValueError with a machine-readable token if the value cannot be
    coerced to a finite Decimal.
    """
    if isinstance(value, bool):
        raise ValueError(f"invalid_decimal_input_{name}_bool_not_allowed")
    if isinstance(value, float):
        raise ValueError(f"invalid_decimal_input_{name}_float_not_allowed")
    if isinstance(value, Decimal):
        return _require_finite(value, name)
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid_decimal_input_{name}") from exc
    return _require_finite(result, name)


def _require_non_negative(d: Decimal, name: str) -> Decimal:
    if d < Decimal("0"):
        raise ValueError(f"negative_decimal_{name}")
    return d


def _require_unit_interval(d: Decimal, name: str) -> Decimal:
    if d < Decimal("0") or d > Decimal("1"):
        raise ValueError(f"decimal_out_of_unit_interval_{name}")
    return d


# ---------------------------------------------------------------------------
# Degree-based centrality computation
# ---------------------------------------------------------------------------

def compute_degree_centrality(
    adjacency: Mapping[str, Sequence[str]],
) -> dict[str, Decimal]:
    """Compute normalized out-degree centrality for all nodes in an adjacency map.

    Parameters
    ----------
    adjacency:
        A mapping from node_id (str) to a sequence of neighbor node_ids.
        The mapping must not be None. An empty mapping returns an empty dict.

    Returns
    -------
    dict[str, Decimal]:
        Mapping from node_id to normalized out-degree centrality in [0, 1].
        For a single-node graph, centrality is Decimal("0") (no edges possible).
        For empty graphs, returns empty dict.

    Raises
    ------
    ValueError:
        If adjacency contains non-string keys or values.
    """
    if not isinstance(adjacency, Mapping):
        raise ValueError("werner_adjacency_must_be_mapping")

    n = len(adjacency)
    if n == 0:
        return {}
    if n > MAX_WERNER_ADJACENCY_NODES:
        raise ValueError("werner_adjacency_node_count_exceeds_maximum")

    # Validate all keys and neighbor node ids are strings.
    node_ids: set[str] = set()
    for node in adjacency:
        if not isinstance(node, str):
            raise ValueError("werner_adjacency_keys_must_be_strings")
        node_ids.add(node)

    # Denominator for normalization: max possible degree = n - 1
    if n == 1:
        return {node: Decimal("0") for node in adjacency}

    max_degree = Decimal(str(n - 1))
    centrality: dict[str, Decimal] = {}
    edge_count = 0
    for node, neighbors in adjacency.items():
        if isinstance(neighbors, (str, bytes)) or not isinstance(neighbors, Sequence):
            raise ValueError("werner_adjacency_neighbors_must_be_sequence")
        neighbor_list = list(neighbors)
        if any(not isinstance(neighbor, str) for neighbor in neighbor_list):
            raise ValueError("werner_adjacency_neighbor_values_must_be_strings")
        neighbor_set = set(neighbor_list)
        if len(neighbor_set) != len(neighbor_list):
            raise ValueError("werner_adjacency_duplicate_neighbor")
        if node in neighbor_set:
            raise ValueError("werner_adjacency_self_neighbor")
        if not neighbor_set.issubset(node_ids):
            raise ValueError("werner_adjacency_neighbor_not_in_graph")
        edge_count += len(neighbor_list)
        if edge_count > MAX_WERNER_ADJACENCY_EDGES:
            raise ValueError("werner_adjacency_edge_count_exceeds_maximum")
        degree = Decimal(str(len(neighbor_list)))
        centrality[node] = (degree / max_degree).quantize(_TWELVE_PLACES)

    return centrality


# ---------------------------------------------------------------------------
# Exponential moving average smoothing
# ---------------------------------------------------------------------------

def compute_smoothed_pressure(
    raw_pressure_sequence: Sequence[Decimal],
    alpha: Decimal,
) -> Decimal:
    """Compute exponentially smoothed pressure from a sequence of raw values.

    Uses the recurrence: S_t = alpha * P_t + (1 - alpha) * S_{t-1}
    with S_0 = P_0 (first observed value).

    Parameters
    ----------
    raw_pressure_sequence:
        Ordered sequence of raw Decimal pressure values (oldest first).
        Must be non-empty.
    alpha:
        Smoothing factor in (0, 1]. Decimal, finite.

    Returns
    -------
    Decimal:
        The smoothed pressure after processing the full sequence.

    Raises
    ------
    ValueError:
        If the sequence is empty, alpha is out of range, or any pressure
        value is non-finite.
    """
    alpha = _coerce_decimal(alpha, "alpha")
    if alpha <= Decimal("0") or alpha > Decimal("1"):
        raise ValueError("werner_smoothing_alpha_must_be_in_open_0_1_interval")

    values = list(raw_pressure_sequence)
    if not values:
        raise ValueError("werner_raw_pressure_sequence_must_be_non_empty")

    with localcontext() as ctx:
        ctx.prec = 28
        one_minus_alpha = Decimal("1") - alpha
        smoothed = _coerce_decimal(values[0], "raw_pressure[0]")
        _require_non_negative(smoothed, "raw_pressure[0]")
        for i, val in enumerate(values[1:], start=1):
            p = _coerce_decimal(val, f"raw_pressure[{i}]")
            _require_non_negative(p, f"raw_pressure[{i}]")
            smoothed = alpha * p + one_minus_alpha * smoothed
        return smoothed.quantize(_TWELVE_PLACES)


# ---------------------------------------------------------------------------
# Beta signal computation (CDL-096 / SIM v3 §3)
# ---------------------------------------------------------------------------

def compute_beta_signal(
    scheduled_capacity: Decimal,
    unserved_capacity: Decimal,
) -> Decimal:
    """Compute the beta signal (productive fraction) for a node's capacity slot.

    Formula (CDL-096 / SIM v3 §3):
        beta_signal = scheduled_capacity / (scheduled_capacity + unserved_capacity)

    If total capacity is zero, returns Decimal("0") (no activity).

    Parameters
    ----------
    scheduled_capacity:
        Productively scheduled capacity. Non-negative Decimal.
    unserved_capacity:
        Demanded but unserved capacity. Non-negative Decimal.

    Returns
    -------
    Decimal in [0, 1].
    """
    scheduled_capacity = _coerce_decimal(scheduled_capacity, "scheduled_capacity")
    unserved_capacity = _coerce_decimal(unserved_capacity, "unserved_capacity")
    _require_non_negative(scheduled_capacity, "scheduled_capacity")
    _require_non_negative(unserved_capacity, "unserved_capacity")

    total = scheduled_capacity + unserved_capacity
    if total == Decimal("0"):
        return Decimal("0")
    with localcontext() as ctx:
        ctx.prec = 28
        return (scheduled_capacity / total).quantize(_TWELVE_PLACES)


# ---------------------------------------------------------------------------
# Spectral trust eligibility check (CDL-096 §2)
# ---------------------------------------------------------------------------

def is_spectral_trust_eligible(
    beta_signal_history: Sequence[Decimal],
    pulse_pressure_history: Sequence[Decimal],
    *,
    k: int = SPECTRAL_TRUST_K,
    n: int = SPECTRAL_TRUST_N,
    beta_floor: Decimal = SPECTRAL_TRUST_BETA_FLOOR,
    pulse_floor: Decimal = SPECTRAL_TRUST_PULSE_FLOOR,
) -> bool:
    """Determine whether a node is spectral-trust eligible per CDL-096.

    A signal is trust-eligible if beta_signal > beta_floor AND
    pulse_pressure > pulse_floor for at least K of the last N epochs.

    Parameters
    ----------
    beta_signal_history:
        Sequence of beta signals (most recent N values, oldest first).
    pulse_pressure_history:
        Sequence of pulse pressures (most recent N values, oldest first).
    k, n:
        Spectral trust window parameters (CDL-096: K=2, N=3).
    beta_floor, pulse_floor:
        Threshold floors (CDL-096: both 0.5).

    Returns
    -------
    bool: True if trust-eligible.
    """
    if not isinstance(k, int) or k < 1:
        raise ValueError("werner_spectral_k_must_be_positive_int")
    if not isinstance(n, int) or n < k:
        raise ValueError("werner_spectral_n_must_be_gte_k")

    beta_floor = _coerce_decimal(beta_floor, "beta_floor")
    pulse_floor = _coerce_decimal(pulse_floor, "pulse_floor")
    _require_unit_interval(beta_floor, "beta_floor")
    _require_unit_interval(pulse_floor, "pulse_floor")

    beta_vals = list(beta_signal_history)
    pulse_vals = list(pulse_pressure_history)

    # Take the last N epochs
    beta_window = beta_vals[-n:]
    pulse_window = pulse_vals[-n:]

    if len(beta_window) < n or len(pulse_window) < n:
        # Insufficient history — not eligible
        return False

    qualifying = 0
    for b_raw, p_raw in zip(beta_window, pulse_window):
        b = _coerce_decimal(b_raw, "beta_signal_history_entry")
        p = _coerce_decimal(p_raw, "pulse_pressure_history_entry")
        if b > beta_floor and p > pulse_floor:
            qualifying += 1

    return qualifying >= k


# ---------------------------------------------------------------------------
# Core Werner pressure-signal computation (CDL-096 §2)
# ---------------------------------------------------------------------------

def compute_werner_pressure_signal(
    node_id: str,
    adjacency: Mapping[str, Sequence[str]],
    centrality: Mapping[str, Decimal],
    alpha: Decimal,
    beta_signal: Decimal,
) -> Decimal:
    """Compute the Werner credit pressure signal for node_id.

    Formula (CDL-096 §2):
        candidate_priority = smoothed_pressure * beta_signal

    Where smoothed_pressure for a node is derived from its centrality score
    and the graph topology. The centrality input is treated as the raw
    pressure value for the node; the smoothing across epochs is the caller's
    responsibility (use compute_smoothed_pressure for multi-epoch use).

    This function computes a SINGLE-EPOCH snapshot pressure signal:
        pressure_signal = centrality[node_id] * beta_signal

    This is the primitive building block; multi-epoch smoothing is composed
    by the caller using compute_smoothed_pressure.

    Returns a dimensionless Decimal in [0, ∞). Does NOT return ECU.
    Does NOT write to any ledger.

    Parameters
    ----------
    node_id:
        The graph node for which to compute the pressure signal.
        Must be a key in adjacency.
    adjacency:
        Full graph adjacency mapping {node_id: [neighbor_id, ...]}.
        Must contain node_id.
    centrality:
        Pre-computed centrality scores {node_id: Decimal}.
        If node_id is absent, falls back to degree centrality computation.
    alpha:
        Smoothing parameter (used in caller context; passed here for
        validation and downstream multi-epoch use). This single-epoch
        snapshot validates alpha for API symmetry but does not apply EMA;
        alpha affects output only in compute_werner_smoothed_candidate_priority().
    beta_signal:
        Productive-fraction signal in [0, 1] (Decimal, finite).

    Returns
    -------
    Decimal:
        Dimensionless pressure signal for node_id. Not ECU. Not ILC.

    Raises
    ------
    ValueError:
        If any input is invalid (non-finite Decimal, float, bad type).
    """
    # Validate node_id
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("werner_node_id_must_be_non_empty_string")

    # Validate and validate adjacency
    if not isinstance(adjacency, Mapping):
        raise ValueError("werner_adjacency_must_be_mapping")

    # Validate alpha (used for validation; single-epoch snapshot does not apply EMA here)
    alpha = _coerce_decimal(alpha, "alpha")
    if alpha <= Decimal("0") or alpha > Decimal("1"):
        raise ValueError("werner_smoothing_alpha_must_be_in_open_0_1_interval")

    # Validate beta_signal
    beta_signal = _coerce_decimal(beta_signal, "beta_signal")
    _require_unit_interval(beta_signal, "beta_signal")

    # Empty topology: return 0
    if len(adjacency) == 0:
        return Decimal("0")
    if node_id not in adjacency:
        raise ValueError("werner_node_id_not_in_adjacency")

    # Resolve centrality for node_id
    if isinstance(centrality, Mapping) and node_id in centrality:
        raw_c = centrality[node_id]
        c = _coerce_decimal(raw_c, "centrality")
        _require_unit_interval(c, "centrality")
    elif isinstance(centrality, Mapping) and len(centrality) > 0:
        computed = compute_degree_centrality(adjacency)
        c = computed.get(node_id, Decimal("0"))
    else:
        # No centrality provided — compute from adjacency
        computed = compute_degree_centrality(adjacency)
        c = computed.get(node_id, Decimal("0"))

    # All centrality zero → return 0
    if c == Decimal("0"):
        return Decimal("0")

    # candidate_priority = centrality * beta_signal (single-epoch)
    with localcontext() as ctx:
        ctx.prec = 28
        priority = c * beta_signal
        return priority.quantize(_TWELVE_PLACES)


# ---------------------------------------------------------------------------
# Multi-epoch smoothed pressure signal (full CDL-096 pipeline)
# ---------------------------------------------------------------------------

def compute_werner_smoothed_candidate_priority(
    node_id: str,
    adjacency: Mapping[str, Sequence[str]],
    centrality: Mapping[str, Decimal],
    beta_signal_sequence: Sequence[Decimal],
    alpha: Decimal = DEFAULT_SMOOTHING_ALPHA,
) -> Decimal:
    """Compute Werner candidate_priority from multi-epoch beta signal history.

    Full CDL-096 pipeline:
        1. For each epoch t: raw_pressure_t = centrality[node_id] * beta_signal_t
        2. Apply EMA: smoothed_pressure = EMA(raw_pressures, alpha)
        3. candidate_priority = smoothed_pressure * beta_signal[-1]

    Returns a dimensionless Decimal. Does NOT return ECU. Does NOT modify state.

    Parameters
    ----------
    node_id:
        Target graph node.
    adjacency:
        Full graph adjacency mapping.
    centrality:
        Pre-computed centrality scores. Keys must include node_id for
        accurate results; falls back to degree centrality otherwise.
    beta_signal_sequence:
        Ordered sequence of beta signals (oldest first, length >= 1).
    alpha:
        EMA smoothing parameter. Decimal in (0, 1].

    Returns
    -------
    Decimal: Dimensionless Werner candidate priority. Not ECU.
    """
    if not isinstance(node_id, str) or not node_id:
        raise ValueError("werner_node_id_must_be_non_empty_string")
    if not isinstance(adjacency, Mapping):
        raise ValueError("werner_adjacency_must_be_mapping")
    if len(adjacency) == 0:
        return Decimal("0")
    if node_id not in adjacency:
        raise ValueError("werner_node_id_not_in_adjacency")

    alpha = _coerce_decimal(alpha, "alpha")
    if alpha <= Decimal("0") or alpha > Decimal("1"):
        raise ValueError("werner_smoothing_alpha_must_be_in_open_0_1_interval")

    betas = list(beta_signal_sequence)
    if not betas:
        raise ValueError("werner_beta_signal_sequence_must_be_non_empty")

    # Resolve centrality
    if isinstance(centrality, Mapping) and node_id in centrality:
        raw_c = centrality[node_id]
        c = _coerce_decimal(raw_c, "centrality")
        _require_unit_interval(c, "centrality")
    else:
        computed = compute_degree_centrality(adjacency)
        c = computed.get(node_id, Decimal("0"))

    if c == Decimal("0"):
        return Decimal("0")

    # Build raw pressure sequence: pressure_t = centrality * beta_t
    raw_pressures: list[Decimal] = []
    with localcontext() as ctx:
        ctx.prec = 28
        for i, b_raw in enumerate(betas):
            b = _coerce_decimal(b_raw, f"beta_signal[{i}]")
            _require_unit_interval(b, f"beta_signal[{i}]")
            raw_pressures.append((c * b).quantize(_TWELVE_PLACES))

    smoothed = compute_smoothed_pressure(raw_pressures, alpha)

    # candidate_priority = smoothed_pressure * beta_signal[-1]
    last_beta = _coerce_decimal(betas[-1], "beta_signal_last")
    _require_unit_interval(last_beta, "beta_signal_last")
    with localcontext() as ctx:
        ctx.prec = 28
        priority = smoothed * last_beta
        return priority.quantize(_TWELVE_PLACES)


# ---------------------------------------------------------------------------
# Flow-budget computation (CDL-096 §2)
# ---------------------------------------------------------------------------

def compute_flow_budget(
    candidate_priority: Decimal,
    runtime_policy_cap: Decimal,
) -> Decimal:
    """Compute Werner flow_budget = min(runtime_policy_cap, candidate_priority).

    Per CDL-096 §2. Both inputs must be non-negative finite Decimals.
    runtime_policy_cap is deferred to a later activation gate per CDL-096;
    callers must supply a validated cap.

    Returns a dimensionless Decimal. Not ECU. Not ILC.
    """
    cp = _coerce_decimal(candidate_priority, "candidate_priority")
    cap = _coerce_decimal(runtime_policy_cap, "runtime_policy_cap")
    _require_non_negative(cp, "candidate_priority")
    _require_non_negative(cap, "runtime_policy_cap")
    return min(cap, cp).quantize(_TWELVE_PLACES)
