"""Claim Extractor — segments document text into candidate assertion units.

A "claim" is a declarative statement that asserts a relationship, mechanism,
or state of affairs. This block identifies candidate claims by looking for
linguistic markers of assertion: definitional forms, causal forms, quantitative
forms, and existence/uniqueness forms.

Each extracted claim is returned as a structured dict with enough provenance
to reconstruct the source location for downstream blocks.

Return format (list of ClaimRecord dicts):
    {
        "claim_id": str,          # "{source_id}::claim_{n}" zero-padded
        "text": str,              # the extracted claim text
        "source_id": str,         # caller-supplied source name (e.g. file path)
        "line_start": int,        # 1-based line number of first char
        "line_end": int,          # 1-based line number of last char
        "form": str,              # "definitional" | "causal" | "quantitative"
                                  # | "existence" | "normative" | "unknown"
        "raw_sentence": str,      # full sentence containing the claim
    }
"""

from __future__ import annotations

import re
from typing import Any

# ---------------------------------------------------------------------------
# Claim form patterns — ordered; first match wins
# ---------------------------------------------------------------------------

_FORM_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # Definitional: "X is defined as", "X is a", "we define X", "call X"
    ("definitional", re.compile(
        r"\b(is defined as|is a type of|is an instance of|we define|"
        r"we call|denote by|refer to as|let \w+ be)\b",
        re.IGNORECASE,
    )),
    # Causal: "X causes", "X leads to", "X increases Y", "if X then Y"
    ("causal", re.compile(
        r"\b(causes?|leads? to|results? in|increases?|decreases?|drives?|"
        r"reduces?|implies?|if .{1,40} then|because|therefore|thus|hence)\b",
        re.IGNORECASE,
    )),
    # Quantitative: numbers, comparisons, bounds, rates
    ("quantitative", re.compile(
        r"\b(equals?|is equal to|is greater than|is less than|is bounded|"
        r"converges? to|grows? at|rate of|fraction of|"
        r"[\d]+[\s]*(percent|%)|on average|in expectation)\b",
        re.IGNORECASE,
    )),
    # Normative: "must", "should", "ought to", "is required"
    ("normative", re.compile(
        r"\b(must|should|ought to|is required|is necessary|"
        r"is sufficient|guarantees?|ensures?)\b",
        re.IGNORECASE,
    )),
    # Existence: "there exists", "there is", "some X", "no X", "all X"
    ("existence", re.compile(
        r"\b(there exists?|there is a|there are|for all|for every|"
        r"no such|it follows that|we (show|prove|demonstrate) that)\b",
        re.IGNORECASE,
    )),
]


def _classify_form(sentence: str) -> str:
    for form, pattern in _FORM_PATTERNS:
        if pattern.search(sentence):
            return form
    return "unknown"


def _split_sentences(text: str) -> list[tuple[int, int, str]]:
    """Split text into (line_start, line_end, sentence) triples.

    Uses a simple heuristic: sentence boundary at period/question/exclamation
    followed by whitespace and an uppercase letter, or a blank line.
    Returns 1-based line numbers.
    """
    # Normalize CRLF
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    # Build a char→line_number index for later lookup
    char_to_line: list[int] = []
    for lineno, line in enumerate(lines, start=1):
        for _ in line:
            char_to_line.append(lineno)
        char_to_line.append(lineno)  # for the newline char

    # Sentence splitting: find boundary positions
    boundary_re = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"\'])")
    boundaries = [0] + [m.end() for m in boundary_re.finditer(text)] + [len(text)]

    sentences: list[tuple[int, int, str]] = []
    for i in range(len(boundaries) - 1):
        start = boundaries[i]
        end = boundaries[i + 1]
        sentence = text[start:end].strip()
        if not sentence:
            continue
        line_start = char_to_line[min(start, len(char_to_line) - 1)]
        line_end = char_to_line[min(end - 1, len(char_to_line) - 1)]
        sentences.append((line_start, line_end, sentence))

    return sentences


def _is_claim_candidate(sentence: str) -> bool:
    """Return True if the sentence is likely to contain an assertion."""
    # Skip very short fragments, headers, code blocks, list bullets without verbs
    stripped = sentence.strip()
    if len(stripped) < 12:
        return False
    # Skip lines that look like headings (all caps or start with #)
    if stripped.startswith("#"):
        return False
    # Skip lines that are pure math/code (start with $, `, or contain only symbols)
    if re.match(r"^[\$`\|]", stripped):
        return False
    # Skip pure citation/reference lines
    if re.match(r"^\[?\d+\]?[\s\.]", stripped):
        return False
    # Must contain a verb-like pattern to be a claim
    if not re.search(
        r"\b(is|are|was|were|will|would|has|have|had|"
        r"can|could|may|might|must|should|ought|do|does|did|"
        r"shows?|proves?|implies?|causes?|leads?|results?|"
        r"accumulates?|equals?|defines?|determines?|holds?|fails?|"
        r"increases?|decreases?|converges?|exhibits?|depends?|"
        r"requires?|produces?|reduces?|follows?|appl(?:y|ies)|means?|"
        r"represents?|generates?|captures?|describes?|models?|"
        r"assumes?|suppose|let \w+ be|denotes?|yields?|gives?)\b",
        stripped, re.IGNORECASE,
    ):
        return False
    return True


def extract_claims(text: str, source_id: str = "unknown") -> list[dict[str, Any]]:
    """Extract candidate assertion units from *text*.

    Args:
        text:       Raw document text (markdown, plain text, or structured spec).
        source_id:  A stable identifier for the source (file path or document name).
                    Used to build claim_id and source_artifact in downstream reports.

    Returns:
        Ordered list of ClaimRecord dicts.
    """
    sentences = _split_sentences(text)
    records: list[dict[str, Any]] = []
    for n, (line_start, line_end, sentence) in enumerate(sentences):
        if not _is_claim_candidate(sentence):
            continue
        form = _classify_form(sentence)
        claim_id = f"{source_id}::claim_{n:04d}"
        records.append({
            "claim_id": claim_id,
            "text": sentence,
            "source_id": source_id,
            "line_start": line_start,
            "line_end": line_end,
            "form": form,
            "raw_sentence": sentence,
        })
    return records
