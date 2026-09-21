# SPDX-License-Identifier: AGPL-3.0-only
"""CLI handlers for scalable sidecar and recipe discovery."""

from __future__ import annotations

import argparse
from typing import Any

from ilc_core.ccss.runtime import apply_confidential_contact_recipe
from ilc_core.sidecars.registry_manifest import build_sidecar_registry_manifest

SIDECAR_CLI_VERSION = "sidecar_cli_v0.1"

_RECIPES: dict[str, dict[str, Any]] = {
    "confidential-contact": {
        "alias_commands": ("ilc ccss",),
        "description": (
            "Local/private CCSS recipe for fixed-size sealed messages, Genesis "
            "contact bootstrap, and direct/Tor/D2d-ready transport selection."
        ),
        "modules": (
            "confidential_coordination_private_gated_shard",
            "confidential_coordination_capability_membership_boundary",
            "confidential_coordination_sealed_sender_local_delivery",
            "confidential_coordination_gossip_jitter_cover_policy",
        ),
        "recipe_id": "confidential-contact",
        "serving_default": "local_private_only",
        "status": "available_local_bootstrap",
    }
}


def _manifest() -> dict[str, Any]:
    return build_sidecar_registry_manifest()


def _sidecar_by_id(sidecar_id: str) -> dict[str, Any]:
    for record in _manifest()["sidecars"]:
        if record.get("sidecar_id") == sidecar_id:
            return record
    raise ValueError(f"sidecar_not_found:{sidecar_id}")


_EXTERNAL_SIDECARS: list[dict[str, Any]] = [
    {
        "sidecar_id": "graph-viz",
        "kind": "external",
        "description": "Epistemic graph visualization — interactive HTML, community detection, StarRank",
        "invoke": "ilc sidecar graph-viz [OPTIONS]",
        "install": "bash ilc-graphics-sidecar/install.sh",
        "module": "ilc_graph_viz.__main__",
    },
    {
        "sidecar_id": "genesis-atlas",
        "kind": "external",
        "description": "Genesis Atlas — semantic hypergraph optimization via AutoResearch loop (Karpathy pattern)",
        "invoke": "ilc sidecar genesis-atlas [OPTIONS]",
        "install": "bash ilc-genesis-atlas-sidecar/install.sh",
        "module": "ilc_genesis_atlas.__main__",
    },
    {
        "sidecar_id": "typesafe",
        "kind": "built-in",
        "description": "TypeSafe Jev — probabilistic judgment engine for epistemic quality, attribution, and claim verification (advisory only; no ECU/ILC mutation)",
        "invoke": "ilc sidecar typesafe {score,classify,verify,manifest} [OPTIONS]",
        "install": "built-in (no additional install required)",
        "module": "ilc_core.sidecars.typesafe_judgment",
    },
]


def _list_external_sidecars() -> list[dict[str, Any]]:
    result = []
    for entry in _EXTERNAL_SIDECARS:
        import importlib.util
        installed = importlib.util.find_spec(entry["module"].split(".")[0]) is not None
        result.append({**entry, "installed": installed})
    return result


def _recipe_by_id(recipe_id: str) -> dict[str, Any]:
    try:
        return dict(_RECIPES[recipe_id])
    except KeyError as exc:
        raise ValueError(f"sidecar_recipe_not_found:{recipe_id}") from exc


def run_sidecar_command(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "sidecar_subcommand", "")
    if subcommand == "recipe":
        recipe_subcommand = getattr(args, "sidecar_recipe_subcommand", "")
        subcommand = f"recipe-{recipe_subcommand}"

    if subcommand == "list":
        manifest = _manifest()
        protocol_sidecars = [
            {
                "implementation_status": item["implementation_status"],
                "public_serving_enabled": item["public_serving_enabled"],
                "sidecar_id": item["sidecar_id"],
                "kind": "protocol",
            }
            for item in manifest["sidecars"]
        ]
        external_sidecars = _list_external_sidecars()
        return {
            "sidecars": protocol_sidecars + external_sidecars,
            "subcommand": "list",
            "version": SIDECAR_CLI_VERSION,
        }

    if subcommand == "inspect":
        return {
            "sidecar": _sidecar_by_id(args.sidecar_id),
            "subcommand": "inspect",
            "version": SIDECAR_CLI_VERSION,
        }

    if subcommand == "recipe-list":
        return {
            "recipes": [
                {
                    "alias_commands": list(item["alias_commands"]),
                    "recipe_id": recipe_id,
                    "status": item["status"],
                }
                for recipe_id, item in sorted(_RECIPES.items())
            ],
            "subcommand": "recipe-list",
            "version": SIDECAR_CLI_VERSION,
        }

    if subcommand == "recipe-inspect":
        recipe = _recipe_by_id(args.recipe_id)
        recipe["alias_commands"] = list(recipe["alias_commands"])
        recipe["modules"] = list(recipe["modules"])
        return {
            "recipe": recipe,
            "subcommand": "recipe-inspect",
            "version": SIDECAR_CLI_VERSION,
        }

    if subcommand == "recipe-apply":
        if args.recipe_id != "confidential-contact":
            raise ValueError(f"sidecar_recipe_apply_not_supported:{args.recipe_id}")
        result = apply_confidential_contact_recipe(
            home=args.ccss_home or None,
            contact_id=args.id,
            name=args.name,
            peer_endpoint=args.peer_endpoint,
            overwrite_identity=args.overwrite_identity,
        )
        result["subcommand"] = "recipe-apply"
        result["version"] = SIDECAR_CLI_VERSION
        return result

    if subcommand == "graph-viz":
        _run_graph_viz(getattr(args, "graph_viz_args", []))
        return {"subcommand": "graph-viz", "version": SIDECAR_CLI_VERSION}

    raise ValueError(f"unknown_sidecar_subcommand:{subcommand}")


def _run_graph_viz(argv: list[str]) -> None:
    """Delegate to ilc_graph_viz.__main__.main(), raising if not installed."""
    try:
        from ilc_graph_viz.__main__ import main as _gv_main  # type: ignore[import]
    except ModuleNotFoundError as exc:
        raise ValueError(
            "graph_viz_sidecar_not_installed: run install.sh from the "
            "ilc-graphics-sidecar repo to install ilc_graph_viz"
        ) from exc
    raise SystemExit(_gv_main(argv))
