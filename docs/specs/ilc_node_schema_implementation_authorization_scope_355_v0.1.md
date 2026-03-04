# ILC Node Schema Implementation Authorization Scope 355 v0.1

## 1. Scope

This artifact defines which ratified node-schema surfaces are eligible for Window-358+ runtime implementation and which boundaries remain in force until Phase 357 closure completes.

## 2. Ratified surfaces authorized for Window 358+ implementation

`Window 358+ may begin implementation of ratified CDL-034 through CDL-038 surfaces only after Phase 357 closure.`

`Authorized implementation set: CDL-034, CDL-035, CDL-036, CDL-037, CDL-038.`

The authorization set is limited to the ratified node-schema stack and its direct implementation dependencies.

## 3. Surfaces that remain implementation-barred

`Implementation remains barred for any unratified surface.`

No additional runtime surface is authorized merely because it is adjacent to a ratified node-schema surface.

This artifact does not authorize Phase-355 runtime changes in `ilc_core/`.

## 4. Dependency-order and coupling constraints

`ADM-003 integration is a prerequisite for implementation, not a substitute for ratified CDL scope.`

`Implementation ordering must respect the dependency chain CDL-034 -> CDL-035 -> CDL-036 -> CDL-037 -> CDL-038 where technically required.`

Cross-CDL coupling remains relevant at implementation time:
- lifecycle semantics constrain promotion continuity,
- envelope placement constrains executable-descriptor integration,
- transport/header work remains downstream of the ratified envelope and lifecycle model.

## 5. Window-357 closure prerequisite

`Phase 357 closure is the final authorization gate for Window 358+ runtime work.`

Phase 355 defines scope only. Phase 356 prepares implementation readiness. Neither phase authorizes runtime changes directly.
