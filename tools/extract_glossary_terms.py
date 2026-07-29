# SPDX-License-Identifier: AGPL-3.0-only
import re
import sys
from pathlib import Path

def extract_terms():
    input_path = Path("docs/research/constitution_dredge_matrix_v0.2.md")
    output_path = Path("docs/reference/glossary_candidates.md")
    
    if not input_path.exists():
        print(f"Error: {input_path} not found.")
        return

    with open(input_path, "r") as f:
        lines = f.readlines()

    terms = set()
    
    # Patterns to catch terms
    patterns = [
        # "Term: Definition" at start, max 40 chars
        re.compile(r"^\s*([A-Z][a-zA-Z0-9\s\-_]{3,40}):\s"),  
        # snake_case_variables
        re.compile(r"([a-z0-9]+_[a-z0-9_]+)"),           
        # Capitalized Phrases (Title Case), e.g. "Genesis Attention Broadcast"
        # Must be at least 2 words, both Capitalized.
        re.compile(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)"),   
        # Acronyms (3+ chars)
        re.compile(r"\b([A-Z]{3,})\b")                       
    ]

    ignored = {
        "MUST", "SHOULD", "NOT", "TODO", "Later", "Goal", "Phase", "Status", 
        "Note", "Example", "Yes", "No", "However", "Also", "But", "ILC", "MVP",
        "Short Answer", "Longer Memory", "Good", "Bad", "Review", "Audit",
        "The", "And", "With", "For", "Exit", "Action", "Topic", "Coverage",
        "Input", "Output", "Description", "Commit", "Prompt", "Walkthrough",
        "Next", "Planned", "Phase"
    }

    for line in lines:
        if "|" not in line or line.strip().startswith("| id |"): 
            continue
        
        parts = line.split("|")
        if len(parts) < 5: 
            continue
            
        claim = parts[4].strip()
        
        for p in patterns:
            matches = p.findall(claim)
            for m in matches:
                clean_term = m.strip(".,;:\"'")
                if len(clean_term) > 2 and clean_term not in ignored:
                   # Extra heuristic: Don't include whole sentences
                   if " " in clean_term and len(clean_term.split()) > 5:
                       continue
                   terms.add(clean_term)

    # Sort and Write
    sorted_terms = sorted(list(terms))
    
    content = f"# Extracted Glossary Candidates ({len(sorted_terms)})\n\n"
    for t in sorted_terms:
        content += f"- {t}\n"
        
    with open(output_path, "w") as f:
        f.write(content)
        
    print(f"Written {len(sorted_terms)} terms to {output_path}")

if __name__ == "__main__":
    extract_terms()
