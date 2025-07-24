#!/bin/bash

set -e

# Define paths - allow override via environment variable
PERSISTENT_STORAGE_PATH="${RUNPOD_VOLUME_PATH:-/storage}"
COMFYUI_DATA_PATH="${PERSISTENT_STORAGE_PATH}/comfyui-data"
COMFYUI_APP_DIR="/app/ComfyUI"

echo "Using persistent storage path: ${PERSISTENT_STORAGE_PATH}"

# Debug: Check what's actually mounted
echo "Checking available storage paths..."
df -h
echo "Contents of potential storage directories:"
ls -la /workspace 2>/dev/null || echo "/workspace not found"
ls -la /runpod-volume 2>/dev/null || echo "/runpod-volume not found"
ls -la /storage 2>/dev/null || echo "/storage not found"

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

# Start File Manager in background
echo "Starting File Manager on port 8189..."
python3 /app/file_manager.py 8189 "${COMFYUI_DATA_PATH}" &

# Start ComfyUI
echo "Starting ComfyUI..."
exec python3 main.py --listen 0.0.0.0 --port 8188