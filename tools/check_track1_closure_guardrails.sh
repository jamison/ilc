#!/usr/bin/env bash
# check_track1_closure_guardrails.sh
# Deterministic Track 1 closure gate for edge-removal guardrails.
#
# Usage:
#   ./tools/check_track1_closure_guardrails.sh [--dry-run]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

DRY_RUN="false"

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

cd "${REPO_ROOT}"

PYTEST_CMD=(python3 -m pytest tests/test_edge_removal_phase1_guardrails.py tests/test_graph_edges.py -q)
DIRECT_APPEND_PATTERN='\.edges\.append\('
EDGE_SYMBOL_PATTERN='from\s+[.\w]+types\s+import\s+.*\bEdge\b|\bEdge\('
EDGES_ATTR_PATTERN='\.edges\b'

if [ "${DRY_RUN}" = "true" ]; then
    echo "Dry run: Track 1 closure guardrail gate commands"
    echo "  ${PYTEST_CMD[*]}"
    echo "  rg -n \"${DIRECT_APPEND_PATTERN}\" ilc_core tests | sort"
    echo "  rg -n \"${EDGE_SYMBOL_PATTERN}\" ilc_core tests | sort"
    echo "  rg -n \"${EDGES_ATTR_PATTERN}\" ilc_core tests | sort"
    exit 0
fi

echo "=== Track 1 Closure Guardrail Gate ==="
echo "Step 1/4: guardrail test subset"
"${PYTEST_CMD[@]}"

echo "Step 2/4: direct .edges.append detection"
direct_append_output="$(rg -n "${DIRECT_APPEND_PATTERN}" ilc_core tests | sort || true)"
if [ -n "${direct_append_output}" ]; then
    echo "Track 1 closure violation: direct .edges.append usage detected:" >&2
    printf "%s\n" "${direct_append_output}" >&2
    exit 1
fi
echo "  OK: no .edges.append usage"

echo "Step 3/4: Edge symbol detection"
edge_symbol_output="$(rg -n "${EDGE_SYMBOL_PATTERN}" ilc_core tests | sort || true)"
if [ -n "${edge_symbol_output}" ]; then
    echo "Track 1 closure violation: Edge symbol usage detected:" >&2
    printf "%s\n" "${edge_symbol_output}" >&2
    exit 1
fi
echo "  OK: no Edge symbol usage"

echo "Step 4/4: .edges attribute usage allowlist check"
edges_attr_output="$(rg -n "${EDGES_ATTR_PATTERN}" ilc_core tests | sort || true)"
if [ -z "${edges_attr_output}" ]; then
    echo "Track 1 closure violation: expected sentinel .edges references were not found." >&2
    exit 1
fi

found_guardrail_file="false"
found_sentinel_file="false"
unexpected_lines=""

while IFS= read -r line; do
    [ -z "${line}" ] && continue
    path="${line%%:*}"
    case "${path}" in
        tests/test_edge_removal_phase1_guardrails.py)
            found_guardrail_file="true"
            ;;
        tests/test_graph_edges.py)
            found_sentinel_file="true"
            ;;
        *)
            unexpected_lines="${unexpected_lines}${line}
"
            ;;
    esac
done <<EOF
${edges_attr_output}
EOF

if [ -n "${unexpected_lines}" ]; then
    echo "Track 1 closure violation: unexpected .edges attribute usage path(s):" >&2
    printf "%s" "${unexpected_lines}" >&2
    exit 1
fi

if [ "${found_guardrail_file}" != "true" ] || [ "${found_sentinel_file}" != "true" ]; then
    echo "Track 1 closure violation: expected allowlist paths are missing in .edges output." >&2
    printf "%s\n" "${edges_attr_output}" >&2
    exit 1
fi

echo "  OK: .edges references constrained to allowlist"
echo "Track 1 closure guardrail gate: PASS"
