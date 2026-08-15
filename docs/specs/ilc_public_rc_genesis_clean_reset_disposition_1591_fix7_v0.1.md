# ILC Public-RC Genesis Clean Reset Disposition 1591-Fix7 v0.1

Date: 2026-08-15
Phase: 1591-Fix7
Status: plan-only committed; live reset not executed in this commit

## Purpose

The Phase 1591-Fix2, Fix4, and Fix6 public VPS harness runs are valid text
evidence, but their validator databases are not public-RC launch state. The
Fix6 evidence records the public endpoint harness advancing from epoch 7 to
epoch 8. Public RC must instead start from the intended RC genesis/config at
epoch 0 in a fresh path-distinct validator namespace.

This disposition prevents the accelerated testnet/adversarial soak LMDB state
from being retained, archived, or misconstrued as an alternate immutable graph
or launch input.

## Artifact Preservation Rule

Permitted retained artifacts:

- phase walkthroughs;
- command transcripts;
- text logs;
- JSON evidence receipts;
- cryptographic summaries such as hashes, endpoint digests, epoch counts, and
  validator IDs.

Forbidden retained launch inputs:

- `data.mdb`;
- `lock.mdb`;
- validator LMDB directories;
- Atlas LMDB directories;
- graph LMDB directories;
- binary database artifacts copied into `out/`, `docs/`, release artifacts, or
  any public-RC launch namespace.

## Fresh Namespace Requirement

The intended public-RC config remains `config/mysticeti_mainnet_rc01/`.
`config/mysticeti_mainnet_rc01/genesis.json` declares `epoch = 0` and
`network_id = "ilc-rc01"`. `config/mysticeti_mainnet_rc01/node_config.toml`
declares the launch LMDB path as `/var/lib/ilc/rc01`.

The launch namespace must be path-distinct from all `phase1591_fix*` harness
directories. Reusing `/home/ilcops/phase1591_fix2/public` or any child
database directory as public-RC launch state is forbidden.

## Classification Table

| Path | Artifact class | Disposition | Reason |
|---|---|---|---|
| `/home/ilcops/phase1591_fix2/public/db_1` | phase-local validator LMDB directory | delete | Pre-RC public soak validator DB ended at epoch 8; not launch state. |
| `/home/ilcops/phase1591_fix2/public/db_1/data.mdb` | validator LMDB data file | delete | Binary LMDB data file is forbidden as launch input or preserved evidence. |
| `/home/ilcops/phase1591_fix2/public/db_1/lock.mdb` | validator LMDB lock file | delete | LMDB lock file is phase-local runtime state and must not be retained. |
| `/home/ilcops/phase1591_fix2/public/db_2` | phase-local validator LMDB directory | delete | Pre-RC public soak validator DB ended at epoch 8; not launch state. |
| `/home/ilcops/phase1591_fix2/public/db_2/data.mdb` | validator LMDB data file | delete | Binary LMDB data file is forbidden as launch input or preserved evidence. |
| `/home/ilcops/phase1591_fix2/public/db_2/lock.mdb` | validator LMDB lock file | delete | LMDB lock file is phase-local runtime state and must not be retained. |
| `/home/ilcops/phase1591_fix2/public/db_3` | phase-local validator LMDB directory | delete | Pre-RC public soak validator DB ended at epoch 8; not launch state. |
| `/home/ilcops/phase1591_fix2/public/db_3/data.mdb` | validator LMDB data file | delete | Binary LMDB data file is forbidden as launch input or preserved evidence. |
| `/home/ilcops/phase1591_fix2/public/db_3/lock.mdb` | validator LMDB lock file | delete | LMDB lock file is phase-local runtime state and must not be retained. |
| `/home/ilcops/phase1591_fix2/public/db_4` | phase-local validator LMDB directory | delete | Pre-RC public soak validator DB ended at epoch 8; not launch state. |
| `/home/ilcops/phase1591_fix2/public/db_4/data.mdb` | validator LMDB data file | delete | Binary LMDB data file is forbidden as launch input or preserved evidence. |
| `/home/ilcops/phase1591_fix2/public/db_4/lock.mdb` | validator LMDB lock file | delete | LMDB lock file is phase-local runtime state and must not be retained. |
| `out/phase_1591_fix6_public_epoch_roll/evidence.json` | text JSON evidence | not_launch_input_text_only | Textual evidence may survive as a receipt, but not as launch state. |
| `config/mysticeti_mainnet_rc01/node_config.toml` | public-RC launch config | exclude_from_launch_namespace | Canonical config input is source-controlled text, not runtime DB state. |
| `/var/lib/ilc/rc01` | fresh public-RC launch namespace | exclude_from_launch_namespace | Fresh path-distinct namespace reserved for public-RC epoch-0 state; it is not reused from any phase1591_fix soak directory. |

## Deletion Plan

The reviewed deletion plan is limited to the four phase-local validator
database directories and their LMDB files under
`/home/ilcops/phase1591_fix2/public/db_1` through
`/home/ilcops/phase1591_fix2/public/db_4`.

This commit does not execute live deletion. The ready token remains blocked
until the live reset is run and all validators are read back at epoch 0 in the
fresh namespace.

## Epoch 0 To 1 Boundary

This phase does not execute the public-RC epoch 0 to 1 ceremony. That ceremony
is reserved for final launch authority after the clean namespace is verified.

## Non-Claims

No public RC was launched. No mainnet activation occurred. No production
minting, external withdrawal, generalized ECU money transfer, public mirror
push, or CDL mutation occurred. No old LMDB database was preserved as a launch
input by this disposition.
