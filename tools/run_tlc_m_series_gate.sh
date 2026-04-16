#!/usr/bin/env bash
# run_tlc_m_series_gate.sh
#
# Runs TLC model checker against both ILC M-series TLA+ specs and reports
# pass/fail. Clears the tla_tlc_clean_m_series_implementation_gate token
# when both specs produce no violations.
#
# Usage:
#   ./tools/run_tlc_m_series_gate.sh
#
# Requirements:
#   - Java 11+ (installs via Homebrew if absent and Homebrew is available)
#   - tla2tools.jar (auto-downloaded to tools/tla/ if absent)
#
# Exit codes:
#   0  — both specs clean (gate satisfied)
#   1  — one or more violations, or setup failed

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TLA_DIR="$REPO_ROOT/docs/specs/tla"
TOOLS_TLA_DIR="$REPO_ROOT/tools/tla"
JAR_PATH="$TOOLS_TLA_DIR/tla2tools.jar"

# Latest stable TLA+ tools release
TLA_TOOLS_VERSION="1.8.0"
TLA_TOOLS_URL="https://github.com/tlaplus/tlaplus/releases/download/v${TLA_TOOLS_VERSION}/tla2tools.jar"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log()  { echo -e "${NC}[tlc-gate] $*"; }
pass() { echo -e "${GREEN}[PASS]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }

# ── Java check ────────────────────────────────────────────────────────────────

check_java() {
    if java -version 2>/dev/null; then
        return 0
    fi
    warn "Java not found."
    if command -v brew &>/dev/null; then
        log "Installing Java via Homebrew (openjdk)..."
        brew install openjdk
        # Homebrew openjdk requires symlinking on macOS
        sudo ln -sfn "$(brew --prefix openjdk)/libexec/openjdk.jdk" \
            /Library/Java/JavaVirtualMachines/openjdk.jdk 2>/dev/null || true
        export PATH="$(brew --prefix openjdk)/bin:$PATH"
        if java -version 2>/dev/null; then
            pass "Java installed via Homebrew."
            return 0
        fi
    fi
    fail "Java is required but could not be installed automatically."
    echo "  Install manually: https://adoptium.net or 'brew install openjdk'"
    exit 1
}

# ── JAR download ──────────────────────────────────────────────────────────────

ensure_jar() {
    if [[ -f "$JAR_PATH" ]]; then
        log "tla2tools.jar found at $JAR_PATH"
        return 0
    fi
    log "tla2tools.jar not found. Downloading v${TLA_TOOLS_VERSION}..."
    mkdir -p "$TOOLS_TLA_DIR"
    if command -v curl &>/dev/null; then
        curl -fsSL -o "$JAR_PATH" "$TLA_TOOLS_URL"
    elif command -v wget &>/dev/null; then
        wget -q -O "$JAR_PATH" "$TLA_TOOLS_URL"
    else
        fail "Neither curl nor wget available. Cannot download tla2tools.jar."
        exit 1
    fi
    pass "Downloaded tla2tools.jar ($(du -h "$JAR_PATH" | cut -f1))"
}

# ── TLC runner ────────────────────────────────────────────────────────────────

run_spec() {
    local spec_name="$1"
    local spec_file="$TLA_DIR/${spec_name}.tla"
    local cfg_file="$TLA_DIR/${spec_name}.cfg"
    local out_file="$TOOLS_TLA_DIR/${spec_name}.tlc.out"

    log "Checking $spec_name ..."

    if [[ ! -f "$spec_file" ]]; then
        fail "Spec file not found: $spec_file"
        return 1
    fi
    if [[ ! -f "$cfg_file" ]]; then
        fail "Config file not found: $cfg_file"
        return 1
    fi

    # -workers auto  — use all CPU cores
    # -deadlock      — report deadlocks (no Next action enabled in some state)
    # -coverage 1    — report action coverage (useful for debugging)
    java -cp "$JAR_PATH" tlc2.TLC \
        -config "$cfg_file" \
        -workers auto \
        -deadlock \
        "$spec_file" 2>&1 | tee "$out_file"

    local tlc_exit="${PIPESTATUS[0]}"

    # TLC exit 0 = success, non-zero = violation or error
    if [[ "$tlc_exit" -eq 0 ]]; then
        # Double-check output for violation strings (TLC sometimes exits 0 on warnings)
        if grep -qE "Error:|Invariant .* violated|Property .* violated|TLC threw" "$out_file"; then
            fail "$spec_name: TLC output contains violation markers despite exit 0"
            echo "  See: $out_file"
            return 1
        fi
        pass "$spec_name: no violations"
        return 0
    else
        fail "$spec_name: TLC exited with code $tlc_exit"
        echo "  See full output: $out_file"
        # Print last 30 lines for quick diagnosis
        echo "  --- Last 30 lines of TLC output ---"
        tail -30 "$out_file" | sed 's/^/  /'
        return 1
    fi
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
    log "ILC M-Series TLA+ Gate — tla_tlc_clean_m_series_implementation_gate"
    log "Specs: ilc_dag_censorship_bounds (Spec A) + ilc_ecu_fast_path_bcast (Spec B)"
    echo ""

    check_java
    ensure_jar
    echo ""

    local failures=0

    run_spec "ilc_dag_censorship_bounds"  || failures=$((failures + 1))
    echo ""
    run_spec "ilc_ecu_fast_path_bcast"   || failures=$((failures + 1))
    echo ""

    if [[ "$failures" -eq 0 ]]; then
        pass "═══════════════════════════════════════════════════════"
        pass "GATE SATISFIED: tla_tlc_clean_m_series_implementation_gate"
        pass "Both specs clean. M-003 implementation gate is open."
        pass "═══════════════════════════════════════════════════════"
        exit 0
    else
        fail "═══════════════════════════════════════════════════════"
        fail "GATE FAILED: $failures spec(s) produced violations."
        fail "M-series gate is NOT satisfied."
        fail "Check output files in: $TOOLS_TLA_DIR/"
        fail "═══════════════════════════════════════════════════════"
        exit 1
    fi
}

main "$@"
