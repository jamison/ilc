# vNext Sign/Publish Rollback Report

**Phase:** `GAP-RC-NATIVE-DISTRIBUTION-VNEXT-SIGN-PUBLISH-00`  
**Release:** `ilc-core 0.4.34`  
**Policy:** `ilc-public-rc-current-policy-v1`, sequence `2`

## Rollback Boundary

This phase published immutable bytes and append-only graph/policy evidence. It
did not deploy the consensus binary to a host, install the Python package on a
validator, activate public RC, advance an epoch, or mutate economic state.
Host rollback is therefore not needed at this boundary.

The sequence-2 policy head must not be rolled back locally to sequence 1. The
control-host cache now records high-water mark `2`, and the pre-update bytes
are retained privately as mode-`0600` ceremony evidence. A legitimate release
rollback requires a newly authorized policy claim with sequence greater than
`2` that explicitly selects retained prior bytes. It must not rewrite or
delete the sequence-2 claim.

## Retained Surfaces

- The v0.4.34 wheel and sdist are immutable on PyPI and GitHub Releases.
- The v0.4.34 consensus tarball is immutable on GitHub Releases.
- The v0.4.34 release tag remains at the initial append-only mirror commit
  `b20b1525fe1007b62c4f49563ff7f50d8fb161ee`.
- Public `main` advances append-only to
  `53790183faaaf9628a1de6170c554cb5457f1b9c`, carrying the portable native
  graph proof discovered during final verification.
- The sequence-1 policy record, v0.4.32 release evidence, and old provider
  bytes remain historical evidence. The PyPI v0.4.32 files are yanked but
  still retrievable; they are not silently eligible under the sequence-2
  high-water mark.
- Native release and policy submissions remain in the receiver LMDB and are
  independently content-checked from `ilc-node-2`.

## Recovery Procedure

1. Stop before any host mutation if sequence 2, release assertion CID, artifact
   hashes, or the selected binary tarball differ from the tracked evidence.
2. Do not lower the policy high-water mark or mutate the existing policy node.
3. If v0.4.34 must be withdrawn, publish append-only withdrawal evidence and a
   higher-sequence authorized policy decision.
4. Select a retained prior release only through that higher-sequence policy.
5. Re-run local resolution, provider fetchback, graph readback, and deployment
   preflight before any host change.

## Non-Claims

This report does not activate public RC, mainnet, minting, settlement,
production economics, native CAS/DHT transport, or automatic policy rollback.
