# SPDX-License-Identifier: AGPL-3.0-only
"""TypeSafe Jev judgment sidecar for ILC epistemic graph advisory scoring.

Provides advisory typed judgments via the TypeSafe Jev API (https://docs.typesafe.ai)
for three ILC use cases:

  score    — Epistemic quality scoring for a submitted node
  classify — Attribution edge-type classification between two nodes
  verify   — Claim verification against provided evidence

All judgments are ADVISORY ONLY. This sidecar does not affect ECU balances,
ILC settlement, protocol state, graph writes, or any value-path surface.
Operator must supply a TYPESAFE_API_KEY environment variable or --api-key flag.

Non-claims:
  - no_ecu_mutation
  - no_ilc_settlement
  - no_protocol_graph_write
  - no_wallet_action
  - no_cdl_authority
  - no_public_serving
  - advisory_output_only
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.request
from typing import Any


TYPESAFE_JUDGMENT_SIDECAR_VERSION = "typesafe_judgment_sidecar_phase_1619.v0.1"
TYPESAFE_JUDGMENT_ADVISORY_ONLY_TOKEN = "typesafe_judgment_advisory_only_phase_1619"
TYPESAFE_JUDGMENT_NO_PROTOCOL_WRITE_TOKEN = (
    "typesafe_judgment_no_protocol_graph_write_phase_1619"
)

TYPESAFE_API_BASE_URL = "https://api.typesafe.ai/v1/systemone"
TYPESAFE_API_MODEL = "jev-latest"

_MAX_RESPONSE_BYTES = 1_048_576  # 1 MiB — OOM guard per CLAUDE.md rule 5
_API_TIMEOUT_SECONDS = 30        # mandatory per CLAUDE.md rule 6
_MAX_CONTENT_BYTES = 65_536      # 64 KiB max state payload to Jev
_MAX_SOURCE_REFS = 16
_PROBABILITY_SUM_TOLERANCE = 0.05

_NON_CLAIMS = (
    "no_ecu_mutation",
    "no_ilc_settlement",
    "no_protocol_graph_write",
    "no_wallet_action",
    "no_cdl_authority",
    "no_public_serving",
    "advisory_output_only",
)

# ── ILC attribution edge types that Jev classifies ──────────────────────────

_ATTRIBUTION_EDGE_CRITERIA: dict[str, str] = {
    "reuse": (
        "Source directly reuses, references, or builds upon the core intellectual "
        "contribution of target — the source's value is substantially derived from target"
    ),
    "co_authorship": (
        "Source and target share substantial authorship overlap — the same contributor(s) "
        "were materially responsible for both, or one was co-produced with the other"
    ),
    "refutation": (
        "Source explicitly contradicts, disproves, or provides decisive counter-evidence "
        "against target's central claim — not mere disagreement but substantive rebuttal"
    ),
    "provenance": (
        "Source traces indirect conceptual lineage through target — target is an ancestor "
        "in the intellectual chain but not directly reused; at least one intermediate step exists"
    ),
    "none": (
        "No meaningful attribution relationship exists — the connection is coincidental, "
        "superficial, or limited to common vocabulary with no intellectual dependency"
    ),
}

_EPISTEMIC_QUALITY_CRITERIA = [
    "Personal opinion, anecdote, or unsubstantiated assertion",
    "General reference, summary, or secondary claim with no new evidence",
    "Factual claim with implicit or unstated evidence",
    "Substantiated claim with explicit citations and traceable sources",
    "Novel insight or first-claim discovery with rigorous, verifiable evidence",
]

_ORIGINALITY_CRITERIA = [
    "Verbatim copy or near-duplicate of a cited source",
    "Minor paraphrase or restatement with trivial variation",
    "Synthesis that combines existing ideas into a new framing",
    "Novel argument, interpretation, or analysis not present in cited sources",
    "Original discovery, first claim, or breakthrough insight",
]

_RELATIONSHIP_STRENGTH_CRITERIA = [
    "Unrelated or coincidental — no intellectual dependency",
    "Tangentially related — shares context or vocabulary only",
    "Clearly related — common subject matter with some intellectual overlap",
    "Directly dependent — one substantively builds on the other",
    "Constitutively derived — one could not exist without the other",
]

_EVIDENCE_QUALITY_CRITERIA = [
    "No relevant evidence provided",
    "Weak or circumstantial evidence only",
    "Moderate evidence with meaningful gaps",
    "Strong direct evidence with minor gaps",
    "Definitive, exhaustive proof",
]


# ── Error type ───────────────────────────────────────────────────────────────


class TypeSafeJudgmentError(ValueError):
    """Fail-closed error for the TypeSafe sidecar with a stable token."""

    def __init__(self, token: str, message: str) -> None:
        super().__init__(message)
        self.token = token


# ── No-redirect handler — API key must not follow redirects ──────────────────
# Per CLAUDE.md rule 12: outbound HTTP that transmits auth credentials must
# disable redirect following to prevent credential exfiltration.


class _NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> None:  # type: ignore[override]
        raise TypeSafeJudgmentError(
            "typesafe_redirect_forbidden_phase_1619",
            f"unexpected redirect from TypeSafe API to {newurl!r} — aborting",
        )


# ── Core API call ─────────────────────────────────────────────────────────────


def _call_jev(
    api_key: str,
    state: str | dict[str, Any],
    questions: dict[str, Any],
) -> dict[str, Any]:
    """POST to the TypeSafe Jev API and return the parsed response.

    Security properties:
    - No redirect following (auth token in header)
    - Hard timeout of _API_TIMEOUT_SECONDS
    - Response capped at _MAX_RESPONSE_BYTES before decode
    - TLS verification enabled (default urllib behaviour)
    - API key validated non-empty before use
    """
    if not isinstance(api_key, str) or not api_key.strip():
        raise TypeSafeJudgmentError(
            "typesafe_api_key_missing_phase_1619",
            "TYPESAFE_API_KEY is required — set it as an env var or pass --api-key",
        )
    if not isinstance(questions, dict):
        raise TypeSafeJudgmentError(
            "typesafe_questions_not_object_phase_1619",
            f"questions must be an object, got {type(questions).__name__}",
        )
    if not questions:
        raise TypeSafeJudgmentError(
            "typesafe_questions_empty_phase_1619",
            "at least one question is required",
        )

    payload = json.dumps(
        {"state": state, "model": TYPESAFE_API_MODEL, "questions": questions},
        allow_nan=False,
        sort_keys=True,
    ).encode("utf-8")

    if len(payload) > _MAX_CONTENT_BYTES:
        raise TypeSafeJudgmentError(
            "typesafe_payload_too_large_phase_1619",
            f"request payload exceeds {_MAX_CONTENT_BYTES} bytes",
        )

    opener = urllib.request.build_opener(_NoRedirectHandler())
    req = urllib.request.Request(
        TYPESAFE_API_BASE_URL,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
    )

    try:
        with opener.open(req, timeout=_API_TIMEOUT_SECONDS) as resp:
            # OOM guard: read at most _MAX_RESPONSE_BYTES
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                total += len(chunk)
                if total > _MAX_RESPONSE_BYTES:
                    raise TypeSafeJudgmentError(
                        "typesafe_response_too_large_phase_1619",
                        "TypeSafe API response exceeds maximum allowed size",
                    )
                chunks.append(chunk)
            raw = b"".join(chunks)
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read(4096).decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            pass
        raise TypeSafeJudgmentError(
            f"typesafe_http_error_{exc.code}_phase_1619",
            f"TypeSafe API returned HTTP {exc.code}: {body[:256]}",
        ) from exc
    except urllib.error.URLError as exc:
        raise TypeSafeJudgmentError(
            "typesafe_network_error_phase_1619",
            f"TypeSafe API network error: {exc.reason}",
        ) from exc
    except TimeoutError as exc:
        raise TypeSafeJudgmentError(
            "typesafe_timeout_phase_1619",
            f"TypeSafe API timed out after {_API_TIMEOUT_SECONDS}s",
        ) from exc

    try:
        result: dict[str, Any] = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TypeSafeJudgmentError(
            "typesafe_response_json_invalid_phase_1619",
            f"TypeSafe API returned non-JSON response: {exc}",
        ) from exc

    _reject_nonstandard_json_numbers("response", result)
    if not isinstance(result, dict) or "answers" not in result:
        raise TypeSafeJudgmentError(
            "typesafe_response_schema_invalid_phase_1619",
            "TypeSafe API response missing 'answers' field",
        )
    _require_mapping("answers", result["answers"])
    return result


# ── NaN/Infinity guard for any float returned from Jev ───────────────────────
# Per CLAUDE.md rule 11: float values must be checked for finiteness before use.


def _reject_nonstandard_json_numbers(name: str, value: object) -> None:
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return
    if isinstance(value, int):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise TypeSafeJudgmentError(
                f"typesafe_{name}_non_finite_phase_1619",
                f"non-finite JSON number in TypeSafe response at {name!r}: {value}",
            )
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonstandard_json_numbers(f"{name}.{index}", item)
        return
    if isinstance(value, dict):
        for key, item in value.items():
            key_name = str(key) if isinstance(key, str) else "<non_string_key>"
            _reject_nonstandard_json_numbers(f"{name}.{key_name}", item)
        return
    raise TypeSafeJudgmentError(
        f"typesafe_{name}_unsupported_json_type_phase_1619",
        f"unsupported JSON value in TypeSafe response at {name!r}: {type(value).__name__}",
    )


def _require_finite_float(name: str, value: object) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_not_numeric_phase_1619",
            f"expected numeric answer for {name!r}, got {type(value).__name__}",
        )
    f = float(value)
    if not math.isfinite(f):
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_non_finite_phase_1619",
            f"non-finite value in TypeSafe answer for {name!r}: {f}",
        )
    return f


def _require_mapping(name: str, value: object) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_not_object_phase_1619",
            f"expected object answer for {name!r}, got {type(value).__name__}",
        )
    return value


def _require_answer_mapping(answers: dict[str, Any], question_id: str) -> dict[str, Any]:
    if question_id not in answers:
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{question_id}_missing_phase_1619",
            f"TypeSafe response missing required answer {question_id!r}",
        )
    return _require_mapping(question_id, answers[question_id])


def _require_probability(name: str, value: object) -> float:
    probability = _require_finite_float(name, value)
    if probability < 0.0 or probability > 1.0:
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_out_of_range_phase_1619",
            f"expected {name!r} in [0, 1], got {probability}",
        )
    return probability


def _require_score(name: str, value: object, max_score: int) -> float:
    score = _require_finite_float(name, value)
    if score < 0.0 or score > float(max_score):
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_out_of_range_phase_1619",
            f"expected {name!r} in [0, {max_score}], got {score}",
        )
    return score


def _validate_probability_map(
    name: str,
    value: object,
    *,
    allowed_keys: set[str] | None = None,
    require_exact_keys: bool = False,
) -> dict[str, float]:
    probabilities = _require_mapping(name, value)
    if not probabilities:
        return {}

    actual_keys = set(probabilities)
    if allowed_keys is not None:
        if require_exact_keys and actual_keys != allowed_keys:
            raise TypeSafeJudgmentError(
                f"typesafe_answer_{name}_keys_invalid_phase_1619",
                f"expected probability keys {sorted(allowed_keys)!r}, got {sorted(actual_keys)!r}",
            )
        unknown_keys = actual_keys - allowed_keys
        if unknown_keys:
            raise TypeSafeJudgmentError(
                f"typesafe_answer_{name}_keys_invalid_phase_1619",
                f"unexpected probability keys for {name!r}: {sorted(unknown_keys)!r}",
            )

    parsed: dict[str, float] = {}
    for key, raw_probability in probabilities.items():
        if not isinstance(key, str) or not key:
            raise TypeSafeJudgmentError(
                f"typesafe_answer_{name}_key_invalid_phase_1619",
                f"probability map {name!r} contains a non-string or empty key",
            )
        parsed[key] = _require_probability(f"{name}.{key}", raw_probability)

    total = math.fsum(parsed.values())
    if abs(total - 1.0) > _PROBABILITY_SUM_TOLERANCE:
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_sum_invalid_phase_1619",
            f"probability map {name!r} sums to {total}, expected 1.0 +/- {_PROBABILITY_SUM_TOLERANCE}",
        )
    return parsed


def _require_choice(name: str, value: object, allowed: set[str]) -> str:
    if not isinstance(value, str):
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_not_string_phase_1619",
            f"expected string choice for {name!r}, got {type(value).__name__}",
        )
    if value not in allowed:
        raise TypeSafeJudgmentError(
            f"typesafe_answer_{name}_choice_invalid_phase_1619",
            f"unexpected choice for {name!r}: {value!r}",
        )
    return value


# ── Public judgment functions ─────────────────────────────────────────────────


def score_node(
    api_key: str,
    node_content: str,
    *,
    node_type: str = "",
    source_refs: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    """Return advisory epistemic quality scores for an ILC node.

    Judgments returned:
      epistemic_quality  — Score 0-4 (Low→Very High epistemic value)
      originality        — Score 0-4 (Derivative→Breakthrough)
      is_well_cited      — Noul 0-1 (probability adequately cites sources)
      refutation_risk    — Noul 0-1 (probability contains readily-refutable claims)

    Non-claims: does NOT write to the ILC graph, does NOT affect ECU.
    """
    if not isinstance(node_content, str) or not node_content.strip():
        raise TypeSafeJudgmentError(
            "typesafe_score_node_content_empty_phase_1619",
            "node_content must be a non-empty string",
        )
    refs = list(source_refs)
    if len(refs) > _MAX_SOURCE_REFS:
        raise TypeSafeJudgmentError(
            "typesafe_score_source_refs_too_many_phase_1619",
            f"source_refs must not exceed {_MAX_SOURCE_REFS} entries",
        )

    state: dict[str, Any] = {"node_content": node_content.strip()}
    if node_type:
        state["node_type"] = str(node_type).strip()
    if refs:
        state["source_refs"] = refs

    questions: dict[str, Any] = {
        "epistemic_quality": {
            "type": "score",
            "instructions": (
                "How epistemically valuable is this contribution to human knowledge? "
                "Consider the quality of evidence, specificity of claims, and intellectual depth."
            ),
            "criteria": _EPISTEMIC_QUALITY_CRITERIA,
        },
        "originality": {
            "type": "score",
            "instructions": (
                "How original is this contribution relative to any cited sources? "
                "Consider whether it reuses, synthesises, or advances beyond existing work."
            ),
            "criteria": _ORIGINALITY_CRITERIA,
        },
        "is_well_cited": {
            "type": "noul",
            "instructions": (
                "Does this node adequately cite its sources? "
                "A well-cited node identifies where its key claims came from."
            ),
            "criteria": {
                "true": "Sources are explicitly named or referenced for key claims",
                "false": "Key claims are asserted without any source attribution",
            },
        },
        "refutation_risk": {
            "type": "noul",
            "instructions": (
                "Does this content contain claims that appear readily refutable, "
                "internally inconsistent, or factually dubious on their face?"
            ),
            "criteria": {
                "true": "Contains claims that are likely to be challenged or disproven",
                "false": "Claims appear well-grounded and internally consistent",
            },
        },
    }

    raw = _call_jev(api_key, state, questions)
    answers = _require_mapping("answers", raw["answers"])

    eq = _require_answer_mapping(answers, "epistemic_quality")
    orig = _require_answer_mapping(answers, "originality")
    cited = _require_answer_mapping(answers, "is_well_cited")
    risk = _require_answer_mapping(answers, "refutation_risk")

    eq_probabilities = _validate_probability_map(
        "epistemic_quality.probabilities", eq.get("probabilities", {})
    )
    orig_probabilities = _validate_probability_map(
        "originality.probabilities", orig.get("probabilities", {})
    )

    return {
        "mode": "score",
        "sidecar_version": TYPESAFE_JUDGMENT_SIDECAR_VERSION,
        "advisory_only": True,
        "non_claims": list(_NON_CLAIMS),
        "judgments": {
            "epistemic_quality": {
                "score": _require_score(
                    "epistemic_quality.score",
                    eq.get("score"),
                    len(_EPISTEMIC_QUALITY_CRITERIA) - 1,
                ),
                "confidence": _require_probability(
                    "epistemic_quality.confidence", eq.get("confidence")
                ),
                "legend": _require_mapping(
                    "epistemic_quality.legend", eq.get("legend", {})
                ),
                "probabilities": eq_probabilities,
            },
            "originality": {
                "score": _require_score(
                    "originality.score",
                    orig.get("score"),
                    len(_ORIGINALITY_CRITERIA) - 1,
                ),
                "confidence": _require_probability(
                    "originality.confidence", orig.get("confidence")
                ),
                "legend": _require_mapping("originality.legend", orig.get("legend", {})),
                "probabilities": orig_probabilities,
            },
            "is_well_cited": {
                "noul": _require_probability("is_well_cited.noul", cited.get("noul")),
            },
            "refutation_risk": {
                "noul": _require_probability("refutation_risk.noul", risk.get("noul")),
            },
        },
        "model": raw.get("model", TYPESAFE_API_MODEL),
        "usage": raw.get("usage", {}),
    }


def classify_attribution(
    api_key: str,
    source_content: str,
    target_content: str,
    *,
    relationship_description: str = "",
) -> dict[str, Any]:
    """Return advisory ILC attribution edge-type classification for a source→target pair.

    Judgments returned:
      attribution_edge_type   — Choice: reuse | co_authorship | refutation | provenance | none
      is_genuine_reuse        — Noul 0-1 (probability source genuinely builds on target)
      relationship_strength   — Score 0-4 (Unrelated→Constitutively derived)

    Non-claims: does NOT open attribution events, does NOT affect ECU.
    """
    if not isinstance(source_content, str) or not source_content.strip():
        raise TypeSafeJudgmentError(
            "typesafe_classify_source_empty_phase_1619",
            "source_content must be a non-empty string",
        )
    if not isinstance(target_content, str) or not target_content.strip():
        raise TypeSafeJudgmentError(
            "typesafe_classify_target_empty_phase_1619",
            "target_content must be a non-empty string",
        )

    state: dict[str, Any] = {
        "source_content": source_content.strip(),
        "target_content": target_content.strip(),
    }
    if relationship_description:
        state["relationship_description"] = relationship_description.strip()

    questions: dict[str, Any] = {
        "attribution_edge_type": {
            "type": "choice",
            "instructions": (
                "What is the ILC attribution edge type that best describes the relationship "
                "from source to target? Select the single best match."
            ),
            "criteria": _ATTRIBUTION_EDGE_CRITERIA,
        },
        "is_genuine_reuse": {
            "type": "noul",
            "instructions": (
                "Does the source genuinely build upon the intellectual contribution of the "
                "target, beyond superficial mention or coincidental overlap?"
            ),
            "criteria": {
                "true": (
                    "Source substantively derives value from target's core contribution"
                ),
                "false": (
                    "Connection is coincidental, superficial, or limited to shared vocabulary"
                ),
            },
        },
        "relationship_strength": {
            "type": "score",
            "instructions": (
                "How strong is the intellectual relationship between source and target? "
                "Consider dependency, derivation, and conceptual overlap."
            ),
            "criteria": _RELATIONSHIP_STRENGTH_CRITERIA,
        },
    }

    raw = _call_jev(api_key, state, questions)
    answers = _require_mapping("answers", raw["answers"])

    edge = _require_answer_mapping(answers, "attribution_edge_type")
    reuse = _require_answer_mapping(answers, "is_genuine_reuse")
    strength = _require_answer_mapping(answers, "relationship_strength")
    edge_choice = _require_choice(
        "attribution_edge_type.choice",
        edge.get("choice"),
        set(_ATTRIBUTION_EDGE_CRITERIA),
    )
    edge_probabilities = _validate_probability_map(
        "attribution_edge_type.probabilities",
        edge.get("probabilities", {}),
        allowed_keys=set(_ATTRIBUTION_EDGE_CRITERIA),
        require_exact_keys=True,
    )
    strength_probabilities = _validate_probability_map(
        "relationship_strength.probabilities", strength.get("probabilities", {})
    )

    return {
        "mode": "classify",
        "sidecar_version": TYPESAFE_JUDGMENT_SIDECAR_VERSION,
        "advisory_only": True,
        "non_claims": list(_NON_CLAIMS),
        "judgments": {
            "attribution_edge_type": {
                "choice": edge_choice,
                "probabilities": edge_probabilities,
                "confidence": _require_probability(
                    "attribution_edge_type.confidence", edge.get("confidence")
                ),
            },
            "is_genuine_reuse": {
                "noul": _require_probability("is_genuine_reuse.noul", reuse.get("noul")),
            },
            "relationship_strength": {
                "score": _require_score(
                    "relationship_strength.score",
                    strength.get("score"),
                    len(_RELATIONSHIP_STRENGTH_CRITERIA) - 1,
                ),
                "confidence": _require_probability(
                    "relationship_strength.confidence", strength.get("confidence")
                ),
                "legend": _require_mapping(
                    "relationship_strength.legend", strength.get("legend", {})
                ),
                "probabilities": strength_probabilities,
            },
        },
        "model": raw.get("model", TYPESAFE_API_MODEL),
        "usage": raw.get("usage", {}),
    }


def verify_claim(
    api_key: str,
    claim: str,
    evidence: str,
) -> dict[str, Any]:
    """Return advisory claim verification judgment.

    Judgments returned:
      claim_supported          — Noul 0-1 (probability evidence supports claim)
      evidence_quality         — Score 0-4 (None→Definitive)
      is_internally_consistent — Noul 0-1 (probability evidence is consistent)

    Non-claims: does NOT affect protocol state, ECU, or graph writes.
    """
    if not isinstance(claim, str) or not claim.strip():
        raise TypeSafeJudgmentError(
            "typesafe_verify_claim_empty_phase_1619",
            "claim must be a non-empty string",
        )
    if not isinstance(evidence, str) or not evidence.strip():
        raise TypeSafeJudgmentError(
            "typesafe_verify_evidence_empty_phase_1619",
            "evidence must be a non-empty string",
        )

    state: dict[str, Any] = {
        "claim": claim.strip(),
        "evidence": evidence.strip(),
    }

    questions: dict[str, Any] = {
        "claim_supported": {
            "type": "noul",
            "instructions": "Is this claim supported by the provided evidence?",
            "criteria": {
                "true": "Evidence directly and sufficiently supports the claim",
                "false": "Evidence does not support, contradicts, or is irrelevant to the claim",
            },
        },
        "evidence_quality": {
            "type": "score",
            "instructions": (
                "How strong is this evidence in supporting the claim? "
                "Consider directness, completeness, and verifiability."
            ),
            "criteria": _EVIDENCE_QUALITY_CRITERIA,
        },
        "is_internally_consistent": {
            "type": "noul",
            "instructions": (
                "Is the provided evidence internally consistent, "
                "with no significant contradictions or self-refutation?"
            ),
            "criteria": {
                "true": "Evidence is coherent and contains no internal contradictions",
                "false": "Evidence contains contradictions, inconsistencies, or self-refutation",
            },
        },
    }

    raw = _call_jev(api_key, state, questions)
    answers = _require_mapping("answers", raw["answers"])

    supported = _require_answer_mapping(answers, "claim_supported")
    quality = _require_answer_mapping(answers, "evidence_quality")
    consistent = _require_answer_mapping(answers, "is_internally_consistent")
    quality_probabilities = _validate_probability_map(
        "evidence_quality.probabilities", quality.get("probabilities", {})
    )

    return {
        "mode": "verify",
        "sidecar_version": TYPESAFE_JUDGMENT_SIDECAR_VERSION,
        "advisory_only": True,
        "non_claims": list(_NON_CLAIMS),
        "judgments": {
            "claim_supported": {
                "noul": _require_probability("claim_supported.noul", supported.get("noul")),
            },
            "evidence_quality": {
                "score": _require_score(
                    "evidence_quality.score",
                    quality.get("score"),
                    len(_EVIDENCE_QUALITY_CRITERIA) - 1,
                ),
                "confidence": _require_probability(
                    "evidence_quality.confidence", quality.get("confidence")
                ),
                "legend": _require_mapping(
                    "evidence_quality.legend", quality.get("legend", {})
                ),
                "probabilities": quality_probabilities,
            },
            "is_internally_consistent": {
                "noul": _require_probability(
                    "is_internally_consistent.noul", consistent.get("noul")
                ),
            },
        },
        "model": raw.get("model", TYPESAFE_API_MODEL),
        "usage": raw.get("usage", {}),
    }


# ── Manifest ──────────────────────────────────────────────────────────────────


def typesafe_judgment_sidecar_manifest() -> dict[str, Any]:
    """Return the static TypeSafe judgment sidecar manifest."""
    return {
        "advisory_only": True,
        "api_base_url": TYPESAFE_API_BASE_URL,
        "api_model": TYPESAFE_API_MODEL,
        "contract_version": TYPESAFE_JUDGMENT_SIDECAR_VERSION,
        "max_response_bytes": _MAX_RESPONSE_BYTES,
        "modes": ["classify", "score", "verify"],
        "non_claims": list(_NON_CLAIMS),
        "public_serving_enabled": False,
        "sidecar_id": "typesafe",
        "timeout_seconds": _API_TIMEOUT_SECONDS,
        "tokens": [
            TYPESAFE_JUDGMENT_ADVISORY_ONLY_TOKEN,
            TYPESAFE_JUDGMENT_NO_PROTOCOL_WRITE_TOKEN,
            TYPESAFE_JUDGMENT_SIDECAR_VERSION,
        ],
        "wiring_modes": ["in_process_import", "local_cli_subprocess"],
    }


# ── CLI entry point ───────────────────────────────────────────────────────────


def _resolve_api_key(args: argparse.Namespace) -> str:
    key = getattr(args, "api_key", None) or os.environ.get("TYPESAFE_API_KEY", "")
    if not key or not key.strip():
        raise TypeSafeJudgmentError(
            "typesafe_api_key_missing_phase_1619",
            "TypeSafe API key required: set TYPESAFE_API_KEY env var or pass --api-key",
        )
    return key.strip()


def _write_result(result: dict[str, Any]) -> None:
    sys.stdout.write(
        json.dumps(result, allow_nan=False, indent=2, sort_keys=True) + "\n"
    )


def _write_error(token: str, message: str, exit_code: int = 1) -> int:
    sys.stderr.write(
        json.dumps({"ok": False, "error": token, "message": message}, sort_keys=True)
        + "\n"
    )
    return exit_code


def main(argv: list[str]) -> int:
    """CLI entry point for `ilc sidecar typesafe <mode> [args]`.

    Modes:
      score    Score a node's epistemic quality
      classify Classify attribution edge type between two nodes
      verify   Verify a claim against evidence
      manifest Print the sidecar manifest
    """
    parser = argparse.ArgumentParser(
        prog="ilc sidecar typesafe",
        description=(
            "TypeSafe Jev advisory judgment sidecar for ILC epistemic graph. "
            "All judgments are advisory only — no ECU, ILC, or protocol writes."
        ),
    )
    parser.add_argument(
        "--api-key",
        default="",
        help="TypeSafe API key (default: TYPESAFE_API_KEY env var)",
    )

    subparsers = parser.add_subparsers(dest="mode", required=True)

    # score
    p_score = subparsers.add_parser(
        "score", help="Score a node's epistemic quality"
    )
    p_score.add_argument(
        "--node-content",
        required=True,
        help="Text content of the node to score",
    )
    p_score.add_argument(
        "--node-type",
        default="",
        help="ILC node type (e.g. assert.truth)",
    )
    p_score.add_argument(
        "--source-ref",
        action="append",
        dest="source_refs",
        default=[],
        metavar="REF",
        help="Source ref cited by the node (repeat for multiple)",
    )

    # classify
    p_classify = subparsers.add_parser(
        "classify", help="Classify attribution edge type between two nodes"
    )
    p_classify.add_argument(
        "--source-content",
        required=True,
        help="Text content of the source node",
    )
    p_classify.add_argument(
        "--target-content",
        required=True,
        help="Text content of the target node",
    )
    p_classify.add_argument(
        "--relationship",
        default="",
        help="Optional description of the known relationship",
    )

    # verify
    p_verify = subparsers.add_parser(
        "verify", help="Verify a claim against provided evidence"
    )
    p_verify.add_argument("--claim", required=True, help="The claim to verify")
    p_verify.add_argument(
        "--evidence", required=True, help="Evidence to evaluate against the claim"
    )

    # manifest
    subparsers.add_parser("manifest", help="Print the sidecar manifest")

    args = parser.parse_args(argv)

    try:
        if args.mode == "manifest":
            _write_result({"ok": True, **typesafe_judgment_sidecar_manifest()})
            return 0

        api_key = _resolve_api_key(args)

        if args.mode == "score":
            result = score_node(
                api_key,
                args.node_content,
                node_type=args.node_type,
                source_refs=args.source_refs,
            )
            _write_result({"ok": True, **result})
            return 0

        if args.mode == "classify":
            result = classify_attribution(
                api_key,
                args.source_content,
                args.target_content,
                relationship_description=args.relationship,
            )
            _write_result({"ok": True, **result})
            return 0

        if args.mode == "verify":
            result = verify_claim(api_key, args.claim, args.evidence)
            _write_result({"ok": True, **result})
            return 0

        return _write_error(
            "typesafe_unknown_mode_phase_1619",
            f"unknown mode: {args.mode!r}",
            exit_code=2,
        )

    except TypeSafeJudgmentError as exc:
        return _write_error(exc.token, str(exc))
    except KeyboardInterrupt:
        return _write_error("typesafe_interrupted_phase_1619", "interrupted", exit_code=1)


__all__ = [
    "TYPESAFE_JUDGMENT_ADVISORY_ONLY_TOKEN",
    "TYPESAFE_JUDGMENT_NO_PROTOCOL_WRITE_TOKEN",
    "TYPESAFE_JUDGMENT_SIDECAR_VERSION",
    "TypeSafeJudgmentError",
    "classify_attribution",
    "main",
    "score_node",
    "typesafe_judgment_sidecar_manifest",
    "verify_claim",
]
