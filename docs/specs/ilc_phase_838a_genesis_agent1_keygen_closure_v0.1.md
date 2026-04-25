# Phase 838a Closure — Genesis Agent 1 PQ Keygen Ceremony

**Phase:** 838a  
**Verdict:** pass  
**Date:** 2026-04-25  
**Governing spec:** CDL-069 (open, ratification pending)

---

## 1. What was accomplished

Phase 838a established the permanent Genesis Agent 1 identity under the
CDL-069 post-quantum architecture.  The following were generated and secured
during a physical cold-storage ceremony:

| Item | Algorithm | Status |
|------|-----------|--------|
| identity_seed | 32 random bytes (CSPRNG) | Plate 1 — physical cold storage |
| ML-DSA-65 root keypair | FIPS 204 / fips204 crate | Plate 2 — physical cold storage |
| SPHINCS+ recovery keypair | FIPS 205 / fips205 crate | Plate 3 — 3 copies, separate locations |
| agent_id | SHA-384("ilc-agent-id-v1:" \|\| identity_seed) | Public — committed to repo |
| Genesis record commitments | SHA-384 (Tier 3 policy) | Public — committed to repo |

The Rust binary `pq_keygen` (token: `pq_keygen_838a_binary_present`) was
built from `ilc_consensus/src/pq_keygen_main.rs` and used for the ceremony.
The Python wrapper `tools/genesis_agent1_keygen.py` delegates to this binary.
All 24 tests pass.

---

## 2. Genesis Agent 1 public identity

**agent_id:**
```
c43f69fcc4dfd021f5e468824c9560c03c45c601f8d004be4d244356ce6043849b9cf2af38bc51a40c1c4bc3e71b04d9
```

Full public record (pk, commitments): `docs/genesis/genesis_agent1_pubkey_record_838a.txt`  
Cold-storage copy: Lexar USB — `genesis_agent1_pubkey_record_838a.txt`

---

## 3. Security contract satisfied

- Secret seed material was printed to terminal stdout once and never written
  to any file by the tool
- The ceremony was run locally (physically at the machine, no remote desktop,
  no screen sharing)
- Terminal history was disabled (`unset HISTFILE`) before the ceremony
- Terminal window was closed immediately after recording all three plates
- The pubkey record on USB and in repo contains no secret seed material

---

## 4. Deferred to Phase 838b

- **Shamir 2-of-3 splitting** of the SPHINCS+ recovery seed (Plate 3).
  Currently three complete copies are held at separate locations.
  Phase 838b will implement the Shamir splitting tool and conduct the
  split ceremony, after which the unsplit copies will be destroyed.

---

## 5. Forward dependencies opened

| CDL | Status | Dependency |
|-----|--------|------------|
| CDL-069 | open | Ratification requires epoch endorsement runtime (Phase 838+) |
| CDL-070 | reserved | Cannot open until CDL-069 ratified |
| CDL-071 | reserved | Cannot open until CDL-069 ratified |

---

## 6. Tokens

```
phase_838a_genesis_agent1_keygen_ceremony_complete
genesis_agent1_pubkey_record_838a
pq_keygen_838a_binary_present
```
