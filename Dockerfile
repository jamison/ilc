# syntax=docker/dockerfile:1
#
# ILC local operator image: Python ilc_core + Rust ilc_consensus binaries.
# This image is local-development packaging only. It does not contain private
# keys, Genesis credentials, API secrets, live validator DBs, or production
# activation material.

FROM rust:1.88-slim-bookworm AS rust-builder

WORKDIR /build

RUN apt-get update \
    && apt-get install -y --no-install-recommends pkg-config libssl-dev ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY ilc_consensus/Cargo.toml ./ilc_consensus/Cargo.toml
COPY ilc_consensus/build.rs ./ilc_consensus/build.rs
COPY ilc_consensus/proto ./ilc_consensus/proto
COPY ilc_consensus/src ./ilc_consensus/src

RUN cd ilc_consensus && cargo build --release --bins

FROM python:3.11-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ILC_NODE_MODE=observer
ENV ILC_DATA_DIR=/var/lib/ilc
ENV ILC_BOOTSTRAP_SEED_PEER=
ENV ILC_BOOTSTRAP_BUNDLE_CID=

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates liblmdb0 \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/lib/ilc /var/lib/ilc/keys /var/log/ilc /usr/local/lib/ilc_consensus

COPY pyproject.toml README.md ./
COPY ilc_core ./ilc_core
COPY run_node.py ./run_node.py

RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -e ".[operator-node]"

COPY --from=rust-builder /build/ilc_consensus/target/release/validator_harness /usr/local/bin/validator_harness
COPY --from=rust-builder /build/ilc_consensus/target/release/testnet_client /usr/local/bin/testnet_client
COPY --from=rust-builder /build/ilc_consensus/target/release/state_extractor /usr/local/bin/state_extractor
COPY --from=rust-builder /build/ilc_consensus/target/release/attribution_batch_ingest /usr/local/bin/attribution_batch_ingest

VOLUME ["/var/lib/ilc"]

EXPOSE 8000

ENTRYPOINT ["python3", "run_node.py"]
