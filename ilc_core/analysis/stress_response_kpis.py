# SPDX-License-Identifier: AGPL-3.0-only
from dataclasses import dataclass
from typing import Dict, Iterable

from ilc_core.analysis.agent_profiles import AgentProfile
from ilc_core.analysis.problem_space_kpis import TaskRowLike

def bucket_stress_level(
    total_stress: float,
    low_threshold: float = 0.5,
    high_threshold: float = 1.5,
) -> str:
    """
    Bucket a scalar stress value into 'low', 'medium', or 'high'.

    This is a toy heuristic used for sim-only stress response analysis.
    """
    if total_stress < low_threshold:
        return "low"
    elif total_stress < high_threshold:
        return "medium"
    else:
        return "high"

@dataclass
class AgentStressResponseRow:
    agent_id: str
    low_tasks: int = 0
    low_successes: int = 0
    high_tasks: int = 0
    high_successes: int = 0

    @property
    def low_success_rate(self) -> float:
        return self.low_successes / self.low_tasks if self.low_tasks > 0 else 0.0

    @property
    def high_success_rate(self) -> float:
        return self.high_successes / self.high_tasks if self.high_tasks > 0 else 0.0

    @property
    def preference(self) -> str:
        """
        Very simple qualitative classification:

          - 'prefers_high'  if high_success_rate > low_success_rate by a margin
          - 'prefers_low'   if low_success_rate > high_success_rate by a margin
          - 'neutral'       otherwise
        """
        margin = 0.1
        if self.high_success_rate - self.low_success_rate > margin:
            return "prefers_high"
        if self.low_success_rate - self.high_success_rate > margin:
            return "prefers_low"
        return "neutral"

def compute_agent_stress_response(
    samples: Iterable[TaskRowLike],
) -> Dict[str, AgentStressResponseRow]:
    """
    Aggregate stress response metrics per agent from a sequence of samples.

    Each sample is expected to provide:
      - 'agent_id': str
      - 'stress': float   (total stress at the time of the task)
      - optional 'success': truthy/falsey
      - optional 'reward': numeric, used as fallback success signal (reward > 0)

    We focus only on 'low' and 'high' buckets for this toy MVP.
    """
    result: Dict[str, AgentStressResponseRow] = {}

    for row in samples:
        agent_id = str(row.get("agent_id", "unknown"))
        stress_raw = row.get("stress", 0.0)
        try:
            stress_val = float(stress_raw)
        except (TypeError, ValueError):
            stress_val = 0.0

        bucket = bucket_stress_level(stress_val)

        # interpret success
        success_flag = row.get("success")
        if success_flag is None:
            reward_raw = row.get("reward", 0.0)
            try:
                reward = float(reward_raw)
            except (TypeError, ValueError):
                reward = 0.0
            success_flag = reward > 0.0

        resp = result.get(agent_id)
        if resp is None:
            resp = AgentStressResponseRow(agent_id=agent_id)
            result[agent_id] = resp

        if bucket == "low":
            resp.low_tasks += 1
            if bool(success_flag):
                resp.low_successes += 1
        elif bucket == "high":
            resp.high_tasks += 1
            if bool(success_flag):
                resp.high_successes += 1
        else:
            # 'medium' stress is ignored in this minimal MVP aggregation,
            # but could be added later if useful.
            pass

    return result

def attach_stress_response_to_profiles(
    profiles: Dict[str, AgentProfile],
    stress_response: Dict[str, AgentStressResponseRow],
) -> Dict[str, AgentProfile]:
    """
    Attach stress-response summaries to AgentProfile objects.

    If an agent_id is not in profiles, create a shell AgentProfile for it.
    """
    for agent_id, row in stress_response.items():
        profile = profiles.get(agent_id)
        if profile is None:
            profile = AgentProfile(agent_id=agent_id)
            profiles[agent_id] = profile

        profile.stress_response = {
            "low_tasks": row.low_tasks,
            "low_successes": row.low_successes,
            "low_success_rate": row.low_success_rate,
            "high_tasks": row.high_tasks,
            "high_successes": row.high_successes,
            "high_success_rate": row.high_success_rate,
            "preference": row.preference,
        }

    return profiles
