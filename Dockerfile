# Use a Runpod base image with PyTorch and CUDA pre-installed
FROM nvidia/cuda:12.8.1-runtime-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV COMFYUI_PORT=8188
ENV APP_DIR=/app

# Set working directory
WORKDIR ${APP_DIR}

# Install system dependencies, including Python, git and aria2 for faster downloads
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    aria2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone the latest ComfyUI repository
RUN git clone https://github.com/comfyanonymous/ComfyUI.git

# Install Python dependencies for ComfyUI
RUN cd ComfyUI && \
    python3 -m pip install --default-timeout=100 --no-cache-dir -r requirements.txt && \
    python3 -m pip install --default-timeout=100 --no-cache-dir xformers

# Copy the entrypoint script into the container and make it executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose the port ComfyUI will run on
EXPOSE ${COMFYUI_PORT}

# Set the entrypoint script to run when the container starts
ENTRYPOINT ["/entrypoint.sh"]