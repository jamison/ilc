# ILC Installable Release Manifest Schema GAP-PUBLIC-INSTALL-01 v0.1

**Phase:** GAP-PUBLIC-INSTALL-01
**Date:** 2026-08-06
**Status:** SCHEMA EXTENSION COMMITTED
**Authority:** CDL-086 ratified at Phase 1220

`installable_release_manifest_schema_committed_GAP_PUBLIC_INSTALL_01`

## 1. Relationship To 1213 Schema

This schema extends `docs/specs/ilc_release_artifact_manifest_schema_1213_v0.1.md`
by reference. It does not modify or supersede the 1213 document.

Every artifact record in an installable release manifest must satisfy all Phase
1213 required fields and all GAP-PUBLIC-INSTALL-01 installer fields. The 1213
artifact types remain valid. This schema only adds installer-required metadata
and three additional artifact types.

## 2. Additional Required Fields Per Artifact

| Field | Type | Rule |
|---|---|---|
| `platform` | string | One of `linux`, `darwin`, `windows`, `any` |
| `arch` | string | One of `amd64`, `arm64`, `any` |
| `channel` | string | One of `stable`, `rc`, `dev` |
| `size_bytes` | integer | Positive integer; zero, negative values, booleans, floats, `NaN`, and infinities are invalid |
| `download_url` | string | Non-empty HTTPS URL; HTTP and placeholder URLs are invalid |

## 3. Conditional Required Fields

| Field | Required when | Rule |
|---|---|---|
| `min_python_version` | `artifact_type` is `python_wheel` or `python_sdist` | Python major/minor string such as `3.10`; records the effective minimum version constraint for Python package installers |

`min_python_version` is omitted for non-Python artifact types.

## 4. Extended Allowed Artifact Types

The combined allowed artifact type list is:

```text
runtime_module
genesis_bundle
cli_binary
documentation_bundle
source_release_tarball
public_repository_tag
container_image
star_map_release_envelope
operator_bootstrap_bundle
verification_bundle
python_wheel
python_sdist
install_script
```

## 5. Allowed Values

| Field | Allowed values |
|---|---|
| `platform` | `linux`, `darwin`, `windows`, `any` |
| `arch` | `amd64`, `arm64`, `any` |
| `channel` | `stable`, `rc`, `dev` |
| `signing_status` | `signed`, `unsigned`, `deferred` |

`download_url` must start with `https://`. The `ilc-core 0.2.0` instance manifest
uses exact `https://files.pythonhosted.org/...` URLs resolved from the PyPI JSON
API.

## 6. Canonical Hash Rule

The canonical hash rule is inherited from Phase 1213:

```text
sha256:<64 lowercase hex characters>
```

Only SHA-256 is valid. Uppercase hex, MD5, SHA-512, empty hash values, and
non-prefixed digests are invalid.

## 7. Machine Validator

`ilc_core/release/installable_release_manifest.py` validates the combined field
set. The validator uses deterministic JSON serialization for canonical bytes:

```python
json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
```

JSON loading rejects `NaN`, `Infinity`, and `-Infinity` through a fail-closed
`parse_constant` hook.

## 8. Non-Claims

| Non-claim | Status |
|---|---|
| Phase 1213 schema mutation | Not performed |
| PyPI upload, re-upload, or yank | Not performed |
| Root `install.sh` implementation | Not performed |
| `ilc update` implementation | Not performed |
| Binary build or cross-compilation | Not performed |
| Manifest signing | Not performed; current PyPI artifact records use `signing_status = "unsigned"` |
| CDL mutation | Not performed; CDL-086 authority is reused |
| Guard clearance | Not performed |
| Public mirror push | Not performed |
| Public RC activation | Not performed |

```text
mirror_disposition=not_stale_no_sensitive_content
```
