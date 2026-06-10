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
import socket
import socketserver
import struct
import tempfile
import time
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


def seal_message(message: str, recipient_pubkey_hex: str) -> bytes:
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
    return {
        "envelope_sha256": hashlib.sha256(envelope).hexdigest(),
        "message": message_bytes.decode("utf-8"),
        "message_bytes": len(message_bytes),
        "ok": True,
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
