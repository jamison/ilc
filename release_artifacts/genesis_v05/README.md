# Genesis v0.5 Public-RC Release Artifacts

This directory contains the portable public release copies of the Phase
1575c-Fix3 signed Genesis graph packages.

## Contents

- `core_slice_0/` — signed 58-node Genesis Core Slice 0 authority package.
- `public_rc_baseline_slice_1/` — signed Public-RC Baseline Slice 1 package.
- `manifest.json` — deterministic SHA-256 manifest for the copied release files.

## Verification

The `.signature_payload.bin` files are the exact payload bytes signed by the
Genesis Agent operator. Verify each signature from the repository root:

```bash
ilc_consensus/target/debug/pq_sign verify \
  --input-file release_artifacts/genesis_v05/core_slice_0/genesis_core_slice_0_authority_package.signature_payload.bin \
  --signature-hex "$(tr -d '\n' < release_artifacts/genesis_v05/core_slice_0/genesis_core_slice_0_authority_package.signature.hex)"

ilc_consensus/target/debug/pq_sign verify \
  --input-file release_artifacts/genesis_v05/public_rc_baseline_slice_1/genesis_v05_public_rc_baseline_slice_1.signature_payload.bin \
  --signature-hex "$(tr -d '\n' < release_artifacts/genesis_v05/public_rc_baseline_slice_1/genesis_v05_public_rc_baseline_slice_1.signature.hex)"
```

Expected output for each command is `signature_verified`.

These JSON packages are portable distribution witnesses. They do not claim to
be raw LMDB bytes, and they do not activate minting, settlement, wallets, public
P2P, or epoch transition.
