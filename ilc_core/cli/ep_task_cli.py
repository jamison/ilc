import argparse
import json
import sys
import requests
from typing import Optional, Any, List

class HttpClient:
    """Simple wrapper for requests to match the interface needed by the CLI."""
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def get(self, path: str) -> Any:
        return requests.get(f"{self.base_url}{path}")

    def post(self, path: str, json: Any) -> Any:
        return requests.post(f"{self.base_url}{path}", json=json)

def run_ep_task_cli(argv: Optional[List[str]] = None, client: Any = None) -> int:
    """
    CLI entrypoint for Epistemic Work Task operations.
    
    Args:
        argv: List of arguments (default: sys.argv[1:])
        client: Optional HTTP client (default: requests wrapper)
    """
    if argv is None:
        argv = sys.argv[1:]

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

    args = parser.parse_args(argv)

    # Setup client
    if client is None:
        client = HttpClient(args.base_url)

    if args.command == "schema":
        try:
            res = client.get("/v1/protocol/ep_task_schema")
            if res.status_code == 200:
                print(json.dumps(res.json(), indent=2))
                return 0
            else:
                print(f"Error fetching schema: {res.status_code}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command == "submit":
        try:
            if args.file:
                with open(args.file, "r") as f:
                    payload = json.load(f)
            else:
                # Read from stdin
                if sys.stdin.isatty():
                    print("Reading JSON from stdin...", file=sys.stderr)
                payload = json.load(sys.stdin)

            res = client.post("/v1/protocol/ep_task", json=payload)
            if res.status_code == 200:
                data = res.json()
                ep = data.get("ep_task", {})
                td = data.get("task_descriptor", {})
                print(f"Accepted EpistemicWorkTask: {ep.get('task_id')}")
                print(f"  Class: {ep.get('task_class')}")
                print(f"  Mapped Task Type: {td.get('task_type')}")
                print("\nFull Response:")
                print(json.dumps(data, indent=2))
                return 0
            else:
                print(f"Error submitting task: {res.status_code}", file=sys.stderr)
                try:
                    print(res.json(), file=sys.stderr)
                except:
                    print(res.text, file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    elif args.command == "demo":
        try:
            payload = {
                "task_id": "task:demo:cli",
                "task_class": "star.map.embedding",
                "agent_id": "agent:cli",
                "region_scope": ["global"],
                "difficulty_factor": 1.0,
                "input_data": {"demo": True},
                "verification_method": "hash-match",
                "task_state": "proposed",
                "timestamp_created": 1700000000,
                "ecu.estimate": 0.1,
            }
            print("Submitting demo task...")
            res = client.post("/v1/protocol/ep_task", json=payload)
            if res.status_code == 200:
                data = res.json()
                print("Success!")
                print(json.dumps(data, indent=2))
                return 0
            else:
                print(f"Error submitting demo task: {res.status_code}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(run_ep_task_cli())
