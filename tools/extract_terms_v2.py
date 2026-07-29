# SPDX-License-Identifier: AGPL-3.0-only
import json
import re
from pathlib import Path
from collections import Counter

def extract_v2():
    drop_path = Path("docs/research/constitution_drop_ledger_v0.1.md")
    raw_path = Path("docs/research/constitution_dredge_raw_v0.1.jsonl")
    output_path = Path("docs/reference/glossary_candidates_v2.md")
    
    # --- 1. Rejected Terms from Drop Ledger ---
    rejected_terms = set()
    if drop_path.exists():
        with open(drop_path, "r") as f:
            content = f.read()
        
        # Regex to find "Claim text: > ... Term ..."
        # Actually, let's just grab capitalized phrases from blockquotes after "Claim text:"
        # But looking at prior file view, claims are often sentences.
        # Let's look for "Term: Definition" pattern inside the blockquotes.
        
        # Or look for Topic headers? No.
        
        # Let's just regex all Capitalized Phrases in the file, but excluding common words.
        pass # We will do a generic pass later.

    # --- 2. Raw Ledger Frequency Analysis ---
    
    phrase_counter = Counter()
    
    # Patterns
    # Caps Phrase (2-5 words, Title Case)
    p_caps = re.compile(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+){1,4})")
    # Acronyms
    p_acro = re.compile(r"\b([A-Z]{3,})\b")
    # Term: Definition
    p_def = re.compile(r"^([A-Z][a-zA-Z0-9\s\-_]{3,40}):\s")

    ignored = {
        "The System", "This Clause", "In Order", "To Be", "As A", "It Is", 
        "If The", "For The", "Of The", "And The", "On The", "By The", "Or The",
        "Genesis Node", "Genesis Agent", "Epistemic Graph" # We already have these
    }

    print("Parsing JSONL...")
    try:
        with open(raw_path, "r") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    text = rec.get("claim_statement", "") + " " + rec.get("quote", "")
                    
                    # Frequency Count
                    matches = p_caps.findall(text)
                    for m in matches:
                        if m not in ignored and len(m) < 50:
                            phrase_counter[m] += 1
                            
                    matches_acro = p_acro.findall(text)
                    for m in matches_acro:
                        phrase_counter[m] += 1
                        
                except Exception:
                    continue
    except FileNotFoundError:
        print("JSONL not found")

    # Filter top results
    common_phrases = phrase_counter.most_common(200)
    
    # --- Output ---
    with open(output_path, "w") as f:
        f.write("# Automated Glossary Extraction (v2)\n\n")
        
        f.write("## 1. High-Frequency Phrases in Raw Ledger (Top 200)\n")
        f.write("*These phrases appear most frequently in the 22k raw records.*\n\n")
        for term, count in common_phrases:
            if count > 2: # Min threshold
                f.write(f"- **{term}** ({count})\n")

        # --- Rejected extraction (Simple regex on drop ledger) ---
        f.write("\n## 2. Potential Rejected Terms (from Drop Ledger)\n")
        if drop_path.exists():
            with open(drop_path, "r") as f_drop:
                 drop_text = f_drop.read()
            drop_phrases = Counter(p_caps.findall(drop_text))
            for term, count in drop_phrases.most_common(50):
                if term not in ignored and count > 1:
                     f.write(f"- {term}\n")

    print(f"Written to {output_path}")

if __name__ == "__main__":
    extract_v2()
