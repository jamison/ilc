#!/bin/bash
# monitor_phases.sh
# Monitors docs/antigravity_tasks/ for new phase files and prompts the user.

TASK_DIR="docs/antigravity_tasks"
check_interval=5

echo "Monitoring $TASK_DIR for new phase files..."
echo "Press Ctrl+C to stop."

# Initial snapshot
initial_files=$(ls "$TASK_DIR")

while true; do
  current_files=$(ls "$TASK_DIR")
  new_files=$(comm -13 <(echo "$initial_files") <(echo "$current_files"))

  if [ -n "$new_files" ]; then
    echo "---------------------------------------------------"
    echo "New phase file(s) detected:"
    echo "$new_files"
    echo "---------------------------------------------------"
    echo "To execute, return to the Agent and run:"
    echo "/run-next-phase"
    echo "---------------------------------------------------"
    
    # Update snapshot
    initial_files="$current_files"
    
    # Optional: Bell sound
    echo -e "\a"
  fi
  
  sleep "$check_interval"
done
