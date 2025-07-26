#!/bin/bash
# update_pytorch_rtx5090.sh
# Script to update PyTorch for RTX 5090 compatibility

echo "Updating PyTorch for RTX 5090 compatibility..."

# Check current GPU
echo "Current GPU information:"
nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader,nounits || echo "nvidia-smi not available"

# Check current PyTorch version and CUDA support
echo "Current PyTorch information:"
python3 -c "
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    try:
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        cap = torch.cuda.get_device_capability(0)
        print(f'GPU compute capability: {cap}')
        
        # Check if this is RTX 5090 with sm_120
        if cap[0] >= 12:
            print('Detected RTX 5090 or similar high-end GPU')
            print('This GPU requires PyTorch nightly build')
        
    except Exception as e:
        print(f'Error getting GPU info: {e}')
"

echo "Installing PyTorch nightly build with CUDA 12.4 support..."
pip uninstall -y torch torchvision torchaudio

# Install PyTorch nightly with CUDA 12.4 support
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu124

echo "PyTorch update completed!"

# Verify installation
echo "Verifying new PyTorch installation:"
python3 -c "
import torch
print(f'New PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
if torch.cuda.is_available():
    print(f'CUDA version: {torch.version.cuda}')
    try:
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        print(f'GPU compute capability: {torch.cuda.get_device_capability(0)}')
        
        # Test CUDA operation
        x = torch.randn(2, 2).cuda()
        y = x @ x
        print('✅ CUDA operations working correctly!')
        
    except Exception as e:
        print(f'❌ CUDA operation failed: {e}')
        print('You may need to restart the container or check your CUDA drivers')
"

echo "PyTorch update process completed!"
echo "If CUDA operations are still failing, you may need to:"
echo "1. Restart the container"
echo "2. Check CUDA driver compatibility"
echo "3. Use CPU mode as fallback: --cpu flag in ComfyUI"
