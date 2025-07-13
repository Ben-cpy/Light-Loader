#!/bin/bash

# Get the function name as an argument
FUNCTION_NAME=$1
USE_SLIM=${2:-false}  # Add USE_SLIM flag, default to false if not provided

if [ -z "$FUNCTION_NAME" ] ; then
  echo "Please provide the function name as an argument (e.g., ./deploy_openfaas.sh app3 [true|false])"
  exit 1
fi

# Create the function folder (if it doesn't exist)
mkdir -p "$FUNCTION_NAME"

# Define the log file path
LOG_FILE="$FUNCTION_NAME/a.log"

> "$LOG_FILE" # Clear the log file

if [ "$USE_SLIM" = "true" ]; then
    # Docker-slim workflow
    echo "Using docker-slim workflow..." | tee -a "$LOG_FILE"
    
    # Step 1: Execute faas build with --shrinkwrap
    echo "Step 1: Building the function with faas build..." | tee -a "$LOG_FILE"
    faas build -f ./$FUNCTION_NAME.yml --shrinkwrap | tee -a "$LOG_FILE"

    # Step 2: Build image folder path
    BUILD_DIR="./build/$FUNCTION_NAME"

    # Step 3: Use Docker to build a temporary image
    docker build -t fat-img:latest "$BUILD_DIR" | tee -a "$LOG_FILE"

    # Step 4: Use docker-slim to build a slimmed image
    echo "Step 4: Slimming down the image with docker-slim..." | tee -a "$LOG_FILE"
    docker-slim build fat-img:latest . | tee -a "$LOG_FILE"

    # Step 5: Rename the slimmed image
    echo "Step 5: Renaming the slimmed image..." | tee -a "$LOG_FILE"
    docker tag fat-img.slim:latest localhost:5000/$FUNCTION_NAME:latest | tee -a "$LOG_FILE"

    # Step 6: Push the image to the Docker registry
    echo "Step 6: Pushing the image to the registry..." | tee -a "$LOG_FILE"
    docker push localhost:5000/$FUNCTION_NAME:latest | tee -a "$LOG_FILE"

else
    # Regular OpenFaaS workflow
    echo "Using regular OpenFaaS workflow..." | tee -a "$LOG_FILE"
    
    # Step 1: Build the function
    echo "Step 1: Building the function..." | tee -a "$LOG_FILE"
    faas-cli build -f ./$FUNCTION_NAME.yml | tee -a "$LOG_FILE"

    # Step 2: Push to registry
    echo "Step 2: Pushing to registry..." | tee -a "$LOG_FILE"
    faas-cli push -f ./$FUNCTION_NAME.yml | tee -a "$LOG_FILE"
fi

# Step 7: Check if the function is already deployed, and wait if it is
echo "Step 7: Checking if function is already deployed..." | tee -a "$LOG_FILE"
while faas list | grep -q "^$FUNCTION_NAME\s"; do
  faas-cli rm $FUNCTION_NAME
  echo "$(date) - Function '$FUNCTION_NAME' is already deployed. Waiting..." | tee -a "$LOG_FILE"
  sleep 2
done

# Step 8: Deploy to OpenFaaS
echo "Step 8: Deploying the function to OpenFaaS..." | tee -a "$LOG_FILE"
faas deploy -f ./$FUNCTION_NAME.yml | tee -a "$LOG_FILE"

echo "Deployment complete!" | tee -a "$LOG_FILE"
