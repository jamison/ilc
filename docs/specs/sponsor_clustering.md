# Specification: Sponsor Clustering (The Independence Graph)

## The Problem
Sybil attackers spin up 1,000 "independent" agents to flood panels.
Labels (Org ID) are cheap. Capital is expensive.

## The Algorithm: Weighted Union-Find
We do not count agents. We count **Capital Roots**.

### 1. The Edges
We build a graph $G_{money}$ where edges represent dependency:
* **Sponsorship:** Wallet A bonded Stake for Agent B.
* **Payout:** Agent B sweeps rewards to Wallet A.
* **Recycling:** Agent B and Agent C were funded by the same tx_hash source within 3 hops.

### 2. The Cluster
Run **Union-Find** (Disjoint Set Union) on $G_{money}$.
* `Cluster(Agent)` = The root ID of the connected component.
* **Independence Rule:** A panel is valid iff:
    `Count(Unique Clusters) >= k` (Default k=3).

### 3. The Decay
Edges in $G_{money}$ have a TTL (Time To Live).
* If Agent B earns enough to stake for themselves (Self-Sovereign), the link to Sponsor A decays after $N$ epochs.
* They become a new, independent Cluster.
* *Result:* Independence is earned by economic maturity.
