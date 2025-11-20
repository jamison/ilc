import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ilc_core.types import Node, Edge

def test_task_lineage():
    print("\n--- TEST: INTELLIGENT LABOR LINEAGE ---")
    
    # 1. Create the Task Node (The Work)
    task_payload = {
        "method": "matrix_inversion_v1",
        "inputs_hash": "a1b2c3...",
        "compute_cost_joules": 0.05
    }
    
    task_node = Node(
        id="",
        type="task",
        content=task_payload,
        agent_id="agent:worker:01",
        signature="sig_task"
    )
    task_node.id = task_node.compute_id()
    
    # 2. Create the Result Claim (The Truth)
    result_node = Node(
        id="",
        type="claim",
        content="Matrix Determinant = 0.0",
        agent_id="agent:worker:01",
        signature="sig_result"
    )
    result_node.id = result_node.compute_id()
    
    # 3. Link Result -> Task
    edge = Edge(
        source_id=result_node.id,
        target_id=task_node.id,
        type="derives_from"
    )
    
    print(f"Task ID: {task_node.id[:8]}")
    print(f"Claim ID: {result_node.id[:8]}")
    print(f"Link: Claim derives from Task? {edge.type == 'derives_from'}")
    
    assert task_node.type == "task"
    assert isinstance(task_node.content, dict)
    print("SUCCESS: Task primitive verified.")

if __name__ == "__main__":
    test_task_lineage()
