#!/bin/bash

# Iterate through all subdirectories in current directory
for dir in */; do
  dir_name=$(basename "$dir")

  # Exclude specified directories
  if [[ "$dir_name" == "info" || "$dir_name" == "_yaml" || "$dir_name" == "__pycache__" || "$dir_name" == "template" ]]; then
    continue
  fi

  # Enter subdirectory
  cd "$dir"

  # Remove .log files and call_graph.json files
  rm -f *.log call_graph.json

  # Return to parent directory
  cd ..

  # Rename directory
  new_dir_name="ori-$dir_name"
  mv "$dir_name" "$new_dir_name"

  # Modify corresponding .yml file
  yml_file="$dir_name.yml"
  if [ -f "$yml_file" ]; then
    sed -i "6s#$dir_name:#ori-$dir_name:#" "$yml_file"  # Modify line 6
    sed -i "8s#./#./ori-#" "$yml_file"
    sed -i "9s#localhost:5000/#localhost:5000/ori-#" "$yml_file"

    # Rename .yml file
    new_yml_file="ori-$yml_file"
    mv "$yml_file" "$new_yml_file"
  fi
done