#!/bin/bash

for file in *.py; do
  if [ -f "$file" ]; then
    python3.11 "$file" &
    echo "Started $file"
  fi
done

echo "All scripts started in background."
#chmod +x run_all.sh
#./run_all.sh