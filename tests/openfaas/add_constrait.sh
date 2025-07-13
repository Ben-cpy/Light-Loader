# #!/bin/bash

# # List of files to exclude from modification
# exclude_files=()

# # Find all yml files in the current directory
# for yml_file in *.yml; do
#     # Skip if file is in exclude list
#     skip=false
#     for exclude in "${exclude_files[@]}"; do
#         if [[ "$yml_file" == "$exclude" ]]; then
#             skip=true
#             break
#         fi
#     done

#     if [ "$skip" == true ]; then
#         echo "Skipping $yml_file"
#         continue
#     fi

#     # Check if file exists and is regular file
#     if [ -f "$yml_file" ]; then
#         echo "Processing $yml_file"
        
#         # Remove any trailing empty lines first
#         sed -i -e :a -e '/^\n*$/{$d;N;ba' -e '}' "$yml_file"
#         # Add the performance constraint with proper indentation
#         echo "    constraints:" >> "$yml_file"
#         echo "    - \"performance=high\"" >> "$yml_file"
        
#         echo "Added constraints to $yml_file"
#     fi
# done

# echo "All files processed successfully"