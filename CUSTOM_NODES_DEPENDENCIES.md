# Custom Nodes Dependencies Guide

This document outlines the dependency issues found with ComfyUI custom nodes and their solutions.

## Issues Identified

Based on the logs analysis, the following custom nodes and core ComfyUI components were failing to load due to missing dependencies:

### Core ComfyUI Dependencies
**Missing dependencies that prevent ComfyUI from starting:**
- `einops` - for tensor operations and rearrangement
- `spandrel` - for super-resolution models
- `kornia` - for computer vision operations

### 1. ComfyUI-Inference-Core-Nodes
**Missing dependencies:**
- `cv2` (OpenCV) - for image processing
- `matplotlib` - for pose detection visualization
- `diffusers` - for layer diffusion functionality

### 2. ComfyUI-KJNodes
**Missing dependencies:**
- `cv2` (OpenCV) - for mask and image operations

### 3. comfyui-mixlab-nodes
**Missing dependencies:**
- `matplotlib` - for data visualization

### 4. ComfyUI-BiRefNet-ZHO
**Missing dependencies:**
- `timm` - for PyTorch image models

### 5. ComfyUI_LayerStyle
**Missing dependencies:**
- `blend_modes` - for image blending operations

### 6. CharacterFaceSwap
**Missing dependencies:**
- `facexlib` - for face detection and manipulation

### 7. ComfyUI-Impact-Pack
**Missing dependencies:**
- `piexif` - for EXIF data handling

### 8. comfyui-jakeupgrade
**Missing dependencies:**
- `simpleeval` - for safe expression evaluation

### 9. System Dependencies
**Missing system libraries:**
- `libGL.so.1` - OpenGL library for GPU-accelerated operations
- Various supporting libraries for OpenCV

## Solutions Implemented

### 1. Updated Dockerfile
Added missing system dependencies:
```dockerfile
libgl1-mesa-glx \
libglib2.0-0 \
libsm6 \
libxext6 \
libxrender-dev \
libgomp1
```

### 2. Created Custom Nodes Requirements File
Created `custom-nodes-requirements.txt` with all necessary Python dependencies.

### 3. Updated Build Process
Modified the Dockerfile to install custom node dependencies during the build process.

## Usage

The custom nodes should now load correctly when the container is rebuilt with the updated Dockerfile.

## Troubleshooting

If you encounter additional custom node dependency issues:

1. Check the logs for `ModuleNotFoundError` messages
2. Add the missing Python package to `custom-nodes-requirements.txt`
3. For system dependencies, add them to the apt-get install section in the Dockerfile
4. Rebuild the container

## Future Considerations

- Consider using a requirements.txt file specific to each custom node
- Implement dynamic dependency installation based on installed custom nodes
- Add version pinning for better reproducibility
