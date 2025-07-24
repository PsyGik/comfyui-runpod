#!/bin/bash

# Local testing script for ComfyUI RunPod container

set -e

echo "🧪 ComfyUI RunPod Local Testing"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

# Create test data directory
print_status "Creating test data directory..."
mkdir -p ./test-data/models/{checkpoints,loras,vae,embeddings,controlnet,clip,unet,upscale_models}
mkdir -p ./test-data/{input,output,custom_nodes}

# Create some test files
echo "Test checkpoint model" > ./test-data/models/checkpoints/test-model.ckpt
echo "Test LoRA model" > ./test-data/models/loras/test-lora.safetensors
echo "Test VAE model" > ./test-data/models/vae/test-vae.pt
echo "Test input image" > ./test-data/input/test-image.png

print_success "Test data directory created"

# Build the Docker image
print_status "Building Docker image..."
if docker build -t comfyui-runpod-test .; then
    print_success "Docker image built successfully"
else
    print_error "Failed to build Docker image"
    exit 1
fi

# Stop any existing containers
print_status "Stopping any existing containers..."
docker stop comfyui-test 2>/dev/null || true
docker rm comfyui-test 2>/dev/null || true

# Run the container
print_status "Starting container..."
docker run -d \
    --name comfyui-test \
    -p 8188:8188 \
    -p 8189:8189 \
    -v "$(pwd)/test-data:/workspace/comfyui-data" \
    -e RUNPOD_VOLUME_PATH=/workspace \
    comfyui-runpod-test

if [ $? -eq 0 ]; then
    print_success "Container started successfully"
else
    print_error "Failed to start container"
    exit 1
fi

# Wait for services to start
print_status "Waiting for services to start..."
sleep 10

# Check if services are running
print_status "Checking service status..."

# Check ComfyUI
if curl -s http://localhost:8188 > /dev/null; then
    print_success "ComfyUI is running at http://localhost:8188"
else
    print_warning "ComfyUI may not be ready yet. Check logs with: docker logs comfyui-test"
fi

# Check File Manager
if curl -s http://localhost:8189 > /dev/null; then
    print_success "File Manager is running at http://localhost:8189"
else
    print_warning "File Manager may not be ready yet. Check logs with: docker logs comfyui-test"
fi

# Show container logs
print_status "Container logs:"
docker logs comfyui-test --tail 20

echo ""
print_success "Testing complete!"
echo ""
echo "🌐 Access points:"
echo "   ComfyUI:      http://localhost:8188"
echo "   File Manager: http://localhost:8189"
echo ""
echo "📊 Useful commands:"
echo "   View logs:    docker logs comfyui-test -f"
echo "   Stop test:    docker stop comfyui-test"
echo "   Cleanup:      docker rm comfyui-test"
echo "   Shell access: docker exec -it comfyui-test /bin/bash"
echo ""
