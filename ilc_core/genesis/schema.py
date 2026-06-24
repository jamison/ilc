# SPDX-License-Identifier: AGPL-3.0-only
import json
from importlib.resources import files

_SCHEMA_RESOURCE = "epistemic_work_task_schema_v1.json"


def load_epistemic_work_task_schema() -> dict:
    """
    Load the canonical EpistemicWorkTask JSON schema from
    epistemic_work_task_schema_v1.json and return it as a dict.
    """
    schema_text = files("ilc_core.genesis").joinpath(_SCHEMA_RESOURCE).read_text(
        encoding="utf-8"
    )
    return json.loads(schema_text)
