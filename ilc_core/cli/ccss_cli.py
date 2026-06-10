# SPDX-License-Identifier: AGPL-3.0-only
"""CLI handlers for the CCSS private-message bootstrap surface."""

from __future__ import annotations

import argparse
from typing import Any

from ilc_core.ccss.runtime import (
    add_contact,
    apply_confidential_contact_recipe,
    generate_identity,
    import_genesis_contact,
    list_contacts,
    list_inbox,
    read_envelope,
    send_message,
    serve_direct,
)

CCSS_CLI_VERSION = "ccss_cli_v0.1"


def run_ccss_command(args: argparse.Namespace) -> dict[str, Any]:
    subcommand = getattr(args, "ccss_subcommand", "")
    home = getattr(args, "ccss_home", "") or None

    if subcommand == "init":
        result = generate_identity(
            home=home,
            contact_id=args.id,
            name=args.name,
            description="Local CCSS identity created by ilc ccss init",
            peer_endpoint=args.peer_endpoint,
            onion=args.onion,
            overwrite=args.overwrite,
        )
        result["subcommand"] = "init"
        return result

    if subcommand == "contacts":
        return {
            "contacts": list_contacts(home=home),
            "subcommand": "contacts",
            "version": CCSS_CLI_VERSION,
        }

    if subcommand == "import-genesis":
        result = import_genesis_contact(home=home, overwrite=args.overwrite)
        result["subcommand"] = "import-genesis"
        result["version"] = CCSS_CLI_VERSION
        return result

    if subcommand == "add-contact":
        result = add_contact(
            home=home,
            contact_id=args.id,
            name=args.name,
            description=args.description,
            public_key_hex=args.pubkey,
            peer_endpoint=args.peer_endpoint,
            onion=args.onion,
            agent_id=args.agent_id,
            overwrite=args.overwrite,
        )
        result["subcommand"] = "add-contact"
        result["version"] = CCSS_CLI_VERSION
        return result

    if subcommand == "send":
        result = send_message(args.contact_id, args.message, home=home)
        result["subcommand"] = "send"
        result["version"] = CCSS_CLI_VERSION
        return result

    if subcommand == "inbox":
        return {
            "envelopes": list_inbox(home=home),
            "subcommand": "inbox",
            "version": CCSS_CLI_VERSION,
        }

    if subcommand == "read":
        result = read_envelope(
            home=home,
            envelope_path=args.envelope,
            latest=args.latest,
            redact=args.redact,
        )
        result["subcommand"] = "read"
        result["version"] = CCSS_CLI_VERSION
        return result

    if subcommand == "serve":
        # Blocking local receiver. Returns only after KeyboardInterrupt or shutdown.
        serve_direct(home=home, host=args.host, port=args.port)
        return {
            "host": args.host,
            "port": args.port,
            "stopped": True,
            "subcommand": "serve",
            "version": CCSS_CLI_VERSION,
        }

    if subcommand == "apply-recipe":
        result = apply_confidential_contact_recipe(
            home=home,
            contact_id=args.id,
            name=args.name,
            peer_endpoint=args.peer_endpoint,
            overwrite_identity=args.overwrite_identity,
        )
        result["subcommand"] = "apply-recipe"
        result["version"] = CCSS_CLI_VERSION
        return result

    raise ValueError(f"unknown_ccss_subcommand:{subcommand}")

