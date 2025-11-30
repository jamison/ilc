import json
from importlib.resources import files

def load_epistemic_work_task_schema() -> dict:
    """
    Load the canonical EpistemicWorkTask JSON schema from
    epistemic_work_task_schema_v1.json and return it as a dict.
    """
    # Adjust path to point to project root from ilc_core/genesis
    # Using files() API to locate the resource relative to the package
    # Assuming epistemic_work_task_schema_v1.json is in the project root,
    # which is 2 levels up from ilc_core/genesis.
    # However, importlib.resources works best with package data.
    # If the file is not in a package, we might need a different approach or ensure it's packaged.
    # For MVP, we'll assume it's accessible via relative path from the module location
    # or try to find it in the project root if running from there.
    
    # Alternative: use absolute path based on __file__ if importlib is tricky with root files
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    schema_path = os.path.join(base_dir, "epistemic_work_task_schema_v1.json")
    
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)
