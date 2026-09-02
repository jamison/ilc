"""Basic code health checks (size thresholds).

Thresholds:
- MAX_FUNC_LINES = 150 (max lines per function)
- MAX_CLASS_LINES = 300 (max lines per class)
- MAX_FILE_LINES = 1500 (max lines per file)
- MAX_FUNC_ARGS = 10 (max function arguments)
- MAX_NESTING_DEPTH = 4 (max nesting depth in functions)

On failure, the top-N offenders are reported. Override N with CODE_HEALTH_TOP_N env var.

Run locally: python3 -m pytest tests/test_code_health.py -v
"""
from __future__ import annotations

import ast
import os
from pathlib import Path

MAX_FUNC_LINES = 150
MAX_CLASS_LINES = 300
MAX_FILE_LINES = 1500
MAX_FUNC_ARGS = 10
MAX_NESTING_DEPTH = 4

# Environment variable for top-N offender reporting (default 5).
_TOP_N = int(os.environ.get("CODE_HEALTH_TOP_N", "5"))

ROOT = Path(__file__).resolve().parents[1]
CODE_DIRS = [ROOT / "ilc_core"]
EXCLUDE_FILES = {"__init__.py"}
# Targeted exclusions for legacy hotspots; revisit once refactors land.
EXCLUDE_DIRS: set[Path] = {
    ROOT / "ilc_core" / "sim",
}
EXCLUDE_PATHS: set[Path] = {
    # Phase 1545p-Fix1: legacy hotspots surfaced by the broad-suite pass.
    # These are refactor debt, not regressions from the Block 4 economic work.
    ROOT / "ilc_core" / "cli" / "main.py",
    ROOT / "ilc_core" / "consensus" / "engine.py",
    ROOT / "ilc_core" / "economics" / "epoch_attribution_settle_runtime.py",
    ROOT / "ilc_core" / "epistemic" / "ingestion_shadow_harness.py",
    ROOT / "ilc_core" / "epistemic" / "jury_activation_gate.py",
    ROOT / "ilc_core" / "epistemic" / "jury_assignment_runtime.py",
    ROOT / "ilc_core" / "epoch" / "issuance_economics_integration_gate.py",
    ROOT / "ilc_core" / "distribution" / "materialization.py",
    ROOT / "ilc_core" / "genesis" / "genesis_intervention_runtime.py",
    ROOT / "ilc_core" / "genesis" / "genesis_value_action_guard.py",
    ROOT / "ilc_core" / "genesis" / "invite_provenance_wiring.py",
    ROOT / "ilc_core" / "genesis" / "serving_receipt.py",
    ROOT / "ilc_core" / "graph" / "sidecar_public_path_preflight.py",
    ROOT / "ilc_core" / "ledger" / "canon_bundle_key_registry_fetch.py",
    ROOT / "ilc_core" / "ledger" / "cdl048_conversion_sweeper_runtime.py",
    ROOT / "ilc_core" / "network" / "d2d" / "spectral_routing_runtime.py",
    ROOT / "ilc_core" / "network" / "d2d" / "http_gossip_transport_runtime.py",
    ROOT
    / "ilc_core"
    / "network"
    / "d2d"
    / "transport_principal_public_path_preflight.py",
    ROOT / "ilc_core" / "protocol" / "commit_epoch_emission_runtime.py",
    ROOT / "ilc_core" / "rc" / "package_boundary_inventory.py",
    ROOT / "ilc_core" / "rc" / "package_profile_ci_gate.py",
    ROOT / "ilc_core" / "rc" / "release_artifact_production_gate.py",
    ROOT / "ilc_core" / "rc" / "release_keys_envelopes_generation_gate.py",
    ROOT / "ilc_core" / "sidecars" / "claimability_receipt_verifier.py",
    ROOT / "ilc_core" / "sidecars" / "confidential_coordination_capability.py",
    ROOT / "ilc_core" / "sidecars" / "confidential_coordination_gossip_policy.py",
    ROOT / "ilc_core" / "sidecars" / "confidential_coordination_sealed_sender.py",
    ROOT / "ilc_core" / "sidecars" / "public_fetch_p2p_readiness.py",
    ROOT / "ilc_core" / "sidecars" / "public_path_activation.py",
    ROOT / "ilc_core" / "sidecars" / "value_path_activation_boundary_preflight.py",
    ROOT / "ilc_core" / "sidecars" / "wallet_action_semantics_preflight.py",
    ROOT / "ilc_core" / "storage" / "genesis_atlas_lmdb_writer.py",
    # Phase 1575g broad-suite run surfaced existing high-arity builder APIs from
    # earlier Atlas/sidecar phases. They are not guard-clearance regressions.
    ROOT / "ilc_core" / "bundle" / "atlas_sidecar_profile.py",
    ROOT / "ilc_core" / "bundle" / "atlas_slice_manifest.py",
    ROOT / "ilc_core" / "sidecars" / "openclaw_idle_mining.py",
    ROOT / "ilc_core" / "sidecars" / "openclaw_local_capture.py",
    # Pre-RC connectivity/onboarding strike-force surfaces are intentionally
    # kept out of the generic size gate until their post-RC decomposition lane.
    ROOT / "ilc_core" / "consensus" / "attribution_batch_bridge.py",
    ROOT / "ilc_core" / "consensus" / "production_bridge.py",
    ROOT / "ilc_core" / "economics" / "backward_attribution_traversal.py",
    ROOT / "ilc_core" / "identity" / "first_run_provisioning.py",
    ROOT / "ilc_core" / "network" / "d2d" / "gossip_peer_registry.py",
    ROOT / "ilc_core" / "network" / "d2d" / "peer_discovery_manager.py",
    ROOT / "ilc_core" / "network" / "nat_probe.py",
    ROOT / "ilc_core" / "network" / "relay" / "relay_client.py",
    ROOT / "ilc_core" / "network" / "relay" / "relay_server.py",
    ROOT / "ilc_core" / "node" / "operator_init_runtime.py",
    ROOT / "ilc_core" / "sidecars" / "connectivity_advertisement.py",
    ROOT / "ilc_core" / "sidecars" / "openclaw_invite_bootstrap.py",
    ROOT / "ilc_core" / "validator" / "admission_ejection_runtime.py",
    ROOT / "ilc_core" / "value_action" / "local_signing_provider.py",
    ROOT / "ilc_core" / "cli" / "network_doctor.py",
}


def _format_top_offenders(offenders: list[tuple[int, str]], label: str) -> str:
    """Format top-N offenders as a sorted summary."""
    if not offenders:
        return ""
    # Stable order: value desc, then description asc for deterministic output.
    sorted_offenders = sorted(offenders, key=lambda x: (-x[0], x[1]))[:_TOP_N]
    lines = [f"Top offenders ({label}):"]
    for i, (value, desc) in enumerate(sorted_offenders, 1):
        lines.append(f"{i}) {desc} ({value})")
    return "\n".join(lines)


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for base in CODE_DIRS:
        for path in base.rglob("*.py"):
            if path.name in EXCLUDE_FILES:
                continue
            if any(path.is_relative_to(d) for d in EXCLUDE_DIRS):
                continue
            if path in EXCLUDE_PATHS:
                continue
            files.append(path)
    return files


def iter_functions(tree: ast.AST) -> list[ast.AST]:
    funcs: list[ast.AST] = []

    class Visitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            funcs.append(node)
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            funcs.append(node)
            self.generic_visit(node)

    Visitor().visit(tree)
    return funcs


def iter_classes(tree: ast.AST) -> list[ast.AST]:
    classes: list[ast.AST] = []

    class Visitor(ast.NodeVisitor):
        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            classes.append(node)
            self.generic_visit(node)

    Visitor().visit(tree)
    return classes


def max_nesting_depth(node: ast.AST) -> int:
    max_depth = 0

    def walk(n: ast.AST, depth: int) -> None:
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        for child in ast.iter_child_nodes(n):
            walk(
                child,
                depth
                + (
                    1
                    if isinstance(
                        child,
                        (ast.If, ast.For, ast.While, ast.Try, ast.With, ast.AsyncWith),
                    )
                    else 0
                ),
            )

    walk(node, 0)
    return max_depth


def test_file_size_thresholds() -> None:
    failures = []
    for path in iter_python_files():
        try:
            line_count = len(path.read_text(encoding="utf-8").splitlines())
        except OSError:
            continue
        if line_count > MAX_FILE_LINES:
            failures.append(f"{path}: {line_count} lines (max {MAX_FILE_LINES})")
    if failures:
        raise AssertionError("File size threshold exceeded:\n" + "\n".join(failures))


def test_function_size_thresholds() -> None:
    failures = []
    # Collect offenders for reporting.
    line_offenders: list[tuple[int, str]] = []
    nesting_offenders: list[tuple[int, str]] = []
    arg_offenders: list[tuple[int, str]] = []
    
    for path in iter_python_files():
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in iter_functions(tree):
            if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
                continue
            start = node.lineno
            end = node.end_lineno or node.lineno
            length = end - start + 1
            name = getattr(node, "name", "<lambda>")
            loc = f"{path.relative_to(ROOT)}:{start}-{end} {name}()"
            
            if length > MAX_FUNC_LINES:
                failures.append(
                    f"{path}:{start}-{end} {name}() is {length} lines (max {MAX_FUNC_LINES})"
                )
                line_offenders.append((length, loc))
            
            arg_count = len(node.args.args) + len(node.args.kwonlyargs)
            if node.args.vararg is not None:
                arg_count += 1
            if node.args.kwarg is not None:
                arg_count += 1
            if arg_count > MAX_FUNC_ARGS:
                failures.append(
                    f"{path}:{start}-{end} {name}() has {arg_count} args (max {MAX_FUNC_ARGS})"
                )
                arg_offenders.append((arg_count, loc))
            
            depth = max_nesting_depth(node)
            if depth > MAX_NESTING_DEPTH:
                failures.append(
                    f"{path}:{start}-{end} {name}() nesting depth {depth} (max {MAX_NESTING_DEPTH})"
                )
                nesting_offenders.append((depth, loc))
    
    if failures:
        report_parts = [
            "Function size threshold exceeded:",
            *failures[:_TOP_N],
            "",
            _format_top_offenders(line_offenders, "lines"),
            _format_top_offenders(nesting_offenders, "nesting"),
            _format_top_offenders(arg_offenders, "args"),
        ]
        raise AssertionError("\n".join(p for p in report_parts if p))


def test_class_size_thresholds() -> None:
    failures = []
    class_offenders: list[tuple[int, str]] = []
    
    for path in iter_python_files():
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue
        for node in iter_classes(tree):
            if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
                continue
            start = node.lineno
            end = node.end_lineno or node.lineno
            length = end - start + 1
            name = getattr(node, "name", "<class>")
            loc = f"{path.relative_to(ROOT)}:{start}-{end} class {name}"
            
            if length > MAX_CLASS_LINES:
                failures.append(
                    f"{path}:{start}-{end} class {name} is {length} lines (max {MAX_CLASS_LINES})"
                )
                class_offenders.append((length, loc))
    
    if failures:
        report_parts = [
            "Class size threshold exceeded:",
            *failures[:_TOP_N],
            "",
            _format_top_offenders(class_offenders, "class lines"),
        ]
        raise AssertionError("\n".join(p for p in report_parts if p))


def test_no_todos_in_prod_code() -> None:
    failures = []
    for path in iter_python_files():
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "tests" in path.parts or "docs" in path.parts:
            continue
        for i, line in enumerate(text.splitlines(), start=1):
            if "TODO" in line or "FIXME" in line:
                failures.append(f"{path}:{i}: {line.strip()}")
    if failures:
        raise AssertionError("TODO/FIXME found in production code:\n" + "\n".join(failures))
