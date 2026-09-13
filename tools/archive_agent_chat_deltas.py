#!/usr/bin/env python3
"""Archive Codex/Claude JSONL chat deltas into private searchable artifacts.

The raw compressed JSONL output is the lossless archive. Markdown extracts and
indexes are redacted, bounded, and intended only as Tier-D historical context
for MemPalace-style retrieval.
"""

from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


_LABEL_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
    re.DOTALL,
)
_SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (_PRIVATE_KEY_RE, "[REDACTED_PRIVATE_KEY_PEM]"),
    (
        re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[A-Za-z0-9._~+/=-]{12,}"),
        r"\1[REDACTED_BEARER_TOKEN]",
    ),
    (
        re.compile(
            r"(?i)\b((?:DIGITALOCEAN_ACCESS_TOKEN|OPENAI_API_KEY|PYPI_TOKEN|GITHUB_TOKEN)\s*=\s*)"
            r"['\"]?[A-Za-z0-9._~+/=-]{12,}['\"]?"
        ),
        r"\1[REDACTED_ENV_TOKEN]",
    ),
    (re.compile(r"\bdop_v1_[A-Za-z0-9_-]{20,}\b"), "[REDACTED_DIGITALOCEAN_TOKEN]"),
    (re.compile(r"\bpypi-[A-Za-z0-9_-]{20,}\b"), "[REDACTED_PYPI_TOKEN]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "[REDACTED_OPENAI_TOKEN]"),
)


@dataclass(frozen=True)
class SourceSpec:
    label: str
    path: Path
    start_line_exclusive: int


@dataclass(frozen=True)
class SourceReceipt:
    label: str
    source_path: str
    raw_archive_file: str
    raw_sha256: str
    raw_size_bytes: int
    extract_file: str
    extract_sha256: str
    extract_size_bytes: int
    index_file: str
    index_sha256: str
    index_size_bytes: int
    start_line_exclusive: int
    first_archived_line: int | None
    last_archived_line: int | None
    decoded_lines: int
    rendered_messages: int
    invalid_json_lines: int


def _atomic_write_text(path: Path, text: str, *, overwrite: bool) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
        os.chmod(path, 0o600)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def _atomic_write_gzip(path: Path, lines: Iterable[str], *, overwrite: bool) -> tuple[str, int]:
    if path.exists() and not overwrite:
        raise FileExistsError(f"refusing to overwrite existing file: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    digest = hashlib.sha256()
    size = 0
    try:
        with os.fdopen(fd, "wb") as raw_handle:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw_handle, mtime=0) as gzip_handle:
                for line in lines:
                    chunk = line.encode("utf-8")
                    gzip_handle.write(chunk)
        with open(tmp_name, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
        os.replace(tmp_name, path)
        os.chmod(path, 0o600)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)
    return digest.hexdigest(), size


def _sha256_file(path: Path) -> tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
            size += len(chunk)
    return digest.hexdigest(), size


def _redact_text(text: str) -> str:
    redacted = text
    for pattern, replacement in _SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def _limit_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n[truncated {len(text) - max_chars} chars]"


def _json_block(value: Any, max_chars: int) -> str:
    text = json.dumps(value, sort_keys=True, ensure_ascii=False)
    return "```json\n" + _limit_text(_redact_text(text), max_chars) + "\n```"


def _markdown_block(text: str, max_chars: int) -> str:
    return "```\n" + _limit_text(_redact_text(text), max_chars) + "\n```"


def _content_blocks_to_markdown(blocks: Any, max_chars: int) -> list[str]:
    if isinstance(blocks, str):
        return [_limit_text(_redact_text(blocks), max_chars)]
    if not isinstance(blocks, list):
        return [_json_block(blocks, max_chars)]

    rendered: list[str] = []
    for block in blocks:
        if isinstance(block, str):
            rendered.append(_limit_text(_redact_text(block), max_chars))
            continue
        if not isinstance(block, dict):
            rendered.append(_json_block(block, max_chars))
            continue
        block_type = block.get("type")
        if block_type in {"text", "input_text", "output_text"} and isinstance(block.get("text"), str):
            rendered.append(_limit_text(_redact_text(block["text"]), max_chars))
        elif block_type == "thinking" and isinstance(block.get("thinking"), str):
            rendered.append("<thinking>\n" + _limit_text(_redact_text(block["thinking"]), max_chars) + "\n</thinking>")
        elif block_type == "tool_result":
            rendered.append("**[tool_result]**\n" + _markdown_block(str(block.get("content", "")), max_chars))
        elif block_type == "tool_use":
            rendered.append("**[tool_use]**\n" + _json_block(block, max_chars))
        else:
            rendered.append(_json_block(block, max_chars))
    return rendered


def _render_claude_record(record: dict[str, Any], line_no: int, max_chars: int) -> tuple[str, str] | None:
    message = record.get("message")
    if not isinstance(message, dict):
        return None
    role = str(message.get("role") or record.get("type") or "unknown")
    timestamp = str(record.get("timestamp", ""))
    parts = _content_blocks_to_markdown(message.get("content"), max_chars)
    if not parts:
        return None
    header = f"## Message {{n}} | {role} | line {line_no} | {timestamp}".rstrip()
    return header, "\n\n".join(parts)


def _render_codex_payload(payload: dict[str, Any], max_chars: int) -> tuple[str, str] | None:
    payload_type = payload.get("type")
    if payload_type == "message":
        role = str(payload.get("role", "assistant"))
        parts = _content_blocks_to_markdown(payload.get("content"), max_chars)
        return role, "\n\n".join(parts)
    if payload_type == "reasoning":
        if payload.get("content"):
            return "reasoning", _json_block(payload.get("content"), max_chars)
        if payload.get("encrypted_content"):
            return "reasoning", "[encrypted reasoning content present in raw log; plaintext unavailable to extractor]"
    if payload_type in {"function_call", "function_call_output", "custom_tool_call_output"}:
        return str(payload_type), _json_block(payload, max_chars)
    if payload_type in {"item_completed", "task_complete"}:
        item = payload.get("item")
        if isinstance(item, dict):
            role = str(item.get("type") or payload_type)
            parts = _content_blocks_to_markdown(item.get("content"), max_chars)
            if parts:
                return role, "\n\n".join(parts)
        return str(payload_type), _json_block(payload, max_chars)
    if payload_type == "token_count":
        return None
    return str(payload_type or "event"), _json_block(payload, max_chars)


def _render_codex_record(record: dict[str, Any], line_no: int, max_chars: int) -> tuple[str, str] | None:
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return None
    rendered = _render_codex_payload(payload, max_chars)
    if rendered is None:
        return None
    role, body = rendered
    timestamp = str(record.get("timestamp", ""))
    header = f"## Message {{n}} | {role} | line {line_no} | {timestamp}".rstrip()
    return header, body


def _render_record(record: dict[str, Any], line_no: int, max_chars: int) -> tuple[str, str] | None:
    if isinstance(record.get("message"), dict):
        return _render_claude_record(record, line_no, max_chars)
    if isinstance(record.get("payload"), dict):
        return _render_codex_record(record, line_no, max_chars)
    return None


def _iter_delta_lines(path: Path, start_line_exclusive: int) -> Iterable[tuple[int, str]]:
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_no, line in enumerate(handle, start=1):
            if line_no > start_line_exclusive:
                yield line_no, line


def _extract_markdown(
    source: SourceSpec,
    *,
    extracted_at: str,
    max_chars: int,
) -> tuple[str, int, int, int, int | None, int | None]:
    rendered_messages = 0
    invalid_json_lines = 0
    decoded_lines = 0
    first_line: int | None = None
    last_line: int | None = None
    title = source.label.replace("_", " ").replace("-", " ").title()
    chunks = [
        f"# {title} Delta Transcript\n\n",
        f"- source: `{source.path}`\n",
        f"- delta_start_line: {source.start_line_exclusive} (1-indexed, exclusive)\n",
        f"- extracted: {extracted_at}\n",
        "- redactions: common API tokens, bearer tokens, environment tokens, and private-key PEM blocks\n\n",
        "---\n\n",
    ]

    for line_no, line in _iter_delta_lines(source.path, source.start_line_exclusive):
        decoded_lines += 1
        first_line = first_line if first_line is not None else line_no
        last_line = line_no
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            invalid_json_lines += 1
            continue
        if not isinstance(record, dict):
            continue
        rendered = _render_record(record, line_no, max_chars)
        if rendered is None:
            continue
        rendered_messages += 1
        header, body = rendered
        chunks.append(header.format(n=rendered_messages) + "\n\n")
        chunks.append(body + "\n\n")

    return (
        "".join(chunks),
        decoded_lines,
        rendered_messages,
        invalid_json_lines,
        first_line,
        last_line,
    )


def _build_index_text(receipt: SourceReceipt, anchors: tuple[str, ...]) -> str:
    anchor_lines = "\n".join(f"- {anchor}" for anchor in anchors) if anchors else "- none supplied"
    return (
        f"# {receipt.label} Archive Index\n\n"
        "Status: private Tier-D historical retrieval aid. Do not treat this index as canonical authority.\n\n"
        f"- source_path: `{receipt.source_path}`\n"
        f"- first_archived_line: `{receipt.first_archived_line}`\n"
        f"- last_archived_line: `{receipt.last_archived_line}`\n"
        f"- decoded_lines: `{receipt.decoded_lines}`\n"
        f"- rendered_messages: `{receipt.rendered_messages}`\n"
        f"- extract_sha256: `{receipt.extract_sha256}`\n"
        f"- raw_sha256: `{receipt.raw_sha256}`\n\n"
        "## Retrieval Anchors\n\n"
        f"{anchor_lines}\n"
    )


def _build_readme(
    archive_dir: Path,
    *,
    snapshot_date: str,
    previous_archive: str | None,
    receipts: list[SourceReceipt],
) -> str:
    raw_rows = "\n".join(
        f"| `{r.raw_archive_file}` | `{r.raw_sha256}` | `{r.raw_size_bytes}` |" for r in receipts
    )
    extract_rows = "\n".join(
        "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` |".format(
            r.extract_file,
            r.start_line_exclusive,
            r.decoded_lines,
            r.rendered_messages,
            r.invalid_json_lines,
            r.extract_sha256,
            r.extract_size_bytes,
        )
        for r in receipts
    )
    previous = f"`{previous_archive}`" if previous_archive else "none supplied"
    return (
        f"# {snapshot_date} Codex and Claude Raw Chat Archive\n\n"
        "Status: raw historical evidence only. These files are hypothesis input for retrieval and gap analysis; "
        "they are not canonical project authority unless a current repo artifact direct-reads and ratifies a "
        "specific claim.\n\n"
        f"Snapshot date: {snapshot_date}\n\n"
        f"Archive directory: `{archive_dir}`\n\n"
        f"Previous archive: {previous}\n\n"
        "## Archived Raw Files\n\n"
        "| Archive file | SHA-256 | Size bytes |\n"
        "|---|---:|---:|\n"
        f"{raw_rows}\n\n"
        "## Extracted Markdown Files\n\n"
        "| Extract file | Delta start line exclusive | Decoded lines | Rendered messages | Invalid JSON lines | SHA-256 | Size bytes |\n"
        "|---|---:|---:|---:|---:|---:|---:|\n"
        f"{extract_rows}\n\n"
        "## Notes\n\n"
        "- Raw logs and extracted Markdown are private historical material under `Z_Past_Chats/` and are gitignored.\n"
        "- Markdown extraction redacts common API-token, bearer-token, environment-token, and private-key PEM patterns.\n"
        "- Tool output snippets are bounded; raw compressed JSONL remains the lossless private archive.\n"
        "- MemPalace indexing should label these files as Tier D historical material; they must not override current "
        "`docs/specs`, `docs/phases/STATUS.md`, or current runtime source reads.\n"
    )


def archive_sources(
    *,
    archive_dir: Path,
    snapshot_date: str,
    extracted_at: str,
    previous_archive: str | None,
    sources: list[SourceSpec],
    anchors: tuple[str, ...],
    max_chars: int,
    overwrite: bool,
) -> dict[str, Any]:
    archive_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(archive_dir, 0o700)
    receipts: list[SourceReceipt] = []

    for source in sources:
        raw_file = f"{source.label}.raw.jsonl.gz"
        extract_file = f"{source.label}_extracted.md"
        index_file = f"{source.label}_index.md"
        raw_path = archive_dir / raw_file
        extract_path = archive_dir / extract_file
        index_path = archive_dir / index_file

        raw_sha, raw_size = _atomic_write_gzip(
            raw_path,
            (line for _, line in _iter_delta_lines(source.path, source.start_line_exclusive)),
            overwrite=overwrite,
        )
        markdown, decoded, rendered, invalid_json, first_line, last_line = _extract_markdown(
            source,
            extracted_at=extracted_at,
            max_chars=max_chars,
        )
        _atomic_write_text(extract_path, markdown, overwrite=overwrite)
        extract_sha, extract_size = _sha256_file(extract_path)
        provisional = SourceReceipt(
            label=source.label,
            source_path=str(source.path),
            raw_archive_file=raw_file,
            raw_sha256=raw_sha,
            raw_size_bytes=raw_size,
            extract_file=extract_file,
            extract_sha256=extract_sha,
            extract_size_bytes=extract_size,
            index_file=index_file,
            index_sha256="",
            index_size_bytes=0,
            start_line_exclusive=source.start_line_exclusive,
            first_archived_line=first_line,
            last_archived_line=last_line,
            decoded_lines=decoded,
            rendered_messages=rendered,
            invalid_json_lines=invalid_json,
        )
        _atomic_write_text(index_path, _build_index_text(provisional, anchors), overwrite=overwrite)
        index_sha, index_size = _sha256_file(index_path)
        receipts.append(
            SourceReceipt(
                **{
                    **provisional.__dict__,
                    "index_sha256": index_sha,
                    "index_size_bytes": index_size,
                }
            )
        )

    readme = _build_readme(
        archive_dir,
        snapshot_date=snapshot_date,
        previous_archive=previous_archive,
        receipts=receipts,
    )
    _atomic_write_text(archive_dir / "README.md", readme, overwrite=overwrite)
    manifest = {
        "schema_version": "ilc.agent_chat_delta_archive_manifest.v0.1",
        "snapshot_date": snapshot_date,
        "extracted_at": extracted_at,
        "previous_archive": previous_archive,
        "sources": [receipt.__dict__ for receipt in receipts],
        "non_claims": [
            "not_canonical_authority",
            "not_public_release_artifact",
            "not_secret_complete_redaction_guarantee",
            "not_mempalace_rebuild_by_itself",
        ],
    }
    _atomic_write_text(
        archive_dir / "archive_manifest.json",
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        overwrite=overwrite,
    )
    return manifest


def _parse_source(values: list[str]) -> SourceSpec:
    label, raw_path, raw_line = values
    if not _LABEL_RE.fullmatch(label):
        raise argparse.ArgumentTypeError(f"invalid source label: {label}")
    try:
        start_line = int(raw_line)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid start line for {label}: {raw_line}") from exc
    if start_line < 0:
        raise argparse.ArgumentTypeError(f"start line must be non-negative for {label}: {start_line}")
    path = Path(raw_path).expanduser()
    if not path.is_file():
        raise argparse.ArgumentTypeError(f"source path is not a file for {label}: {path}")
    return SourceSpec(label=label, path=path, start_line_exclusive=start_line)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Archive raw Codex/Claude JSONL deltas and produce redacted Markdown extracts.",
    )
    parser.add_argument("--archive-dir", required=True, type=Path)
    parser.add_argument("--snapshot-date", required=True)
    parser.add_argument("--previous-archive")
    parser.add_argument("--extracted-at", required=True)
    parser.add_argument("--max-field-chars", type=int, default=12_000)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--anchor", action="append", default=[])
    parser.add_argument(
        "--source",
        action="append",
        nargs=3,
        metavar=("LABEL", "JSONL_PATH", "DELTA_START_LINE_EXCLUSIVE"),
        required=True,
        help="Add a source JSONL delta. The line number is 1-indexed and exclusive.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.max_field_chars < 256:
        parser.error("--max-field-chars must be at least 256")
    try:
        sources = [_parse_source(values) for values in args.source]
    except argparse.ArgumentTypeError as exc:
        parser.error(str(exc))
    manifest = archive_sources(
        archive_dir=args.archive_dir,
        snapshot_date=args.snapshot_date,
        extracted_at=args.extracted_at,
        previous_archive=args.previous_archive,
        sources=sources,
        anchors=tuple(args.anchor),
        max_chars=args.max_field_chars,
        overwrite=args.overwrite,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
