#!/bin/bash
# quick_fix_einops.sh
# Quick fix script for missing einops dependency

echo "🔧 Quick fix for missing 'einops' dependency..."

# Install einops
echo "Installing einops..."
pip install einops

# Verify installation
echo "Verifying einops installation..."
python3 -c "
try:
    import einops
    print(f'✅ einops successfully installed: {einops.__version__}')
    
    # Test basic functionality
    from einops import rearrange
    import torch
    x = torch.randn(2, 3, 4)
    y = rearrange(x, 'a b c -> b a c')
    print('✅ einops functionality working correctly')
    
except ImportError as e:
    print(f'❌ Failed to import einops: {e}')
    exit(1)
except Exception as e:
    print(f'⚠️  einops imported but functionality test failed: {e}')
"

echo "🎉 einops quick fix completed!"
echo "You can now restart ComfyUI."
