#!/bin/bash

set -e

# Define paths
PERSISTENT_STORAGE_PATH="/storage/persistent"
COMFYUI_DATA_PATH="${PERSISTENT_STORAGE_PATH}/comfyui-data"
COMFYUI_APP_DIR="/app/ComfyUI"

# Create persistent directories for ComfyUI data if they don't exist
mkdir -p "${COMFYUI_DATA_PATH}/models"
mkdir -p "${COMFYUI_DATA_PATH}/input"
mkdir -p "${COMFYUI_DATA_PATH}/output"
mkdir -p "${COMFYUI_DATA_PATH}/custom_nodes"

# Navigate to the ComfyUI installation directory
cd "${COMFYUI_APP_DIR}"

# Remove the default directories and create symbolic links to the persistent storage.
# This ensures that any data written to these folders is saved on the network volume.
echo "Creating symbolic links to persistent storage..."
rm -rf models input output custom_nodes
ln -sfn "${COMFYUI_DATA_PATH}/models" models
ln -sfn "${COMFYUI_DATA_PATH}/input" input
ln -sfn "${COMFYUI_DATA_PATH}/output" output
ln -sfn "${COMFYUI_DATA_PATH}/custom_nodes" custom_nodes

echo "Symbolic links created:"
ls -l "${COMFYUI_APP_DIR}"

# Start ComfyUI
echo "Starting ComfyUI..."
exec python3 main.py --listen 0.0.0.0 --port 8188