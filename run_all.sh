#!/bin/bash

# Array of Python scripts to run for HTML-based cricket data processing
scripts=(
    "generateCommentry.py"
    "getCommentaryHTML.py"
    "getScoreHTML.py"
    "commentary_data_processor.py"
    "score_data_processor.py"
    "playCommentaryFiles.py"
)

# Use the virtual environment Python
PYTHON_CMD="./crickScore_venv/bin/python"

echo "Starting all HTML-based cricket data processing scripts..."
echo "Using Python: $PYTHON_CMD"

for script in "${scripts[@]}"; do
  if [ -f "$script" ]; then
    $PYTHON_CMD "$script" &
    echo "Started $script"
    sleep 1  # Small delay between starts
  else
    echo "Warning: $script not found"
  fi
done

echo "All scripts started in background."
echo "Use 'ps aux | grep python' to see running processes"
echo "Use 'pkill -f python' to stop all scripts"

#chmod +x run_all.sh
#./run_all.sh