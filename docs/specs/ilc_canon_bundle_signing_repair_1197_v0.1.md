# ILC Canon Bundle Signing Repair 1197 v0.1

**Phase:** 1197
**Window:** 1191-1199
**Date:** 2026-05-05
**Status:** PASS
**Token:** `canon_bundle_signing_repair_pass_phase_1197`

---

## 1. Scope

Phase 1197 repaired the canon bundle signing/report/audit regression named in roadmap
v1.0 Gap 6:

- `tests/test_canon_bundle_audit_artifact.py`
- `tests/test_canon_bundle_pipeline_report.py`

This was a tooling/test-fixture repair only. No signed Genesis v0.1 artifact, immutable
diagnostic artifact, CDL register row, runtime protocol surface, release key, or public
launch state was mutated.

---

## 2. Failure

The affected tests built a bundle with this partial export payload:

```python
{"canon_hash": "abc123", "canon_export_format": "v0.1"}
```

That payload declares `canon_export_format = "v0.1"` but does not carry the required v0.1
shape (`exported_at`, `meta`, `epochs`, `snapshots`). The production pipeline correctly
delegates bundle export validation to `validate_canon_export_v0_1`, which rejects malformed
v0.1 exports. Because the fixture failed validation before signing, downstream report and
audit assertions could not reach the intended sign/verify/report/audit path.

---

## 3. Repair

The repair adds a deterministic testing snapshot:

```text
tests/fixtures/canon_bundle_valid_export_v0_1_snapshot.json
```

The two affected test files now use an explicit test-only toggle:

```python
USE_TESTING_CANON_EXPORT_SNAPSHOT = True
```

When the toggle is enabled, fixtures build canon bundles from the deterministic valid v0.1
snapshot rather than from an invalid partial export. This preserves production behavior:
the CLI pipeline and bundle validator still reject malformed v0.1 exports by default.

The toggle is intentionally visible migration debt. Before eventual production hardening of
the canon bundle test surface, this should either be replaced by a reusable canonical export
fixture factory or removed after all tests emit fully valid v0.1 exports directly.

---

## 4. Verification

Required Phase 1197 check:

```bash
.venv/bin/python -m pytest tests/test_canon_bundle_audit_artifact.py tests/test_canon_bundle_pipeline_report.py -q
```

Result:

```text
17 passed
```

Phase assertion check:

```bash
.venv/bin/python -m pytest tests/test_phase_1197_canon_bundle_signing_repair.py -q
```

---

## 5. Guardrails

- Production validation was not weakened.
- No CLI testing bypass was added.
- No signed Genesis v0.1 artifact was touched.
- No immutable diagnostic artifact was regenerated intentionally or committed.
- No runtime/economic path was modified.
- Canonical JSON discipline is preserved by the existing bundle writer.

`canon_bundle_signing_repair_pass_phase_1197`
