# Phase 1322 Fix1 VPS Git Workflow Restore

```text
phase_1322_fix1_restore_vps_git_workflow.v0.1
remote_rsync_tree_provenance_blocker_resolved_phase_1322_fix1
vps_git_clone_head_matches_local_commit_phase_1322_fix1
sync_repo_git_workflow_restored_phase_1322_fix1
phase_1323_remote_sync_precondition_cleared_phase_1322_fix1
public_rc_remains_blocked_after_phase_1322_fix1
```

## Summary

Phase 1322 Fix1 restored Git provenance on the three private
DigitalOcean/Tailscale VPS nodes used by the Phase 1322 rehearsal. The prior
remote trees were rsynced working trees without `.git`, which made
`tools/testbed/sync_repo.sh` unsuitable for Phase 1323. Each remote
`/opt/ilc/current` tree is now a clean Git clone at local committed `HEAD`
`a982c567171c76488bed6c9d7143290ad801fcf7`, with origin set to
`git@github.com:jamison/ilc-core.git`.

Because local `main` was ahead of `origin/main` by three commits, Fix1 used a
Git bundle from the committed local branch rather than cloning stale GitHub
state. GitHub publication was not authorized by this Fix1.

## Node Evidence

| Node | Tailscale IP | Remote HEAD | Branch | Dirty files | Origin | Ahead/behind `origin/main` | Backup path | Sync result |
|------|--------------|-------------|--------|-------------|--------|-----------------------------|-------------|-------------|
| ilc-node-2 | 100.112.32.42 | a982c567171c76488bed6c9d7143290ad801fcf7 | main | 0 | git@github.com:jamison/ilc-core.git | 0 3 | `/opt/ilc/current.rsync_backup_phase1322_fix1_20260512T174002Z` | pass |
| ilc-node-3 | 100.91.33.46 | a982c567171c76488bed6c9d7143290ad801fcf7 | main | 0 | git@github.com:jamison/ilc-core.git | 0 3 | `/opt/ilc/current.rsync_backup_phase1322_fix1_20260512T174002Z` | pass |
| ilc-node-6 | 100.72.17.38 | a982c567171c76488bed6c9d7143290ad801fcf7 | main | 0 | git@github.com:jamison/ilc-core.git | 0 3 | `/opt/ilc/current.rsync_backup_phase1322_fix1_20260512T174002Z` | pass |

## Venv Repair

The first editable reinstall failed because earlier setup left root-owned files
inside `/opt/ilc/venv`. Fix1 normalized the venv ownership with:

```bash
sudo chown -R ilcops:ilcops /opt/ilc/venv
```

After ownership normalization, editable reinstall passed on all three nodes and
`find /opt/ilc/venv -maxdepth 3 \( ! -user ilcops -o ! -group ilcops \)` returned
zero non-`ilcops` entries on each node.

## Sync Verification

The intended operator workflow now passes:

```bash
bash tools/testbed/sync_repo.sh ilc-node-2 ilc-node-3 ilc-node-6
```

The script fetches `origin/main`, observes that local `main` remains ahead of
GitHub by three commits, and reports `sync_repo_ok` for all three nodes. This
means the remote sync precondition for Phase 1323 private rehearsal work is
cleared, while GitHub publication remains separate. Phase 1323 remains sensitive
and requires explicit `GO Phase 1323`.

## Import Smoke Test

Each node imported the restored editable checkout through the venv:

```text
NODE=ilc-node-2 SIDECARS=10 PROFILES=3
NODE=ilc-node-3 SIDECARS=10 PROFILES=3
NODE=ilc-node-6 SIDECARS=10 PROFILES=3
```

## Non-Claims

This Fix1 does not authorize public RC, public launch, source export execution,
source publication, package publication, clean public tree materialization,
release artifacts, release keys, release envelopes, release signing, signatures,
Genesis/Atlas mutation or signing, v0.2 signing, CDL mutation, CDL-088 opening,
identity artifact creation, genesis record creation, seed commitment creation,
`identity_seed_commitment` creation, dummy Agent Birth artifact creation, public
serving, public P2P, public claimability/API activation, public confidential
messaging, wallet-facing activation, ECU minting, ILC settlement, wallet write
authority, or value-path activation.

## Graph Delta

```text
graph_delta=support_only:docs/antigravity_tasks/antigravity_prompt__phase_1322_g8_restore_vps_git_workflow_fix1.md,docs/specs/ilc_phase_1322_fix1_vps_git_workflow_restore_v0.1.json,docs/specs/ilc_phase_1322_fix1_vps_git_workflow_restore_v0.1.md,docs/phases/phase_1322_fix1_vps_git_workflow_restore_walkthrough.md,docs/phases/STATUS.md,docs/PLANNING_INDEX.md,docs/specs/ilc_antigravity_context_capsule_v5.54.md,tests/test_phase_1322_fix1_vps_git_workflow_restore.py -> planning/frontier
```
