#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-only
# setup_ccss_hs.sh — Deploy CCSS Tor hidden service on ilc-node-2 or ilc-node-3
#
# Run as root (or with sudo) on the deployment host.
#
# What this does:
#   1. Installs tor if not present
#   2. Appends the CCSS hidden service config to /etc/tor/torrc
#   3. Installs and enables the ccss-relay systemd service
#   4. Creates the ccss user and inbox directory
#   5. Restarts tor and the relay
#   6. Waits for the .onion address to be generated and prints it
#
# After running this script:
#   - Record the printed .onion address in:
#       docs/contact/genesis_agent_contact_protocol_v0.1.md  (replace ONION_ADDRESS_PLACEHOLDER)
#       SECURITY.md  (replace ONION_ADDRESS_PLACEHOLDER)
#   - Replace GENESIS_AGENT_PUBKEY_PLACEHOLDER and GENESIS_AGENT_ID_PLACEHOLDER
#     in docs/contact/ using the output of your keygen tool.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

RELAY_PORT=8420
INBOX_DIR=/var/lib/ccss/inbox/genesis
HS_DIR=/var/lib/tor/ccss_hs
CCSS_USER=ccss

echo "=== CCSS hidden service setup ==="
echo "Repo:     $REPO_ROOT"
echo "Port:     $RELAY_PORT"
echo "Inbox:    $INBOX_DIR"
echo "HS dir:   $HS_DIR"

# 1. Install tor
if ! command -v tor &>/dev/null; then
    echo "[1/6] Installing tor..."
    apt-get update -qq
    apt-get install -y tor
else
    echo "[1/6] tor already installed: $(tor --version | head -1)"
fi

# 2. Append CCSS HS config to torrc (idempotent)
TORRC=/etc/tor/torrc
if ! grep -q "ccss_hs" "$TORRC"; then
    echo "[2/6] Appending CCSS hidden service config to $TORRC ..."
    cat >> "$TORRC" <<'EOF'

# CCSS Genesis Agent hidden service (added by setup_ccss_hs.sh)
HiddenServiceDir /var/lib/tor/ccss_hs/
HiddenServicePort 80 127.0.0.1:8420
HiddenServiceVersion 3
EOF
else
    echo "[2/6] CCSS hidden service config already in $TORRC — skipping."
fi

# 3. Install relay service and code
echo "[3/6] Installing ccss-relay service..."
# Create ccss user if needed
if ! id "$CCSS_USER" &>/dev/null; then
    useradd --system --no-create-home --shell /usr/sbin/nologin "$CCSS_USER"
fi
# Install code
mkdir -p /opt/ilc/tools/ccss_relay
cp "$REPO_ROOT/tools/ccss_relay/ccss_relay_server.py" /opt/ilc/tools/ccss_relay/
cp "$REPO_ROOT/tools/ccss_relay/ccss_inbox_reader.py" /opt/ilc/tools/ccss_relay/

# 4. Create inbox directory
echo "[4/6] Creating inbox at $INBOX_DIR ..."
mkdir -p "$INBOX_DIR"
chown "$CCSS_USER:$CCSS_USER" "$INBOX_DIR"

# Install and enable systemd service
cp "$REPO_ROOT/deploy/systemd/ccss-relay.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable ccss-relay.service

# 5. Start services
echo "[5/6] Starting ccss-relay and tor..."
systemctl restart ccss-relay.service
systemctl restart tor.service

# 6. Wait for .onion address
echo "[6/6] Waiting for Tor to generate .onion address..."
HOSTNAME_FILE="$HS_DIR/hostname"
for i in $(seq 1 30); do
    if [[ -f "$HOSTNAME_FILE" ]]; then
        ONION_ADDR=$(cat "$HOSTNAME_FILE")
        break
    fi
    sleep 2
done

if [[ -z "${ONION_ADDR:-}" ]]; then
    echo "ERROR: .onion address not generated after 60s."
    echo "  Check: journalctl -u tor.service"
    exit 1
fi

echo ""
echo "=== CCSS Hidden Service Ready ==="
echo ""
echo "  .onion address:  $ONION_ADDR"
echo "  Submit endpoint: http://$ONION_ADDR/submit"
echo "  Health check:    http://$ONION_ADDR/health"
echo ""
echo "Next steps:"
echo "  1. Replace ONION_ADDRESS_PLACEHOLDER in:"
echo "       docs/contact/genesis_agent_contact_protocol_v0.1.md"
echo "       SECURITY.md"
echo "  2. Verify relay is running:  systemctl status ccss-relay.service"
echo "  3. Check inbox:              python3 /opt/ilc/tools/ccss_relay/ccss_inbox_reader.py --inbox $INBOX_DIR"
