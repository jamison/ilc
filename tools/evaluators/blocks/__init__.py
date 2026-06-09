"""Base logical blocks for ILC claim decomposition and evaluation.

PUBLIC_RC_EXCLUDE: ilc_decomposition_evaluator_blocks_support_only
PUBLIC_RC_EXCLUDE_REASON: Local sidecar-layer analytical building blocks.
No graph writes, no ECU, no CDL/ADR mutation, not public-serving.

Each block is a pure function operating on structured text.
Blocks return structured dicts compatible with the sidecar RefutationReport contract.
Blocks are composable by evaluator recipes — they do not call each other.

Blocks in this package:
  claim_extractor      — segments document text into candidate assertion units
  scope_binder         — tags each claim with conditions of applicability
  evidence_classifier  — labels evidence type for each claim
  falsifiability_checker — tests whether each claim has an operational falsification condition
"""

from tools.evaluators.blocks.claim_extractor import extract_claims
from tools.evaluators.blocks.scope_binder import bind_scope
from tools.evaluators.blocks.evidence_classifier import classify_evidence
from tools.evaluators.blocks.falsifiability_checker import check_falsifiability

__all__ = [
    "extract_claims",
    "bind_scope",
    "classify_evidence",
    "check_falsifiability",
]
