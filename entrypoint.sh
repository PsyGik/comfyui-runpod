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

# Check CUDA compatibility before starting ComfyUI
echo "Checking CUDA compatibility..."
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    print(f'GPU: {torch.cuda.get_device_name(0)}')
    print(f'GPU compute capability: {torch.cuda.get_device_capability(0)}')
    # Test a simple CUDA operation
    try:
        x = torch.randn(2, 2).cuda()
        y = x @ x
        print('CUDA operations working correctly')
    except Exception as e:
        print(f'CUDA operation failed: {e}')
        print('Will try to use CPU fallback')
" || echo "CUDA check failed, continuing with startup..."

# Start ComfyUI
echo "Starting ComfyUI..."

# Try to start with CUDA first, fallback to CPU if it fails
if python3 -c "import torch; torch.randn(1).cuda()" 2>/dev/null; then
    echo "CUDA is working, starting with GPU acceleration..."
    exec python3 main.py --listen 0.0.0.0 --port 8188
else
    echo "⚠️  CUDA not working properly, starting in CPU mode..."
    echo "For better performance, try running: /app/update_pytorch_rtx5090.sh"
    exec python3 main.py --listen 0.0.0.0 --port 8188 --cpu
fi