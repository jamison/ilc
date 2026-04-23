# ILC Coherence Report 781 v0.1

**Phase:** 781  
**Window:** 775-782  
**Date:** 2026-04-23  
**Status:** complete

## 1. What changed in Window 775-782

Window 775-782 changed the row-5 remediation surface in four concrete ways:

- BUG-001 through BUG-006 remained verified on committed head at window open
- Phase 776 removed plaintext AgentID bytes from runtime logs outside the
  explicit debug feature gate
- Phase 778 added testnet-only Layer-2 relay forwarding plus bounded
  per-submission batching on the measured submission path
- Phase 777 and Phase 779 executed the two required SIM-LEAKAGE reruns:
  post-Layer-1 and post-both-layers

The measured Run 2 outcome is honest and specific:

- Variant A improved from `1.0` in Run 1 to `0.8888888888888888` at `500ms`
  and `0.7777777777777778` at `1000ms`
- Variant B remained structurally `1.0`
- Variant C remained structurally `1.0`
- both Run 2 calibration points produced only `18 / 20` final-destination
  acknowledgements at validator-1

## 2. Row-5 verdict and meaning

The window verdict for row 5 is:

- `row_5_honest_nonclosure_verdict=bands_not_met`

What that means:

- row `5` remains `spec_closed_runtime_pending`
- Layer-1 did remove the direct plaintext AgentID leak
- Layer-2 did remove the direct contributor-to-validator destination mapping
- neither layer combination satisfied the commissioned leakage bands
- the row-5 problem is narrowed and better understood, but not closed

The best measured Run 2 point was `1000ms`, but it still failed Variant A and
did nothing to close Variant B or Variant C. No recommended default batch window is justified from this window because both calibration points showed a
delivery shortfall.

## 3. What did not change

This window did not change:

- row `8`, which remains inherited with no candidate evaluation
- Option B, which remains `no-go`
- the H-series frontier, which remains unchanged by this window
- CDL state, because no constitutional decision-log mutation occurred anywhere
  in Window 775-782

The window therefore closes as a row-5 remediation attempt and verdict record,
not as a constitutional or substrate-selection window.

## 4. ZK nullifier residual path

The surviving long-term carry-forward is explicit:

- true row-5 closure still needs a privacy mechanism stronger than fixed-path
  relay forwarding,
- the named path remains a ZK nullifier / selective-disclosure overlay on the
  linkage surfaces,
- that path must preserve the Phase 679 observability floor rather than
  suppressing public receipts outright.

H-series posture stays unchanged in this window.
