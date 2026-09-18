# ILC Release Pipeline Template

**Version:** v0.1
**Date:** 2026-09-18
**Applies to:** all future `ilc-core` public-RC releases
**Relationship to `docs/specs/ilc_public_release_workflow_v0.1.md`:** this document is the per-release checklist operationalization of the public release workflow. Both remain authoritative. If they differ, stop and reconcile before publishing.

## Preamble

Use this template whenever runtime, CLI, installer, user-facing skill, or package metadata changes must reach public users through a new `ilc-core` release. Documentation-only, test-only, or planning-only changes do not trigger a package release unless a phase prompt explicitly says they must be packaged.

Release work is split into:

- **Track A:** NON-SENSITIVE local build and preflight. No PyPI upload, no release signing, no mirror push.
- **Track B:** SENSITIVE publish/sign/mirror. Requires an exact Genesis GO phrase for the release phase.
- **Post-Publish Conditional Gates:** smoke tests and skill updates required by the existing workflow when applicable.

## Known Hazards

1. **cbor2 6.x resolver hazard.** `cbor2` 6.x has no binary wheel for the project’s Intel macOS / Python 3.12 fetchback baseline and can fail source-build without the needed Rust/toolchain setup. Every release carrying `cbor2` must preserve `cbor2>=5.9.0,<6` unless a security review replaces the pin. Track A must prove a clean dry-run resolves `cbor2-5.x`, not `cbor2-6.x`.

2. **Clean fetchback Python.** Use `/usr/local/bin/python3.12` for clean public-install proof when available. Earlier fetchback attempts using the repo-default Python selected an unsupported dependency build path and blocked release verification.

3. **GitHub Release sequencing.** Do not create the helper binary GitHub Release before the public mirror push. The release tag must target the post-push public mirror head. The 0.4.26 lane showed that pre-push helper release creation can root the tag at the wrong commit.

4. **GitHub asset upload instability.** Prefer a two-step release creation and bounded asset upload: create the release with `gh api`, then upload with `curl --upload-file --max-time 300 --retry 3`. If upload fails, remove any empty release/tag before blocking.

5. **Signing preimages are build outputs.** Wheel and sdist signing preimages are unknown until Track A computes artifact hashes. Never pre-fill signing preimages in a Track B prompt. Read them from the Track A build receipt.

6. **Mirror append-only may fail.** Attempt append-only or current ratified mirror path first. If denylist/object-database history requires full filtered regeneration, stop for explicit Genesis authorization and force-with-lease bind to the exact previous public head.

## Track A — NON-SENSITIVE: Local Build and Preflight

### A1 — Worktree Hygiene

Record:

```bash
git rev-parse HEAD
git status --short
```

Hard stop on unexpected dirty tracked files. Leave unrelated known-dirty files unstaged.

### A2 — Version Bump

Patch both version sentinels atomically:

```text
pyproject.toml       version = "{VER}"
ilc_core/__init__.py __version__ = "{VER}"
```

Verify:

```bash
grep -n "^version" pyproject.toml
grep "__version__" ilc_core/__init__.py
python3 -c "import ilc_core; print(ilc_core.__version__)"
```

### A3 — Build

Remove stale artifacts first:

```bash
rm -rf dist/
.venv/bin/python -m build
```

Expected artifacts:

```text
dist/ilc_core-{VER}-py3-none-any.whl
dist/ilc_core-{VER}.tar.gz
```

### A4 — Twine Check

```bash
.venv/bin/python -m twine check \
  dist/ilc_core-{VER}-py3-none-any.whl \
  dist/ilc_core-{VER}.tar.gz
```

Hard stop on any warning promoted by the release prompt or any error.

### A5 — Hash and Size

```bash
shasum -a 256 dist/ilc_core-{VER}-py3-none-any.whl dist/ilc_core-{VER}.tar.gz
wc -c < dist/ilc_core-{VER}-py3-none-any.whl
wc -c < dist/ilc_core-{VER}.tar.gz
```

These four values become authoritative for Track B.

### A6 — Dependency Dry-Run

Use `/usr/local/bin/python3.12` when available:

```bash
TMP_DRY="$(mktemp -d /tmp/ilc-{VER_NODOT}-dryrun.XXXXXX)"
/usr/local/bin/python3.12 -m venv "${TMP_DRY}"
"${TMP_DRY}/bin/python" -m pip install --upgrade pip --quiet
"${TMP_DRY}/bin/python" -m pip install --dry-run --no-cache-dir \
  dist/ilc_core-{VER}-py3-none-any.whl
```

Hard stops:

- at least one resolver line must match `cbor2-5.`
- no resolver line may match `cbor2-6.`
- no resolver output may mention building a `cbor2` wheel, Rust, or cargo

### A7 — Outside-Repo Wheel Boundary Smoke

Use a temporary cwd outside the repository and install the local wheel with `--no-deps`:

```bash
TMP_SMOKE="$(mktemp -d /tmp/ilc-{VER_NODOT}-smoke.XXXXXX)"
/usr/local/bin/python3.12 -m venv "${TMP_SMOKE}/venv"
cd "${TMP_SMOKE}"
"${TMP_SMOKE}/venv/bin/python" -m pip install --no-deps --no-cache-dir \
  /absolute/path/to/dist/ilc_core-{VER}-py3-none-any.whl
"${TMP_SMOKE}/venv/bin/python" - <<'PY'
from pathlib import Path
import ilc_core
assert ilc_core.__version__ == "{VER}"
assert Path(ilc_core.__file__).resolve().is_relative_to(Path("{TMP_SMOKE}/venv").resolve())
print("wheel_boundary_smoke_pass")
PY
```

Do not use `sys.path.insert()` or `PYTHONPATH`.

### A8 — Wheel Content Inspection

Inspect the wheel for every release-relevant change:

```bash
.venv/bin/python - <<'PY'
import zipfile
with zipfile.ZipFile("dist/ilc_core-{VER}-py3-none-any.whl") as z:
    names = set(z.namelist())
    assert "ilc_core/__init__.py" in names
    print("wheel_content_inspection_pass")
PY
```

Add phase-specific assertions for changed modules.

### A9 — Focused Tests

Always include release signing, installer, and changed-surface tests. For releases carrying AgentID submit fixes, include:

```bash
.venv/bin/python -m pytest \
  tests/test_gap_epoch_00d_preflight_fix1_circular_import.py \
  tests/test_phase_652_ecu_ilc_lifecycle_runtime.py \
  tests/test_gap_release_sign_00b_signature_schema.py \
  tests/test_gap_public_install_02_install_sh.py \
  tests/test_phase_874_d2e_submit_cli.py \
  -q --tb=short
```

Hard stop on failure.

### A10 — Fix38 Ledger Entries

Every new or modified file in `ilc_core/`, `tests/`, `docs/specs/`, `docs/antigravity_tasks/`, or `tools/` requires a Fix38 ledger entry in the same release commit. Write the ledger atomically with `tempfile.mkstemp` and `os.replace`.

This is a per-release obligation. It is distinct from CDL-098 Atlas LMDB materialization.

### A11 — Signing Preimages

Compute preimages from actual artifact hashes:

```python
from ilc_core.release.installable_release_signature import compute_signed_preimage_sha256

wheel_preimage = compute_signed_preimage_sha256(
    release_id="ilc-core-{VER}",
    artifact_id="ilc-artifact:ilc-core-python-wheel-{VER_NODOT}@phase-1628",
    artifact_sha256="{WHEEL_SHA256}",
)
sdist_preimage = compute_signed_preimage_sha256(
    release_id="ilc-core-{VER}",
    artifact_id="ilc-artifact:ilc-core-python-sdist-{VER_NODOT}@phase-1628",
    artifact_sha256="{SDIST_SHA256}",
)
```

Record both values in the build receipt. Do not sign in Track A.

### A12 — Build Receipt

Write `docs/specs/ilc_package_build_receipt_GAP_PACKAGE_{VER_NODOT}_00a_v0.1.json` atomically. Required fields:

- schema version, phase, release id, predecessor release id
- source private commit before version bump
- changes from predecessor
- wheel/sdist paths, SHA-256 values, and sizes
- cbor2 dry-run proof
- wheel-boundary smoke proof
- focused test output summary
- signing preimages
- output token
- non-claims

### A13 — Prompt Validation

Validate both release prompts:

```bash
python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_gap_package_{VER_NODOT}_00a_*.md
python3 tools/validate_phase_prompt.py docs/antigravity_tasks/antigravity_prompt__phase_gap_package_{VER_NODOT}_00b_*.md
```

### A14 — Track A Completion Commit

Stage only release-local files. Do not commit `dist/`.

## Hard Stop Between Track A and Track B

Before Track B, Genesis must confirm:

1. the Phase 1335 offline signing key is accessible to Genesis;
2. the Track A receipt hashes, sizes, and preimages are reviewed;
3. the exact GO phrase is issued in the current chat:

```text
GO Phase GAP-PACKAGE-{VER_NODOT}-00b PUBLISH-AUTHORIZED
```

Codex must not search for, read, or use the private signing key.

## Track B — SENSITIVE: Publish, Sign, Mirror

### B1 — Immediate Preflight

Confirm:

- Track A output token is present
- Track B output token is absent
- local `dist/` files match the Track A receipt exactly
- `twine check` still passes
- PyPI does not already have `{VER}`
- active superseded predecessor versions are identified

### B2 — Signing Ceremony

Present the Track A preimages to Genesis. Genesis signs the raw 32 bytes decoded from each preimage hex using the Phase 1335 Ed25519 key. Codex verifies supplied signatures against:

```text
5bf71c1e0ac93f2d7414b0dc315161fc4a57462c198ba1618e2890ec89a5b15a
```

Hard stop if verification fails.

### B3 — PyPI Upload

Use explicit filenames only:

```bash
.venv/bin/python -m twine upload \
  dist/ilc_core-{VER}-py3-none-any.whl \
  dist/ilc_core-{VER}.tar.gz
```

Never upload with `dist/*`.

### B4 — PyPI Fetchback

From an outside-repo cwd, use a clean `/usr/local/bin/python3.12` venv:

```bash
pip install --no-cache-dir ilc-core=={VER}
```

Assert:

- PyPI JSON SHA-256 and size match Track A
- `ilc_core.__version__ == "{VER}"`
- `cbor2` resolves to 5.x
- circular-import fresh-process checks pass
- release-relevant guard imports pass
- module paths resolve inside the fetchback venv

### B5 — Yank Superseded Active Versions

Yank the immediate predecessor. If an earlier incomplete publish left another superseded active version, yank it too and record a separate reason. Confirm via PyPI JSON.

### B6 — Release Envelopes and Installable Manifest

Write atomically:

- `docs/specs/ilc_core_{VER_NODOT}_release_envelopes_GAP_PACKAGE_{VER_NODOT}_00b_v0.1.json`
- `docs/specs/ilc_installable_manifest_GAP_PACKAGE_{VER_NODOT}_00b_v0.1.json`

Envelope artifact IDs must use `@phase-1628` unless a later ratified authority changes the phase suffix.

### B7 — Helper Tarball Local Verification

If Rust helpers are unchanged, verify and re-tag the predecessor helper payload. Current unchanged helper payload baseline:

```text
SHA-256 ced6fcb008d45efe8c9361fb5ee4de52a11c99e195f7279367bd0c43746d63a9
size 4560519
```

Do not create the GitHub Release here.

### B8 — Retarget `tools/install.sh`

Update all wheel, envelope, manifest, signer, version, helper URL, helper hash, and helper size fields. The helper URL may be deterministic before the release exists, but the GitHub Release asset must be uploaded later at the post-push public head.

Run installer/version sentinel tests after retargeting.

### B9 — Source Commit

Commit release envelopes, manifest, installer retarget, upload receipt draft if applicable, walkthrough/status/planning updates, and Fix38 ledger entries.

### B10 — Public Mirror

Run the ratified mirror pipeline from the exact committed source state. Attempt append-only/current path first. If full filtered regeneration is needed, stop for explicit Genesis authorization and push with force-with-lease bound to the exact previous public head.

Record:

- source private commit
- previous public head
- post-push public head
- denylist scan result
- `PUBLIC_RC_EXCLUDE` scan result

### B11 — GitHub Release at Post-Push Head

Create GitHub Release `v{VER}` with target equal to the post-push public mirror head. Upload the helper tarball asset using the bounded two-step API/curl pattern. Confirm asset state is `uploaded`.

### B12 — Raw-GitHub Fetchback

Fetch public raw URLs for:

- `tools/install.sh`
- release envelopes
- installable manifest
- monthly-close runner

Confirm internal/private exclusions, including `ADR_0016`, return 404 where required.

### B13 — Upload Receipt and STATUS

Write `docs/specs/ilc_pypi_upload_receipt_GAP_PACKAGE_{VER_NODOT}_00b_v0.1.json` atomically and append the package publish output token only after all Track B checks pass.

## Post-Publish Conditional Gates

The existing public release workflow includes conditional user-surface and smoke obligations:

- If install command syntax, onboarding UX, skill text, invite flow, or public CLI surface changed, update and publish the relevant user-facing skill/doc surface in a named follow-on phase.
- Run the release-specific smoke phase before relying on the release for public onboarding, unless the phase prompt explicitly routes the smoke to a named downstream phase with a blocker token.

For the post-LAUNCH mini-window, these obligations are routed to:

- `GAP-PUBLIC-RC-HELLO-WORLD-00a`
- `GAP-PUBLIC-RC-HELLO-WORLD-00b`
- `GAP-ECU-ATTRIBUTION-PIPELINE-SMOKE-00`

## CDL-098 Atlas Note

Fix38 ledger entries are per-release mandatory. CDL-098 Atlas LMDB materialization is periodic and threshold-triggered. Do not conflate the two:

- Fix38 ledger entries: candidate/intake record for every release-touched graph-relevant file
- CDL-098 materialization: separate 00a/00b Atlas LMDB materialization cycle, sensitive when it writes/signs

## Step Coverage Against `ilc_public_release_workflow_v0.1.md`

| Workflow step | Template coverage |
|---|---|
| Step 1 Code and Tests | Track A A1, A9, A10 |
| Step 2 Version Bump | Track A A2 |
| Step 3 Local Build | Track A A3-A8, A12 |
| Step 4 Signing Ceremony | Hard stop + Track B B2 |
| Step 5 PyPI Publish | Track B B1-B4 |
| Step 6 Yank Previous Version | Track B B5 |
| Step 7 Release Envelope Set | Track B B6 |
| Step 8 `tools/install.sh` Update | Track B B8 |
| Step 9 LMDB and Graph Slice Update | Track A A10 and CDL-098 Atlas note |
| Step 10 Public Mirror Refresh | Track B B10-B12 |
| Step 11 ClawHub Skill Update | Post-Publish Conditional Gates |
| Step 12 STATUS/PLANNING_INDEX Update | Track A A14 and Track B B13 |
| Step 13 Smoke Test | Post-Publish Conditional Gates |

## Non-Claims

This template does not publish to PyPI, sign artifacts, mutate LMDB, push the public mirror, change runtime code, activate guards, advance epochs, mint ECU, settle ILC, or replace the existing release workflow spec.
