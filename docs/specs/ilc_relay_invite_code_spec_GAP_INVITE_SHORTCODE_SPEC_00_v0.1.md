# ILC Relay Invite Code Protocol Spec

Version: v0.1
Phase: GAP-INVITE-SHORTCODE-SPEC-00
Date: 2026-09-03
Status: spec-committed
Authority inputs: GAP-RELAY-BOOTSTRAP-CAPSULE-SIGN-00, GAP-PRE-RC-CONNECTIVITY-CLAIM-GATE-00, GAP-RELAY-RENDEZVOUS-SPEC-00, CDL-039, CDL-078, CDL-102, CDL-112 opening
Output token: `invite_shortcode_spec_committed_GAP_INVITE_SHORTCODE_SPEC_00`

## 1. Motivation And Launch Scenario

The current public-RC invite flow is correct but too manual for a public launch funnel. An inviter must create a signed peer hint, create an invite batch, assemble an invite bundle, transfer the JSON bundle out-of-band, and then instruct the invitee to run `tools/install.sh --invite-bundle PATH`.

The target flow separates cryptographic authority from distribution convenience:

```bash
ilc identity invite generate --upload --slots 500 --ttl 24h
```

The command produces a relay-hosted short code and a pasteable install command:

```bash
curl -fsSL <install-sh-url> | bash -s -- --invite-code ILC-H7K2-X9P4
```

The short code is not an identity credential, relay authentication token, validator admission, reputation grant, or economic entitlement. It is only a human-readable retrieval handle for one pre-signed invite bundle held by a relay. The installer must verify the fetched bundle exactly as it verifies a file supplied through `--invite-bundle`.

The public launch scenario is a bounded public announcement with a visible remaining-slot status URL. A relay may learn redemption timing and associate a code with the authenticated store request; that privacy trade-off is accepted for this pre-RC user-acquisition path and must not be described as anonymous onboarding.

## 2. Code Format

Invite codes use this exact wire/display format:

```text
ILC-[A-HJ-NP-Z2-9]{4}-[A-HJ-NP-Z2-9]{4}
```

The alphabet is:

```text
ABCDEFGHJKLMNPQRSTUVWXYZ23456789
```

This is the uppercase English alphabet excluding `I` and `O`, followed by digits `2` through `9`. The format also excludes `0` and `1`. The total alphabet size is 32.

The visible code contains 7 random payload characters and 1 checksum character:

```text
ILC-PPPP-PPPC
```

`P` is payload and `C` is checksum. `ILC-H7K2-X9P4` is a valid example for payload `H7K2X9P`.

Checksum algorithm:

1. Remove the `ILC-` prefix and the hyphen separator, leaving 8 characters.
2. Take the first 7 characters as the payload.
3. Reject any character not present in `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`.
4. Map each payload character to its zero-based alphabet index.
5. Compute `sum(index(char[i]) * (i + 1) for i in range(7)) % 32`.
6. The checksum character is `ALPHABET[result]`.
7. Validation recomputes the checksum from the first 7 characters and compares it to character 8.

This is a deterministic typo-detection checksum, not a cryptographic integrity check. Code-guessing resistance comes from 7 random base-32 payload characters: `32^7 = 34,359,738,368` possible payloads before relay rate limits and TTL expiry.

The relay generates codes using `secrets` or an equivalent OS CSPRNG. Inviting agents do not choose code strings. On collision with an unexpired code, the relay generates a fresh payload and retries up to a bounded implementation limit before returning `invite_code_generation_exhausted`.

## 3. Relay Control-Plane Endpoints

This section defines the relay `control-plane endpoints` for shortcode storage,
retrieval, and public status.

The shortcode surface adds three HTTPS endpoints to the relay control plane on `51151/tcp`. These endpoints are control-plane JSON endpoints. They do not terminate, inspect, re-sign, rewrite, or re-origin consensus/QUIC data-plane traffic.

All JSON request bodies must be bounded before parsing. All protocol JSON that feeds hashing, signing, storage receipts, or response verification must use canonical JSON with `sort_keys=True`, compact separators, `ensure_ascii=True`, and `allow_nan=False`.

### POST /relay/invite/store

This endpoint stores one relay-hosted batch of pre-signed invite bundles and returns a short code.

Request body:

```json
{
  "bundles": ["<base64-encoded signed invite bundle>", "<base64-encoded signed invite bundle>"],
  "inviting_agent_id": "<96-char lowercase hex inviter identity/provenance id>",
  "inviting_bls_public_key_hex": "<96-char lowercase hex BLS G1 public key>",
  "request_signature": "<192-char lowercase hex BLS G2 signature>",
  "ttl_seconds": 86400
}
```

`request_signature` is computed over `sha384(canonical_json(body_without_request_signature))` and verified with `inviting_bls_public_key_hex`.

The legacy `InviteBatchRecord.inviter_sig` field is not sufficient by itself for shortcode storage. Historical invite runtime only required that field to be non-empty. The shortcode CDL/implementation must either replace it with a real BLS signature field for deposited bundles or bind it explicitly to the new `inviting_bls_public_key_hex` verifier contract.

The relay must enforce all of these rules before storage:

- `inviting_agent_id` is a 96-character lowercase hex string used for provenance display and rate-limit identity.
- `inviting_bls_public_key_hex` is a 96-character BLS G1 public key used for signature verification.
- If the active onboarding profile defines AgentID as the BLS G1 public key, `inviting_agent_id` and `inviting_bls_public_key_hex` may be identical.
- If a future profile reintroduces non-BLS AgentID commitments, the request must carry and verify an explicit key-binding between `inviting_agent_id` and `inviting_bls_public_key_hex`.
- Every submitted bundle must be base64-decodable, at most 32 KiB after decoding, structurally valid, and signed by `inviting_bls_public_key_hex` or by a key proven equivalent through the same key-binding.
- All bundles in the batch must bind to the same inviting identity/key context.
- `ttl_seconds` is a positive integer, rejects `bool`, and is capped at 2,592,000 seconds.
- Absolute protocol ceiling is 10,000 bundles per code, but pre-RC relays must also enforce an aggregate request byte cap before JSON parsing. The recommended pre-RC cap is 16 MiB, which may force a lower operational `bundles` count for large bundles.
- Store requests are rate limited to 5 accepted or rejected store attempts per `inviting_agent_id` per hour, with an implementation memory cap on the tracker.

Success response:

```json
{
  "code": "ILC-H7K2-X9P4",
  "expires_at": "2026-09-04T14:00:00Z",
  "schema_version": "relay_invite_code_store_response.v0.1",
  "slots": 500,
  "status_url": "https://164.90.201.11:51151/relay/invite/ILC-H7K2-X9P4/status"
}
```

Failure responses use JSON `{"error": "<stable_token>"}` and appropriate HTTP status:

- `400` malformed code, request, base64, bundle, TTL, or signature field.
- `401` invalid `request_signature` or invalid bundle signature.
- `413` request or bundle exceeds size cap.
- `429` rate limit exceeded.
- `503` code generation exhausted or relay storage unavailable.

### GET /relay/invite/{code}

This endpoint returns one bundle from a stored batch.

Rules:

- Code format and checksum are validated before lookup.
- Retrieval is unauthenticated by design.
- The relay atomically removes exactly one available bundle from the batch before returning a `200` response body.
- A bundle returned once must never be returned again, even under concurrent requests.
- Consumption is relay-level distribution burn only. It does not prove the invitee installed successfully, does not register the invite nullifier, and does not create invite provenance by itself.
- The response body is capped at 32 KiB decoded bundle size plus bounded JSON/base64 overhead.
- Requests are rate limited to 10 fetch attempts per source IP per minute, with a memory cap on the tracker.
- Redirects are not part of the protocol. Clients and installers must not follow redirects for this endpoint.

Success response:

```json
{
  "bundle_b64": "<base64-encoded signed invite bundle>",
  "schema_version": "relay_invite_code_fetch_response.v0.1",
  "slots_remaining": 499
}
```

Exhaustion and expiry:

```json
{"error":"code_exhausted"}
```

```json
{"error":"code_expired"}
```

Both use HTTP `410 Gone`.

### GET /relay/invite/{code}/status

This endpoint exposes bounded public status for a code:

```json
{
  "code": "ILC-H7K2-X9P4",
  "expires_at": "2026-09-04T14:00:00Z",
  "inviting_agent_id": "<96-char lowercase hex>",
  "inviting_bls_public_key_hex": "<96-char lowercase hex>",
  "schema_version": "relay_invite_code_status_response.v0.1",
  "slots_remaining": 499,
  "slots_total": 500
}
```

The status endpoint is public and unauthenticated. It must not expose private invite nonces, invite nullifiers, bundle JSON, relay admission material, IP history, requester identity, or per-slot redemption timestamps. Expired or exhausted codes return the same `410 Gone` error bodies as the fetch endpoint.

## 4. Inviting Agent CLI: ilc identity invite generate

The canonical inviting-agent command is:

```bash
ilc identity invite generate
```

The zero-flag form must auto-discover relay endpoint candidates from bundled package data at `ilc_core/data/relay_bootstrap_capsule.json`. The bundled capsule is Genesis-signed by `GENESIS_CAPSULE_SIGNING_PK_HEX` and contains relay self-signed records. If the bundled capsule is absent or verifies to zero records, and no `--relay-url` override is supplied, the command fails closed with:

```text
invite_generate_no_relay_url_and_no_bundled_capsule
```

The command wraps the currently manual sequence:

1. Select a verified relay endpoint from the bundled capsule unless overridden.
2. Generate an ephemeral signed peer hint for the selected relay endpoint.
3. Create an invite batch record with `N` private nonces.
4. Assemble one or more install-ready invite bundles with peer hints, relay bootstrap capsule material, and existing invite nullifier/PoP fields.
5. If `--upload` is present, store the bundle batch with `POST /relay/invite/store` and print the returned code.

Flags:

```text
ilc identity invite generate [--slots N] [--ttl DURATION] [--relay-url URL]
                              [--output PATH] [--upload] [--stdout]
```

- `--slots N`: number of invite slots to generate. Default `1`. Must reject `bool`, zero, negatives, and values over the active cap.
- `--ttl DURATION`: duration such as `24h`, `7d`, or `30d`. Default `24h`. Maximum `30d`.
- `--relay-url URL`: override bundled relay selection. If used for upload or bundle relay material, the implementation must also require or derive a TLS DER pin from a verified capsule record.
- `--output PATH`: local bundle output path. Default `~/.ilc/invite_bundle.json` when `--slots 1`; for multiple local bundles, use a deterministic directory or indexed filename scheme.
- `--upload`: deposit all generated bundles at the relay and print code, relay URL, status URL, slot count, expiry, and install command.
- `--stdout`: write the local invite bundle JSON to stdout. This is mutually exclusive with multi-bundle output unless the implementation emits a documented JSON container.

`--enable-invites` is eliminated for `generate`. Existing `create`, `hint`, and `bundle` commands may retain legacy guard flags until their own cleanup phases.

## 5. Installer Changes

`tools/install.sh` adds:

```text
--invite-code CODE
```

The existing `--invite-bundle PATH` path remains supported. Exactly one of `--invite-code` or `--invite-bundle` must be supplied unless a later phase defines a different default.

Installer flow for `--invite-code`:

1. Validate `CODE` locally against the format and checksum algorithm in Section 2.
2. Resolve relay endpoint and TLS trust material from the bundled relay bootstrap capsule in the installed wheel metadata or from explicit `--relay-url` / TLS-pin overrides.
3. Fetch `GET https://<relay>:51151/relay/invite/<code>` with pinned-DER TLS verification, no redirect following, explicit timeout, response status checking, and a 32 KiB decoded bundle cap.
4. Decode `bundle_b64` into a temporary file in a private temp directory.
5. Verify the fetched bundle's inviting-agent BLS signature and key-binding before invoking onboarding.
6. On verification failure, stop with `install_sh_invite_code_bundle_signature_invalid`.
7. On `410 {"error":"code_exhausted"}`, stop with `install_sh_invite_code_exhausted`.
8. On `410 {"error":"code_expired"}`, stop with `install_sh_invite_code_expired`.
9. Proceed through the same verified `ilc install --from-invite` flow used by `--invite-bundle`.
10. Remove temporary bundle material during cleanup.

The installer must not trust the relay as an authority for bundle contents. The relay only transports the bundle. All bundle cryptography and invite/nullifier validation remain end-to-end between inviter, invitee, and existing ILC runtime verifiers.

## 6. Security Model

Security properties:

- Bundle authenticity: each bundle is signed by the inviting BLS key; both relay store and installer fetch paths verify it.
- Legacy boundary: historical `InviteBatchRecord.inviter_sig` placeholder semantics do not satisfy bundle authenticity unless amended into a verified signature contract by the shortcode CDL/implementation phase.
- Store authentication: `POST /relay/invite/store` is signed by the inviting BLS key over canonical request JSON.
- Identity binding: the spec separates `inviting_agent_id` from `inviting_bls_public_key_hex`; future non-BLS AgentID profiles require explicit key-binding rather than verifier-key overloading.
- Single-use relay distribution: fetch atomically burns one relay-hosted slot. This prevents double serving by the relay but does not replace invite nullifier registration.
- Nullifier authority unchanged: invite nullifier registration remains in the existing install/onboarding path and durable registry.
- Relay cannot forge bundles: the inviting private key never leaves the inviter's device.
- Relay cannot mint authority: a code grants no validator, graph, reputation, wallet, ECU, ILC, or settlement authority.
- Transport security: relay control-plane fetch uses HTTPS with pinned-DER verification or an explicitly authorized equivalent.
- Redirect safety: installers must not follow redirects when fetching identity-bound invite material.
- Size safety: store and fetch paths enforce request and decoded-bundle caps before unbounded parsing.
- Rate limiting: store and fetch endpoints are independently rate-limited with bounded memory trackers.
- Privacy honesty: relay operators can observe store, status, and fetch timing and can correlate a code to the authenticated store request. This is acceptable for pre-RC but is not anonymity.
- No sealed-sender claim: ADR-0034 sealed-sender privacy is separate and not provided by shortcode relay fetch.

## 7. CDL Authority Scope

The next SENSITIVE CDL phase must open or amend authority for this exact surface before live activation:

- Invite code format, alphabet, grouping, checksum algorithm, and collision behavior.
- `POST /relay/invite/store` request/response schema and BLS request authentication.
- `GET /relay/invite/{code}` unauthenticated retrieval schema and atomic slot burn semantics.
- `GET /relay/invite/{code}/status` public status schema and redaction boundaries.
- `inviting_agent_id` and `inviting_bls_public_key_hex` as distinct fields, including future key-binding requirements if AgentID is not the BLS verifier key.
- Bundle-level signature verification by the relay before storage and by the installer before onboarding.
- TTL limits, exhaustion behavior, HTTP status semantics, and stable error tokens.
- Per-bundle size cap, aggregate store request byte cap, and parser fail-closed requirements.
- Store and fetch rate limiting, including memory caps and non-use of IP identity as protocol identity.
- Privacy trade-off language: relay visibility/correlation accepted for this distribution path, without anonymity claims.
- Activation boundary: implementation remains guarded until SENSITIVE deployment clears the shortcode guard under this CDL authority.

This authority must preserve CDL-039 no-central-broker direction: relay-hosted shortcode distribution is a bootstrap convenience, not a permanent single-broker architecture. It must also preserve CDL-078's rejection of per-hop micro-payments and CDL-102's rejection of standalone referral fees.

## 8. Explicit Non-Claims

This section records the phase `non-claims`.

- This phase does not implement runtime code.
- This phase does not open, amend, prelock, or ratify a CDL.
- This phase does not activate any relay shortcode endpoint.
- This phase does not mutate relay VPS, validator VPS, firewall, systemd, LMDB, Atlas, or PyPI state.
- This phase does not change invite bundle cryptography, invite nullifier derivation, invite PoP semantics, or onboarding AgentID derivation.
- This phase does not authorize public RC, epoch transition, settlement, ECU minting, ILC minting, wallet writes, validator admission, relay rewards, DHT, sealed-sender activation, or public mirror push.
