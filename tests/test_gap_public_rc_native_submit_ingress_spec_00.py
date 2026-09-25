from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/specs/ilc_public_rc_native_submit_ingress_spec_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_SPEC_00_v0.1.md"
CDL = REPO_ROOT / "docs/specs/ilc_cdl_native_submit_ingress_opening_candidate_GAP_PUBLIC_RC_NATIVE_SUBMIT_INGRESS_SPEC_00_v0.1.md"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_spec_file_exists() -> None:
    assert SPEC.exists()


def test_cdl_candidate_file_exists() -> None:
    assert CDL.exists()


def test_endpoint_assertion_schema_defined() -> None:
    text = _text(SPEC)
    assert "public_submit_ingress_endpoint_assertion.v0.1" in text
    assert '"node_kind": "public_submit_ingress_endpoint_assertion"' in text


def test_endpoint_assertion_required_slots() -> None:
    text = _text(SPEC)
    for needle in (
        "serving_agent_id",
        "purpose_scoped_public_submit_ingress",
        "transport_public_key_hex",
        "tls_cert_sha256_fingerprint",
        "valid_from_epoch",
        "valid_until_epoch",
        "revocation_policy",
        "signing_dst",
        "json.dumps(payload, sort_keys=True, separators=(\",\", \":\"), allow_nan=False).encode(\"utf-8\")",
        "bls_public_key_hex",
        "bls_signature_hex",
    ):
        assert needle in text


def test_external_transports_are_not_trust_roots() -> None:
    text = _text(SPEC)
    assert "DNS, WebPKI, certbot, Caddy, nginx, Tailscale, Headscale, IP, and hostname are pipes, not trust roots." in text


def test_cdl101_non_overlap_sentence() -> None:
    text = _text(SPEC)
    assert (
        "CDL-101 signed D2D gossip envelopes govern private validator-to-validator "
        "or known-peer communication and are not the user-to-network native public "
        "submit ingress path."
    ) in text


def test_posk_non_dependency_sentence() -> None:
    text = _text(SPEC)
    assert (
        "PoSK and Merkle-Laplacian mechanisms are research/pre-CDL surfaces for this "
        "lane and are not dependencies of native submit ingress SPEC-00, CDL-00, or "
        "IMPL-00."
    ) in text


def test_native_sig_object_contract() -> None:
    text = _text(SPEC)
    for needle in (
        'Native ingress requires `sig` to be an object, not the string `"UNSIGNED"`',
        '"dst": "ILC_NATIVE_TRUTH_SUBMIT_V1:ilc-public-rc-01-testnet-harness"',
        "payload_sha256",
        "signature_hex",
        "verifier_profile",
        "payload_without_sig",
        "canonical preimage bytes",
    ):
        assert needle in text


def test_unsigned_placeholder_rejection_token() -> None:
    assert "native_submit_sig_unsigned_placeholder_rejected" in _text(SPEC)


def test_cdl_candidate_number_and_guards() -> None:
    text = _text(CDL)
    assert "CDL-117" in text
    for needle in (
        "PUBLIC_SUBMIT_INGRESS_ENDPOINT_ASSERTION_NOT_ACTIVATED=True",
        "NATIVE_SUBMISSION_SIG_VERIFICATION_NOT_ACTIVATED=True",
        "PUBLIC_RC_NATIVE_SUBMIT_INGRESS_CDL_NOT_RATIFIED=True",
    ):
        assert needle in text


def test_cdl_candidate_is_not_register_mutation() -> None:
    text = _text(CDL)
    assert "is not a CDL register mutation" in text
    assert "does not open CDL-117" in text
    assert "does not ratify CDL-117" in text


def test_no_activation_or_release_claims() -> None:
    combined = _text(SPEC) + "\n" + _text(CDL)
    forbidden_positive_claims = (
        "runtime activated",
        "signature verification activated",
        "package published",
        "validators synced",
        "public mirror pushed",
        "Phase 1603 retried",
    )
    for phrase in forbidden_positive_claims:
        assert phrase not in combined
    for required_non_claim in (
        "does not build or publish a package",
        "does not sync validators",
        "does not push a public mirror",
        "does not retry Phase 1603",
    ):
        assert required_non_claim in combined
