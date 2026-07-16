# ILC Genesis Core Slice 0 Authority Package Spec — Phase 1575c-Fix3 v0.1

Status: complete pending operator signatures
Date: 2026-07-16
Phase: 1575c-Fix3

## 1. Purpose

This spec records the Phase 1575c-Fix3 Genesis Core Slice 0 authority package and the derived Public-RC Baseline Slice 1 amendment.

Core Slice 0 is the 58-node authority kernel produced by Fix3a. It is distinct from:

- the Phase 1575c-Fix1 v0.5 public-RC signing envelope, which is an evidence/source commitment envelope;
- the Phase 1575c-Fix2 1,035-node public-RC baseline package;
- the full local LMDB row-store.

## 2. Source Choice

The source file choice was resolved by Phase 1575c-Fix3a.

| Field | Value |
|---|---|
| Source file | `out/genesis_v05_core_slice_0_1575c_fix3a/genesis_core_slice_0_hardened_candidate.json` |
| Source file SHA-256 | `bad74893437ff2c56197d6815283c7ba325a3fb025aa2c69f2e60e51aa2f191d` |
| Node count | `58` |
| Edge count | `90` |
| Added node | `cdl:098_genesis_graph_update_authority` |
| Fix3a audit status | `all_gaps_closed`, `open_gap_count = 0`, `fix3_gate = PASS` |

The immutable v0.4 source remains independently committed by the v0.5 envelope through `source_inputs.genesis_core_star_map_v04.sha256 = 09eae05dee80ec998334760922a812ee828f7220668572e6f97b9ff20c3c9bef`.

## 3. Core Slice 0 Package

| Field | Value |
|---|---|
| Artifact kind | `genesis_core_slice_0_authority_package` |
| Schema version | `genesis_core_slice_0_authority_package_1575c_fix3.v0.1` |
| Domain separator | `ilc-genesis-core-slice-0-authority-package` |
| Package path | `out/genesis_v05_core_slice_0_1575c_fix3/genesis_core_slice_0_authority_package.json` |
| Package SHA-256 | `38a9f7351d00a1b92b6476c894552d78936400cf707076ccb6967fb5af5541e1` |
| Signing payload path | `out/genesis_v05_core_slice_0_1575c_fix3/genesis_core_slice_0_authority_package.signature_payload.bin` |
| Signing payload SHA-256 | `e33d5e7f9d57661c08a06e6e6e8012dc701d46b187b5c5e965b4d769f94643b6` |
| Signing request path | `out/genesis_v05_core_slice_0_1575c_fix3/genesis_core_slice_0_authority_package.signing_request.json` |
| Signature status | `blocked_pending_operator_signature` |

## 4. Public-RC Baseline Slice 1

The Fix2 package was amended into Public-RC Baseline Slice 1 by adding the Core Slice 0 authority package digest reference and changing the domain separator.

| Field | Value |
|---|---|
| Artifact kind | `genesis_public_rc_baseline_slice_1` |
| Schema version | `genesis_public_rc_baseline_slice_1_1575c_fix3.v0.1` |
| Domain separator | `ilc-genesis-public-rc-baseline-slice-1` |
| Package path | `out/genesis_v05_atlas_graph_package_fix3/genesis_v05_public_rc_baseline_slice_1.json` |
| Package SHA-256 | `d923e935b2444e3f81f8041862409c6ec3cbfd1636d1dce82679f70f711f9083` |
| Signing payload path | `out/genesis_v05_atlas_graph_package_fix3/genesis_v05_public_rc_baseline_slice_1.signature_payload.bin` |
| Signing payload SHA-256 | `2a5418a4c117f3e0819cb14e5063170660e6af8cb8b5cc17229179277c636188` |
| Signing request path | `out/genesis_v05_atlas_graph_package_fix3/genesis_v05_public_rc_baseline_slice_1.signing_request.json` |
| Signature status | `blocked_pending_operator_signature` |

## 5. Signature Boundary

Codex did not request, receive, echo, store, or process human-held seed material.

The operator signature step remains pending. The signing requests contain the exact command pattern for the human operator:

```text
ilc_consensus/target/debug/pq_sign --input-file <signature_payload.bin> > <signature.hex>
```

After signatures are produced, each signature must be verified with:

```text
ilc_consensus/target/debug/pq_sign verify --input-file <signature_payload.bin> --signature-hex "$(tr -d '\n' < <signature.hex>)"
```

## 6. Non-Claims

This phase does not activate public RC, production minting, live settlement, wallet writes, treasury writes, public P2P, public mirror push, repository visibility change, or epoch transition.

This phase does not sign raw LMDB bytes.

This phase does not supersede the v0.5 public-RC signing envelope.

This phase does not complete Core Slice 0 or Slice 1 signature verification because detached operator signatures are not yet present.
