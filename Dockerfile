# Use a Runpod base image with PyTorch and CUDA pre-installed
FROM nvidia/cuda:12.8.1-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV COMFYUI_PORT=8188
ENV APP_DIR=/app
ENV RUNPOD_VOLUME_PATH=/storage/persistent

# Set working directory
WORKDIR ${APP_DIR}

# Install system dependencies, including Python, git, aria2 and OpenGL libraries
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    aria2 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone the latest ComfyUI repository
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

# Install latest stable PyTorch with CUDA 12.1+ support for RTX 5090
# Using nightly builds which include support for newer GPU architectures
RUN python3 -m pip install --default-timeout=100 --no-cache-dir \
    --pre torch torchvision torchaudio \
    --index-url https://download.pytorch.org/whl/nightly/cu128

# Install Python dependencies for ComfyUI (excluding torch requirements)
RUN cd ComfyUI && \
    python3 -m pip install --default-timeout=100 --no-cache-dir \
    $(grep -v "^torch" requirements.txt | tr '\n' ' ') || \
    python3 -m pip install --default-timeout=100 --no-cache-dir \
    accelerate transformers safetensors aiohttp pyyaml Pillow scipy tqdm psutil einops spandrel kornia

# Copy and install additional dependencies for custom nodes
COPY custom-nodes-requirements.txt /app/custom-nodes-requirements.txt
RUN python3 -m pip install --default-timeout=100 --no-cache-dir -r /app/custom-nodes-requirements.txt

# Install additional dependencies for file manager
RUN python3 -m pip install --no-cache-dir requests aiohttp aiofiles

# Copy the file manager, installation script, and entrypoint script into the container
COPY file_manager.py /app/file_manager.py
COPY install_custom_node_deps.sh /app/install_custom_node_deps.sh
COPY update_pytorch_rtx5090.sh /app/update_pytorch_rtx5090.sh
COPY quick_fix_einops.sh /app/quick_fix_einops.sh
COPY test_cuda.py /app/test_cuda.py
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh /app/install_custom_node_deps.sh /app/update_pytorch_rtx5090.sh /app/quick_fix_einops.sh

# Expose the ports ComfyUI and File Manager will run on
EXPOSE ${COMFYUI_PORT}
EXPOSE 8189

# Set the entrypoint script to run when the container starts
ENTRYPOINT ["/entrypoint.sh"]