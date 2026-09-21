# SPDX-License-Identifier: AGPL-3.0-only
"""Tests for the TypeSafe Jev judgment sidecar.

Coverage:
  - _require_finite_float: NaN, Infinity, non-numeric, valid float
  - TypeSafeJudgmentError: token + message attributes
  - _call_jev: missing/empty API key, empty questions, payload too large,
                HTTP errors, timeout, non-JSON response, missing 'answers'
  - score_node: empty content, too many source_refs, valid (mocked)
  - classify_attribution: empty source/target, valid (mocked)
  - verify_claim: empty claim/evidence, valid (mocked)
  - typesafe_judgment_sidecar_manifest: structure check
  - main() CLI: manifest subcommand (no network needed), missing-key error,
                missing subcommand → usage error
  - _NoRedirectHandler: raises on 3xx
"""

from __future__ import annotations

import json
import unittest
from unittest.mock import MagicMock, patch

# Import under test
from ilc_core.sidecars.typesafe_judgment import (
    TypeSafeJudgmentError,
    _NoRedirectHandler,
    _call_jev,
    _require_finite_float,
    classify_attribution,
    main,
    score_node,
    typesafe_judgment_sidecar_manifest,
    verify_claim,
    TYPESAFE_JUDGMENT_SIDECAR_VERSION,
)


# ── _require_finite_float ─────────────────────────────────────────────────────


class TestRequireFiniteFloat(unittest.TestCase):
    def test_valid_float(self):
        self.assertAlmostEqual(_require_finite_float("x", 0.5), 0.5)

    def test_valid_int(self):
        self.assertEqual(_require_finite_float("x", 3), 3.0)

    def test_nan_rejected(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _require_finite_float("myfield", float("nan"))
        self.assertIn("non_finite", ctx.exception.token)

    def test_inf_rejected(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _require_finite_float("myfield", float("inf"))
        self.assertIn("non_finite", ctx.exception.token)

    def test_neg_inf_rejected(self):
        with self.assertRaises(TypeSafeJudgmentError):
            _require_finite_float("myfield", float("-inf"))

    def test_string_rejected(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _require_finite_float("myfield", "0.5")
        self.assertIn("not_numeric", ctx.exception.token)

    def test_none_rejected(self):
        with self.assertRaises(TypeSafeJudgmentError):
            _require_finite_float("myfield", None)

    def test_bool_rejected(self):
        # bool is subclass of int but must be rejected per the guard
        with self.assertRaises(TypeSafeJudgmentError):
            _require_finite_float("myfield", True)

    def test_zero_valid(self):
        self.assertEqual(_require_finite_float("x", 0), 0.0)


# ── TypeSafeJudgmentError ─────────────────────────────────────────────────────


class TestTypeSafeJudgmentError(unittest.TestCase):
    def test_token_attribute(self):
        err = TypeSafeJudgmentError("my_token", "my message")
        self.assertEqual(err.token, "my_token")

    def test_message_attribute(self):
        err = TypeSafeJudgmentError("tok", "hello world")
        self.assertEqual(str(err), "hello world")

    def test_is_value_error(self):
        self.assertIsInstance(TypeSafeJudgmentError("t", "m"), ValueError)


# ── _NoRedirectHandler ────────────────────────────────────────────────────────


class TestNoRedirectHandler(unittest.TestCase):
    def test_raises_on_redirect(self):
        handler = _NoRedirectHandler()
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            handler.redirect_request(None, None, 301, "Moved", None, "https://evil.example.com/")
        self.assertIn("redirect_forbidden", ctx.exception.token)

    def test_raises_on_302(self):
        handler = _NoRedirectHandler()
        with self.assertRaises(TypeSafeJudgmentError):
            handler.redirect_request(None, None, 302, "Found", None, "https://other.example.com/")


# ── _call_jev ─────────────────────────────────────────────────────────────────


class TestCallJev(unittest.TestCase):
    def test_empty_api_key_raises(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("", "state", {"q1": {}})
        self.assertIn("api_key_missing", ctx.exception.token)

    def test_whitespace_api_key_raises(self):
        with self.assertRaises(TypeSafeJudgmentError):
            _call_jev("   ", "state", {"q1": {}})

    def test_non_string_api_key_raises(self):
        with self.assertRaises(TypeSafeJudgmentError):
            _call_jev(None, "state", {"q1": {}})  # type: ignore[arg-type]

    def test_empty_questions_raises(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("valid-key", "state", {})
        self.assertIn("questions_empty", ctx.exception.token)

    def test_questions_must_be_object(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("valid-key", "state", [])  # type: ignore[arg-type]
        self.assertIn("questions_not_object", ctx.exception.token)

    def test_payload_too_large_raises(self):
        huge_state = "x" * 70_000  # > _MAX_CONTENT_BYTES (65536)
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("valid-key", huge_state, {"q1": {"type": "noul"}})
        self.assertIn("payload_too_large", ctx.exception.token)

    def _make_mock_response(self, body: dict) -> MagicMock:
        raw = json.dumps(body).encode("utf-8")
        mock_resp = MagicMock()
        mock_resp.read.side_effect = [raw, b""]
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def _make_chunked_mock_response(self, body: dict):
        raw = json.dumps(body).encode("utf-8")
        # Simulate chunked reads: 8192 bytes at a time
        chunks = [raw[i:i+8192] for i in range(0, len(raw), 8192)] + [b""]
        mock_resp = MagicMock()
        mock_resp.read.side_effect = chunks
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.OpenerDirector.open")
    def test_successful_call(self, mock_open):
        body = {"answers": {"q1": {"noul": 0.8}}, "model": "jev-latest", "usage": {}}
        mock_resp = self._make_chunked_mock_response(body)
        mock_open.return_value = mock_resp
        result = _call_jev("valid-key", "test state", {"q1": {"type": "noul"}})
        self.assertIn("answers", result)

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.build_opener")
    def test_http_error_raises(self, mock_build_opener):
        import urllib.error
        mock_opener = MagicMock()
        error_resp = MagicMock()
        error_resp.read.return_value = b"Unauthorized"
        mock_opener.open.side_effect = urllib.error.HTTPError(
            url=None, code=401, msg="Unauthorized", hdrs=None, fp=error_resp
        )
        mock_build_opener.return_value = mock_opener
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("bad-key", "state", {"q1": {"type": "noul"}})
        self.assertIn("http_error_401", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.build_opener")
    def test_timeout_raises(self, mock_build_opener):
        mock_opener = MagicMock()
        mock_opener.open.side_effect = TimeoutError()
        mock_build_opener.return_value = mock_opener
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("key", "state", {"q1": {"type": "noul"}})
        self.assertIn("timeout", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.build_opener")
    def test_non_json_response_raises(self, mock_build_opener):
        mock_opener = MagicMock()
        mock_resp = MagicMock()
        mock_resp.read.side_effect = [b"NOT JSON {{{", b""]
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp
        mock_build_opener.return_value = mock_opener
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("key", "state", {"q1": {"type": "noul"}})
        self.assertIn("json_invalid", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.build_opener")
    def test_missing_answers_field_raises(self, mock_build_opener):
        mock_opener = MagicMock()
        mock_resp = MagicMock()
        mock_resp.read.side_effect = [b'{"model": "jev-latest"}', b""]
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp
        mock_build_opener.return_value = mock_opener
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("key", "state", {"q1": {"type": "noul"}})
        self.assertIn("schema_invalid", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.build_opener")
    def test_oversized_response_raises(self, mock_build_opener):
        mock_opener = MagicMock()
        mock_resp = MagicMock()
        mock_resp.read.side_effect = [b"x" * (1024 * 1024 + 1), b""]
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp
        mock_build_opener.return_value = mock_opener
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("key", "state", {"q1": {"type": "noul"}})
        self.assertIn("response_too_large", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.build_opener")
    def test_answers_must_be_object(self, mock_build_opener):
        mock_opener = MagicMock()
        mock_resp = MagicMock()
        mock_resp.read.side_effect = [b'{"answers": []}', b""]
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp
        mock_build_opener.return_value = mock_opener
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("key", "state", {"q1": {"type": "noul"}})
        self.assertIn("answers_not_object", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment.urllib.request.build_opener")
    def test_nonstandard_json_number_rejected_recursively(self, mock_build_opener):
        mock_opener = MagicMock()
        mock_resp = MagicMock()
        mock_resp.read.side_effect = [b'{"answers": {"q1": {"noul": 0.5}}, "usage": {"cost": NaN}}', b""]
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_opener.open.return_value = mock_resp
        mock_build_opener.return_value = mock_opener
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            _call_jev("key", "state", {"q1": {"type": "noul"}})
        self.assertIn("non_finite", ctx.exception.token)


# ── score_node ────────────────────────────────────────────────────────────────


class TestScoreNode(unittest.TestCase):
    def test_empty_content_raises(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            score_node("key", "")
        self.assertIn("content_empty", ctx.exception.token)

    def test_whitespace_content_raises(self):
        with self.assertRaises(TypeSafeJudgmentError):
            score_node("key", "   ")

    def test_too_many_source_refs_raises(self):
        refs = [f"ref_{i}" for i in range(20)]  # > _MAX_SOURCE_REFS (16)
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            score_node("key", "some content", source_refs=refs)
        self.assertIn("source_refs_too_many", ctx.exception.token)

    def _mock_jev_response(self, answers: dict) -> dict:
        return {"answers": answers, "model": "jev-latest", "usage": {}}

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_valid_score_node(self, mock_call):
        mock_call.return_value = self._mock_jev_response({
            "epistemic_quality": {"score": 3.2, "confidence": 0.85, "legend": {}, "probabilities": {}},
            "originality": {"score": 2.1, "confidence": 0.7, "legend": {}, "probabilities": {}},
            "is_well_cited": {"noul": 0.9},
            "refutation_risk": {"noul": 0.1},
        })
        result = score_node("valid-key", "A well-sourced node about deep learning.")
        self.assertTrue(result["advisory_only"])
        self.assertIn("no_ecu_mutation", result["non_claims"])
        self.assertIn("epistemic_quality", result["judgments"])
        self.assertAlmostEqual(result["judgments"]["epistemic_quality"]["score"], 3.2)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_nan_in_score_response_raises(self, mock_call):
        mock_call.return_value = self._mock_jev_response({
            "epistemic_quality": {"score": float("nan"), "confidence": 0.5, "legend": {}, "probabilities": {}},
            "originality": {"score": 2.0, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "is_well_cited": {"noul": 0.5},
            "refutation_risk": {"noul": 0.2},
        })
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            score_node("key", "Some node content.")
        self.assertIn("non_finite", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_infinity_in_noul_raises(self, mock_call):
        mock_call.return_value = self._mock_jev_response({
            "epistemic_quality": {"score": 2.0, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "originality": {"score": 2.0, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "is_well_cited": {"noul": float("inf")},
            "refutation_risk": {"noul": 0.2},
        })
        with self.assertRaises(TypeSafeJudgmentError):
            score_node("key", "Some node content.")

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_score_confidence_above_one_raises(self, mock_call):
        mock_call.return_value = self._mock_jev_response({
            "epistemic_quality": {"score": 2.0, "confidence": 1.2, "legend": {}, "probabilities": {}},
            "originality": {"score": 2.0, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "is_well_cited": {"noul": 0.5},
            "refutation_risk": {"noul": 0.2},
        })
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            score_node("key", "Some node content.")
        self.assertIn("out_of_range", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_score_above_rubric_range_raises(self, mock_call):
        mock_call.return_value = self._mock_jev_response({
            "epistemic_quality": {"score": 99, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "originality": {"score": 2.0, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "is_well_cited": {"noul": 0.5},
            "refutation_risk": {"noul": 0.2},
        })
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            score_node("key", "Some node content.")
        self.assertIn("out_of_range", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_negative_noul_raises(self, mock_call):
        mock_call.return_value = self._mock_jev_response({
            "epistemic_quality": {"score": 2.0, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "originality": {"score": 2.0, "confidence": 0.5, "legend": {}, "probabilities": {}},
            "is_well_cited": {"noul": -0.1},
            "refutation_risk": {"noul": 0.2},
        })
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            score_node("key", "Some node content.")
        self.assertIn("out_of_range", ctx.exception.token)


# ── classify_attribution ──────────────────────────────────────────────────────


class TestClassifyAttribution(unittest.TestCase):
    def test_empty_source_raises(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            classify_attribution("key", "", "target content")
        self.assertIn("source_empty", ctx.exception.token)

    def test_empty_target_raises(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            classify_attribution("key", "source content", "")
        self.assertIn("target_empty", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_valid_classify(self, mock_call):
        mock_call.return_value = {
            "answers": {
                "attribution_edge_type": {
                    "choice": "reuse",
                    "confidence": 0.9,
                    "probabilities": {"reuse": 0.7, "co_authorship": 0.1, "refutation": 0.05, "provenance": 0.1, "none": 0.05},
                },
                "is_genuine_reuse": {"noul": 0.8},
                "relationship_strength": {"score": 3.5, "confidence": 0.85, "legend": {}, "probabilities": {}},
            },
            "model": "jev-latest",
            "usage": {},
        }
        result = classify_attribution("key", "source text", "target text")
        self.assertEqual(result["mode"], "classify")
        self.assertTrue(result["advisory_only"])
        self.assertEqual(result["judgments"]["attribution_edge_type"]["choice"], "reuse")

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_unknown_attribution_choice_raises(self, mock_call):
        mock_call.return_value = {
            "answers": {
                "attribution_edge_type": {
                    "choice": "invented_relation",
                    "confidence": 0.9,
                    "probabilities": {"reuse": 0.7, "co_authorship": 0.1, "refutation": 0.05, "provenance": 0.1, "none": 0.05},
                },
                "is_genuine_reuse": {"noul": 0.8},
                "relationship_strength": {"score": 3.5, "confidence": 0.85, "legend": {}, "probabilities": {}},
            },
        }
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            classify_attribution("key", "source text", "target text")
        self.assertIn("choice_invalid", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_negative_attribution_probability_raises(self, mock_call):
        mock_call.return_value = {
            "answers": {
                "attribution_edge_type": {
                    "choice": "reuse",
                    "confidence": 0.9,
                    "probabilities": {"reuse": -2, "co_authorship": 0.1, "refutation": 0.05, "provenance": 0.1, "none": 0.05},
                },
                "is_genuine_reuse": {"noul": 0.8},
                "relationship_strength": {"score": 3.5, "confidence": 0.85, "legend": {}, "probabilities": {}},
            },
        }
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            classify_attribution("key", "source text", "target text")
        self.assertIn("out_of_range", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_attribution_probability_keys_must_match_choices(self, mock_call):
        mock_call.return_value = {
            "answers": {
                "attribution_edge_type": {
                    "choice": "reuse",
                    "confidence": 0.9,
                    "probabilities": {"reuse": 0.7, "invented_relation": 0.3},
                },
                "is_genuine_reuse": {"noul": 0.8},
                "relationship_strength": {"score": 3.5, "confidence": 0.85, "legend": {}, "probabilities": {}},
            },
        }
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            classify_attribution("key", "source text", "target text")
        self.assertIn("keys_invalid", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_attribution_probability_sum_must_be_plausible(self, mock_call):
        mock_call.return_value = {
            "answers": {
                "attribution_edge_type": {
                    "choice": "reuse",
                    "confidence": 0.9,
                    "probabilities": {"reuse": 0.7, "co_authorship": 0.7, "refutation": 0.05, "provenance": 0.1, "none": 0.05},
                },
                "is_genuine_reuse": {"noul": 0.8},
                "relationship_strength": {"score": 3.5, "confidence": 0.85, "legend": {}, "probabilities": {}},
            },
        }
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            classify_attribution("key", "source text", "target text")
        self.assertIn("sum_invalid", ctx.exception.token)


# ── verify_claim ──────────────────────────────────────────────────────────────


class TestVerifyClaim(unittest.TestCase):
    def test_empty_claim_raises(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            verify_claim("key", "", "evidence")
        self.assertIn("claim_empty", ctx.exception.token)

    def test_empty_evidence_raises(self):
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            verify_claim("key", "some claim", "")
        self.assertIn("evidence_empty", ctx.exception.token)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_valid_verify(self, mock_call):
        mock_call.return_value = {
            "answers": {
                "claim_supported": {"noul": 0.75},
                "evidence_quality": {"score": 3.0, "confidence": 0.8, "legend": {}, "probabilities": {}},
                "is_internally_consistent": {"noul": 0.9},
            },
            "model": "jev-latest",
            "usage": {},
        }
        result = verify_claim("key", "The sky is blue.", "Spectroscopy shows blue wavelength dominance.")
        self.assertEqual(result["mode"], "verify")
        self.assertTrue(result["advisory_only"])
        self.assertAlmostEqual(result["judgments"]["claim_supported"]["noul"], 0.75)

    @patch("ilc_core.sidecars.typesafe_judgment._call_jev")
    def test_verify_evidence_score_out_of_range_raises(self, mock_call):
        mock_call.return_value = {
            "answers": {
                "claim_supported": {"noul": 0.75},
                "evidence_quality": {"score": 5.1, "confidence": 0.8, "legend": {}, "probabilities": {}},
                "is_internally_consistent": {"noul": 0.9},
            },
            "model": "jev-latest",
            "usage": {},
        }
        with self.assertRaises(TypeSafeJudgmentError) as ctx:
            verify_claim("key", "The sky is blue.", "Spectroscopy shows blue wavelength dominance.")
        self.assertIn("out_of_range", ctx.exception.token)


# ── typesafe_judgment_sidecar_manifest ────────────────────────────────────────


class TestManifest(unittest.TestCase):
    def test_manifest_structure(self):
        m = typesafe_judgment_sidecar_manifest()
        self.assertIn("sidecar_id", m)
        self.assertEqual(m["sidecar_id"], "typesafe")
        self.assertIn("contract_version", m)
        self.assertIn("non_claims", m)
        self.assertIn("no_ecu_mutation", m["non_claims"])
        self.assertIn("no_ilc_settlement", m["non_claims"])

    def test_manifest_advisory_only(self):
        m = typesafe_judgment_sidecar_manifest()
        self.assertTrue(m.get("advisory_only", False))

    def test_manifest_version_matches_constant(self):
        m = typesafe_judgment_sidecar_manifest()
        self.assertEqual(m["contract_version"], TYPESAFE_JUDGMENT_SIDECAR_VERSION)


# ── main() CLI ────────────────────────────────────────────────────────────────


class TestMain(unittest.TestCase):
    def test_manifest_subcommand_no_network(self):
        """manifest subcommand must work without an API key or network."""
        from io import StringIO
        buf = StringIO()
        with patch("sys.stdout", buf):
            exit_code = main(["manifest"])
        self.assertEqual(exit_code, 0)
        output = buf.getvalue()
        self.assertTrue(output.strip(), "Expected some output from manifest subcommand")
        parsed = json.loads(output)
        self.assertIn("sidecar_id", parsed)

    def test_no_subcommand_returns_usage_error(self):
        with self.assertRaises(SystemExit) as ctx:
            main([])
        self.assertEqual(ctx.exception.code, 2)

    def test_score_missing_api_key_env(self):
        """score subcommand without API key must fail with exit code 1."""
        env_without_key = {}
        with patch.dict("os.environ", env_without_key, clear=True):
            # Remove TYPESAFE_API_KEY if present
            exit_code = main(["score", "--node-content", "test content"])
        # Should fail with exit 1 (no key available)
        self.assertEqual(exit_code, 1)

    def test_score_empty_content_flag_returns_error(self):
        """score with empty --node-content must return exit code 1."""
        with patch.dict("os.environ", {"TYPESAFE_API_KEY": "dummy-key"}):
            exit_code = main(["score", "--node-content", ""])
        self.assertEqual(exit_code, 1)

    def test_classify_missing_target_returns_error(self):
        """classify without --target-content must fail (argparse or validation)."""
        with patch.dict("os.environ", {"TYPESAFE_API_KEY": "dummy-key"}):
            # Missing --target-content → argparse error → exit 2
            try:
                exit_code = main(["classify", "--source-content", "src"])
            except SystemExit as exc:
                exit_code = exc.code
        self.assertIn(exit_code, (1, 2))

    def test_verify_missing_evidence_returns_error(self):
        """verify without --evidence must fail."""
        with patch.dict("os.environ", {"TYPESAFE_API_KEY": "dummy-key"}):
            try:
                exit_code = main(["verify", "--claim", "some claim"])
            except SystemExit as exc:
                exit_code = exc.code
        self.assertIn(exit_code, (1, 2))

    @patch("ilc_core.sidecars.typesafe_judgment.score_node")
    def test_score_output_is_valid_json(self, mock_score):
        from io import StringIO
        mock_score.return_value = {
            "mode": "score",
            "advisory_only": True,
            "non_claims": ["no_ecu_mutation"],
            "judgments": {
                "epistemic_quality": {"score": 2.5, "confidence": 0.8, "legend": {}, "probabilities": {}},
                "originality": {"score": 1.5, "confidence": 0.7, "legend": {}, "probabilities": {}},
                "is_well_cited": {"noul": 0.6},
                "refutation_risk": {"noul": 0.3},
            },
            "model": "jev-latest",
            "usage": {},
            "sidecar_version": TYPESAFE_JUDGMENT_SIDECAR_VERSION,
        }
        buf = StringIO()
        with patch("sys.stdout", buf):
            with patch.dict("os.environ", {"TYPESAFE_API_KEY": "dummy-key"}):
                exit_code = main(["score", "--node-content", "Hello world node content."])
        self.assertEqual(exit_code, 0)
        parsed = json.loads(buf.getvalue())
        self.assertTrue(parsed["advisory_only"])


if __name__ == "__main__":
    unittest.main()
