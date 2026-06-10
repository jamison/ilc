# SPDX-License-Identifier: AGPL-3.0-only
"""CCSS local runtime helpers for CLI-first private message bootstrap.

This module implements a local bootstrap surface only. It does not activate
public confidential coordination serving, public P2P, D2d CCSS routing, or any
protocol authority gate.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import socket
import socketserver
import struct
import tempfile
import time
import unicodedata
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.asymmetric.x25519 import (
    X25519PrivateKey,
    X25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.hashes import SHA256
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

CCSS_LOCAL_RUNTIME_VERSION = "ccss_local_runtime_v0.1"

_VERSION = 0x01
_INNER_PLAINTEXT = 2048
_INNER_ENVELOPE = 2108
_OUTER_PLAINTEXT = 4096
_OUTER_ENVELOPE = 4156
_OVERHEAD = 60
_MAX_MESSAGE_BYTES = 2000
_NONCE_LEN = 12
_TAG_LEN = 16
_KEY_LEN = 32
_HKDF_INFO_INNER = b"ccss-003-inner-v1"
_HKDF_INFO_OUTER = b"ccss-003-outer-v1"

_MAX_HTTP_RESPONSE_BYTES = 64 * 1024
_MAX_DIRECT_RECEIPT_BYTES = 8192
_INBOX_CAP = 1024
_PRIVATE_FILE_MODE = 0o600
_DIR_MODE = 0o700

# Whitelist of non-printable ASCII characters that are safe in message content.
# Everything else below U+0020 is rejected (see _validate_message_content).
_ALLOWED_CONTROL_CHARS: frozenset[str] = frozenset("\t\n\r")

# ── L2: language-independent obfuscation detection ───────────────────────────
# These characters appear in adversarial text specifically to evade keyword
# filters — they almost never appear in legitimate messages.

# Zero-width and invisible formatting characters used to split keywords.
# e.g. "ign\u200bore" renders as "ignore" but breaks naive regex.
_ZERO_WIDTH_CHARS: frozenset[str] = frozenset(
    "\u200b"  # ZERO WIDTH SPACE
    "\u200c"  # ZERO WIDTH NON-JOINER
    "\u200d"  # ZERO WIDTH JOINER
    "\u2060"  # WORD JOINER
    "\u00ad"  # SOFT HYPHEN
    "\ufeff"  # ZERO WIDTH NO-BREAK SPACE (BOM)
)

# Right-to-left control characters that can reverse displayed text order,
# making "evil command" appear as "dnammoc live" to a human reviewer.
_RTL_CONTROL_CHARS: frozenset[str] = frozenset(
    "\u202e"  # RIGHT-TO-LEFT OVERRIDE
    "\u202d"  # LEFT-TO-RIGHT OVERRIDE
    "\u200f"  # RIGHT-TO-LEFT MARK
    "\u202b"  # RIGHT-TO-LEFT EMBEDDING
)

# ── Message safety inspection patterns ───────────────────────────────────────
# These run on decrypted plaintext at unseal time.
# Two tiers:
#   _SAFE_FALSE_PATTERNS — any match sets safe=False; agents MUST NOT act
#                          on the message without human review.
#   _FLAG_ONLY_PATTERNS  — informational; safe remains True but flags are
#                          populated so agents can make their own decisions.
#
# All patterns use bounded quantifiers to prevent ReDoS on adversarial input.

_SAFE_FALSE_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # Prompt injection — attempts to override an agent's instruction context.
    (
        "prompt_injection:ignore_instructions",
        re.compile(
            r"\b(ignore|disregard|forget|override|bypass)\b.{0,60}"
            r"\b(instructions?|directives?|rules?|prompt|guidelines?|constraints?)\b",
            re.I | re.S,
        ),
    ),
    (
        "prompt_injection:role_override",
        re.compile(r"\byou\s+are\s+(now\s+)?(a\b|an\b|the\b|no\s+longer\b)", re.I),
    ),
    (
        "prompt_injection:act_as",
        re.compile(
            r"\b(act|pretend|behave|respond|roleplay)\s+(as\s+)?(if\s+)?"
            r"(you\s+(are|were)\b|a\b|an\b|the\b)",
            re.I,
        ),
    ),
    (
        "prompt_injection:system_directive",
        re.compile(
            r"(^|\n)\s*(\[SYSTEM\]|<SYSTEM>|##\s*SYSTEM\b|SYSTEM\s*:)",
            re.I | re.M,
        ),
    ),
    (
        "prompt_injection:jailbreak_keyword",
        re.compile(
            r"\b(jailbreak|DAN\s+mode|developer\s+mode|unrestricted\s+mode"
            r"|god\s+mode|do\s+anything\s+now)\b",
            re.I,
        ),
    ),
    (
        "prompt_injection:new_instructions",
        re.compile(
            r"\b(your\s+(new|updated?|real|actual|true)\s+instructions?\s+(are|is)\b"
            r"|new\s+instructions?\s*:)",
            re.I,
        ),
    ),
    # Shell pipe-to-interpreter — targets agents that execute subprocesses.
    (
        "shell_injection:pipe_to_interpreter",
        re.compile(r"\|\s*(bash|sh|zsh|fish|ksh|cmd\.exe|powershell|pwsh)\b", re.I),
    ),
]

_FLAG_ONLY_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # URLs — agents should not auto-fetch without explicit user confirmation.
    (
        "url_present",
        re.compile(r"\b(https?|ftp|file)://\S{1,500}", re.I),
    ),
    # Code execution — informational; legitimate in bug reports and code snippets.
    (
        "code_execution:eval",
        re.compile(r"\beval\s*\(", re.I),
    ),
    (
        "code_execution:exec",
        re.compile(r"\bexec\s*\(", re.I),
    ),
    (
        "code_execution:shell_subshell",
        re.compile(r"\$\([^)]{1,200}\)|\`[^`\n]{1,200}\`"),
    ),
    (
        "code_execution:os_system",
        re.compile(r"\bos\.(system|popen|execvp?e?|spawnv?[ep]?)\s*\(", re.I),
    ),
    (
        "code_execution:subprocess",
        re.compile(r"\bsubprocess\.(run|call|Popen|check_output|check_call)\s*\(", re.I),
    ),
    # Sensitive filesystem paths — agents should not read/write these paths.
    (
        "sensitive_path:system_credentials",
        re.compile(
            r"/etc/(passwd|shadow|sudoers|ssh[^/\s]*)"
            r"|~/?\.(ssh|aws|config/gcloud|docker/config)\b",
            re.I,
        ),
    ),
    (
        "sensitive_path:proc_sys",
        re.compile(r"/proc/\d+|/sys/kernel", re.I),
    ),
    # Encoded payloads — long blobs that could be shellcode or encoded commands.
    (
        "encoded_payload:base64_blob",
        re.compile(r"[A-Za-z0-9+/]{200,}={0,3}"),
    ),
    (
        "encoded_payload:hex_blob",
        re.compile(r"\b[0-9a-fA-F]{200,}\b"),
    ),
]


class CCSSRuntimeError(ValueError):
    """Stable exception for packaged CCSS runtime failures."""


def default_home() -> Path:
    return Path.home() / ".ilc" / "ccss"


def _home(home: str | Path | None = None) -> Path:
    return Path(home).expanduser() if home else default_home()


def identity_path(home: str | Path | None = None) -> Path:
    return _home(home) / "identity.json"


def contacts_path(home: str | Path | None = None) -> Path:
    return _home(home) / "contacts.json"


def inbox_dir(home: str | Path | None = None) -> Path:
    return _home(home) / "inbox"


def sent_dir(home: str | Path | None = None) -> Path:
    return _home(home) / "sent"


def _ensure_private_dir(path: Path) -> None:
    existed = path.exists()
    path.mkdir(parents=True, exist_ok=True)
    if not existed:
        os.chmod(path, _DIR_MODE)


def _atomic_write_json(path: Path, payload: dict[str, Any], *, mode: int) -> None:
    _ensure_private_dir(path.parent)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, allow_nan=False, indent=2, sort_keys=True)
            fh.write("\n")
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _read_json(path: Path, *, missing_default: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return missing_default
    except json.JSONDecodeError as exc:
        raise CCSSRuntimeError(f"ccss_json_invalid:{path}:{exc.pos}") from exc


def _validate_hex_key(value: str, *, field: str) -> str:
    try:
        raw = bytes.fromhex(value)
    except ValueError as exc:
        raise CCSSRuntimeError(f"{field}_invalid_hex") from exc
    if len(raw) != _KEY_LEN:
        raise CCSSRuntimeError(f"{field}_invalid_length")
    return value.lower()


def _agent_id_from_public_key(public_key_hex: str) -> str:
    digest = hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest()
    return f"ccss-agent:{digest}"


def _live(value: str) -> bool:
    return bool(value) and "PLACEHOLDER" not in value.upper()


def build_public_contact(
    *,
    contact_id: str,
    name: str,
    description: str,
    public_key_hex: str,
    peer_endpoint: str = "",
    onion: str = "",
    agent_id: str = "",
) -> dict[str, Any]:
    public_key_hex = _validate_hex_key(public_key_hex, field="public_key")
    return {
        "agent_id": agent_id or _agent_id_from_public_key(public_key_hex),
        "ccss_contact_onion": onion,
        "ccss_peer_endpoint": peer_endpoint,
        "ccss_recipient_pubkey": public_key_hex,
        "description": description,
        "id": contact_id,
        "name": name,
    }


def generate_identity(
    *,
    home: str | Path | None = None,
    contact_id: str = "local-user",
    name: str = "Local ILC User",
    description: str = "Local CCSS identity",
    peer_endpoint: str = "",
    onion: str = "",
    overwrite: bool = False,
) -> dict[str, Any]:
    path = identity_path(home)
    if path.exists() and not overwrite:
        raise CCSSRuntimeError(f"identity_already_exists:{path}")

    private_key = X25519PrivateKey.generate()
    private_key_hex = private_key.private_bytes(
        Encoding.Raw,
        PrivateFormat.Raw,
        NoEncryption(),
    ).hex()
    public_key_hex = private_key.public_key().public_bytes(
        Encoding.Raw,
        PublicFormat.Raw,
    ).hex()
    agent_id = _agent_id_from_public_key(public_key_hex)
    private_record = {
        "agent_id": agent_id,
        "ccss_private_key_hex": private_key_hex,
        "ccss_recipient_pubkey": public_key_hex,
        "description": description,
        "id": contact_id,
        "name": name,
        "schema": "ccss_identity_v0.1",
    }
    public_contact = build_public_contact(
        contact_id=contact_id,
        name=name,
        description=description,
        public_key_hex=public_key_hex,
        peer_endpoint=peer_endpoint,
        onion=onion,
        agent_id=agent_id,
    )
    _atomic_write_json(path, private_record, mode=_PRIVATE_FILE_MODE)
    _atomic_write_json(_home(home) / "self.contact.json", public_contact, mode=0o644)
    _ensure_private_dir(inbox_dir(home))
    _ensure_private_dir(sent_dir(home))
    return {
        "agent_id": agent_id,
        "home": str(_home(home)),
        "identity_path": str(path),
        "ok": True,
        "public_contact_path": str(_home(home) / "self.contact.json"),
        "public_key_sha256": hashlib.sha256(bytes.fromhex(public_key_hex)).hexdigest(),
        "version": CCSS_LOCAL_RUNTIME_VERSION,
    }


def _genesis_placeholder_contact() -> dict[str, Any]:
    return {
        "agent_id": "GENESIS_AGENT_ID_PLACEHOLDER",
        "ccss_contact_onion": "ONION_ADDRESS_PLACEHOLDER",
        "ccss_peer_endpoint": "PEER_ENDPOINT_PLACEHOLDER",
        "ccss_recipient_pubkey": "GENESIS_AGENT_PUBKEY_HEX_PLACEHOLDER",
        "description": "ILC founding authority. Placeholder until public RC contact values are published.",
        "id": "genesis",
        "name": "Genesis Agent",
    }


def _load_contacts(path: Path) -> list[dict[str, Any]]:
    raw = _read_json(path, missing_default=[])
    if not isinstance(raw, list):
        raise CCSSRuntimeError(f"contacts_file_not_list:{path}")
    return [dict(item) for item in raw if isinstance(item, dict)]


def _write_contacts(path: Path, contacts: list[dict[str, Any]]) -> None:
    _ensure_private_dir(path.parent)
    fd, tmp = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(contacts, fh, allow_nan=False, indent=2, sort_keys=True)
            fh.write("\n")
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def import_genesis_contact(*, home: str | Path | None = None, overwrite: bool = False) -> dict[str, Any]:
    path = contacts_path(home)
    contacts = _load_contacts(path)
    existing = [item for item in contacts if item.get("id") == "genesis"]
    if existing and not overwrite:
        return {"contact_id": "genesis", "contacts_path": str(path), "imported": False, "ok": True}
    contacts = [item for item in contacts if item.get("id") != "genesis"]
    contacts.append(_genesis_placeholder_contact())
    _write_contacts(path, sorted(contacts, key=lambda item: item.get("id", "")))
    return {
        "contact_id": "genesis",
        "contacts_path": str(path),
        "imported": True,
        "ok": True,
        "warning": "genesis_contact_contains_placeholders_until_public_rc_values_are_published",
    }


def add_contact(
    *,
    home: str | Path | None = None,
    contact_id: str,
    name: str,
    public_key_hex: str,
    description: str = "",
    peer_endpoint: str = "",
    onion: str = "",
    agent_id: str = "",
    overwrite: bool = False,
) -> dict[str, Any]:
    contact = build_public_contact(
        contact_id=contact_id,
        name=name,
        description=description,
        public_key_hex=public_key_hex,
        peer_endpoint=peer_endpoint,
        onion=onion,
        agent_id=agent_id,
    )
    path = contacts_path(home)
    contacts = _load_contacts(path)
    if any(item.get("id") == contact_id for item in contacts) and not overwrite:
        raise CCSSRuntimeError(f"contact_already_exists:{contact_id}")
    contacts = [item for item in contacts if item.get("id") != contact_id]
    contacts.append(contact)
    _write_contacts(path, sorted(contacts, key=lambda item: item.get("id", "")))
    return {"contact_id": contact_id, "contacts_path": str(path), "ok": True}


def list_contacts(*, home: str | Path | None = None) -> list[dict[str, Any]]:
    result = []
    for contact in _load_contacts(contacts_path(home)):
        pubkey_ok = _live(str(contact.get("ccss_recipient_pubkey", "")))
        peer_endpoint = str(contact.get("ccss_peer_endpoint", ""))
        onion = str(contact.get("ccss_contact_onion", ""))
        agent_id = str(contact.get("agent_id", ""))
        transports = []
        if _live(peer_endpoint):
            transports.append("direct")
        if _live(onion):
            transports.append("tor")
        if _live(agent_id):
            transports.append("d2d(stub)")
        result.append(
            {
                "agent_id": agent_id,
                "configured": pubkey_ok and bool(transports),
                "description": contact.get("description", ""),
                "id": contact.get("id", ""),
                "name": contact.get("name", ""),
                "onion": onion if _live(onion) else None,
                "peer_endpoint": peer_endpoint if _live(peer_endpoint) else None,
                "transports": transports,
            }
        )
    return result


def _derive_key(private_key: X25519PrivateKey, public_key: X25519PublicKey, info: bytes) -> bytes:
    shared = private_key.exchange(public_key)
    return HKDF(algorithm=SHA256(), length=32, salt=None, info=info).derive(shared)


def _seal_layer(plaintext: bytes, recipient_pub: X25519PublicKey, info: bytes) -> bytes:
    ephemeral_private = X25519PrivateKey.generate()
    ephemeral_public = ephemeral_private.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    key = _derive_key(ephemeral_private, recipient_pub, info)
    nonce = os.urandom(_NONCE_LEN)
    ciphertext_with_tag = ChaCha20Poly1305(key).encrypt(nonce, plaintext, None)
    return ephemeral_public + nonce + ciphertext_with_tag


def _l2_obfuscation_flags(text: str) -> list[str]:
    """Detect language-independent obfuscation techniques.

    These checks are independent of English keywords and catch attacks that
    use invisible or directional Unicode to evade pattern matching:

    - Zero-width characters split keywords so regex can't match them.
      e.g. "ign\\u200bore all instructions" renders as "ignore all
      instructions" to a human but breaks the regex pattern.

    - RTL override characters reverse the visual display order of text,
      hiding the true content from a human reviewer while the raw bytes
      still carry the payload.

    Note on Unicode confusables (Cyrillic 'а' for Latin 'a', etc.):
    NFKC normalization silently fixes *compatibility* equivalents (fullwidth
    chars, ligatures, superscripts) as part of ``_normalize_for_scan`` —
    those attacks are caught without a separate flag.  Cross-script
    lookalikes (e.g. Cyrillic U+0456 'і' for Latin 'i') are NOT
    compatibility equivalents in Unicode and require the Unicode confusables
    table (TR39) to detect.  That lookup is not bundled here; it is noted as
    a known gap in TODO.md under "message safety: language-independent L2".
    Flagging NFKC differences directly causes false positives on legitimate
    multilingual text (e.g. Japanese fullwidth punctuation) so it is omitted.
    """
    found: list[str] = []
    if any(c in _ZERO_WIDTH_CHARS for c in text):
        found.append("obfuscation:zero_width_chars")
    if any(c in _RTL_CONTROL_CHARS for c in text):
        found.append("obfuscation:rtl_override")
    return found


def _normalize_for_scan(text: str) -> str:
    """Return NFKC-normalized text with zero-width chars stripped.

    Applied to every scan target before pattern matching so that Unicode
    lookalike and zero-width-split attacks are caught by the same patterns
    that catch plaintext attacks.
    """
    stripped = "".join(c for c in text if c not in _ZERO_WIDTH_CHARS)
    return unicodedata.normalize("NFKC", stripped)


def _inspect_message_safety(text: str) -> tuple[bool, list[str]]:
    """Scan decrypted plaintext for patterns that pose a risk to agent consumers.

    Returns ``(safe, flags)`` where:
      - ``safe=False`` means an agent MUST NOT act on the message without
        explicit human review — a high-confidence threat pattern was found.
      - ``flags`` is a sorted list of machine-readable token strings, one per
        matched pattern, present regardless of the safe value.

    Scanning is three-level:
      1. L2 obfuscation checks on the raw text (language-independent).
      2. Pattern matching on NFKC-normalized, zero-width-stripped text so
         Unicode lookalikes and invisible-char splits don't evade the patterns.
      3. If the text parses as a v1 allow-reply envelope ``{"v":1,"msg":"..."}``,
         the inner ``msg`` field is also normalized and scanned independently.

    This function never raises; it returns ``(True, [])`` on any internal
    error so that decryption is never blocked by the inspector.
    """
    # Collect raw scan targets (v1 envelope unwrapping).
    raw_targets: list[str] = [text]
    try:
        parsed = json.loads(text)
        if isinstance(parsed, dict) and parsed.get("v") == 1 and isinstance(parsed.get("msg"), str):
            inner = parsed["msg"]
            if inner and inner != text:
                raw_targets.append(inner)
    except (ValueError, TypeError, AttributeError):
        pass

    flags: set[str] = set()
    safe = True

    try:
        # L2: obfuscation detection on raw text (before normalization strips evidence).
        for oflag in _l2_obfuscation_flags(text):
            flags.add(oflag)

        # L1: pattern matching on normalized text.
        for raw in raw_targets:
            target = _normalize_for_scan(raw)
            for token, pattern in _SAFE_FALSE_PATTERNS:
                if token not in flags and pattern.search(target):
                    flags.add(token)
                    safe = False
            for token, pattern in _FLAG_ONLY_PATTERNS:
                if token not in flags and pattern.search(target):
                    flags.add(token)

    except Exception:  # pragma: no cover — defensive; pattern bugs must not block decryption
        return True, []

    return safe, sorted(flags)


def _validate_message_content(message: str) -> None:
    """Reject message content that is unsafe to store, display, or forward.

    Blocks raw control bytes that can cause harm downstream:
      - NUL (U+0000)   — C-string termination in native (Rust/C) consumers
      - ESC (U+001B)   — ANSI/VT100 terminal manipulation when printed by CLI
      - DEL (U+007F)   — terminal control
      - C1 range (U+0080–U+009F) — additional terminal control sequences
      - Any other C0 control char not in the safe whitelist {\\t, \\n, \\r}

    NOTE: this operates on *raw bytes*, not text escape sequences. A Python
    source file containing the text ``print("\\x1b[31m")`` passes fine because
    the actual bytes in that string are printable ASCII ('\\', 'x', '1', 'b').
    Only a message that contains the literal 0x1B byte is rejected. Code
    samples, bug reports, and scripts are safe to send via CCSS.
    """
    for ch in message:
        cp = ord(ch)
        if cp == 0x00:
            raise CCSSRuntimeError("message_invalid:null_byte")
        if cp == 0x1B:
            raise CCSSRuntimeError("message_invalid:escape_sequence")
        if cp < 0x20 and ch not in _ALLOWED_CONTROL_CHARS:
            raise CCSSRuntimeError(f"message_invalid:control_char:U+{cp:04X}")
        if 0x7F <= cp <= 0x9F:
            raise CCSSRuntimeError(f"message_invalid:control_char:U+{cp:04X}")


def seal_message(message: str, recipient_pubkey_hex: str) -> bytes:
    _validate_message_content(message)
    message_bytes = message.encode("utf-8")
    if len(message_bytes) > _MAX_MESSAGE_BYTES:
        raise CCSSRuntimeError(f"message_too_long:{len(message_bytes)}:{_MAX_MESSAGE_BYTES}")
    raw_key = bytes.fromhex(_validate_hex_key(recipient_pubkey_hex, field="recipient_pubkey"))
    recipient_pub = X25519PublicKey.from_public_bytes(raw_key)

    inner_plain = bytearray(_INNER_PLAINTEXT)
    inner_plain[0] = _VERSION
    struct.pack_into("<H", inner_plain, 1, len(message_bytes))
    inner_plain[3 : 3 + len(message_bytes)] = message_bytes
    inner_envelope = _seal_layer(bytes(inner_plain), recipient_pub, _HKDF_INFO_INNER)

    outer_plain = bytearray(_OUTER_PLAINTEXT)
    outer_plain[0] = _VERSION
    struct.pack_into("<H", outer_plain, 1, _INNER_ENVELOPE)
    outer_plain[3 : 3 + _INNER_ENVELOPE] = inner_envelope
    outer_envelope = _seal_layer(bytes(outer_plain), recipient_pub, _HKDF_INFO_OUTER)
    if len(outer_envelope) != _OUTER_ENVELOPE:
        raise CCSSRuntimeError("outer_envelope_size_mismatch")
    return outer_envelope


def _open_layer(
    envelope: bytes,
    recipient_private: X25519PrivateKey,
    *,
    info: bytes,
    expected_plaintext_len: int,
) -> bytes:
    expected_len = expected_plaintext_len + _OVERHEAD
    if len(envelope) != expected_len:
        raise CCSSRuntimeError(f"ccss_envelope_size_invalid:{len(envelope)}:{expected_len}")
    ephemeral_public = X25519PublicKey.from_public_bytes(envelope[:_KEY_LEN])
    nonce = envelope[_KEY_LEN : _KEY_LEN + _NONCE_LEN]
    ciphertext_with_tag = envelope[_KEY_LEN + _NONCE_LEN :]
    if len(ciphertext_with_tag) != expected_plaintext_len + _TAG_LEN:
        raise CCSSRuntimeError("ccss_ciphertext_size_invalid")
    try:
        key = _derive_key(recipient_private, ephemeral_public, info)
        return ChaCha20Poly1305(key).decrypt(nonce, ciphertext_with_tag, None)
    except (ValueError, InvalidTag) as exc:
        raise CCSSRuntimeError("ccss_layer_authentication_failed") from exc


def _require_zero_padding(buf: bytes, start: int, *, token: str) -> None:
    if any(buf[start:]):
        raise CCSSRuntimeError(token)


def _load_private_key(home: str | Path | None = None) -> X25519PrivateKey:
    raw = _read_json(identity_path(home), missing_default=None)
    if not isinstance(raw, dict):
        raise CCSSRuntimeError(f"identity_not_found:{identity_path(home)}")
    key_hex = _validate_hex_key(str(raw.get("ccss_private_key_hex", "")), field="private_key")
    return X25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex))


def unseal_message(envelope: bytes, *, home: str | Path | None = None) -> dict[str, Any]:
    private_key = _load_private_key(home)
    outer_plain = _open_layer(
        envelope,
        private_key,
        info=_HKDF_INFO_OUTER,
        expected_plaintext_len=_OUTER_PLAINTEXT,
    )
    if outer_plain[0] != _VERSION:
        raise CCSSRuntimeError("ccss_outer_version_invalid")
    inner_len = struct.unpack_from("<H", outer_plain, 1)[0]
    if inner_len != _INNER_ENVELOPE:
        raise CCSSRuntimeError("ccss_inner_envelope_length_invalid")
    inner_start = 3
    inner_end = inner_start + inner_len
    inner_envelope = outer_plain[inner_start:inner_end]
    _require_zero_padding(outer_plain, inner_end, token="ccss_outer_padding_nonzero")

    inner_plain = _open_layer(
        inner_envelope,
        private_key,
        info=_HKDF_INFO_INNER,
        expected_plaintext_len=_INNER_PLAINTEXT,
    )
    if inner_plain[0] != _VERSION:
        raise CCSSRuntimeError("ccss_inner_version_invalid")
    message_len = struct.unpack_from("<H", inner_plain, 1)[0]
    if message_len > _MAX_MESSAGE_BYTES:
        raise CCSSRuntimeError("ccss_message_length_invalid")
    message_start = 3
    message_end = message_start + message_len
    message_bytes = inner_plain[message_start:message_end]
    _require_zero_padding(inner_plain, message_end, token="ccss_inner_padding_nonzero")
    message = message_bytes.decode("utf-8")
    safe, flags = _inspect_message_safety(message)
    return {
        "envelope_sha256": hashlib.sha256(envelope).hexdigest(),
        "flags": flags,
        "message": message,
        "message_bytes": len(message_bytes),
        "ok": True,
        "safe": safe,
    }


def _direct_send(envelope: bytes, endpoint: str) -> dict[str, Any]:
    host, _, port_s = endpoint.rpartition(":")
    if not host or not port_s:
        raise CCSSRuntimeError(f"direct_endpoint_invalid:{endpoint}")
    try:
        port = int(port_s)
    except ValueError as exc:
        raise CCSSRuntimeError("direct_endpoint_port_invalid") from exc
    if port < 1 or port > 65535:
        raise CCSSRuntimeError("direct_endpoint_port_invalid")
    with socket.create_connection((host, port), timeout=15) as sock:
        sock.sendall(envelope)
        sock.shutdown(socket.SHUT_WR)
        raw = b""
        while True:
            chunk = sock.recv(512)
            if not chunk:
                break
            if len(raw) + len(chunk) > _MAX_DIRECT_RECEIPT_BYTES:
                raise CCSSRuntimeError("direct_receipt_too_large")
            raw += chunk
    if not raw:
        raise CCSSRuntimeError("direct_receipt_empty")
    try:
        return json.loads(raw.decode("utf-8").strip())
    except json.JSONDecodeError as exc:
        raise CCSSRuntimeError("direct_receipt_json_invalid") from exc


def _tor_send(envelope: bytes, onion: str) -> dict[str, Any]:
    if not onion.endswith(".onion"):
        raise CCSSRuntimeError("tor_endpoint_not_onion")
    host_b = onion.encode("utf-8")
    if len(host_b) > 255:
        raise CCSSRuntimeError("tor_endpoint_too_long")
    with socket.create_connection(("127.0.0.1", 9050), timeout=30) as sock:
        sock.sendall(b"\x05\x01\x00")
        if sock.recv(2) != b"\x05\x00":
            raise CCSSRuntimeError("socks5_auth_failed")
        sock.sendall(b"\x05\x01\x00\x03" + bytes([len(host_b)]) + host_b + b"\x00\x50")
        resp = sock.recv(10)
        if len(resp) < 2 or resp[1] != 0:
            raise CCSSRuntimeError("socks5_connect_failed")
        req = (
            f"POST /submit HTTP/1.0\r\nHost: {onion}\r\n"
            f"Content-Type: application/octet-stream\r\n"
            f"Content-Length: {len(envelope)}\r\n\r\n"
        ).encode("utf-8") + envelope
        sock.sendall(req)
        raw = b""
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            if len(raw) + len(chunk) > _MAX_HTTP_RESPONSE_BYTES:
                raise CCSSRuntimeError("tor_http_response_too_large")
            raw += chunk
    _, _, body = raw.partition(b"\r\n\r\n")
    if not body:
        raise CCSSRuntimeError("tor_http_response_invalid")
    return json.loads(body)


def _select_contact(contact_id: str, *, home: str | Path | None = None) -> dict[str, Any]:
    for contact in _load_contacts(contacts_path(home)):
        if contact.get("id") == contact_id:
            return contact
    raise CCSSRuntimeError(f"contact_not_found:{contact_id}")


def send_message(
    contact_id: str,
    message: str,
    *,
    home: str | Path | None = None,
) -> dict[str, Any]:
    contact = _select_contact(contact_id, home=home)
    pubkey = str(contact.get("ccss_recipient_pubkey", ""))
    if not _live(pubkey):
        raise CCSSRuntimeError(f"contact_pubkey_not_configured:{contact_id}")
    envelope = seal_message(message, pubkey)
    peer_endpoint = str(contact.get("ccss_peer_endpoint", ""))
    onion = str(contact.get("ccss_contact_onion", ""))
    if _live(peer_endpoint):
        receipt = _direct_send(envelope, peer_endpoint)
        transport = "direct"
    elif _live(onion):
        receipt = _tor_send(envelope, onion)
        transport = "tor"
    else:
        raise CCSSRuntimeError(f"contact_endpoint_not_configured:{contact_id}")
    receipt_token = str(receipt.get("receipt_token", hashlib.sha256(envelope).hexdigest()))
    record = {
        "contact_id": contact_id,
        "message_bytes": len(message.encode("utf-8")),
        "message_sha256": hashlib.sha256(message.encode("utf-8")).hexdigest(),
        "plaintext_stored": False,
        "receipt": receipt_token,
        "transport": transport,
        "ts": int(time.time()),
    }
    target_dir = sent_dir(home) / contact_id
    _ensure_private_dir(target_dir)
    _atomic_write_json(target_dir / f"{record['ts']}_{receipt_token[:8]}.json", record, mode=0o600)
    return {
        "contact_id": contact_id,
        "ok": True,
        "receipt": receipt_token,
        "transport": transport,
        "version": CCSS_LOCAL_RUNTIME_VERSION,
    }


def list_inbox(*, home: str | Path | None = None) -> list[dict[str, Any]]:
    path = inbox_dir(home)
    if not path.is_dir():
        return []
    entries = []
    for envelope_path in path.iterdir():
        if envelope_path.suffix != ".envelope":
            continue
        stat = envelope_path.stat()
        entries.append(
            {
                "receipt": envelope_path.stem,
                "received": int(stat.st_mtime),
                "size": stat.st_size,
                "size_ok": stat.st_size == _OUTER_ENVELOPE,
            }
        )
    return sorted(entries, key=lambda item: item["received"], reverse=True)


def _latest_envelope_path(home: str | Path | None = None) -> Path:
    path = inbox_dir(home)
    candidates = [item for item in path.iterdir() if item.suffix == ".envelope"] if path.is_dir() else []
    if not candidates:
        raise CCSSRuntimeError(f"inbox_empty:{path}")
    return max(candidates, key=lambda item: item.stat().st_mtime)


def read_envelope(
    *,
    home: str | Path | None = None,
    envelope_path: str | Path | None = None,
    latest: bool = False,
    redact: bool = False,
) -> dict[str, Any]:
    if latest:
        path = _latest_envelope_path(home)
    elif envelope_path:
        path = Path(envelope_path).expanduser()
    else:
        raise CCSSRuntimeError("read_requires_latest_or_envelope")
    result = unseal_message(path.read_bytes(), home=home)
    result["envelope_path"] = str(path)
    if redact:
        result.pop("message", None)
        result["plaintext_redacted"] = True
    return result


class _PeerHandler(socketserver.BaseRequestHandler):
    inbox: Path

    def handle(self) -> None:
        conn: socket.socket = self.request
        conn.settimeout(15)
        envelope = b""
        while len(envelope) < _OUTER_ENVELOPE + 1:
            chunk = conn.recv(min(4096, _OUTER_ENVELOPE + 1 - len(envelope)))
            if not chunk:
                break
            envelope += chunk
        if len(envelope) != _OUTER_ENVELOPE:
            self._reply({"error": "invalid_envelope_size", "status": "error"})
            return
        _ensure_private_dir(self.inbox)
        if len([item for item in self.inbox.iterdir() if item.suffix == ".envelope"]) >= _INBOX_CAP:
            self._reply({"error": "inbox_full", "status": "error"})
            return
        receipt = hashlib.sha256(envelope).hexdigest()
        out = self.inbox / f"{receipt}.envelope"
        if not out.exists():
            fd, tmp = tempfile.mkstemp(dir=self.inbox)
            try:
                with os.fdopen(fd, "wb") as fh:
                    fh.write(envelope)
                os.replace(tmp, out)
            except Exception:
                try:
                    os.unlink(tmp)
                except OSError:
                    pass
                self._reply({"error": "write_error", "status": "error"})
                return
        self._reply({"receipt_token": receipt, "status": "accepted"})

    def _reply(self, payload: dict[str, Any]) -> None:
        try:
            self.request.sendall((json.dumps(payload, sort_keys=True) + "\n").encode("utf-8"))
        except OSError:
            pass


def serve_direct(
    *,
    home: str | Path | None = None,
    host: str = "127.0.0.1",
    port: int = 9001,
) -> None:
    if port < 1 or port > 65535:
        raise CCSSRuntimeError("serve_port_invalid")

    class Handler(_PeerHandler):
        pass

    Handler.inbox = inbox_dir(home)
    _ensure_private_dir(Handler.inbox)
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer((host, port), Handler)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def apply_confidential_contact_recipe(
    *,
    home: str | Path | None = None,
    contact_id: str = "local-user",
    name: str = "Local ILC User",
    peer_endpoint: str = "",
    overwrite_identity: bool = False,
) -> dict[str, Any]:
    identity_created = False
    if overwrite_identity or not identity_path(home).exists():
        generate_identity(
            home=home,
            contact_id=contact_id,
            name=name,
            description="Local CCSS identity created by confidential-contact recipe",
            peer_endpoint=peer_endpoint,
            overwrite=overwrite_identity,
        )
        identity_created = True
    genesis = import_genesis_contact(home=home, overwrite=False)
    return {
        "home": str(_home(home)),
        "identity_created": identity_created,
        "ok": True,
        "recipe_id": "confidential-contact",
        "steps": [
            "local_ccss_identity_ready",
            "genesis_contact_placeholder_imported",
            "ccss_direct_or_tor_transport_available_when_contact_values_are_configured",
        ],
        "warnings": [genesis.get("warning")] if genesis.get("warning") else [],
        "version": CCSS_LOCAL_RUNTIME_VERSION,
    }
