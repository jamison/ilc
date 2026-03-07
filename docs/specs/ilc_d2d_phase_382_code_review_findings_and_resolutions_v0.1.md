# D2d Phase 382 Code Review: Findings and Proposed Resolutions

**Author:** Claude Sonnet 4.6 (local architectural reviewer), with Codex addendum 2026-03-07
**Date:** 2026-03-07 (updated with Codex review)
**Source:** External audit findings on Phases 380-382 D2d runtime code
**Files reviewed:** `ilc_core/network/d2d/gossip.py`, `ilc_core/network/d2d/interface.py`

---

## MODERATE 1 — `creator_agent_id` bypass via case and separator variants (`gossip.py:57`)

### Finding

`sanitize_transport_headers` does `.strip()` on raw keys (via `_validate_non_empty_string`) but no case or separator normalization. `Creator_Agent_Id`, `CREATOR_AGENT_ID`, and `creator-agent-id` all pass the `key == "creator_agent_id"` check unchallenged. CDL-039 invariant 1 is bypassable with trivial key casing or separator substitution.

**Codex addendum:** A case-only fix (`key.lower() == "creator_agent_id"`) is incomplete. Separator variants such as `creator-agent-id` (hyphen) remain a bypass because the check still compares against `creator_agent_id` (underscore). The canonical form check must also normalize separators.

**Compound concern.** `interface.py:validate_d2d_message_envelope` (lines 168-179) also processes transport headers but has no `creator_agent_id` check at all. Messages validated there but not through `sanitize_transport_headers` carry no invariant check at the interface layer.

### Proposed fix

The normalization has two distinct layers with different purposes:

- **Storage normalization:** lowercase only (`key.lower()`) — preserves original separator choice in the stored output
- **Banned-alias check:** canonical form = lowercase + separator normalization (`re.sub(r'[-.]', '_', key_lower)`) — used only for the invariant check, not for storage

**Complete replacement for `gossip.py:sanitize_transport_headers` loop body:**

```python
import re  # add at top of module if not already present

normalized: dict[str, str] = {}
for raw_key, raw_value in headers.items():
    key = _validate_non_empty_string(
        raw_key,
        "d2d_transport_header_key_invalid",
        "transport_header_key_invalid",
    )
    # Step 1: lowercase for storage
    key_lower = key.lower()

    # Step 2: canonical form for banned-alias check (case + separator normalization)
    key_canonical = re.sub(r"[-.]", "_", key_lower)
    if key_canonical == "creator_agent_id":
        raise D2dGossipValidationError(
            "d2d_creator_agent_id_forbidden",
            "creator_agent_id_forbidden_in_transport_headers",
        )

    # Step 3: collision rejection (see MODERATE 3)
    if key_lower in normalized:
        raise D2dGossipValidationError(
            "d2d_transport_header_key_collision",
            f"transport_header_key_collision:{key_lower}",
        )

    value = _validate_non_empty_string(
        raw_value,
        "d2d_transport_header_value_invalid",
        f"transport_header_value_invalid:{key_lower}",
    )
    normalized[key_lower] = value
```

**Defense-in-depth:** Apply the same canonical-form check in `interface.py:validate_d2d_message_envelope` (after normalizing each header key), using `D2dInterfaceValidationError` instead of `D2dGossipValidationError`.

### Test update required

- Add a case-variant probe: `{"Creator_Agent_Id": "x"}` must raise
- Add a separator-variant probe: `{"creator-agent-id": "x"}` must raise
- Add a combined-variant probe: `{"Creator-Agent-Id": "x"}` must raise

---

## MODERATE 2 — Normalization collision: duplicate keys silently overwrite (`gossip.py:67`)

### Finding (Codex addendum)

After normalizing keys to lowercase for storage, two incoming keys that differ only by case (`Topic` and `topic`) both map to `topic`. The second assignment at line 67 silently overwrites the first. This is a data-integrity violation: the caller receives a header map that does not faithfully represent the input, and the discarded value produces no error signal.

The same issue applies to `interface.py:validate_d2d_message_envelope` wherever headers are normalized.

### Proposed fix

After computing `key_lower` and before writing to `normalized`, check for an existing entry and raise a deterministic error if found. This check is shown in the MODERATE 1 Step 3 block above. The error token is `d2d_transport_header_key_collision`.

For `interface.py:validate_d2d_message_envelope`, apply the equivalent check using `D2dInterfaceValidationError` with token `d2d_transport_header_key_collision`.

### Test update required

- Add probe: `{"Topic": "a", "topic": "b"}` must raise with token `d2d_transport_header_key_collision`

---

## MODERATE 3 — Channel validator rejects canonical CIDv1 (`interface.py:106,114`)

### Finding

The validator accepts `cid:<16+ hex chars>` and `rand:<16+ hex chars>`. Looking at the canonical test vectors in the same file:
- `payload_cid` (lines 20, 30): uses real CIDv1 strings (`bafybei...`) — payload CIDs are IPFS content addresses (CDL-036 pull-fetch semantics)
- `channel_id` (lines 21, 31): uses `cid:<hex>` and `rand:<hex>` — ILC's own opaque routing identifier format

**This is actually correct by design.** The channel identifier is NOT an IPFS CID — it is an opaque routing tag. The `cid:` prefix is ILC's own convention meaning "opaque channel bytes with structured prefix", not "IPFS CIDv1". The validator is semantically right. The finding is a legitimate concern about naming confusion, not a behavioral bug.

### Proposed fix (documentation only — no validator behavior change)

1. Add a module-level constant and comment block immediately above `validate_d2d_channel`:
   ```python
   # ILC channel identifiers use a structured opaque prefix convention:
   #   "cid:<hex>"  — deterministic channel bytes (NOT an IPFS CIDv1; the prefix
   #                  signals opaque channel routing, not content addressing)
   #   "rand:<hex>" — uniformly random channel bytes
   # Payload CIDs (bafybei... strings) are IPFS CIDv1 and appear in message_id/
   # payload_cid fields only. They must NOT be used as channel identifiers.
   _ILC_CHANNEL_OPAQUE_PREFIXES = frozenset({"cid", "rand"})
   ```
   Replace the inline `{"cid", "rand"}` set literal with `_ILC_CHANNEL_OPAQUE_PREFIXES`.

2. Add this design decision to the master plan as a locked annotation on section 5.1 (Phase 380 interface contract), so it is visible at Phase 390/391 and to Window 392+ prompt authors.

**Codex confirms:** This is a naming/contract clarity issue, not a runtime bug. Documentation constant/comment is the right fix.

### Answer to Open Question 1

**`cid:<opaque-hex>` is the intentional transport contract.** The validator behavior is correct. Accepting canonical CIDv1 is NOT the goal and would blur the distinction between content addressing (payload) and transport routing (channel). No validator change required.

---

## LOW 1 — Non-inferrability check is key-blacklist only (`gossip.py:171`)

### Finding

`analyze_passive_observer_membership_leakage` checks for the *presence* of obviously forbidden keys (`cluster_id`, `cluster_members`, etc.). It does not detect statistical inference. Looking at `build_observer_metadata_trace` (lines 142-168), the `channel_tag` field is derived as `SHA-256(channel_id)[:16]` — a constant per channel per session. A passive observer correlating `(relay_peer_id, channel_tag)` pairs across multiple epoch slots can infer that a stable set of peers routes the same channel, which is a structural membership signal.

**What cannot be fixed purely in code.** Perfect non-inferrability requires formal k-anonymity analysis over a topology model — it is a simulation problem, not a validator problem. A deterministic validator can prevent structural leaks; it cannot prevent statistical inference from aggregated traces.

### Proposed disposition

1. Add a scope-boundary comment at `gossip.py:171`:
   ```python
   # NOTE: This analysis detects structural cluster-membership disclosure only.
   # Statistical inference via (relay_peer_id, channel_tag) correlation across
   # epochs is a known limitation. See Phase-390 coherence report and
   # Window-392+ SIM-008 commissioning for formal remediation evidence.
   ```

2. Document in the master plan (sections 5.3 and 12) as a known limitation: "current non-inferrability validator asserts structural absence of prohibited keys; statistical correlation inference (e.g., stable `channel_tag` + `relay_peer_id` across epochs) is not covered — requires SIM-008 evidence in Window 392+."

3. Commission as SIM-008 input in the Window 392-413 candidate grouping (Phase 406 slot): run a passive observer model over mock topology traces and measure k-anonymity for cluster membership disclosure across epoch windows.

4. Consider a per-epoch channel tag rotation as a medium-term mitigation: derive `channel_tag` as `SHA-256(f"{epoch_slot}:{channel_id}")[:16]` instead of `SHA-256(channel_id)[:16]`. This prevents cross-epoch correlation at the cost of making intra-session trace correlation harder. This is a design choice — document it and defer to Window 392+ governance if needed.

---

## LOW 2 — Broad `except Exception` in `validate_gossip_channel` (`gossip.py:75`)

### Finding

Lines 75-80 catch all exceptions from `validate_d2d_channel`, including bugs like `ImportError`, `AttributeError`, `RecursionError`. Programming errors get re-raised as `D2dGossipValidationError`, masking root causes.

**Codex confirms:** Narrowing to `D2dInterfaceValidationError` is the correct fix.

### Proposed fix

Narrow the catch to only `D2dInterfaceValidationError`, which is the only exception type that `validate_d2d_channel` raises by contract:

```python
from .interface import validate_d2d_channel, validate_d2d_peer_id, D2dInterfaceValidationError

def validate_gossip_channel(channel_id: Any) -> str:
    try:
        return str(validate_d2d_channel(channel_id))
    except D2dInterfaceValidationError as exc:
        raise D2dGossipValidationError(exc.token, exc.message) from exc
```

Non-validation exceptions now propagate normally, preserving debuggability. The `from exc` chain is retained for traceability.

---

## Open Question resolutions

### Q1 — Should channel validation accept canonical CIDv1 representations?

**No.** `cid:<opaque-hex>` is the intentional transport contract. See MODERATE 2 above. The validator is correct; only documentation needs to be added.

### Q2 — Should transport header keys be canonicalized case-insensitively before invariant checks?

**Yes — and separator normalization is also required.** The architectural reasons:
- CDL-039's transport privacy intent is not satisfied by an exact-string match on a key that protocols routinely case-fold or hyphenate
- HTTP/2 (RFC 7540) mandates lowercase header field names; `creator_agent_id`, `Creator_Agent_Id`, and `creator-agent-id` are semantically identical at the transport layer
- Case-only normalization (`key.lower()`) is insufficient — `creator-agent-id` still passes
- The canonical-form check must apply `re.sub(r"[-.]", "_", key.lower())` to cover all separator variants

The normalization is two-layered: **lowercase for storage**, **lowercase + separator normalization for the banned-alias check only**. Stored keys retain their original separators (preventing unexpected key rewrites), while the invariant check is bypasses-proof. See MODERATE 1 for the complete proposed implementation.

---

## Recommended patch commit sequencing

All four fixes involve only `ilc_core/network/d2d/` — no CDL mutation. They are not a new phase and do not require the full prompt/walkthrough structure.

### Before Phase 384 at latest (standalone patch commit)

- **MODERATE 1:** `gossip.py:57` — canonical-form check (lowercase + `re.sub(r"[-.]","_",...)`) + lowercase output keys + test probes for case-variant, separator-variant, and combined-variant bypass
- **MODERATE 2 (Codex):** `gossip.py:67` — collision rejection after normalization + test probe for `{"Topic":"a","topic":"b"}`; same fix in `interface.py:validate_d2d_message_envelope`
- **MODERATE 3:** `interface.py` — add `_ILC_CHANNEL_OPAQUE_PREFIXES` constant + disambiguation comment block
- **LOW 2:** `gossip.py:75` — narrow `except Exception` to `except D2dInterfaceValidationError`

**Note on ordering:** MODERATE 1 and MODERATE 2 (Codex) are tightly coupled — both touch the same `sanitize_transport_headers` loop body and must be implemented together in a single pass. The complete replacement block in MODERATE 1 already incorporates the Step 3 collision check.

### Deferred to Phase 390 coherence report + Window 392+ SIM queue

- **LOW 1:** scope boundary comment in `gossip.py:171` + coherence report note + SIM-008 input

### Phase 383 unblocked

Phase 383 (CDL-040 prelock) CAN proceed without blocking on this patch — it is a constitutional prelock and touches no D2d code. The patch should land before Phase 385 closes, so that CDL-040/041/043 prelock artifacts reference the corrected D2d implementation.
