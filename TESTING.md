# Local Testing Guide for ComfyUI RunPod

This guide shows you how to test your ComfyUI RunPod setup locally before deploying.

## 🚀 Quick Start

### Method 1: File Manager Only (Fastest)
```bash
# 1. Setup
python3 -m venv venv
source venv/bin/activate
pip install requests

# 2. Create test data
mkdir -p test-data/models/{checkpoints,loras,vae}
echo "Test model" > test-data/models/checkpoints/test.ckpt

# 3. Run file manager
python3 file_manager.py 8189 "$(pwd)/test-data"

# 4. Open browser
open http://localhost:8189
```

### Method 2: Full Docker Container
```bash
# Run the automated test script
./test-local.sh
```

### Method 3: API Testing
```bash
# With file manager running:
source venv/bin/activate
python3 test-api.py
```

## 🧪 Detailed Testing Steps

### 1. File Manager Features to Test

#### Download Functionality:
- [ ] UI loads at http://localhost:8189
- [ ] Folder dropdown populates with model types
- [ ] Can enter download URLs
- [ ] Download validation works (try empty URL)
- [ ] Test with a small file download

#### File Management:
- [ ] Browse tab shows directory structure
- [ ] Can navigate through folders
- [ ] Can create new folders
- [ ] Can delete files/folders (test with caution!)
- [ ] File sizes display correctly

#### Downloads Tab:
- [ ] Shows download progress
- [ ] Updates in real-time
- [ ] Shows completed downloads
- [ ] Error handling works

### 2. Test URLs for Downloads

**Safe test downloads (small files):**
```
https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/README.md
https://github.com/comfyanonymous/ComfyUI/archive/refs/heads/master.zip
```

**HuggingFace test (small model):**
```
https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/model_index.json
```

### 3. Docker Testing

The `test-local.sh` script will:
1. ✅ Build the Docker image
2. ✅ Create test data
3. ✅ Run the container with proper port mapping
4. ✅ Test both services
5. ✅ Show logs and access URLs

### 4. Common Issues & Solutions

#### Port Already in Use:
```bash
# Kill processes using the ports
lsof -ti:8188 | xargs kill -9
lsof -ti:8189 | xargs kill -9
```

#### Docker Build Issues:
```bash
# Clean Docker cache
docker system prune -f
docker build --no-cache -t comfyui-runpod-test .
```

#### Permission Issues:
```bash
# Fix test data permissions
chmod -R 755 test-data/
```

### 5. Manual Testing Checklist

#### UI Tests:
- [ ] Dark theme loads correctly
- [ ] Tabs switch properly
- [ ] Forms submit without errors
- [ ] Progress bars animate
- [ ] File browser navigation works

#### API Tests:
- [ ] GET /api/folders returns model folders
- [ ] GET /api/files/ returns directory contents
- [ ] POST /api/download starts downloads
- [ ] GET /api/downloads shows progress

#### Integration Tests:
- [ ] File manager can create folders
- [ ] Downloads save to correct directories
- [ ] Files persist between restarts
- [ ] Error messages display properly

### 6. Performance Testing

```bash
# Test with multiple concurrent downloads
curl -X POST http://localhost:8189/api/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/file1.zip","folder":"models/checkpoints"}'

curl -X POST http://localhost:8189/api/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/file2.zip","folder":"models/loras"}'
```

### 7. Clean Up After Testing

```bash
# Stop file manager
pkill -f file_manager.py

# Stop Docker container
docker stop comfyui-test
docker rm comfyui-test

# Remove test data
rm -rf test-data/

# Deactivate virtual environment
deactivate
```

## 🔧 Debugging Tips

### Check Logs:
```bash
# File manager logs (if running in terminal)
# Docker logs
docker logs comfyui-test -f

# API response testing
curl -v http://localhost:8189/api/folders
```

### Test File Structure:
```bash
# Verify test data structure
tree test-data/

# Check permissions
ls -la test-data/
```

### Network Testing:
```bash
# Test if ports are accessible
nc -zv localhost 8189
nc -zv localhost 8188

# Test from different terminal
curl http://localhost:8189
```

## 🎯 Before Deploying

### Final Checklist:
- [ ] All API endpoints respond correctly
- [ ] File operations work (create, move, delete)
- [ ] Downloads complete successfully
- [ ] UI is responsive and functional
- [ ] No errors in logs
- [ ] Docker image builds without issues
- [ ] Container starts and runs services

### Ready to Deploy!
Once all tests pass, your container is ready for RunPod deployment.
