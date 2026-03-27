# ILC Genesis Validator Architecture Scoping 468 v0.1

Status: scoped
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Minimum viable configuration

Genesis validator architecture scoping is complete as of Phase 468.

The minimum viable genesis-validator configuration is scoped as:
- signer key material for ratified CDL-051 validator identity,
- initial validator-set enrollment record,
- initial cluster assignment material,
- initial vote-weight material,
- epoch-zero state record and quorum-record seed,
- admission-control list pre-populated for authorized genesis validators.

This is a bootstrap scope only. It defines the minimum documents and state that a genesis
validator would need before runtime implementation begins.

## 2. CDL-051 consensus dependency

The genesis validator depends directly on CDL-051 consensus semantics:
- validator identity and membership must satisfy the ratified validator-set contract,
- cluster assignment must satisfy the diversity-floor interpretation,
- weight assignment must respect quorum-threshold semantics,
- epoch-zero records must seed the finality state machine consistently with CDL-051.

No Phase 468 scoping text overrides CDL-051. It only scopes the implementation boundary that a
future runtime lane would need to satisfy.

## 3. Admission control pre-population

Admission control pre-population is scoped as a static bootstrap bundle containing:
- authorized validator identities,
- cluster-membership assignments,
- initial vote weights,
- initial epoch-state metadata,
- genesis quorum-record anchor.

This bundle is not implemented in Phase 468. It is a future delivery item for a runtime lane.

## 4. Deferred implementation items

Genesis validator implementation is deferred beyond Window 460-468.

Deferred items include:
- runtime validator bootstrap tooling,
- key-loading and ceremony integration,
- epoch-zero state materialization in executable form,
- admission-control runtime enforcement,
- validator network join and recovery flow.
