#!/usr/bin/env bash
# check_reproducible_build.sh
# Deterministic rebuild gate for Phase 230 (D1 reproducibility baseline).
#
# Usage:
#   ./tools/check_reproducible_build.sh [--dry-run] [--help|-h]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"
SOURCE_DATE_EPOCH_VALUE="0"
PYTHON_HASH_SEED_VALUE="0"
GZIP_FLAGS_VALUE="-n"

usage() {
    cat <<'USAGE'
Usage: check_reproducible_build.sh [--dry-run] [--help|-h]

Options:
  --dry-run  Print deterministic command plan without executing.
  --help     Show this help text.
  -h         Show this help text.
USAGE
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        --help|-h)
            usage
            exit 0
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: phase-230 reproducible build commands"
    echo "  python3 -m venv <tmp>/build_venv"
    echo "  <tmp>/build_venv/bin/pip install build"
    echo "  create isolated source snapshots <tmp>/src_a and <tmp>/src_b from ${REPO_ROOT}"
    echo "  SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH_VALUE} PYTHONHASHSEED=${PYTHON_HASH_SEED_VALUE} GZIP=${GZIP_FLAGS_VALUE} <tmp>/build_venv/bin/python -m build --sdist --wheel <tmp>/src_a --outdir <tmp>/dist_a"
    echo "  SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH_VALUE} PYTHONHASHSEED=${PYTHON_HASH_SEED_VALUE} GZIP=${GZIP_FLAGS_VALUE} <tmp>/build_venv/bin/python -m build --sdist --wheel <tmp>/src_b --outdir <tmp>/dist_b"
    echo "  compare SHA-256 manifests for dist_a vs dist_b"
    exit 0
fi

echo "=== Phase 230 Reproducible Build Gate ==="

TMP_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/ilc_phase230_build_XXXXXX")"
trap 'rm -rf "${TMP_ROOT}"' EXIT

BUILD_VENV="${TMP_ROOT}/build_venv"
BUILD_PYTHON="${BUILD_VENV}/bin/python"
BUILD_PIP="${BUILD_VENV}/bin/pip"
SRC_A="${TMP_ROOT}/src_a"
SRC_B="${TMP_ROOT}/src_b"
DIST_A="${TMP_ROOT}/dist_a"
DIST_B="${TMP_ROOT}/dist_b"
MANIFEST_A="${TMP_ROOT}/manifest_a.txt"
MANIFEST_B="${TMP_ROOT}/manifest_b.txt"

mkdir -p "${SRC_A}" "${SRC_B}" "${DIST_A}" "${DIST_B}"

echo "Step 1/6: create isolated build virtualenv"
python3 -m venv "${BUILD_VENV}"

echo "Step 2/6: install build frontend"
"${BUILD_PIP}" install --quiet build

echo "Step 3/6: create isolated source snapshots"
python3 - "${REPO_ROOT}" "${SRC_A}" "${SRC_B}" <<'PY'
from __future__ import annotations

import pathlib
import shutil
import sys

source = pathlib.Path(sys.argv[1]).resolve()
dest_a = pathlib.Path(sys.argv[2]).resolve()
dest_b = pathlib.Path(sys.argv[3]).resolve()

ignore_dirs = {
    ".git",
    ".venv",
    "out",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
}
ignore_files = {".DS_Store"}


def ignore(_path: str, names: list[str]) -> set[str]:
    ignored: set[str] = set()
    for name in names:
        if name in ignore_dirs or name in ignore_files:
            ignored.add(name)
    return ignored


shutil.copytree(source, dest_a, dirs_exist_ok=True, ignore=ignore)
shutil.copytree(source, dest_b, dirs_exist_ok=True, ignore=ignore)
PY

echo "Step 4/6: deterministic build run A"
SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH_VALUE}" \
PYTHONHASHSEED="${PYTHON_HASH_SEED_VALUE}" \
GZIP="${GZIP_FLAGS_VALUE}" \
"${BUILD_PYTHON}" -m build --sdist --wheel "${SRC_A}" --outdir "${DIST_A}"

echo "Step 5/6: deterministic build run B"
SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH_VALUE}" \
PYTHONHASHSEED="${PYTHON_HASH_SEED_VALUE}" \
GZIP="${GZIP_FLAGS_VALUE}" \
"${BUILD_PYTHON}" -m build --sdist --wheel "${SRC_B}" --outdir "${DIST_B}"

echo "Step 6/6: compare artifact manifests"
python3 - "${DIST_A}" > "${MANIFEST_A}" <<'PY'
import hashlib
import pathlib
import sys
import tarfile

dist = pathlib.Path(sys.argv[1])


def normalized_sdist_digest(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with tarfile.open(path, "r:gz") as archive:
        for member in sorted(archive.getmembers(), key=lambda item: item.name):
            digest.update(member.name.encode("utf-8"))
            digest.update(str(member.type).encode("utf-8"))
            digest.update(str(member.mode).encode("utf-8"))
            if member.isfile():
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise RuntimeError(f"Unable to extract file member: {member.name}")
                digest.update(extracted.read())
            elif member.issym() or member.islnk():
                digest.update((member.linkname or "").encode("utf-8"))
    return digest.hexdigest()


for file_path in sorted(path for path in dist.iterdir() if path.is_file()):
    if file_path.name.endswith(".tar.gz"):
        digest = normalized_sdist_digest(file_path)
        print(f"{file_path.name} normalized_payload_sha256={digest}")
    else:
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        print(f"{file_path.name} sha256={digest}")
PY

python3 - "${DIST_B}" > "${MANIFEST_B}" <<'PY'
import hashlib
import pathlib
import sys
import tarfile

dist = pathlib.Path(sys.argv[1])


def normalized_sdist_digest(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with tarfile.open(path, "r:gz") as archive:
        for member in sorted(archive.getmembers(), key=lambda item: item.name):
            digest.update(member.name.encode("utf-8"))
            digest.update(str(member.type).encode("utf-8"))
            digest.update(str(member.mode).encode("utf-8"))
            if member.isfile():
                extracted = archive.extractfile(member)
                if extracted is None:
                    raise RuntimeError(f"Unable to extract file member: {member.name}")
                digest.update(extracted.read())
            elif member.issym() or member.islnk():
                digest.update((member.linkname or "").encode("utf-8"))
    return digest.hexdigest()


for file_path in sorted(path for path in dist.iterdir() if path.is_file()):
    if file_path.name.endswith(".tar.gz"):
        digest = normalized_sdist_digest(file_path)
        print(f"{file_path.name} normalized_payload_sha256={digest}")
    else:
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        print(f"{file_path.name} sha256={digest}")
PY

if ! cmp -s "${MANIFEST_A}" "${MANIFEST_B}"; then
    echo "Reproducible-build mismatch detected between run A and run B." >&2
    echo "--- run A manifest" >&2
    cat "${MANIFEST_A}" >&2
    echo "--- run B manifest" >&2
    cat "${MANIFEST_B}" >&2
    exit 1
fi

echo "Reproducible-build manifests match:"
cat "${MANIFEST_A}"
echo "Phase 230 reproducible build gate: PASS"
