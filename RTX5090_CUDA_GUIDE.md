# RTX 5090 CUDA Compatibility Guide

This document addresses CUDA compatibility issues with the RTX 5090 and other high-end GPUs.

## The Problem

The RTX 5090 uses CUDA compute capability `sm_120`, which is newer than what most stable PyTorch releases support. This results in the error:

```
RuntimeError: CUDA error: no kernel image is available for execution on the device
```

## Root Cause

- RTX 5090 has compute capability `sm_120`
- Most stable PyTorch releases only support up to `sm_90`
- PyTorch needs to be compiled with kernels for your specific GPU architecture

## Solutions Implemented

### 1. Updated Dockerfile
- Changed base image to use CUDA 12.8.1 runtime
- Install PyTorch nightly builds with extended GPU support
- Use CUDA 12.4 wheel index for compatibility

### 2. Runtime Detection
- Added CUDA compatibility check in entrypoint script
- Displays GPU information and PyTorch compatibility
- Attempts basic CUDA operations to verify functionality

### 3. Update Script
- Created `update_pytorch_rtx5090.sh` for manual PyTorch updates
- Can be run inside the container if issues persist
- Installs latest nightly builds with RTX 5090 support

## Quick Fixes

### Option 1: Rebuild Container (Recommended)
```bash
docker build -t comfyui-runpod .
```
The updated Dockerfile should automatically install compatible PyTorch.

### Option 2: Update PyTorch at Runtime
```bash
# Inside the container
/app/update_pytorch_rtx5090.sh
```

### Option 3: CPU Fallback
If CUDA issues persist, you can run ComfyUI in CPU mode:
```bash
python3 main.py --listen 0.0.0.0 --port 8188 --cpu
```

## Verification

After applying fixes, verify CUDA is working:

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Compute capability: {torch.cuda.get_device_capability(0)}")
    
    # Test CUDA operation
    x = torch.randn(2, 2).cuda()
    y = x @ x
    print("✅ CUDA working!")
```

## Technical Details

### RTX 5090 Specifications
- Architecture: Ada Lovelace
- Compute Capability: 12.0 (sm_120)
- CUDA Cores: 21,760
- Memory: 32GB GDDR7

### PyTorch Requirements
- PyTorch 2.4+ nightly builds
- CUDA 12.4+ toolkit
- Proper compute capability support

### Alternative GPUs
This solution also helps with other high-end GPUs:
- RTX 4090 (sm_89)
- RTX 4080 (sm_89)
- H100 (sm_90)
- A100 (sm_80)

## Troubleshooting

### Issue: Still getting CUDA errors after rebuild
**Solution:** 
1. Check if you're using the latest container image
2. Try the manual PyTorch update script
3. Verify CUDA driver version on the host

### Issue: Performance is slow
**Possible causes:**
- Using CPU fallback mode
- Incompatible CUDA version
- Memory constraints

### Issue: Container won't start
**Check:**
1. Host CUDA driver compatibility
2. Container runtime CUDA support
3. GPU access permissions

## Performance Notes

With proper CUDA support, RTX 5090 should provide:
- 2-3x faster than RTX 4090
- Excellent performance for large models
- 32GB VRAM for high-resolution generation

## Future Considerations

- Monitor PyTorch stable releases for sm_120 support
- Consider using NVIDIA's official PyTorch containers
- Keep CUDA drivers updated on the host system
