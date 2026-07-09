# SPDX-License-Identifier: AGPL-3.0-only
"""Packaged CCSS local runtime helpers for the public CLI surface."""

from ilc_core.ccss.runtime import (
    CCSSRuntimeError,
    add_contact,
    apply_confidential_contact_recipe,
    build_allow_reply_message,
    generate_identity,
    import_genesis_contact,
    list_contacts,
    list_inbox,
    read_envelope,
    send_message,
)
from ilc_core.ccss.contact_gate import (
    CONTACT_GATE_ADMISSION_MODES,
    CONTACT_GATE_PUBLIC_SERVING_NOT_ACTIVATED,
    CONTACT_GATE_RUNTIME_VERSION,
    ContactGateError,
    assert_no_private_gate_fields,
    evaluate_contact_gate,
    make_contact_gate_nullifier,
)
from ilc_core.ccss.safe_message import (
    HeuristicClassifier,
    MessageSafetyClassifier,
    SafeCCSSMessage,
    SafetyVerdict,
    receive_message,
)

__all__ = [
    "CCSSRuntimeError",
    "CONTACT_GATE_ADMISSION_MODES",
    "CONTACT_GATE_PUBLIC_SERVING_NOT_ACTIVATED",
    "CONTACT_GATE_RUNTIME_VERSION",
    "ContactGateError",
    "HeuristicClassifier",
    "MessageSafetyClassifier",
    "SafeCCSSMessage",
    "SafetyVerdict",
    "add_contact",
    "apply_confidential_contact_recipe",
    "assert_no_private_gate_fields",
    "build_allow_reply_message",
    "evaluate_contact_gate",
    "generate_identity",
    "import_genesis_contact",
    "list_contacts",
    "list_inbox",
    "make_contact_gate_nullifier",
    "read_envelope",
    "receive_message",
    "send_message",
]
