# SPDX-License-Identifier: AGPL-3.0-only
import argparse
import json
import sys
from typing import List, Optional, Protocol, TypeAlias, cast

import requests

from ilc_core.cli._cli_error import build_cli_error_payload

JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | dict[str, "JsonValue"] | list["JsonValue"]
CONNECT_TIMEOUT_S = 2.0
READ_TIMEOUT_S = 30.0


class HttpResponseLike(Protocol):
    status_code: int
    text: str

    def json(self) -> JsonValue:
        ...


class HttpClientLike(Protocol):
    def get(self, path: str) -> HttpResponseLike:
        ...

    def post(self, path: str, json: object) -> HttpResponseLike:
        ...


def _as_json_object(value: JsonValue) -> dict[str, JsonValue]:
    if isinstance(value, dict):
        return cast(dict[str, JsonValue], value)
    return {}


def _emit_cli_error(error: str, detail: str | None = None) -> int:
    payload = build_cli_error_payload(error, detail=detail)
    print(json.dumps(payload, separators=(",", ":")))
    return 1

class HttpClient:
    """Simple wrapper for requests to match the interface needed by the CLI."""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get(self, path: str) -> requests.Response:
        return requests.get(f"{self.base_url}{path}", timeout=(CONNECT_TIMEOUT_S, READ_TIMEOUT_S))

    def post(self, path: str, json: object) -> requests.Response:
        return requests.post(
            f"{self.base_url}{path}",
            json=json,
            timeout=(CONNECT_TIMEOUT_S, READ_TIMEOUT_S),
        )

def _handle_schema(client: HttpClientLike) -> int:
    try:
        res = client.get("/v1/protocol/ep_task_schema")
        if res.status_code == 200:
            print(json.dumps(res.json(), indent=2))
            return 0
        return _emit_cli_error(
            "schema_fetch_failed", detail=f"Error fetching schema: {res.status_code}"
        )
    except requests.RequestException as e:
        return _emit_cli_error("schema_fetch_error", detail=f"Error: {e}")
    except ValueError as e:
        return _emit_cli_error("schema_fetch_error", detail=f"Error: {e}")

def _handle_submit(client: HttpClientLike, file_path: Optional[str]) -> int:
    try:
        if file_path:
            with open(file_path, "r") as f:
                payload = cast(object, json.load(f))
        else:
            # Read from stdin
            if sys.stdin.isatty():
                print("Reading JSON from stdin...", file=sys.stderr)
            payload = cast(object, json.load(sys.stdin))

        res = client.post("/v1/protocol/ep_task", json=payload)
        if res.status_code == 200:
            data = res.json()
            data_obj = _as_json_object(data)
            ep = _as_json_object(data_obj.get("ep_task"))
            td = _as_json_object(data_obj.get("task_descriptor"))
            print(f"Accepted EpistemicWorkTask: {ep.get('task_id')}")
            print(f"  Class: {ep.get('task_class')}")
            print(f"  Mapped Task Type: {td.get('task_type')}")
            print("\nFull Response:")
            print(json.dumps(data, indent=2))
            return 0
        else:
            response_body = ""
            try:
                response_body = json.dumps(res.json(), separators=(",", ":"))
            except ValueError:
                response_body = res.text
            return _emit_cli_error(
                "submit_failed",
                detail=f"Error submitting task: {res.status_code}; response: {response_body}",
            )
    except (OSError, json.JSONDecodeError, requests.RequestException, ValueError) as e:
        return _emit_cli_error("submit_error", detail=f"Error: {e}")

def _handle_demo(client: HttpClientLike) -> int:
    try:
        payload = {
            "task_id": "task:demo:cli",
            "task_class": "star.map.embedding",
            "agent_id": "agent:cli",
            "region_scope": ["global"],
            "difficulty_factor": "1.0",  # string - float literals not valid at protocol boundaries
            "input_data": {"demo": True},
            "verification_method": "hash-match",
            "task_state": "proposed",
            "timestamp_created": 1700000000,
            "ecu.estimate": "0.1",  # string - float literals not valid at protocol boundaries
        }
        print("Submitting demo task...")
        res = client.post("/v1/protocol/ep_task", json=payload)
        if res.status_code == 200:
            data = res.json()
            print("Success!")
            print(json.dumps(data, indent=2))
            return 0
        else:
            return _emit_cli_error(
                "demo_submit_failed", detail=f"Error submitting demo task: {res.status_code}"
            )
    except (requests.RequestException, ValueError) as e:
        return _emit_cli_error("demo_submit_error", detail=f"Error: {e}")

def _build_cli_parser() -> argparse.ArgumentParser:
    """Helper to construct the CLI argument parser."""
    parser = argparse.ArgumentParser(description="Epistemic Work Task CLI")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Base URL of the ILC node")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Subcommand: schema
    subparsers.add_parser("schema", help="Fetch and print the EpistemicWorkTask schema")
    
    # Subcommand: submit
    submit_parser = subparsers.add_parser("submit", help="Submit an EpistemicWorkTask")
    submit_parser.add_argument("--file", help="Path to JSON file (default: stdin)")
    
    # Subcommand: demo
    subparsers.add_parser("demo", help="Submit a demo task")
    
    return parser

def _dispatch_cli_command(args: argparse.Namespace, client: HttpClientLike) -> int:
    """Helper to route CLI commands to handlers."""
    if args.command == "schema":
        return _handle_schema(client)

    if args.command == "submit":
        return _handle_submit(client, args.file)

    if args.command == "demo":
        return _handle_demo(client)

    return 0

def run_ep_task_cli(argv: Optional[List[str]] = None, client: Optional[HttpClientLike] = None) -> int:
    """
    CLI entrypoint for Epistemic Work Task operations.
    
    Args:
        argv: List of arguments (default: sys.argv[1:])
        client: Optional HTTP client (default: requests wrapper)
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = _build_cli_parser()
    args = parser.parse_args(argv)

    # Setup client
    if client is None:
        client = HttpClient(args.base_url)

    return _dispatch_cli_command(args, client)

if __name__ == "__main__":
    raise SystemExit(run_ep_task_cli())
