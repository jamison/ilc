# ILC ADR-0021 Epistemic Finality Claims 461 v0.1

Status: completed architectural decision record
Date: 2026-03-27
Owner lane: G8 Constitution Cluster A

## 1. Problem statement

ADR-0021 covers epistemic finality claims in the ILC consensus machinery.

The problem is to define how finality records should be treated once they appear as knowledge-bearing artifacts in the graph.
CDL-051 governs consensus and epoch-finality protocol records.
CDL-052 governs epistemic evaluation of graph nodes.
The boundary becomes sensitive when a finality assertion is itself represented as a node or evidence-bearing graph object.

## 2. CDL-051 finality domain boundary

CDL-051 owns protocol truth for:
- validator-set evolution,
- quorum formation,
- epoch advancement,
- fork resolution,
- finality records as consensus-state outputs.

Within this domain, a finality assertion is authoritative only insofar as it is backed by the ratified consensus machinery and epoch record semantics.

## 3. CDL-052 knowledge graph domain boundary

CDL-052 owns epistemic evaluation for graph-native claims, refutations, anomaly-triggered auditor review, and the three-mode routing architecture.

A finality assertion may appear inside the graph as:
- a reference node,
- a citation-bearing evidence node,
- an object of downstream commentary or refutation.

When this happens, CDL-052 governs the graph-side representation and evaluation of the claim, but not the underlying protocol-finality truth source itself.

## 4. Domain overlap and boundary conditions

The overlap boundary is narrow.

Boundary conditions:
- protocol-finality truth remains sourced from CDL-051 semantics,
- graph-side discussion of that truth may be represented and routed under CDL-052,
- CDL-052 may evaluate claims about whether a cited finality record is being correctly described, but it does not override the finality record itself,
- if a graph node disputes the existence or interpretation of a finality event, the dispute is epistemic and graph-side unless it asserts a protocol-state defect that requires a separate CDL-051 amendment lane.

This keeps the domains composable:
- CDL-051 remains authoritative over finality generation,
- CDL-052 remains authoritative over graph-side handling of claims about finality.

## 5. Gate 1 compatibility statement

Gate 1 compatibility: cleared

The CDL-051 finality domain and CDL-052 knowledge graph domain have been examined and no blocking conflict was identified at the boundary defined in Section 4.
No CDL-052 opening occurs in Phase 461.
