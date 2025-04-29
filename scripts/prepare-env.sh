#!/bin/bash

# Check if global env file exists
if [ ! -f ../.global.env ]; then
    echo "Error: ../.global.env not found"
    exit 1
fi

# Get the project directory from argument
PROJECT_DIR=$1
if [ -z "$PROJECT_DIR" ]; then
    echo "Error: Project directory not provided"
    exit 1
fi

# Define the env files
GLOBAL_ENV="../.global.env"
PROJECT_ENV="../$PROJECT_DIR/.${PROJECT_DIR}.env"
PROJECT_ENV_EXAMPLE="../$PROJECT_DIR/.${PROJECT_DIR}.env.example"

# Create temporary files
TMP_FILE=$(mktemp)
TMP_GLOBAL=$(mktemp)
TMP_PROJECT=$(mktemp)

# First add the project-specific variables (excluding include line)
if [ -f "$PROJECT_ENV_EXAMPLE" ]; then
    grep -v "^include" "$PROJECT_ENV_EXAMPLE" > "$TMP_PROJECT"
else
    touch "$TMP_PROJECT"
fi

# Get list of project variable names (excluding comments and empty lines)
PROJECT_VARS=$(grep -v '^#' "$TMP_PROJECT" | grep -v '^$' | cut -d'=' -f1)

# Process global variables, excluding those already in project
while IFS= read -r line; do
    # Skip comments and empty lines
    if [[ "$line" =~ ^#.*$ ]] || [[ -z "$line" ]]; then
        echo "$line" >> "$TMP_GLOBAL"
        continue
    fi
    
    # Get variable name
    VAR_NAME=$(echo "$line" | cut -d'=' -f1)
    
    # Only add if not in project variables
    if ! echo "$PROJECT_VARS" | grep -q "^$VAR_NAME$"; then
        echo "$line" >> "$TMP_GLOBAL"
    fi
done < "$GLOBAL_ENV"

# Combine files with newline
cat "$TMP_PROJECT" > "$TMP_FILE"
echo "" >> "$TMP_FILE"
cat "$TMP_GLOBAL" >> "$TMP_FILE"

# Move the temporary file to the project env file
mv "$TMP_FILE" "$PROJECT_ENV"

# Clean up
rm -f "$TMP_GLOBAL" "$TMP_PROJECT"

echo "Prepared environment file for $PROJECT_DIR" 