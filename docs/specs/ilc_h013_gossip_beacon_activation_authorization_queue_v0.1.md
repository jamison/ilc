# H-013: Gossip Beacon Activation — Authorization Queue

**Status:** AWAITING HUMAN AUTHORIZATION to open implementation window
**Prepared:** Phase 928 (2026-04-28)
**ADR:** ADR-0034 (sealed sender) — already accepted
**Blocks:** `node_startup_runtime.py` L3 wiring (live peer fingerprints),
            SIM-BEACON-01 (noise budget calibration), spectral routing in production

---

## 1. What H-013 Is

H-013 is the implementation window for **gossip beacon activation** — the
mechanism by which nodes emit sealed spectral fingerprint beacons over the
D2d gossip layer. This is the live-fingerprint infrastructure that CDL-080 L3
routing currently lacks: `query_route_index_spectral()` exists but has no
real peer fingerprint cache to query against.

Without H-013:
- L3 spectral routing operates on manually-configured or test fingerprints only
- `node_startup_runtime.py` cannot wire L3 route resolution from live data
- SIM-BEACON-01 (noise budget calibration) cannot be commissioned

---

## 2. What Is Already Done (No Authorization Needed)

| Item | Status | Commit / Phase |
|------|--------|---------------|
| ADR-0034 accepted (sealed sender protocol) | Done | Prior window |
| `spectral_distance()` utility | Done | `ilc_core/analysis/spectral_utils.py` |
| `SpectralBeacon` dataclass stub | Done per planning doc | Needs confirmation |
| H-015 spectral routing primitive | Done | `spectral_routing_runtime_h015.v0.1` |
| L3 route index runtime (CDL-080) | Done | Phase 923–926 |
| `gossip_transport.py` envelope | Done | Phase 558+ (CDL-061) |

---

## 3. What Requires Authorization

The following implementation steps require explicit human authorization before
execution, because they activate live gossip emission from validator nodes:

### Step A — Sealed sender implementation in `gossip_transport.py`

Add `sealed: bool` field to outbound gossip message envelope. When `sealed=True`,
the transport layer strips all origin-identifying headers before forwarding.
This is the privacy guarantee in ADR-0034.

**Why this needs authorization:** Sealed sender changes the trust model of the
gossip layer. A relay node can no longer see the origin of sealed messages.
This has implications for rate limiting, DDoS attribution, and abuse prevention.
The tradeoff must be explicitly accepted.

### Step B — Spectral beacon emission in validator node

Validator nodes begin emitting `SpectralBeacon` messages at epoch boundaries:

```python
{
  "epoch": current_epoch,
  "lambda_local": [top-k eigenvalues, noise-perturbed],  # ~200 bytes
  "noise_sigma": epsilon  # differential privacy noise level
}
```

**Why this needs authorization:** Beacon emission is a live network behavior
change. Validators begin revealing (noised) spectral fingerprints to the gossip
layer. The noise level `epsilon` must be calibrated by SIM-BEACON-01 first —
emitting without calibration risks revealing more structural information than
intended.

### Step C — Peer fingerprint cache in node runtime

The node maintains a rolling cache of received peer spectral fingerprints,
keyed by peer endpoint. This cache feeds `query_route_index_spectral()`.

**Why this needs authorization:** Cache sizing, eviction policy, and epoch
staleness threshold need to be decided. A too-large cache wastes memory;
a too-aggressive eviction policy degrades L3 routing quality.

---

## 4. Open Questions for Human Decision

### Q1 — Should H-013 open before or after SIM-BEACON-01?

**Context:** SIM-BEACON-01 calibrates the noise budget `epsilon` for spectral
beacon privacy. Without SIM-BEACON-01, we don't know how much noise to add to
protect structural information.

**Options:**

| Option | Description | Risk |
|--------|-------------|------|
| A: H-013 after SIM-BEACON-01 | Implement only after noise is calibrated | Delays live fingerprints; L3 routing stays theoretical longer |
| B: H-013 in parallel with SIM-BEACON-01 | Implement with placeholder `epsilon`; update when SIM completes | Risk: production nodes reveal un-calibrated structural info during calibration period |
| C: H-013 with testnet-only flag | Implement and emit on testnet only; gate mainnet emission on SIM-BEACON-01 | Clean separation; requires a `BEACON_EMISSION_MODE=testnet|mainnet` env flag |

**My recommendation:** Option C (testnet-only flag). This unblocks L3 routing
integration and SIM-BEACON-01 commissioning without exposing mainnet to
un-calibrated privacy risk. The env flag is a single additional gate that can
be lifted when SIM-BEACON-01 completes.

**Your decision needed:** Option A, B, or C?

---

### Q2 — What noise level `epsilon` (differential privacy) should be used provisionally?

**Context:** Until SIM-BEACON-01 completes, some epsilon must be used for
testnet emission. The planning doc mentions `sigma=0.005` as a CDL-080 phase
planning figure — but this was never validated.

**Options:**
- A: `sigma=0.005` (from CDL-080 planning doc) — use as testnet placeholder
- B: `sigma=0.05` (10× more noise, more conservative) — safer for testnet
- C: No noise on testnet (raw eigenvalues) — maximum routing accuracy; zero privacy
- D: Defer — do not emit beacons until SIM-BEACON-01 completes (becomes Option A from Q1)

**My recommendation:** Option B for testnet (`sigma=0.05`). More conservative
than the planning doc figure. Testnet privacy matters less than mainnet privacy,
but we shouldn't establish a habit of emitting raw eigenvalues even on testnet.
SIM-BEACON-01 will calibrate the real figure.

**Your decision needed:** Provisional sigma value for testnet emission.

---

### Q3 — How large is the peer fingerprint cache, and what is the staleness threshold?

**Context:** Each cached fingerprint is a list of ~32 floats (~256 bytes).
At 100 peers, this is 25 KB — trivial. The real question is staleness: how
many epochs before a cached fingerprint is considered stale and evicted?

**Options:**
- A: Cache entries expire after 1 epoch (always fresh, high churn)
- B: Cache entries expire after 10 epochs (balance freshness vs. stability)
- C: Cache entries expire after 1 validation epoch duration (wall clock, e.g., 60s)
- D: Cache entries are never evicted; they are overwritten only when a newer beacon arrives

**My recommendation:** Option D (overwrite-only). Since beacons are emitted
at epoch boundaries, a peer's fingerprint is always at most 1 epoch old if the
peer is active. If a peer goes silent, keeping the stale fingerprint is better
than having no routing hint at all. Add a `last_seen_epoch` field to detect
dead peers separately from fingerprint staleness.

**Your decision needed:** Cache eviction policy.

---

### Q4 — What is the beacon emission frequency?

**Context:** CDL-080 §4.3 specifies beacons operate on locally-cached
fingerprints only. The question is how often a node re-emits its own beacon.

**Options:**
- A: Once per validation epoch (1 minute cadence — matches epoch commit)
- B: Once per issuance epoch (1 month — too infrequent; topology changes too fast)
- C: On demand, triggered by routing query (lazy emission — may reveal query patterns)
- D: Once per validation epoch, but only if spectral fingerprint changed by > threshold

**My recommendation:** Option D. Emitting on every epoch even if fingerprint
is unchanged wastes bandwidth and reveals that a node's neighborhood is stable
(which is itself structural information). A change threshold (e.g., `spectral_distance(lambda_prev, lambda_curr) > 0.1`) gates emission. This also naturally reduces beacon frequency for stable nodes.

**Your decision needed:** Beacon emission frequency and change threshold.

---

### Q5 — Does sealed sender apply to ALL gossip, or only beacon messages?

**Context:** ADR-0034 defines the sealed sender protocol. But applying it to
all gossip messages may be premature — rate limiting and DDoS attribution
become harder when all messages are sealed.

**Options:**
- A: Sealed sender for beacon messages only (targeted application)
- B: Sealed sender for all gossip (maximum privacy; maximum complexity)
- C: Sealed sender as opt-in per message type (future-proof; complex)

**My recommendation:** Option A (beacon messages only). Beacon messages are
the specific use case ADR-0034 was designed for — hiding spectral fingerprint
origin. Applying sealed sender to all gossip is a much larger trust model
change that deserves its own deliberation. Do the minimum first.

**Your decision needed:** Sealed sender scope.

---

## 5. Implementation Sequence (Once Authorized)

Assuming Option C from Q1 (testnet-only flag):

```
Phase X+0: H-013 sequence lock
Phase X+1: SpectralBeacon dataclass finalized; sealed sender flag in gossip_transport.py
Phase X+2: Beacon emission runtime (testnet mode only; epsilon from Q2 answer)
Phase X+3: Peer fingerprint cache in node_startup_runtime.py
Phase X+4: node_startup_runtime.py L3 wiring (live fingerprints → query_route_index_spectral)
Phase X+5: SIM-BEACON-01 commissioned (uses live testnet data)
Phase X+6: Ratification evidence + tests (≥20 tests)
Phase X+7: Closure gate
Phase X+8: Spare
```

Window size: 8 phases. Dependency on SIM-BEACON-01 means the ratification
milestone is reached only after SIM completes (or with a clear SIM-pending
forward obligation).

---

## 6. Authorization Checklist

Before this window can open, the following must be confirmed:

- [ ] Q1: H-013 before/after/parallel to SIM-BEACON-01 decided
- [ ] Q2: Provisional epsilon (noise sigma) for testnet decided
- [ ] Q3: Peer fingerprint cache eviction policy decided
- [ ] Q4: Beacon emission frequency and change threshold decided
- [ ] Q5: Sealed sender scope (beacon-only vs. all gossip) decided
- [ ] ADR-0034 implementation scope reviewed and confirmed current
- [ ] Human authorization: "open H-013 window"

`h_013_authorization_queue_ready`
`five_open_questions_require_human_decision`
`option_c_testnet_flag_recommended_for_q1`
`sealed_sender_beacon_only_recommended_for_q5`
