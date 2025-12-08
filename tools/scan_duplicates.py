import os
import re

DIRS_TO_SCAN = ['ilc_core', 'simulations', 'tests']

def is_import_line(line):
    line = line.strip()
    return line.startswith('import ') or line.startswith('from ')

def scan_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    seen_imports = {}
    issues = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue

        # Check duplicate imports
        if is_import_line(line):
            if stripped in seen_imports:
                issues.append(f"Line {i+1}: Duplicate import '{stripped}' (first seen at line {seen_imports[stripped]})")
            else:
                seen_imports[stripped] = i + 1

        # Check consecutive duplicate lines (simple heuristic)
        # We look at the previous non-empty line
        if i > 0:
            prev_idx = i - 1
            while prev_idx >= 0 and not lines[prev_idx].strip():
                prev_idx -= 1
            
            if prev_idx >= 0:
                prev_line = lines[prev_idx].strip()
                if prev_line == stripped and len(stripped) > 5: # Ignore short lines like "pass", "return", "}"
                     # Ignore comments
                    if not stripped.startswith('#'):
                         issues.append(f"Line {i+1}: Consecutive duplicate line '{stripped}'")

    if issues:
        print(f"\nFile: {filepath}")
        for issue in issues:
            print(f"  {issue}")

def main():
    root_dir = os.getcwd()
    for d in DIRS_TO_SCAN:
        dir_path = os.path.join(root_dir, d)
        if not os.path.exists(dir_path):
            continue
            
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.endswith('.py'):
                    scan_file(os.path.join(root, file))

if __name__ == '__main__':
    main()
