# SPDX-License-Identifier: AGPL-3.0-only
import sys
import re
from pathlib import Path
import json

IN_FILE = Path("docs/research/@NatebJones Youtube Transcript - I broke Down Anthropic's $2.5 Billion Leak. Your Agent is Missing 12 Critical Pieces.md")
OUT_FILE = Path("docs/research/transcript_dredge_matrix_v0.1.md")

def extract_primitives(text):
    matrix = []
    
    # We know the video outlines 12 primitives.
    keywords = {
        "Tool Registry": ["registry", "metadata"],
        "Permission System": ["permission", "trust tier", "bash tool", "approval"],
        "Session Persistence": ["session persistence", "crash", "resume", "reconstruct"],
        "Workflow State": ["workflow state", "checkpoint", "task state"],
        "Token Budget": ["token budget", "input tokens", "compaction threshold"],
        "Structured Streaming": ["streaming event", "stream of thought", "typed event"],
        "System Event Logging": ["event logging", "history log"],
        "Verification": ["verification", "guardrail", "verify changes"],
        "Tool Pool Assemblies": ["tool pool", "subset dynamically"],
        "Transcript Compaction": ["compaction", "transaction store"],
        "Permission Audit Trail": ["permission audit", "interactive handler", "boolean gate"],
        "Agent Type System": ["agent type", "explore", "plan", "verify"],
    }
    
    # Split text into sentences roughly
    sentences = re.split(r'(?<=[.!?]) +', text)
    
    for primitive, words in keywords.items():
        found_sentences = []
        for i, s in enumerate(sentences):
            if any(w.lower() in s.lower() for w in words):
                # Grab context (sentence before, matching sentence, sentence after)
                start = max(0, i-1)
                end = min(len(sentences), i+2)
                context = " ".join(sentences[start:end])
                found_sentences.append(context)
        
        if found_sentences:
            snippet = found_sentences[0]
            if len(snippet) > 400:
                snippet = snippet[:397] + "..."
            matrix.append({
                "primitive": primitive,
                "snippet": snippet,
                "leverage_score": min(10, 5 + len(found_sentences))
            })
            
    return matrix

def generate_markdown(matrix):
    lines = [
        "# Transcript Dredge Matrix: Anthropic Agent Leak",
        "",
        "**Source:** @NatebJones Youtube Transcript",
        "**Method:** Applied ILC logic gates to extract agentic primitives.",
        "",
        "| Paradigm / Primitive | Description Snippet | Leverage Score |",
        "|---|---|---|"
    ]
    
    # Sort by leverage
    matrix.sort(key=lambda x: x['leverage_score'], reverse=True)
    
    for item in matrix:
        safe_snippet = item['snippet'].replace('\n', ' ').replace('|', '-')
        lines.append(f"| {item['primitive']} | {safe_snippet} | {item['leverage_score']} |")
        
    OUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated dredge matrix at {OUT_FILE}")

def main():
    text = IN_FILE.read_text(encoding="utf-8")
    matrix = extract_primitives(text)
    generate_markdown(matrix)

if __name__ == "__main__":
    main()
