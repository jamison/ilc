from __future__ import annotations

from pathlib import Path
import re
import unittest


NODE_RS = Path("ilc_consensus/src/node.rs")
CARGO_TOML = Path("ilc_consensus/Cargo.toml")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestPhase776Layer1LogHygiene(unittest.TestCase):
    def test_log_hygiene_token_and_helpers_exist(self) -> None:
        text = _read(NODE_RS)
        self.assertIn("layer1_agentid_log_hygiene_applied", text)
        self.assertIn("fn fmt_agent_id(", text)
        self.assertIn("fn fmt_object_ref(", text)

    def test_debug_feature_exists(self) -> None:
        text = _read(CARGO_TOML)
        self.assertIn("[features]", text)
        self.assertIn("debug_agent_ids = []", text)

    def test_non_debug_path_uses_constant_redaction_token(self) -> None:
        text = _read(NODE_RS)
        self.assertIn('#[cfg(not(feature = "debug_agent_ids"))]', text)
        self.assertIn("[redacted:agent_id]", text)

    def test_debug_path_keeps_explicit_debug_render(self) -> None:
        text = _read(NODE_RS)
        self.assertIn('#[cfg(feature = "debug_agent_ids")]', text)
        self.assertIn('format!("{:?}", id)', text)

    def test_log_sites_use_formatted_object_ref(self) -> None:
        text = _read(NODE_RS)
        required_markers = (
            'acking transfer obj_ref={}',
            'ack from peer={} for obj_ref={}',
            'AckFor for unknown obj_ref={}',
            'assembled certificate for obj_ref={}',
            'received Certificate for obj_ref={}',
            'MissingCertResponse: replaying certificate obj_ref={}',
        )
        for marker in required_markers:
            self.assertIn(marker, text)
        self.assertGreaterEqual(text.count("fmt_object_ref(&object_ref)"), 4)
        self.assertGreaterEqual(text.count("fmt_object_ref(&cert.transfer.object_ref)"), 2)

    def test_no_bare_object_ref_debug_in_runtime_log_macros(self) -> None:
        text = _read(NODE_RS)
        self.assertNotRegex(
            text,
            re.compile(r'eprintln!\(\s*"[^"\n]*obj_ref=\{:\?\}'),
        )

    def test_no_plaintext_agentid_array_literal_in_runtime_log_messages(self) -> None:
        text = _read(NODE_RS)
        self.assertNotIn("AgentID([", text.split("#[cfg(test)]")[0])


if __name__ == "__main__":
    unittest.main()
