# ILC Operator Configuration Guide

This directory contains runtime configuration inputs used by governance and simulation-adjacent hardware helpers.

## Files

- `genesis.json`: Axiomatic core bootstrap payload.
- `governance_mvp.json`: Default governance policy config.
- `governance_mvp.yaml`: Optional YAML-format governance config.
- `hardware_archetypes_mvp.json`: Default hardware archetype config.
- `hardware_archetypes_mvp.yaml`: Optional YAML-format hardware archetype config.

## Loader policy (Phase 1006 lock)

### Governance loader (`ilc_core/config.py`)

- Default load path is `config/governance_mvp.json`.
- Explicit YAML paths (`.yaml` or `.yml`) are supported when PyYAML is available.
- If explicit YAML is requested and PyYAML is unavailable, loader checks sibling `.json`.
- If no valid source can be loaded, loader returns empty config for default-missing cases and raises `ConfigNotFoundError` for user-supplied missing paths.

### Hardware loader (`ilc_core/hardware.py`)

- Default load path is `config/hardware_archetypes_mvp.json`.
- Explicit YAML paths (`.yaml` or `.yml`) are supported when PyYAML is available.
- If explicit YAML is requested and PyYAML is unavailable, loader checks sibling `.json`.
- If default sources are missing, loader raises `FileNotFoundError`.

## Operator guidance

1. Keep JSON files as the canonical operational source of truth.
2. Treat YAML files as optional convenience mirrors.
3. When changing governance or hardware values, update both JSON and YAML files to keep parity.
4. Use focused tests after config changes:
   - `python3 -m pytest tests/test_governance_config.py -q`
   - `python3 -m pytest tests/test_hardware_archetypes.py -q`
