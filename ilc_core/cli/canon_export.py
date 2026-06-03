# SPDX-License-Identifier: AGPL-3.0-only

import argparse
import json
import sys
from pathlib import Path
from typing import NoReturn

from ilc_core.cli._cli_error import emit_cli_error
from ilc_core.ledger.canon_export_format import export_canon_format_v0_1
from ilc_core.ledger.canon_export_validate import validate_canon_export_v0_1

def fail(error: str, detail: str) -> NoReturn:
    emit_cli_error(error, detail=detail, exit_code=1)

def main() -> int:
    parser = argparse.ArgumentParser(description="Export canon state to standardized v0.1 format.")
    parser.add_argument("--input", required=True, help="Path to source canon_state.json")
    parser.add_argument("--output", required=True, help="Path to destination export file")
    parser.add_argument("--validate", action="store_true", help="Run validator on the generated export")
    parser.add_argument("--pretty", action="store_true", help="Output pretty-printed JSON")
    parser.add_argument("--overwrite", action="store_true", help="Allow overwriting existing output file")
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    # 1. Load Input
    if not input_path.exists():
        fail("input_file_not_found", f"Input file not found: {input_path}")
        
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            canon_state = json.load(f)
    except json.JSONDecodeError as e:
        fail("invalid_input_json", f"Invalid JSON in input file: {e}")
    except Exception as e:
        fail("input_read_error", f"Failed to read input file: {e}")
        
    # 2. Generate Export
    try:
        export_payload = export_canon_format_v0_1(canon_state)
    except ValueError as e:
        fail("export_generation_failed", f"Export generation failed: {e}")
        
    # 3. Write Output
    if output_path.exists() and not args.overwrite:
        fail("output_exists", f"Output file exists (use --overwrite to force): {output_path}")
        
    try:
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
        with open(output_path, "w", encoding="utf-8") as f:
            if args.pretty:
                json.dump(export_payload, f, indent=2, sort_keys=True)
            else:
                json.dump(export_payload, f, separators=(",", ":"))
                
    except Exception as e:
        fail("output_write_error", f"Failed to write output file: {e}")
        
    # 4. Optional Validation
    if args.validate:
        report = validate_canon_export_v0_1(export_payload)
        # Print report to stdout
        print(json.dumps(report, separators=(",", ":")))
        
        if not report["ok"]:
            # Even if we wrote the file successfully, if validation fails, we exit non-zero
            return 1
            
    return 0

if __name__ == "__main__":
    sys.exit(main())
