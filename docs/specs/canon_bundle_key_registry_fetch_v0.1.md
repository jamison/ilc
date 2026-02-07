# Canon Bundle Key Registry Fetch v0.1

## Overview

Fetch and verify registry bundles from local or remote sources.

---

## Source Types

| Source | Description |
|--------|-------------|
| Local path | `/path/to/bundle` or `/path/to/bundle.tar.gz` |
| `file://` URL | `file:///path/to/bundle` |
| `https://` URL | `https://example.com/bundle.tar.gz` (requires `--allow-network`) |

---

## CLI Usage

```bash
# Local directory
python3 -m ilc_core.cli.canon_bundle_key_registry_fetch \
  --source /path/to/bundle --key-file key.txt --dest ./installed

# file:// URL
python3 -m ilc_core.cli.canon_bundle_key_registry_fetch \
  --source file:///path/to/bundle --key-file key.txt --dest ./installed

# https:// URL (requires --allow-network)
python3 -m ilc_core.cli.canon_bundle_key_registry_fetch \
  --source https://example.com/bundle.tar.gz --key-file key.txt --dest ./installed --allow-network
```

---

## Flags

| Flag | Description |
|------|-------------|
| `--source` | Source path or URL |
| `--key-file` | Verification key |
| `--dest` | Destination directory |
| `--force` | Overwrite existing bundle |
| `--allow-network` | Enable https downloads |
| `--timeout` | Network timeout (default 20s) |
| `--keep-temp` | Keep temp dir on failure |
| `--strict` | Strict registry validation |

---

## Security

- Mandatory signature verification
- Bundle whitelist enforcement
- Path traversal protection in archives
- Single top-level directory required
- Network disabled by default
