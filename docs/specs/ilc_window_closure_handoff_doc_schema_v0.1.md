# ILC Window Closure Handoff Document Schema v0.1

**Author:** Codex
**Date:** 2026-04-12
**Purpose:** standard contract for end-of-window closure and carry-forward handoff docs

This schema defines the standard structure for window-ending closure and handoff
documents such as:

- `docs/specs/ilc_window_596_605_handoff_605_v0.1.md`
- `docs/specs/ilc_window_565_574_handoff_574_v0.1.md`
- `docs/specs/ilc_window_424_433_handoff_433_v0.1.md`

It is a documentation contract only. It does not make MemPalace a required
runtime or CI dependency.

## 1. Document type and naming convention

**File path:** `docs/specs/ilc_window_NNN_MMM_handoff_MMM_vX.Y.md`

**Title:** `# ILC Window NNN-MMM Handoff MMM vX.Y`

**Required header fields:**
```text
Status: handoff artifact
Date: <date>
Classification: closure and carry-forward handoff
```

## 2. Required sections

Every closure/handoff doc should contain these sections, in this order:

1. `## 1. Window identity and closure basis`
2. `## 2. Inputs and closure inheritance`
3. `## 3. Closure verdict summary`
4. `## 4. Carry-forward items and residual blockers`
5. `## 5. Next-window entry criteria and routing`
6. `## 6. MemPalace refresh disposition`

Additional sections may follow if the window needs them.

## 3. Required section content

### 3.1 Window identity and closure basis

Must state:
- the window being closed
- the closure phase and verdict source
- the authoritative closure inputs used

### 3.2 Inputs and closure inheritance

Must list:
- relevant sequence lock
- relevant closure gate artifacts
- governing handoff or prior closure artifact
- active capsule / ADR references when needed

### 3.3 Closure verdict summary

Must summarize:
- what closed
- what remained deferred
- whether any scope remained explicitly blocked

### 3.4 Carry-forward items and residual blockers

Must separate:
- closed and not carried forward
- carried-forward items
- blocked items requiring future routing

### 3.5 Next-window entry criteria and routing

Must record:
- what the next window may assume
- what still requires explicit confirmation
- what lane or artifact should carry unresolved items

## 4. MemPalace refresh disposition section

This section is required for every closure/handoff doc, but it is a decision
record, not a mandatory rebuild.

The section must contain these exact fields:

- `Disposition:` `required` | `not_required`
- `Active working set impacted:` `yes` | `no`
- `Basis:` short explanation of why the frontier or retrieval surface did or did not change

If `Disposition: required`, the section must also include:

- `Working-set descriptor:` `docs/tools/mempalace/ilc_mempalace_active_working_set_v0.1.json`
- `Manifest:` `docs/tools/mempalace/ilc_mempalace_current_frontier_manifest_v0.1.json`
- `Rebuild command:` `bash tools/mempalace/build_active_working_set.sh`

If `Disposition: not_required`, the section must explicitly state why the
authoritative frontier, planning surface, or retrieval surface did not change
enough to justify a rebuild.

## 5. MemPalace boundary rule

This schema does not authorize MemPalace to act as canon.

The closure/handoff document may record:
- whether the active working set should be refreshed
- whether a retrieval brief informed drafting
- which provenance questions were checked

It must not:
- treat retrieval output as authoritative by itself
- require a live MemPalace run for document validity
- replace direct repo reads, gate outputs, or accepted ADR material

## 6. Relationship to window-guidance docs

The beginning-of-window planning artifact should follow:
- `docs/specs/ilc_window_guidance_doc_schema_v0.1.md`

The end-of-window closure artifact should follow this schema.

Together they form the intended start-of-window / end-of-window document pair:
- window guidance at entry
- closure/handoff at exit
