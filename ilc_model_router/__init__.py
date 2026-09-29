# SPDX-License-Identifier: AGPL-3.0-only
"""Local-first Model Router sidecar receipt package."""

from .adapter import (
    PROVIDER_ADAPTER_VERSION,
    PROVIDER_RESPONSE_STATUSES,
    ProviderAdapter,
    ProviderAdapterError,
    ProviderResponse,
    RouterRequest,
)
from .anthropic_adapter import (
    ANTHROPIC_ADAPTER_VERSION,
    AnthropicAdapter,
)
from .receipt_schema import (
    CAPABILITY_CLASSES,
    CONSENT_STATUSES,
    MODEL_ROUTER_PACKAGE_NAME,
    MODEL_ROUTER_RECEIPT_SCHEMA_VERSION,
    RouterCompanionRecord,
    RouterReceipt,
    RouterReceiptError,
)
from .receipt_store import (
    COMPANION_DB,
    NULLIFIERS_DB,
    PENDING_NULLIFIER_VALUE,
    RECEIPTS_DB,
    ROUTER_RECEIPT_STORE_VERSION,
    TOKEN_INDEX_DB,
    check_nullifier,
    finalize_reserved_router_receipt,
    lookup_by_token,
    open_router_receipt_env,
    reserve_router_nullifier,
    store_router_receipt,
)
from .router_engine import (
    ROUTER_DST,
    ROUTER_ENGINE_VERSION,
    ROUTER_NULLIFIER_SCHEMA_VERSION,
    ROUTER_TIMEOUT_SECONDS,
    RouterEngine,
)

__all__ = [
    "ANTHROPIC_ADAPTER_VERSION",
    "CAPABILITY_CLASSES",
    "COMPANION_DB",
    "CONSENT_STATUSES",
    "AnthropicAdapter",
    "MODEL_ROUTER_PACKAGE_NAME",
    "MODEL_ROUTER_RECEIPT_SCHEMA_VERSION",
    "NULLIFIERS_DB",
    "PENDING_NULLIFIER_VALUE",
    "PROVIDER_ADAPTER_VERSION",
    "PROVIDER_RESPONSE_STATUSES",
    "RECEIPTS_DB",
    "ROUTER_DST",
    "ROUTER_ENGINE_VERSION",
    "ROUTER_NULLIFIER_SCHEMA_VERSION",
    "ROUTER_RECEIPT_STORE_VERSION",
    "ROUTER_TIMEOUT_SECONDS",
    "ProviderAdapter",
    "ProviderAdapterError",
    "ProviderResponse",
    "RouterEngine",
    "RouterRequest",
    "RouterCompanionRecord",
    "RouterReceipt",
    "RouterReceiptError",
    "TOKEN_INDEX_DB",
    "check_nullifier",
    "finalize_reserved_router_receipt",
    "lookup_by_token",
    "open_router_receipt_env",
    "reserve_router_nullifier",
    "store_router_receipt",
]
