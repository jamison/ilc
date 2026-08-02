# ILC CDL-104 Spectral Hash Epoch Commitment Opening

**Phase:** 1580 / GAP-SPECTRAL-01a
**Status:** OPEN
**Date:** 2026-08-02
**GO phrase:** `GO GAP-SPECTRAL-01a CDL-104-OPEN`
**Opening token:** `cdl_104_opened_gap_spectral_01a`

---

## 1. Authority And Source Reconciliation

CDL-104 is opened because the public whitepaper and canonical glossary require
epoch commitments of the form `C(t) = (M(t), S(t))`, while the live Rust
`EpochSettlementRecord` still carries no spectral field. ADR-0029 explicitly
states that adding `spectral_hash` to the epoch consensus record is a protocol
change requiring a CDL.

| Source | Finding | Disposition |
|---|---|---|
| `WHITEPAPER.md:169` | `S(t)` is the sorted top-k eigenvalue fingerprint of the normalized hypergraph Laplacian. | Governing public claim. |
| `WHITEPAPER.md:1137-1145` | Initial deployment uses `k = 20` and `C(t) = (M(t), S(t))`. | CDL-104 opens the recipe needed before Rust implementation. |
| `WHITEPAPER.md:1882` | Validators sign epoch record `C(t) = (M(t), S(t))` with BLS key. | GAP-SPECTRAL-01b must wire the ratified field into the signed record. |
| `docs/architecture/ilc_canonical_glossary_and_concepts_v0.2.md:281-282` | Defines Delta and `Spectral Hash S(t)` as SHA-256 over sorted top-k eigenvalues. | Confirms 32-byte digest and CDL requirement. |
| `docs/adr/ADR_0029_Hypergraph_Substrate.md:97-112,125-132` | Laplacian is computed on demand; spectral hash in epoch commitment requires CDL. | Direct authority for this opening. |
| `ilc_core/analysis/spectral_utils.py:90-141` | Live v0.2 helper uses fixed-point int64 little-endian SHA-256 with `q = 1_000_000`. | Adopted as the candidate canonical recipe. |
| `ilc_core/analysis/spectral_utils.py:144-158` | Legacy float64 helper is retained only for older beacon/routing tests and is not reproducible enough for `S(t)`. | Rejected for epoch commitment. |
| `ilc_consensus/src/types.rs:262-277` | `EpochSettlementRecord` has `epoch`, `state_root`, `proposal_commitment_sha256`, and `not_before_unix_ms`; no `spectral_hash`. | Confirms implementation gap; prompt's older three-field description was stale. |
| `docs/research/ilc_sim_spectral_01_results_v0.1.md:8,200-207` | SIM-SPECTRAL-01 produced `sim_spectral_01_lambda2_signal_viable=true` and cleared H-007. | Simulation gate satisfied. |

Prompt-token reconciliation: the prompt's exact tokens
`sim_spectral_01_completed`, `adr_0029_accepted`, and
`phase_1575h_canonical_soak_complete` are not the live token spellings in
`STATUS.md`. The equivalent live evidence is:

| Prompt token | Live evidence |
|---|---|
| `sim_spectral_01_completed` | `sim_spectral_01_lambda2_signal_viable=true` in `docs/research/ilc_sim_spectral_01_results_v0.1.md`. |
| `adr_0029_accepted` | `docs/adr/ADR_0029_Hypergraph_Substrate.md:3-5` and `docs/adr/README.md:46` record ADR-0029 as Accepted. |
| `phase_1575h_canonical_soak_complete` | `canonical_private_economic_soak_49_epochs_complete_phase_1575h_canonical` in `docs/phases/STATUS.md`. |

---

## 2. CDL-104 Open Questions

CDL-104 opens the following ratification questions for GAP-SPECTRAL-01b:

1. Confirm whether the Phase 1580 candidate recipe below is ratified unchanged.
2. Confirm that the Rust field name is `spectral_hash` and the Rust field type is `[u8; 32]`.
3. Confirm that `spectral_hash` is included in the canonical BLS-signed `EpochSettlementRecord` preimage after ratification.
4. Confirm how Python/Rust bridge code obtains or supplies the epoch eigenvalue vector.
5. Confirm whether phase 01b requires additional runtime validation that independently recomputes `S(t)`, or only commits the supplied digest and defers full recomputation enforcement to a later activation phase.

---

## 3. Candidate Canonical Recipe

CDL-104 opens with the following candidate recipe as the recommended ratifiable
form for `S(t)`.

| Parameter | Candidate value |
|---|---|
| Laplacian | Normalized hypergraph Laplacian `Delta(t)` from ADR-0029 sparse incidence state. |
| Eigenvalue ordering | Sort eigenvalues ascending before truncation. |
| `k` | `20` for initial deployment. If fewer than 20 finite eigenvalues exist, commit all available finite eigenvalues. |
| Quantization | `mu_i = round_ties_to_even(lambda_i * 1_000_000)`. |
| Integer encoding | Signed int64 little-endian for each `mu_i`. |
| Digest | SHA-256 over the concatenated int64 little-endian byte sequence. |
| Rust field width | `[u8; 32]`. |
| Python source anchor | `spectral_hash_fixed_point_int64_le(eigenvalues, q=1_000_000, k=20)`. |

This deliberately chooses the live fixed-point helper over the legacy raw
float64 helper. The legacy helper is retained for beacon/routing compatibility
only and is not acceptable for the epoch commitment because raw floating-point
byte hashing is not robust enough as a cross-language consensus preimage.

The older SHA-384 / `[u8; 48]` window-guidance candidate is rejected for
CDL-104 v1 because it conflicts with the glossary's 32-byte SHA-256 definition,
the public whitepaper's SHA-256 claim, and the live v0.2 helper. A SHA-384
successor would require a later CDL amendment.

---

## 4. Ratification Boundary For GAP-SPECTRAL-01b

GAP-SPECTRAL-01b may proceed only after this CDL opening is present and the
human GO for ratification is issued. Its implementation scope is expected to:

1. Ratify CDL-104 or explicitly amend this candidate recipe before code changes.
2. Add `spectral_hash: [u8; 32]` to Rust `EpochSettlementRecord`.
3. Include `spectral_hash` in serialization and BLS signing preimages.
4. Update Python -> Rust bridge surfaces to supply the 32-byte digest.
5. Add conformance vectors proving Python and Rust agree on the digest recipe.

This opening does not itself modify Rust, add a consensus field, alter BLS
signing, activate spectral recomputation enforcement, write LMDB state, clear
public RC gates, push a public mirror, or activate mainnet.

---

## 5. Non-Claims

This phase does not ratify CDL-104, implement `spectral_hash` in Rust, modify
`EpochSettlementRecord`, alter validator signatures, modify settlement roots,
activate public RC, activate mainnet, publish a public mirror, write wallet
state, mint ECU/ILC, settle ILC, or authorize transfer/spend/withdrawal.

Output tokens recorded by Phase 1580:

```text
cdl_104_opened_gap_spectral_01a
spectral_digest_recipe_canonicalized_gap_spectral_01a
cdl_104_recipe_conflicts_reconciled_gap_spectral_01a
gap_spectral_01a_complete
whitepaper_spectral_obligation_documented_gap_spectral_01a
```
