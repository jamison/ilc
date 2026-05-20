# ADR-0042: VRF Proof Verifier

**Status:** Accepted
**Date:** 2026-05-20
**Phase:** 1410
**Author:** Jamison and Codex
**Dependencies:** ADR-0040, ADR-0038, CDL-068, Phase 1396/J-006, Phase 1398/J-008, Phase 1409

`vrf_proof_verifier_adr_accepted_phase_1410`
`vrf_proof_verifier_not_activated_phase_1410`

---

## Context

ADR-0040 accepts deterministic epoch-hash assignment only for shadow,
non-value, quote-only panel construction. It records
`vrf_required_for_production_high_value_assignment` and
`vrf_proof_verifier_not_implemented` for production high-value assignment.

Phase 1396 implemented `jury_assignment_runtime.py` as a default-off quote
runtime. Its `_agent_score()` function uses canonical JSON and SHA-256 to
produce deterministic epoch-hash shadow scores, and
`PRODUCTION_ASSIGNMENT_NOT_ACTIVATED` remains `True`.

Phase 1398/J-008 records `VRF_VERIFIER_IMPLEMENTED` as a blocking NOT_MET
condition through `vrf_verifier_required_not_implemented_phase_j008`.
Phase 1410 closes the design obligation only. It does not implement a verifier,
wire jury assignment to VRF output, or flip the J-008 condition.

## Claim Verification Table

| Claim | File/symbol checked | Result |
|-------|---------------------|--------|
| ADR-0042 is the next ADR number | `docs/adr/` directory listing | confirmed: ADR-0040 and ADR-0041 are present; no ADR-0042 existed before this phase |
| ADR-0040 records the VRF production boundary | `docs/adr/ADR_0040_Jury_Eligibility_Assignment.md` | confirmed: `vrf_required_for_production_high_value_assignment` and `vrf_proof_verifier_not_implemented` are present |
| Current jury assignment runtime is epoch-hash shadow only | `ilc_core/epistemic/jury_assignment_runtime.py::_agent_score` and `quote_jury_assignment` | confirmed: canonical JSON plus SHA-256, `assignment_mode="epoch_hash_shadow"` |
| Current topology shuffle runtime has only a VRF threshold hook | `ilc_core/validator/topology_shuffle_runtime.py` | confirmed: threshold 10 fails closed with `vrf_upgrade_required_at_10_validators_phase_1354`; no proof verifier exists |
| J-008 still treats VRF verifier implementation as NOT_MET | `ilc_core/epistemic/jury_activation_gate.py` | confirmed: `VRF_VERIFIER_IMPLEMENTED` is hardcoded NOT_MET |
| No selected VRF dependency exists in current dependency files | `pyproject.toml`, `requirements.txt`, `requirements-*.txt` | confirmed: `cryptography` exists; no VRF-specific package or PyNaCl dependency is currently declared |

## Decision

ILC selects RFC 9381 ECVRF as the proof-verifier contract for production
high-value jury assignment and any later production maintenance-lottery draw
that chooses the same randomness path.

The selected ciphersuite is:

```text
ECVRF-EDWARDS25519-SHA512-ELL2
```

The verifier implementation must follow RFC 9381 and its RFC 9380
hash-to-curve dependency for the ELL2 suite. The verifier module must verify
proofs and derive VRF output bytes. It must not generate proofs, hold private
keys, perform assignment production activation, or write ledger/wallet state.

The selected Python implementation support library is:

```text
PyNaCl==1.6.2
```

Phase 1411 may add this dependency. PyNaCl is a maintained Python binding to
libsodium and exposes Ed25519/signature/hash primitives needed for a minimal
RFC 9381 verifier support layer. The project does not select an unreviewed
"VRF" package from PyPI in this ADR. Local package inspection during Phase 1410
found obvious candidate packages that were incomplete, non-RFC-9381, or
demonstration-grade; those are rejected below.

Primary references:

- RFC 9381: <https://www.rfc-editor.org/rfc/rfc9381>
- PyNaCl 1.6.2 documentation: <https://pynacl.readthedocs.io/en/latest/>

## Proof Format

All JSON artifacts carrying VRF material must be canonicalized with
`sort_keys=True`, `separators=(",", ":")`, and `allow_nan=False` before hashing,
signing, or deriving alpha bytes.

Canonical proof record fields:

| Field | Type | Rule |
|-------|------|------|
| `algorithm` | string | exactly `ECVRF-EDWARDS25519-SHA512-ELL2` |
| `public_key_b64u` | base64url string | raw 32-byte Ed25519 VRF public key, no padding |
| `alpha_b64u` | base64url string | canonical UTF-8 JSON bytes for the assignment input |
| `pi_b64u` | base64url string | raw RFC 9381 proof bytes; expected length is 80 bytes for this suite |
| `beta_b64u` | base64url string | raw RFC 9381 VRF output bytes; expected length is 64 bytes for this suite |
| `assignment_context_hash` | hex string | SHA-256 of the canonical assignment input bytes for audit indexing only |
| `vrf_key_ref` | string | non-secret reference binding this VRF public key to the agent identity or availability commitment |

The verifier accepts bytes, not JSON strings, at the function boundary. JSON is
an artifact serialization layer only.

## Alpha Input Contract

The VRF input `alpha` is the canonical UTF-8 JSON encoding of the assignment
context:

```json
{
  "assignment_nonce": "<domain-specific nonce>",
  "capability_tier_or_lane_score": "<canonical string>",
  "claim_or_task_id": "<content-addressed claim or task id>",
  "cluster_id": "<agent cluster id>",
  "domain_separator": "ilc.vrf.jury_assignment.v1",
  "eligible_agent_id": "<agent_id>",
  "identity_lineage_ref": "<ADR-0038/CDL-090-compatible identity lineage ref>",
  "outsider_candidate_flag": true,
  "review_epoch": 0,
  "review_lane": "<lane id>"
}
```

Canonicalization rules:

- The field set above is closed for Phase 1411 and Phase 1412 unless a later
  ADR/CDL explicitly amends it.
- `review_epoch` is protocol epoch time, not wall-clock time.
- `assignment_nonce` must be supplied by the caller from a ratified epoch or
  review-lane source; it must not be generated by `random`.
- `capability_tier_or_lane_score` remains a string, not an economic amount.
- `identity_lineage_ref` binds the key to the ADR-0038 identity/birth-attestation
  lineage without embedding secret key material.

## Verification API

Phase 1411 must implement a pure verifier module with this public contract:

```python
def verify_vrf_proof(*, pi: bytes, public_key: bytes, alpha: bytes) -> bool:
    """Return True only when RFC 9381 verification succeeds."""

def vrf_beta_from_proof(*, pi: bytes, public_key: bytes, alpha: bytes) -> bytes:
    """Return beta bytes for a valid proof; raise a stable verification error otherwise."""
```

Verifier requirements:

- no private key operations;
- no proof generation;
- no `import random`;
- no float values;
- no wall-clock protocol decisions;
- bounded input lengths before any expensive decode or group operation;
- stable `ValueError` or module-specific verification error on malformed input;
- RFC 9381 test vectors in Phase 1411 tests before any integration claim.

## Integration Contract

Phase 1412 extends `ilc_core/epistemic/jury_assignment_runtime.py` without
removing the epoch-hash shadow path.

Integration rules:

1. Non-high-value, shadow, and non-production assignment may continue to use
   `assignment_mode="epoch_hash_shadow"`.
2. High-value production assignment must require a valid proof record for each
   candidate used in the VRF ordering pool.
3. Candidate ordering is `(beta_bytes, agent_id)` ascending, where `beta_bytes`
   is returned by `vrf_beta_from_proof(...)` over that candidate's canonical
   alpha bytes.
4. Missing or invalid proof material excludes the candidate from high-value VRF
   assignment and must be visible in the quote/audit response.
5. Phase 1412 must preserve `PRODUCTION_ASSIGNMENT_NOT_ACTIVATED: bool = True`;
   integrated verification is not production activation.
6. J-008 may not mark `VRF_VERIFIER_IMPLEMENTED` MET until the verifier exists,
   jury assignment integration exists, and Phase 1413 security/integration
   tests pass.

The VRF prover is external to the verifier module. Proof material is expected to
come from the agent/controller side through availability commitments or a later
ratified assignment-proof submission path. Phase 1411 implements verification
only; Phase 1412 consumes proof material only.

## Rejected Alternatives

| Alternative | Disposition |
|-------------|-------------|
| Keep epoch-hash shadow for high-value production slots | rejected: ADR-0040 explicitly forbids marketing epoch-hash shadow as production privacy or production unpredictability |
| Select `python-ecvrf-4o==0.1.1` | rejected: local source inspection found placeholder verification behavior and demonstration-grade logic rather than a complete RFC 9381 verifier |
| Select `vrf==1.0.7` | rejected: local source inspection found an ECDSA/signature-style package, not RFC 9381 ECVRF |
| Implement proof generation inside `vrf_proof_verifier.py` | rejected: verifier module must not hold private keys or generate proofs |
| Use RSA-FDH-VRF | rejected for this lane: larger keys/proofs and weaker fit with the existing compact agent-key/Edwards-curve direction |

## Non-Activation

`vrf_proof_verifier_not_activated_phase_1410`

This ADR does not:

- create `ilc_core/epistemic/vrf_proof_verifier.py`;
- implement a VRF verifier;
- generate VRF proofs;
- modify `jury_assignment_runtime.py`;
- replace epoch-hash shadow assignment;
- mark J-008 `VRF_VERIFIER_IMPLEMENTED` as MET;
- activate production jury assignment;
- activate maintenance lottery draws;
- distribute ECU;
- mutate ledger, treasury, wallet, graph, or CDL state.

## Phase 1411 Implementation Guidance — PyNaCl API Gap

RFC 9381 ECVRF-EDWARDS25519-SHA512-ELL2 verification requires:

1. Compressed Ed25519 point decompression (32 bytes to group element)
2. Scalar multiplication on Edwards25519
3. Point addition on Edwards25519
4. Hash-to-curve using Elligator2 (RFC 9380 Section 6.7.1 for Ed25519)
5. Challenge hash computation (SHA-512 over concatenated points)

PyNaCl 1.6.2 exposes Ed25519 signature primitives at the opaque level through
`nacl.signing` and `nacl.bindings.crypto_sign_*`. Since PyNaCl 1.6.0 it also
exposes low-level Ed25519 group arithmetic through `nacl.bindings`:
`crypto_core_ed25519_add`, `crypto_core_ed25519_sub`,
`crypto_core_ed25519_from_uniform`, `crypto_scalarmult_ed25519_noclamp`, and
related functions. These map to libsodium 1.0.18 or newer symbols and may be
sufficient for the point decompression, scalar multiplication, and point
addition required by RFC 9381 verification.

Hash-to-curve Elligator2 (RFC 9380 Section 6.7.1 for Ed25519) maps to
`crypto_core_ed25519_from_uniform`, which libsodium implements. Phase 1411 must
verify this mapping against RFC 9380 Section 6.7.1 before relying on it.

Required path for Phase 1411:

1. Attempt to implement RFC 9381 ECVRF-EDWARDS25519-SHA512-ELL2 verification
   using `nacl.bindings` low-level Ed25519 group operations where they map to
   the required RFC operations.
2. Validate the implementation against RFC 9381 Appendix B.4 test vectors
   (ECVRF-EDWARDS25519-SHA512-ELL2) before any integration claim. If
   `nacl.bindings` operations produce incorrect results on the Appendix B.4
   vectors, fall back to a pure-Python Edwards25519 implementation derived from
   the RFC 9381 reference.
3. Do not skip the test-vector validation step under any circumstance.

PyNaCl==1.6.2 remains the pinned dependency as selected in this ADR; this note
clarifies the scope of what it provides and the validation gate Phase 1411 must
pass.

`vrf_pynacl_api_gap_documented_phase_1410_fix1`

## Consequences

Phase 1411 has a concrete algorithm/library/proof-format contract to implement.
Phase 1412 has an integration contract for replacing epoch-hash scoring only
where production high-value assignment requires VRF. Phase 1413 must test the
verifier and integration before any gate update can be considered.

Graph delta:
`graph_delta=load_bearing_artifact_added:docs/adr/ADR_0042_VRF_Proof_Verifier.md -> adr/vrf_jury_assignment`.
