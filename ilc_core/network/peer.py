from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Set
import logging
from pydantic import BaseModel
import requests
import random

logger = logging.getLogger(__name__)

PeerSender = Callable[[str, dict[str, Any], float], Any]


class Peer(BaseModel):
    host: str
    port: int
    agent_id: str

class PeerManager:
    def __init__(
        self,
        local_port: int,
        *,
        fanout_limit: int = 3,
        request_timeout_s: float = 1.0,
        sender: PeerSender | None = None,
    ):
        self.local_port = local_port
        self.fanout_limit = max(1, fanout_limit)
        self.request_timeout_s = request_timeout_s
        self.peers: Set[str] = set() # Set of "host:port" strings
        self.banned: Set[str] = set()
        self._sender = sender or _default_sender

    def add_peer(self, host: str, port: int):
        address = f"{host}:{port}"
        if address not in self.banned and address != f"127.0.0.1:{self.local_port}":
            self.peers.add(address)
            logger.info("network_peer_added address=%s", address)

    def _select_targets(self) -> list[str]:
        fanout = min(len(self.peers), self.fanout_limit)
        if fanout <= 0:
            return []
        return random.sample(list(self.peers), fanout)

    def _broadcast_url(self, target: str, endpoint: str) -> str:
        normalized_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        return f"http://{target}{normalized_endpoint}"

    def broadcast(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """
        Attempt delivery to a random subset of peers over HTTP fanout.
        """
        targets = self._select_targets()

        logger.info(
            "network_gossip_broadcast endpoint=%s fanout=%s targets=%s",
            endpoint,
            len(targets),
            targets,
        )

        if not targets:
            return {
                "attempted": 0,
                "succeeded": 0,
                "failed": 0,
                "targets": [],
            }

        successes = 0
        failures = 0
        target_urls = {target: self._broadcast_url(target, endpoint) for target in targets}

        with ThreadPoolExecutor(max_workers=len(targets)) as executor:
            future_to_target = {
                executor.submit(
                    self._sender,
                    target_urls[target],
                    payload,
                    self.request_timeout_s,
                ): target
                for target in targets
            }

            for future in as_completed(future_to_target):
                target = future_to_target[future]
                try:
                    response = future.result()
                    status_code = getattr(response, "status_code", None)
                    ok = bool(
                        getattr(
                            response,
                            "ok",
                            status_code is not None and 200 <= status_code < 300,
                        )
                    )
                    if ok:
                        successes += 1
                        logger.info(
                            "network_gossip_delivery_succeeded target=%s status=%s",
                            target,
                            status_code,
                        )
                    else:
                        failures += 1
                        logger.warning(
                            "network_gossip_delivery_failed target=%s status=%s",
                            target,
                            status_code,
                        )
                except requests.RequestException as exc:
                    failures += 1
                    logger.warning(
                        "network_gossip_delivery_failed target=%s error=%s",
                        target,
                        exc.__class__.__name__,
                    )
                except Exception as exc:  # pragma: no cover - defensive logging path
                    failures += 1
                    logger.exception(
                        "network_gossip_delivery_failed target=%s error=%s",
                        target,
                        exc.__class__.__name__,
                    )

        return {
            "attempted": len(targets),
            "succeeded": successes,
            "failed": failures,
            "targets": targets,
        }


def _default_sender(url: str, payload: dict[str, Any], timeout_s: float) -> requests.Response:
    return requests.post(url, json=payload, timeout=timeout_s)
