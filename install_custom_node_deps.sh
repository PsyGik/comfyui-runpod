#!/bin/bash
# install_custom_node_deps.sh
# Script to install missing dependencies for ComfyUI custom nodes

echo "Installing additional dependencies for ComfyUI custom nodes..."

# Update package list
apt-get update

# Install system dependencies
echo "Installing system dependencies..."
apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    || echo "Some system packages may already be installed"

# Install Python dependencies
echo "Installing Python dependencies..."
pip install \
    einops \
    opencv-python-headless \
    matplotlib \
    diffusers \
    timm \
    blend-modes \
    facexlib \
    piexif \
    simpleeval \
    watchdog \
    pyOpenSSL \
    scipy \
    scikit-image \
    imageio \
    imageio-ffmpeg \
    deepdiff \
    volcengine \
    replicate \
    segment_anything \
    || echo "Some Python packages may already be installed"

echo "Custom node dependencies installation completed!"
echo "You may need to restart ComfyUI for changes to take effect."
