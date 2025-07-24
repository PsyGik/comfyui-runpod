# ComfyUI RunPod

A Docker container for running ComfyUI on RunPod with persistent storage and an integrated file manager.

## Features

- 🎨 **ComfyUI** - Latest version with full GPU support
- 🚀 **RTX 5090 Support** - Optimized PyTorch installation for latest GPUs
- 💾 **Persistent Storage** - Models and data persist between pod restarts
- 📁 **File Manager** - Web-based UI for downloading and managing models
- ⬇️ **Smart Downloads** - Support for HuggingFace, CivitAI, and direct links
- 🔄 **Progress Tracking** - Real-time download progress monitoring

## Quick Start

1. Create a new RunPod pod using this container
2. Access ComfyUI at `http://your-pod-ip:8188`
3. Access File Manager at `http://your-pod-ip:8189`

## File Manager Features

### Download Models
- **Multiple Sources**: Support for HuggingFace, CivitAI, and any direct download links
- **Smart Organization**: Choose specific folders (checkpoints, LoRA, VAE, etc.)
- **Progress Tracking**: Real-time download progress with visual indicators
- **Custom Naming**: Optional custom filenames for downloads

### File Management
- **Browse Files**: Navigate through your model directories
- **Move Files**: Reorganize models with drag-and-drop interface
- **Delete Files**: Remove unwanted models and files
- **Create Folders**: Organize your collection with custom folders

### Supported Model Types
- Checkpoints (`models/checkpoints`)
- LoRA models (`models/loras`)
- VAE models (`models/vae`)
- Embeddings (`models/embeddings`)
- ControlNet (`models/controlnet`)
- CLIP models (`models/clip`)
- UNET models (`models/unet`)
- Upscaling models (`models/upscale_models`)

## Usage

### Accessing the File Manager

1. Open your browser to `http://your-pod-ip:8189`
2. Use the **Download** tab to add new models
3. Use the **Browse Files** tab to manage existing files
4. Use the **Downloads** tab to monitor progress

### Downloading Models

1. Copy the download URL (HuggingFace, CivitAI, or direct link)
2. Select the appropriate folder type
3. Optionally provide a custom filename
4. Click "Start Download"
5. Monitor progress in the Downloads tab

### Managing Files

- **Navigate**: Click on folders to browse
- **Move**: Use the Move button to relocate files
- **Delete**: Remove unwanted files with the Delete button
- **Create Folders**: Use the "New Folder" button to organize

## Persistent Storage

All your models, inputs, outputs, and custom nodes are automatically saved to persistent storage:

- `models/` - All model files organized by type
- `input/` - Input images and files
- `output/` - Generated images and outputs
- `custom_nodes/` - Installed custom nodes

## Environment Variables

- `COMFYUI_PORT` - Port for ComfyUI (default: 8188)
- `RUNPOD_VOLUME_PATH` - Path to persistent storage (default: /workspace)

## Troubleshooting

### Storage Issues
If your models don't persist between pod restarts:
1. Ensure you're using the same RunPod volume
2. Check that the volume is attached to your pod
3. Verify you're in the same region as your volume

### Download Issues
If downloads fail:
1. Check the URL is accessible
2. Ensure you have sufficient storage space
3. Try downloading smaller files first

### GPU Issues
For RTX 5090 or other new GPUs:
- The container includes the latest PyTorch with CUDA 12.4 support
- Ensure your pod has GPU access enabled

## Development

To build and run locally:

```bash
docker build -t comfyui-runpod .
docker run -p 8188:8188 -p 8189:8189 -v $(pwd)/data:/workspace comfyui-runpod
```

## Support

For issues and questions:
1. Check the RunPod logs for error messages
2. Verify your persistent storage is properly mounted
3. Ensure both ports 8188 and 8189 are accessible
