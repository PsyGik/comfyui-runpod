#!/usr/bin/env python3
"""
CUDA Compatibility Test for ComfyUI
Tests if your GPU and PyTorch setup is working correctly
"""

import sys
import subprocess

def run_test():
    print("🔍 ComfyUI CUDA Compatibility Test")
    print("=" * 50)
    
    # Test 1: Check if torch is installed
    try:
        import torch
        print(f"✅ PyTorch installed: {torch.__version__}")
    except ImportError:
        print("❌ PyTorch not installed!")
        return False
    
    # Test 2: Check CUDA availability
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        print(f"✅ CUDA available: {torch.version.cuda}")
    else:
        print("❌ CUDA not available")
        return False
    
    # Test 3: Check GPU information
    try:
        gpu_count = torch.cuda.device_count()
        print(f"✅ GPU count: {gpu_count}")
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            compute_cap = torch.cuda.get_device_capability(i)
            memory = torch.cuda.get_device_properties(i).total_memory / 1024**3
            
            print(f"   GPU {i}: {gpu_name}")
            print(f"   Compute capability: {compute_cap[0]}.{compute_cap[1]}")
            print(f"   Memory: {memory:.1f} GB")
            
            # Check for RTX 5090 specifically
            if compute_cap[0] >= 12:
                print(f"   🎯 High-end GPU detected (sm_{compute_cap[0]}{compute_cap[1]})")
                if compute_cap == (12, 0):
                    print("   📝 RTX 5090 detected - ensure you're using PyTorch nightly")
                
    except Exception as e:
        print(f"❌ Error getting GPU info: {e}")
        return False
    
    # Test 4: Basic CUDA operation
    try:
        print("🧪 Testing basic CUDA operations...")
        device = torch.device('cuda:0')
        
        # Simple tensor operations
        x = torch.randn(100, 100, device=device)
        y = torch.randn(100, 100, device=device)
        z = torch.mm(x, y)
        
        print("✅ Basic CUDA operations working")
        
        # Test autocast (mixed precision)
        with torch.autocast(device_type='cuda'):
            z_mixed = torch.mm(x, y)
        print("✅ Mixed precision (autocast) working")
        
    except Exception as e:
        print(f"❌ CUDA operations failed: {e}")
        print("💡 Try running: /app/update_pytorch_rtx5090.sh")
        return False
    
    # Test 5: Memory allocation
    try:
        print("🧪 Testing GPU memory allocation...")
        # Try to allocate 1GB
        large_tensor = torch.randn(1024, 1024, 128, device=device)
        del large_tensor
        torch.cuda.empty_cache()
        print("✅ GPU memory allocation working")
        
    except Exception as e:
        print(f"⚠️  GPU memory test failed: {e}")
        print("   This might be due to insufficient GPU memory")
    
    print("\n🎉 CUDA compatibility test completed successfully!")
    print("ComfyUI should work with GPU acceleration.")
    return True

def show_fixes():
    print("\n🔧 If tests failed, try these fixes:")
    print("1. Rebuild container with latest Dockerfile")
    print("2. Run: /app/update_pytorch_rtx5090.sh")
    print("3. Use CPU mode: python main.py --cpu")
    print("4. Check host CUDA drivers")

if __name__ == "__main__":
    success = run_test()
    if not success:
        show_fixes()
        sys.exit(1)
