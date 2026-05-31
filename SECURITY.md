# Security Policy

## Reporting a Vulnerability

**Do not open a public GitHub issue for security findings.**

Report security vulnerabilities to: `genesis@ilc.foundation`

If that address is not yet active, use: `ilcops@proton.me`

Include in your report:
- Description of the vulnerability and affected component
- Steps to reproduce or proof-of-concept (if safe to share)
- Your assessment of severity and exploitability
- Any proposed fix or mitigation, if you have one

We will acknowledge receipt within 72 hours and provide an initial assessment within 7 days. We will keep you informed of remediation progress and credit you in the disclosure unless you prefer to remain anonymous.

---

## Scope

The repository is still pre-publication and Epoch 0 has not transitioned to a
production mainnet. Security scope is therefore limited to implemented or staged
public-RC code surfaces, release tooling, and any component that could affect a
future public artifact if published.

**In scope:**
- `ilc_core/` Python protocol implementation
- `ilc_consensus/` Rust consensus implementation
- CDL enforcement logic and signing ceremony tooling
- Cryptographic key handling, BLS signatures, PQ key generation
- ECU/ILC arithmetic, claimability, and any staged settlement logic that could affect future accounting
- Epoch processor and network transport
- Any component that could affect settlement correctness, key material security, or consensus safety

**Out of scope (design decisions, not vulnerabilities):**
- The fact that Epoch 0 is not mainnet and minting is not active
- The use of provisional algorithms documented as pre-production
- Protocol behaviors that are the intended result of a ratified CDL
- Aspirational features described in research documents but not yet implemented
- Patent-pending research, draft filing text, raw conversations, and internal gap analyses that are not shipped in the public-RC tree

---

## Security Baseline

The Phase 1387 security review established the current baseline: AI-assisted LLM review of the full protocol codebase, with community contributions. No commercial audit firm has reviewed the code at this stage. This is documented transparently in the methodology.

The following invariants are considered security-critical and are enforced by the codebase:

- No `float` for settlement values (IEEE 754 drift is a ledger integrity risk)
- JSON canonical serialization (`sort_keys=True, separators=(',', ':'), allow_nan=False`) for all hashed protocol artifacts
- No `import random` in `ilc_core/` (Mersenne Twister is not safe for quorum selection)
- Mandatory socket timeouts on all outbound HTTP
- TLS verification must not be disabled
- Atomic writes for all protocol artifacts

---

## Disclosure Policy

We follow coordinated disclosure. We ask that you:

1. Report to us privately before any public disclosure.
2. Allow reasonable time for remediation (we target 30 days for critical findings, 90 days for others).
3. Do not exploit a vulnerability beyond what is necessary to demonstrate it.

We will not take legal action against good-faith security researchers who follow this policy.

---

## Known Limitations (Epoch 0)

- Mainnet is not active. No real economic value is at risk from protocol-layer vulnerabilities at this stage.
- The jury system is authorized but not yet live in production.
- The SIM-SPECTRAL-02 Scenario B Sybil discrimination finding (Phase 1141) is an open advisory. The S3 Sybil discrimination mechanism is unresolved.
- Spectral graph commitment and directed-hyperedge extensions remain research/IP-gated unless and until shipped in public code; backward attribution is not yet canonical.
