from __future__ import annotations

from typing import Iterable, Literal, Mapping, Sequence, TypedDict, TypeAlias, cast

from ilc_core.exceptions import NodeValueInputValidationError


NodeValueInputKind = Literal["task_outcome", "claim", "refutation", "commit.epoch"]


class TaskOutcomeInputPayload(TypedDict):
    task_id: str
    agent_id: str
    epoch: int
    reward_paid: float
    stake_spent: float
    success: bool
    domain: str


class ClaimInputPayload(TypedDict, total=False):
    id: str
    agent_id: str
    timestamp: str
    net_stake: float
    parent_ids: list[str]
    target_id: str


class RefutationInputPayload(TypedDict, total=False):
    id: str
    agent_id: str
    timestamp: str
    target_id: str
    net_stake: float


class CommitEpochInputPayload(TypedDict):
    event_kind: str
    epoch_index: int
    epoch_id: str
    namespace_id: str


NodeValueInputPayload: TypeAlias = (
    TaskOutcomeInputPayload
    | ClaimInputPayload
    | RefutationInputPayload
    | CommitEpochInputPayload
)


class NodeValueInputEvent(TypedDict):
    kind: NodeValueInputKind
    payload: NodeValueInputPayload


class NodeValueInputTelemetry(TypedDict):
    total_seen: int
    accepted: int
    rejected_invalid_shape: int
    rejected_unknown_kind: int


_ALLOWED_KINDS = {"task_outcome", "claim", "refutation", "commit.epoch"}


def _expect_mapping(value: object, token: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise NodeValueInputValidationError(token)
    return cast(Mapping[str, object], value)


def _expect_str(payload: Mapping[str, object], key: str, token: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or value == "":
        raise NodeValueInputValidationError(token)
    return value


def _expect_int(payload: Mapping[str, object], key: str, token: str) -> int:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise NodeValueInputValidationError(token)
    return value


def _expect_float(payload: Mapping[str, object], key: str, token: str) -> float:
    value = payload.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise NodeValueInputValidationError(token)
    return float(value)


def _expect_bool(payload: Mapping[str, object], key: str, token: str) -> bool:
    value = payload.get(key)
    if not isinstance(value, bool):
        raise NodeValueInputValidationError(token)
    return value


def _expect_str_list(payload: Mapping[str, object], key: str, token: str) -> list[str]:
    value = payload.get(key)
    if value is None:
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise NodeValueInputValidationError(token)
    out: list[str] = []
    for item in value:
        if not isinstance(item, str) or item == "":
            raise NodeValueInputValidationError(token)
        out.append(item)
    return out


def _validate_task_outcome_payload(payload: Mapping[str, object]) -> TaskOutcomeInputPayload:
    return {
        "task_id": _expect_str(payload, "task_id", "node_value_input_missing_task_id"),
        "agent_id": _expect_str(payload, "agent_id", "node_value_input_missing_agent_id"),
        "epoch": _expect_int(payload, "epoch", "node_value_input_invalid_epoch"),
        "reward_paid": _expect_float(payload, "reward_paid", "node_value_input_invalid_reward_paid"),
        "stake_spent": _expect_float(payload, "stake_spent", "node_value_input_invalid_stake_spent"),
        "success": _expect_bool(payload, "success", "node_value_input_invalid_success"),
        "domain": _expect_str(payload, "domain", "node_value_input_missing_domain"),
    }


def _validate_claim_payload(payload: Mapping[str, object]) -> ClaimInputPayload:
    return {
        "id": _expect_str(payload, "id", "node_value_input_missing_claim_id"),
        "agent_id": _expect_str(payload, "agent_id", "node_value_input_missing_agent_id"),
        "timestamp": _expect_str(payload, "timestamp", "node_value_input_missing_timestamp"),
        "net_stake": _expect_float(payload, "net_stake", "node_value_input_invalid_net_stake"),
        "parent_ids": _expect_str_list(payload, "parent_ids", "node_value_input_invalid_parent_ids"),
        "target_id": _expect_str(payload, "target_id", "node_value_input_missing_target_id"),
    }


def _validate_refutation_payload(payload: Mapping[str, object]) -> RefutationInputPayload:
    return {
        "id": _expect_str(payload, "id", "node_value_input_missing_refutation_id"),
        "agent_id": _expect_str(payload, "agent_id", "node_value_input_missing_agent_id"),
        "timestamp": _expect_str(payload, "timestamp", "node_value_input_missing_timestamp"),
        "target_id": _expect_str(payload, "target_id", "node_value_input_missing_target_id"),
        "net_stake": _expect_float(payload, "net_stake", "node_value_input_invalid_net_stake"),
    }


def _validate_commit_epoch_payload(payload: Mapping[str, object]) -> CommitEpochInputPayload:
    event_kind = _expect_str(
        payload,
        "event_kind",
        "node_value_input_missing_event_kind",
    )
    if event_kind != "commit.epoch":
        raise NodeValueInputValidationError("node_value_input_invalid_commit_event_kind")

    return {
        "event_kind": event_kind,
        "epoch_index": _expect_int(
            payload,
            "epoch_index",
            "node_value_input_invalid_epoch_index",
        ),
        "epoch_id": _expect_str(payload, "epoch_id", "node_value_input_missing_epoch_id"),
        "namespace_id": _expect_str(
            payload,
            "namespace_id",
            "node_value_input_missing_namespace_id",
        ),
    }


def validate_node_value_input_event(event: Mapping[str, object]) -> NodeValueInputEvent:
    kind_value = event.get("kind")
    if not isinstance(kind_value, str):
        raise NodeValueInputValidationError("node_value_input_missing_kind")

    payload_mapping = _expect_mapping(
        event.get("payload"),
        "node_value_input_missing_payload",
    )

    if kind_value not in _ALLOWED_KINDS:
        raise NodeValueInputValidationError(
            f"node_value_input_unknown_kind:{kind_value}"
        )

    if kind_value == "task_outcome":
        return {
            "kind": "task_outcome",
            "payload": _validate_task_outcome_payload(payload_mapping),
        }
    if kind_value == "claim":
        return {
            "kind": "claim",
            "payload": _validate_claim_payload(payload_mapping),
        }
    if kind_value == "refutation":
        return {
            "kind": "refutation",
            "payload": _validate_refutation_payload(payload_mapping),
        }

    return {
        "kind": "commit.epoch",
        "payload": _validate_commit_epoch_payload(payload_mapping),
    }


def collect_node_value_input_events(
    events: Iterable[Mapping[str, object]],
) -> tuple[list[NodeValueInputEvent], NodeValueInputTelemetry]:
    accepted_rows: list[NodeValueInputEvent] = []
    telemetry: NodeValueInputTelemetry = {
        "total_seen": 0,
        "accepted": 0,
        "rejected_invalid_shape": 0,
        "rejected_unknown_kind": 0,
    }

    for raw_event in events:
        telemetry["total_seen"] += 1
        try:
            normalized = validate_node_value_input_event(raw_event)
            accepted_rows.append(normalized)
            telemetry["accepted"] += 1
        except NodeValueInputValidationError as exc:
            token = str(exc)
            if token.startswith("node_value_input_unknown_kind"):
                telemetry["rejected_unknown_kind"] += 1
            else:
                telemetry["rejected_invalid_shape"] += 1

    return accepted_rows, telemetry
