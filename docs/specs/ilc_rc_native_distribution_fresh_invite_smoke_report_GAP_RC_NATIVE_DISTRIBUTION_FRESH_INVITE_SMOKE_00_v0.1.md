# RC Native Distribution Fresh-Invite Smoke Report

**Phase:** `GAP-RC-NATIVE-DISTRIBUTION-FRESH-INVITE-SMOKE-00`
**Date:** 2026-10-26
**Disposition:** PASS within the bounded Genesis `public_rc` profile

## Result

A new isolated identity namespace on `ilc-node-6` installed ILC Core v0.4.34
from public bytes using a freshly generated and relay-served invite bundle. The
installer verified all three Ed25519 release envelopes, installed the signed
wheel and seven signed consensus binaries, redeemed the invite, materialized
the bounded star-map slice, and wrote an install receipt. The remote namespace
was deleted after its sanitized evidence and private log were captured.

The fresh target AgentID is represented in tracked evidence only by SHA-256
`42ceedad74acf76b317fb14cc410475338dfbe3908f577d1de2dc3b95549e7af`.
The inviter AgentID is represented by SHA-256
`82e71c48586ad639d3d039d050b9ea78e22c340442598486bbbd13decaf225a0`.
The private shortcode, nonce, signing key, and raw identity remain untracked.

## Trust Path

The invite bundle passed its outer BLS verification. The separate linkage
verifier confirmed the signed witness and materialization payload agree on
signature scope, slice ID, version, authority root, recomputed Merkle root,
projection, and privacy class. Its positive fixture passes and its negative
fixtures reject mismatches.

Genesis Core Slice 0 was independently verified with `pq_sign verify` as 58
nodes and package SHA-256
`38a9f7351d00a1b92b6476c894552d78936400cf707076ccb6967fb5af5541e1`.
Genesis Slice 1 was independently verified as 1,035 nodes and package SHA-256
`37e57cb137a849d77ab3f386235ec672edc091a22d0120b5bca226ebd87ef278`.
Both ML-DSA-65 commands returned `signature_verified`. The BLS and ML-DSA-65
checks are distinct and neither was substituted for the other.

## Release And Transport

The local resolver produced `verified_current_policy` under CDL-122 policy
sequence 2 and policy head
`bafyreih55qz222zprbsyveljr5ak27r5cd5guta27cyzs2oia4jsmobh6y` before
URL selection or retrieval. The selected release assertion is
`bafyreihdrkharlpx2oejwpdbmjeaypsnnk7az5vaixqjzoftdk4o6ko4d4` and the
software-release CID is
`bafyreia77sx3vbzbyki5xc6wz4vw47d5segxhuvebrfokaqe2mhixiitai`.

The v0.4.34 wheel was fetched in both PyPI-to-GitHub and GitHub-to-PyPI order.
All four downloads were byte-identical, 1,630,572 bytes, with SHA-256
`5d6cc7f6877ce3b7efa41e869ef94daadc3881a26377db9973f075329ef599f2`.
The current-policy-authorized consensus archive was 5,053,300 bytes with
SHA-256
`9e7bcc2a8737a785e6ad69b9abcafc4788bc0e73150c0a82d6e51d84a8473f9f`.

The smoke discovered and repaired five public-RC defects: stale installer
artifact pins, incomplete envelope verification, CA-first relay TLS handling
that could not use the signed self-signed-certificate pin, and an HTTPS bridge
that rejected the bounded GitHub release-asset redirect, plus a linkage verifier
that could be imported by tests but not executed directly from the repository
root. Each repair received focused tests and append-only public-mirror
validation. Public `main` ended at
`e103ade8583e1be24ebabcf5bbed381cdafd185e`; denylist and
`PUBLIC_RC_EXCLUDE` scans passed.

## Endpoint And Health

The invite was served by non-primary relay `ilc-node-3` over the signed DER
certificate pin. The isolated target reported `local_only` connectivity because
no external probe observer was configured. This result is not validator
admission or production readiness.

After cleanup, all four live validator services retained their exact pre-smoke
PIDs and zero restart counts. Their executable SHA-256 remained
`3c3b8ea0c6d697c597f53fcd1572625422ea2f5823a3a64d67da0a3f64d71449`.
All four LMDB `data.mdb` files remained 32,768 bytes with SHA-256
`e96dddc6a64c7c3a27d9fccc13ddf3dbaaf22731dc04cbb283af59b70b7b9ef5`.
The separate control-host wallet LMDB retained its previously recorded SHA-256
`e45dec9bcc25b689ffe65a1bca9a86143317e68977d0863168caa439ebd65848`;
the smoke performed no wallet or economic write.

## Non-Claims

- This is not generic arbitrary-agent signed-slice selection.
- This is not native CAS/DHT retrieval; only the authorized HTTPS bridge ran.
- This is not universal installation permission outside the Genesis
  `public_rc` observer profile.
- LMDB carried materialized state but conferred no authority.
- This did not admit a validator, activate public RC, transition an epoch,
  issue ECU or ILC, activate minting or settlement, or activate mainnet.
