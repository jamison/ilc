# ILC Public Release Workflow

**Version:** v0.1
**Date:** 2026-09-08
**Status:** committed mandatory agent workflow; not CDL-ratified
**Authority:** This document governs every `ilc-core` PyPI release. No package
version may be published without completing all mandatory steps in order.

---

## When This Workflow Applies

Run this workflow whenever any of the following change and need to reach public users:

- Any file under `ilc_core/` (runtime, CLI, genesis, network, sidecars, data)
- `tools/install.sh` (installer script)
- Any file under `skills/` that affects user-facing install or onboarding UX

Changes to `docs/`, `tests/`, phase prompts, walkthroughs, or planning specs do
**not** trigger a release cycle on their own.

---

## Version Bump Policy

| Change type | Bump |
|---|---|
| Bug fix, UX improvement, security patch | Patch (0.4.18 → 0.4.19) |
| New user-visible capability, new CLI surface | Minor (0.4.x → 0.5.0) |
| Breaking protocol change | Major (requires explicit governance phase) |

Only one package version is released per set of changes committed together. Batch
related changes into one version rather than releasing many micro-versions.

---

## Phase Naming Convention

Release phases use the GAP-PUBLIC-RC naming lane:

| Phase | Naming | Sensitivity |
|---|---|---|
| Local build + verification | `GAP-PUBLIC-RC-INVITE-PACKAGE-{VER}-00a` | NON-SENSITIVE |
| PyPI publish + sign + mirror | `GAP-PUBLIC-RC-INVITE-PACKAGE-{VER}-00b` | SENSITIVE |
| Smoke test | `GAP-PUBLIC-RC-INVITE-00c` (or versioned equivalent) | SENSITIVE |

After LAUNCH-00, sequential integer naming resumes; the same step structure applies.

---

## Step-by-Step Workflow

### Step 1 — Code and Tests (private repo)

- All `ilc_core/` changes are committed to the private repo `main` branch.
- Full test suite passes: `.venv/bin/python -m pytest tests/ -q`.
- No `assert` in production paths; no `import random`; no bare floats for ECU values.
- LMDB/graph intake: every new file in `ilc_core/`, `tests/`, `docs/specs/`,
  `docs/antigravity_tasks/`, or `tools/` requires a candidate node record in
  `docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json` (see CLAUDE.md
  §Graph Intake Protocol). Write atomically (`tempfile.mkstemp` + `os.replace`).
- Commit all files including ledger update in a single atomic commit.

### Step 2 — Version Bump

Update these two files atomically (same commit or immediately before Step 3):

```
pyproject.toml          [project] version = "X.Y.Z"
ilc_core/__init__.py    __version__ = "X.Y.Z"
```

Verify: `python3 -c "import ilc_core; print(ilc_core.__version__)"` → new version.

### Step 3 — Local Build (NON-SENSITIVE)

```bash
python -m build
twine check dist/ilc_core-{VER}-py3-none-any.whl dist/ilc_core-{VER}.tar.gz
```

Record and verify:

| Artifact | Expected | Command |
|---|---|---|
| Wheel SHA-256 | (compute) | `sha256sum dist/ilc_core-{VER}-py3-none-any.whl` |
| Wheel size | (compute) | `wc -c < dist/ilc_core-{VER}-py3-none-any.whl` |
| Sdist SHA-256 | (compute) | `sha256sum dist/ilc_core-{VER}.tar.gz` |
| Sdist size | (compute) | `wc -c < dist/ilc_core-{VER}.tar.gz` |

Verify wheel contents contain the expected changed symbols:

```bash
python3 -c "
import zipfile
whl = 'dist/ilc_core-{VER}-py3-none-any.whl'
with zipfile.ZipFile(whl) as z:
    src = z.read('ilc_core/cli/main.py').decode()
    assert 'SYMBOL_TO_CHECK' in src
    print('PASS')
"
```

Quarantine any stale `dist/` artifacts from prior versions before upload.

Commit the version bump if not already committed. Record SHA-256 and size in the
build receipt at `docs/specs/ilc_package_build_receipt_GAP_..._00a_v0.1.json`.

### Step 4 — Signing Ceremony (SENSITIVE — offline key required)

Compute signed preimages:

```python
from ilc_core.release.installable_release_signature import compute_signed_preimage_sha256
wheel_preimage = compute_signed_preimage_sha256(
    release_id="ilc-core-{VER}",
    artifact_id="ilc-artifact:ilc-core-python-wheel-{VER_NODOT}@phase-{PHASE}",
    artifact_sha256="{WHEEL_SHA256}",
)
sdist_preimage = compute_signed_preimage_sha256(
    release_id="ilc-core-{VER}",
    artifact_id="ilc-artifact:ilc-core-python-sdist-{VER_NODOT}@phase-{PHASE}",
    artifact_sha256="{SDIST_SHA256}",
)
```

Operator signs the raw 32 bytes decoded from each preimage hex with the offline
Phase 1335 Ed25519 release key:

```python
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from pathlib import Path

key = load_pem_private_key(Path(RELEASE_KEY_PATH).read_bytes(), password=None)
wheel_sig = key.sign(bytes.fromhex(wheel_preimage)).hex()
sdist_sig = key.sign(bytes.fromhex(sdist_preimage)).hex()
```

**Hard stop:** Do not proceed to PyPI upload without valid signatures.
The signatures go into the release envelope set (see Step 6).

### Step 5 — PyPI Publish (SENSITIVE)

```bash
twine upload dist/ilc_core-{VER}-py3-none-any.whl dist/ilc_core-{VER}.tar.gz
```

Explicit filenames only — never `dist/*`.

Fetchback verification:

```python
import requests
resp = requests.get(f"https://pypi.org/pypi/ilc-core/{VER}/json")
data = resp.json()
for f in data["urls"]:
    print(f["filename"], f["digests"]["sha256"], f["size"])
# Verify SHA-256 and size match Step 3 values exactly.
```

**Hard stop:** If fetchback SHA-256 or size does not match local build, yank
immediately and halt. Do not proceed.

### Step 6 — Yank Previous Version

Yank the immediately preceding active version:

```
Reason: superseded by {VER} which <one-line description of key change>
```

Verify via PyPI JSON API: `releases[PREV_VER][0]["yanked"] == True`.

Policy: always yank the immediate predecessor. Earlier yanked versions are not
re-yanked. If yank cannot complete programmatically, do it manually before
proceeding.

### Step 7 — Release Envelope Set

Produce a release envelope set analogous to
`docs/specs/ilc_core_{PREV_VER}_release_envelopes_*.json`:

```json
{
  "schema_version": "ilc_release_envelope_v0.1",
  "package_name": "ilc-core",
  "version": "{VER}",
  "artifacts": [
    {
      "filename": "ilc_core-{VER}-py3-none-any.whl",
      "sha256": "<wheel_sha256>",
      "size": <wheel_size>,
      "signed_preimage_sha256": "<wheel_preimage>",
      "ed25519_signature_hex": "<wheel_sig>",
      "signer_public_key_hex": "<phase_1335_pubkey>"
    },
    {
      "filename": "ilc_core-{VER}.tar.gz",
      "sha256": "<sdist_sha256>",
      "size": <sdist_size>,
      "signed_preimage_sha256": "<sdist_preimage>",
      "ed25519_signature_hex": "<sdist_sig>",
      "signer_public_key_hex": "<phase_1335_pubkey>"
    }
  ]
}
```

Validate with the existing envelope validator. Write atomically.

Commit the envelope to the private repo.

### Step 8 — tools/install.sh Update

Update `tools/install.sh`:
- Wheel SHA-256 and size → new values from Step 3
- Version string → `{VER}`
- Envelope ref URL → public HTTPS URL for the envelope JSON
- Signer public key hex → unchanged (same Phase 1335 key)

Verify locally: `tools/install.sh --verify-signature` passes against the PyPI-fetched artifact.

### Step 9 — LMDB and Graph Slice Update

For any new `ilc_core/` modules or updated graph-relevant files:

1. Confirm node records are present in
   `docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json` (written in Step 1).
2. Run the graph coverage audit: `python tools/graph_coverage_audit.py`.
3. If the release adds new protocol-layer modules (new CDL-bearing paths), open
   a graph update phase to register them as `load_bearing_artifact_added` nodes
   before the release goes fully public.
4. LMDB production state (on VPS): no LMDB mutation occurs during a packaging
   release. LMDB state is only mutated by epoch transition phases with explicit GO.

### Step 10 — Public Mirror Refresh

Run the current ratified public mirror path from the exact `source_private_commit`
(the HEAD after all release commits). If the phase uses the full filtered mirror
generator, use:

```bash
bash tools/scripts/generate_public_mirror.sh "$SOURCE_WORKTREE" "$OUTPUT_DIR"
```

If the phase uses append-only public sync, use
`tools/public_release_append_only_sync.py` per that phase prompt.

Verify:
- Denylist scan: pass
- `PUBLIC_RC_EXCLUDE` scan: pass (no internal prompts or keys leak)
- Public-head safety: either append-only check
  `previous_public_head_is_ancestor=true` for append-only sync mode, or an
  explicit `--force-with-lease` bound to the exact previous public head for full
  filtered mirror replacement mode

Push to public remote. Record:
- `source_private_commit`
- `candidate_public_head`
- append-only receipt path or filtered-mirror receipt path

Verify the envelope URL resolves publicly:

```bash
curl -fsSL {ENVELOPE_URL} | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['version'])"
```

### Step 11 — ClawHub Skill Update

Trigger if **any** of the following changed:
- Install command syntax or UX
- Version referenced in the skill (`pip install ilc-core==X.Y.Z`)
- Onboarding flow (invite path, identity init, new CLI commands)
- Contact information or authority boundary

Steps:
1. Update `skills/ilc/SKILL.md` with the new version and any UX changes.
2. Commit to private repo.
3. Run the current public mirror path (Step 10 covers this if done after SKILL.md commit).
4. `clawhub skill publish skills/ilc --slug ilc --version {SKILL_VER} --tags latest ...`
5. Verify: `clawhub skill verify ilc --json` → `security.status: clean`, correct SKILL.md size.
6. Note: ClawHub tag propagation may lag by 1–3 versions due to async security scanning.
   If `latest` does not advance, publish one more patch version to push past pending
   scan states.

### Step 12 — STATUS.md Token and PLANNING_INDEX Update

Append to `docs/phases/STATUS.md`:

```
## GAP-PUBLIC-RC-PACKAGE-{VER}-00b COMPLETE

Output token: invite_enforcement_package_{VER_NODOT}_published_GAP_PUBLIC_RC_INVITE_PACKAGE_{VER_NODOT}_00B

PyPI version: {VER} (active, not yanked)
Yanked: {PREV_VER}
Source private commit: {COMMIT}
Public mirror head: {PUBLIC_HEAD}
Envelope: {ENVELOPE_URL}
```

Update `docs/PLANNING_INDEX.md §0`:
- Frontier row → next phase after packaging
- Last updated line

### Step 13 — Smoke Test (SENSITIVE)

Run the versioned smoke test phase (`GAP-PUBLIC-RC-INVITE-00c` or successor):
- Install from PyPI in a clean venv: `pip install ilc-core=={VER}`
- Verify `ilc_core.__version__ == "{VER}"`
- Exercise durable LMDB nullifier registration and restart-persistent replay rejection
- Exercise the shortcode path (if changed in this release)
- Record evidence JSON atomically
- Run all smoke tests: `pytest tests/test_gap_public_rc_invite_00c_bootstrap_smoke.py -v`
- Emit output token only after all scenarios pass

---

## Non-Mutual-Exclusion Rule

Steps 9 (LMDB/graph) and 11 (ClawHub) may be deferred to a follow-on phase if
the release is time-critical, **only if**:
- The deferral is explicitly named in the release phase walkthrough
- A follow-on phase is opened immediately with a named blocker token
- No epoch transition or user onboarding runs before the deferred steps close

Steps 1–8 and 13 are never deferrable.

---

## Commit Discipline

Each release requires these commits in order (may be batched if no pre-commit hook
separation is required):

| Commit | Contents |
|---|---|
| `feat(core): <description> ({VER})` | Runtime changes, test changes |
| `chore(release): bump version to {VER}` | `pyproject.toml`, `ilc_core/__init__.py` |
| `feat(release): publish signed {VER} artifacts` | Envelope JSON, receipt JSON |
| `chore(install): retarget install.sh to {VER}` | `tools/install.sh` |
| `feat(skill): update ilc ClawHub skill for {VER}` | `skills/ilc/SKILL.md` |

Do not combine runtime changes and CDL/ADR mutations in the same commit
(pre-commit hook enforces separation).

---

## Hard Stops

Stop and surface to human before proceeding if:

1. Fetchback SHA-256 does not match local build
2. Signing ceremony cannot complete (offline key unavailable)
3. `twine check` fails
4. Public mirror safety check fails: append-only ancestry fails in append-only
   mode, or force-with-lease previous-head binding cannot be proven in filtered
   mirror replacement mode
5. Smoke test fails any scenario
6. `INVITE_ENFORCEMENT_ENABLED` is not `True` in the published wheel
7. ClawHub security scan returns `suspicious` on the `latest` version after retry

---

## Reference Files

| File | Purpose |
|---|---|
| `docs/specs/ilc_package_build_receipt_GAP_*_00a_v0.1.json` | Per-release build receipt template |
| `docs/specs/ilc_core_{VER}_release_envelopes_*.json` | Per-release envelope set |
| `tools/install.sh` | Public signed installer |
| `ilc_core/release/installable_release_signature.py` | `compute_signed_preimage_sha256()` |
| `docs/phases/STATUS.md` | Token ledger |
| `docs/PLANNING_INDEX.md` | Session frontier |
| `docs/specs/ilc_fix38_manual_edge_annotation_ledger_v0.1.json` | Graph node registry |
