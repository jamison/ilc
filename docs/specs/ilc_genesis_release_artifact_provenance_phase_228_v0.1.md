# ILC Genesis Release Artifact Provenance (Phase 228) v0.1

Status: Phase-228 release provenance artifact
Date: 2026-02-18

Source output path:
- `out/phase_228_release_artifacts/dist`

Build method summary:
1. Create isolated build virtualenv under `out/phase_228_release_artifacts/build_venv`.
2. Install `build` toolchain into that virtualenv.
3. Run `python -m build --sdist --wheel <repo> --outdir out/phase_228_release_artifacts/dist`.

## Artifact Checksums

| Artifact Type | Filename | SHA-256 | Source Path |
|---|---|---|---|
| wheel | `ilc_core-0.1.0-py3-none-any.whl` | `d1dfeca5d355c1bcf7bdca6bdc79f6ef9a0f0c2339ef846046fe320907d6b1e4` | `out/phase_228_release_artifacts/dist/ilc_core-0.1.0-py3-none-any.whl` |
| sdist | `ilc_core-0.1.0.tar.gz` | `d818ccac6affad086f6d5f49482bbb3d9339ccc972801978cc7d3d0941b36908` | `out/phase_228_release_artifacts/dist/ilc_core-0.1.0.tar.gz` |

## Verification note

Both artifacts were subsequently install-validated in clean virtual environments during Phase-228 execution.

## Provenance scope limitation

Checksums recorded here are from a single authoritative build at Phase-228 execution time.
They are not continuously re-verified by the test suite against fresh rebuild outputs.
Independent verification requires rebuilding from the same commit (for example with `python -m build`)
and comparing SHA-256 outputs with this artifact.
