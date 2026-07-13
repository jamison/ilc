# ILC OpenClaw Real Harness Strike Force 1575b-Fix2e-Fix2

```text
schema: ilc_openclaw_real_harness_strikeforce_1575b_fix2e_fix2.v0.1
phase: 1575b-Fix2e-Fix2
sensitivity: NON-SENSITIVE
```

## Purpose

This strike-force phase upgrades the prior two-VPS fixture proof into a real
OpenClaw harness installation proof on two private VPS nodes.

## Result

The retained evidence is:

```text
out/block6_openclaw_real_harness_strikeforce_fix2e_fix2/evidence_records.json
```

Evidence payload SHA-256:

```text
6dcf97fc1718fca6b8b7bff131d506cc55b13860727faabf4742a9ffad4705e4
```

Confirmed:

- OpenClaw is installed on `ilc-node-2` and `ilc-node-3`.
- ILC source is installed in a node-local Python venv on both nodes.
- The ILC OpenClaw skill is installed in both OpenClaw workspaces.
- The ILC OpenClaw skill has frontmatter, is named `ilc-openclaw-local-capture`, and has identical SHA-256 on both nodes.
- `ilc-node-2` runs the OpenClaw Gateway.
- `ilc-node-3` runs the OpenClaw node host.
- `ilc-node-3` is paired in node2 Gateway state and has a fresh `lastConnectedAtMs`.

## Transport Boundary

The Gateway is not exposed on the public interface. The test uses:

```text
node2 loopback Gateway: 127.0.0.1:18789
node2 Tailscale-bound test forwarder: 100.112.32.42:18790 -> 127.0.0.1:18789
node3 node host: connects to 100.112.32.42:18790
```

The forwarder is a private strike-force test harness, not a public serving
configuration.

## Honest Boundary

Remote command invocation through `openclaw nodes invoke` is not claimed in this
phase. The blocker is OpenClaw operator CLI scope escalation:

```text
operator_cli_read_invoke_scope_upgrade_requires_openclaw_operator_approval
```

This phase proves real installation, skill visibility, Gateway operation,
node-host operation, pairing, and connection. It does not prove remote command
invocation.

## Non-Claims

This phase does not publish OpenClaw, create a ClawHub listing, submit public
graph nodes, mint ECU, settle ILC, write wallets, activate public RC, clear
runtime guards, or transition epochs.
