#!/usr/bin/env python3
"""
ComfyUI File Manager Server
A web-based file manager for downloading and managing ComfyUI models and files.
"""

import os
import json
from urllib.parse import urlparse
import shutil
from datetime import datetime
import hashlib
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import threading
import urllib.parse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileManagerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.base_path = kwargs.pop('base_path', '/workspace/comfyui-data')
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/':
            self.serve_ui()
        elif self.path == '/api/folders':
            self.api_get_folders()
        elif self.path.startswith('/api/files/'):
            self.api_get_files()
        elif self.path.startswith('/api/download-status/'):
            self.api_get_download_status()
        elif self.path == '/api/downloads':
            self.api_get_downloads()
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/api/download':
            self.api_download()
        elif self.path == '/api/move':
            self.api_move_file()
        elif self.path == '/api/delete':
            self.api_delete_file()
        elif self.path == '/api/create-folder':
            self.api_create_folder()
        else:
            self.send_error(404)
    
    def serve_ui(self):
        """Serve the main HTML interface"""
        html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ComfyUI File Manager</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            min-height: 100vh;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            color: #4CAF50;
            margin-bottom: 10px;
        }
        
        .tabs {
            display: flex;
            background: #2d2d2d;
            border-radius: 8px;
            margin-bottom: 20px;
            overflow: hidden;
        }
        
        .tab {
            flex: 1;
            padding: 15px;
            background: #2d2d2d;
            border: none;
            color: #ffffff;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .tab.active {
            background: #4CAF50;
        }
        
        .tab:hover {
            background: #3d3d3d;
        }
        
        .tab.active:hover {
            background: #45a049;
        }
        
        .tab-content {
            display: none;
            background: #2d2d2d;
            border-radius: 8px;
            padding: 20px;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #cccccc;
        }
        
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #444;
            border-radius: 4px;
            color: #ffffff;
            font-size: 14px;
        }
        
        .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
            outline: none;
            border-color: #4CAF50;
        }
        
        .btn {
            background: #4CAF50;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }
        
        .btn:hover {
            background: #45a049;
        }
        
        .btn:disabled {
            background: #666;
            cursor: not-allowed;
        }
        
        .btn-secondary {
            background: #666;
        }
        
        .btn-secondary:hover {
            background: #777;
        }
        
        .btn-danger {
            background: #f44336;
        }
        
        .btn-danger:hover {
            background: #da190b;
        }
        
        .progress-container {
            background: #1a1a1a;
            border-radius: 4px;
            margin: 10px 0;
            overflow: hidden;
        }
        
        .progress-bar {
            height: 20px;
            background: #4CAF50;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
        }
        
        .download-item {
            background: #1a1a1a;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            border-left: 4px solid #4CAF50;
        }
        
        .download-item.error {
            border-left-color: #f44336;
        }
        
        .download-item.completed {
            border-left-color: #2196F3;
        }
        
        .file-browser {
            display: grid;
            gap: 20px;
        }
        
        .breadcrumb {
            background: #1a1a1a;
            padding: 10px;
            border-radius: 4px;
            margin-bottom: 10px;
        }
        
        .breadcrumb a {
            color: #4CAF50;
            text-decoration: none;
            margin-right: 5px;
        }
        
        .breadcrumb a:hover {
            text-decoration: underline;
        }
        
        .file-list {
            background: #1a1a1a;
            border-radius: 4px;
            max-height: 400px;
            overflow-y: auto;
        }
        
        .file-item {
            display: flex;
            align-items: center;
            padding: 12px;
            border-bottom: 1px solid #333;
            transition: background 0.3s;
        }
        
        .file-item:hover {
            background: #333;
        }
        
        .file-item:last-child {
            border-bottom: none;
        }
        
        .file-icon {
            margin-right: 10px;
            width: 20px;
            text-align: center;
        }
        
        .file-name {
            flex: 1;
            cursor: pointer;
        }
        
        .file-name.clickable {
            color: #4CAF50;
        }
        
        .file-name.clickable:hover {
            text-decoration: underline;
        }
        
        .file-size {
            margin-right: 10px;
            color: #999;
            font-size: 12px;
        }
        
        .file-actions {
            display: flex;
            gap: 5px;
        }
        
        .file-actions button {
            padding: 5px 10px;
            font-size: 12px;
        }
        
        .error {
            color: #f44336;
            background: rgba(244, 67, 54, 0.1);
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        
        .success {
            color: #4CAF50;
            background: rgba(76, 175, 80, 0.1);
            padding: 10px;
            border-radius: 4px;
            margin: 10px 0;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #999;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎨 ComfyUI File Manager</h1>
            <p>Download and manage your AI models and files</p>
        </div>
        
        <div class="tabs">
            <button class="tab active" data-tab="download">📥 Download</button>
            <button class="tab" data-tab="browse">📁 Browse Files</button>
            <button class="tab" data-tab="downloads">⬇️ Downloads</button>
        </div>
        
        <!-- Download Tab -->
        <div id="download-tab" class="tab-content active">
            <div class="form-group">
                <label for="download-url">Download URL:</label>
                <input type="url" id="download-url" placeholder="https://huggingface.co/... or https://civitai.com/... or any direct download link">
            </div>
            
            <div class="form-group">
                <label for="download-folder">Save to Folder:</label>
                <select id="download-folder">
                    <option value="">Loading folders...</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="download-filename">Custom Filename (optional):</label>
                <input type="text" id="download-filename" placeholder="Leave empty to use original filename">
            </div>
            
            <button class="btn" id="start-download-btn">Start Download</button>
            
            <div id="download-status"></div>
        </div>
        
        <!-- Browse Files Tab -->
        <div id="browse-tab" class="tab-content">
            <div class="form-group">
                <button class="btn btn-secondary" id="create-folder-btn">📁 New Folder</button>
                <button class="btn btn-secondary" id="refresh-files-btn">🔄 Refresh</button>
            </div>
            
            <div class="breadcrumb" id="breadcrumb">
                <a href="#" data-path="">🏠 Home</a>
            </div>
            
            <div class="file-list" id="file-list">
                <div class="loading">Loading files...</div>
            </div>
        </div>
        
        <!-- Downloads Tab -->
        <div id="downloads-tab" class="tab-content">
            <div class="form-group">
                <button class="btn btn-secondary" id="refresh-downloads-btn">🔄 Refresh</button>
                <button class="btn btn-danger" id="clear-downloads-btn">🗑️ Clear Completed</button>
            </div>
            
            <div id="downloads-list">
                <div class="loading">Loading downloads...</div>
            </div>
        </div>
    </div>

    <script>
        let currentPath = '';
        let downloads = {};
        
        // Tab switching
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
            
            document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
            document.getElementById(`${tabName}-tab`).classList.add('active');
            
            if (tabName === 'browse') {
                loadFiles(currentPath);
            } else if (tabName === 'downloads') {
                loadDownloads();
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            // Set up tab event listeners
            document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', function() {
                    const tabName = this.getAttribute('data-tab');
                    showTab(tabName);
                });
            });
            
            // Set up button event listeners
            document.getElementById('start-download-btn').addEventListener('click', startDownload);
            document.getElementById('create-folder-btn').addEventListener('click', createFolder);
            document.getElementById('refresh-files-btn').addEventListener('click', refreshFiles);
            document.getElementById('refresh-downloads-btn').addEventListener('click', refreshDownloads);
            document.getElementById('clear-downloads-btn').addEventListener('click', clearDownloads);
            
            // Set up breadcrumb navigation
            document.addEventListener('click', function(e) {
                if (e.target.matches('.breadcrumb a[data-path]')) {
                    e.preventDefault();
                    const path = e.target.getAttribute('data-path');
                    navigateToPath(path);
                }
            });
            
            loadFolders();
            loadFiles('');
            setInterval(updateDownloadProgress, 2000);
        });
        
        // Load available folders
        async function loadFolders() {
            try {
                const response = await fetch('/api/folders');
                const folders = await response.json();
                
                const select = document.getElementById('download-folder');
                select.innerHTML = '';
                
                folders.forEach(folder => {
                    const option = document.createElement('option');
                    option.value = folder.path;
                    option.textContent = folder.name;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading folders:', error);
            }
        }
        
        // Start download
        async function startDownload() {
            const url = document.getElementById('download-url').value;
            const folder = document.getElementById('download-folder').value;
            const filename = document.getElementById('download-filename').value;
            
            if (!url || !folder) {
                alert('Please provide a URL and select a folder');
                return;
            }
            
            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url, folder, filename })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    document.getElementById('download-status').innerHTML = 
                        '<div class="success">Download started successfully!</div>';
                    document.getElementById('download-url').value = '';
                    document.getElementById('download-filename').value = '';
                } else {
                    document.getElementById('download-status').innerHTML = 
                        `<div class="error">Error: ${result.error}</div>`;
                }
            } catch (error) {
                document.getElementById('download-status').innerHTML = 
                    `<div class="error">Network error: ${error.message}</div>`;
            }
        }
        
        // Load files in directory
        async function loadFiles(path) {
            currentPath = path;
            
            try {
                // Clean up path to avoid double slashes
                const cleanPath = path.replace(/\/+/g, '/').replace(/^\/|\/$/g, '');
                const response = await fetch(`/api/files/${encodeURIComponent(cleanPath)}`);
                const data = await response.json();
                
                if (response.ok) {
                    updateBreadcrumb(path);
                    displayFiles(data.files || []);
                } else {
                    console.error('API Error:', data.error);
                    document.getElementById('file-list').innerHTML = 
                        `<div class="error">Error: ${data.error || 'Failed to load files'}</div>`;
                }
            } catch (error) {
                console.error('Error loading files:', error);
                document.getElementById('file-list').innerHTML = 
                    '<div class="error">Network error loading files</div>';
            }
        }
        
        // Update breadcrumb navigation
        function updateBreadcrumb(path) {
            const breadcrumb = document.getElementById('breadcrumb');
            breadcrumb.innerHTML = '<a href="#" data-path="">🏠 Home</a>';
            
            if (path) {
                const parts = path.split('/');
                let currentPath = '';
                
                parts.forEach((part, index) => {
                    if (part) {
                        currentPath += (currentPath ? '/' : '') + part;
                        breadcrumb.innerHTML += ` / <a href="#" data-path="${currentPath}">${part}</a>`;
                    }
                });
            }
        }
        
        // Display files
        function displayFiles(files) {
            const fileList = document.getElementById('file-list');
            fileList.innerHTML = '';
            
            if (!files || !Array.isArray(files)) {
                fileList.innerHTML = '<div class="error">No files found or invalid data</div>';
                return;
            }
            
            if (files.length === 0) {
                fileList.innerHTML = '<div class="loading">This folder is empty</div>';
                return;
            }
            
            files.forEach(file => {
                const fileItem = document.createElement('div');
                fileItem.className = 'file-item';
                
                const icon = file.type === 'directory' ? '📁' : '📄';
                const size = file.type === 'directory' ? '' : formatFileSize(file.size);
                
                fileItem.innerHTML = `
                    <div class="file-icon">${icon}</div>
                    <div class="file-name ${file.type === 'directory' ? 'clickable' : ''}" data-filename="${file.name}" data-type="${file.type}">${file.name}</div>
                    <div class="file-size">${size}</div>
                    <div class="file-actions">
                        ${file.type !== 'directory' ? `<button class="btn btn-secondary move-file-btn" data-filename="${file.name}">Move</button>` : ''}
                        <button class="btn btn-danger delete-file-btn" data-filename="${file.name}" data-type="${file.type}">Delete</button>
                    </div>
                `;
                
                fileList.appendChild(fileItem);
            });
            
            // Add event listeners for file actions
            document.querySelectorAll('.file-name.clickable').forEach(element => {
                element.addEventListener('click', function() {
                    const filename = this.getAttribute('data-filename');
                    const newPath = currentPath ? `${currentPath}/${filename}` : filename;
                    navigateToPath(newPath);
                });
            });
            
            document.querySelectorAll('.move-file-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const filename = this.getAttribute('data-filename');
                    moveFile(filename);
                });
            });
            
            document.querySelectorAll('.delete-file-btn').forEach(button => {
                button.addEventListener('click', function() {
                    const filename = this.getAttribute('data-filename');
                    const type = this.getAttribute('data-type');
                    deleteFile(filename, type);
                });
            });
        }
        
        // Navigate to path
        function navigateToPath(path) {
            loadFiles(path);
        }
        
        // Format file size
        function formatFileSize(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        // Delete file or folder
        async function deleteFile(name, type) {
            if (!confirm(`Are you sure you want to delete this ${type}?`)) {
                return;
            }
            
            try {
                const response = await fetch('/api/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: currentPath, name })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    loadFiles(currentPath);
                } else {
                    alert(`Error: ${result.error}`);
                }
            } catch (error) {
                alert(`Network error: ${error.message}`);
            }
        }
        
        // Move file
        async function moveFile(filename) {
            const newPath = prompt('Enter new path (relative to current folder):');
            if (!newPath) return;
            
            try {
                const response = await fetch('/api/move', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        oldPath: `${currentPath}/${filename}`,
                        newPath: `${currentPath}/${newPath}`
                    })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    loadFiles(currentPath);
                } else {
                    alert(`Error: ${result.error}`);
                }
            } catch (error) {
                alert(`Network error: ${error.message}`);
            }
        }
        
        // Create folder
        async function createFolder() {
            const name = prompt('Enter folder name:');
            if (!name) return;
            
            try {
                const response = await fetch('/api/create-folder', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ path: currentPath, name })
                });
                
                const result = await response.json();
                
                if (result.success) {
                    loadFiles(currentPath);
                } else {
                    alert(`Error: ${result.error}`);
                }
            } catch (error) {
                alert(`Network error: ${error.message}`);
            }
        }
        
        // Refresh files
        function refreshFiles() {
            loadFiles(currentPath);
        }
        
        // Load downloads
        async function loadDownloads() {
            try {
                const response = await fetch('/api/downloads');
                const downloads = await response.json();
                
                const downloadsList = document.getElementById('downloads-list');
                downloadsList.innerHTML = '';
                
                if (downloads.length === 0) {
                    downloadsList.innerHTML = '<div class="loading">No downloads</div>';
                    return;
                }
                
                downloads.forEach(download => {
                    const downloadItem = document.createElement('div');
                    downloadItem.className = `download-item ${download.status}`;
                    
                    let progressBar = '';
                    if (download.status === 'downloading') {
                        progressBar = `
                            <div class="progress-container">
                                <div class="progress-bar" style="width: ${download.progress || 0}%">
                                    ${download.progress || 0}%
                                </div>
                            </div>
                        `;
                    }
                    
                    downloadItem.innerHTML = `
                        <div><strong>${download.filename}</strong></div>
                        <div>Status: ${download.status}</div>
                        <div>URL: ${download.url}</div>
                        <div>Folder: ${download.folder}</div>
                        ${progressBar}
                        ${download.error ? `<div class="error">Error: ${download.error}</div>` : ''}
                    `;
                    
                    downloadsList.appendChild(downloadItem);
                });
            } catch (error) {
                console.error('Error loading downloads:', error);
            }
        }
        
        // Update download progress
        async function updateDownloadProgress() {
            if (document.getElementById('downloads-tab').classList.contains('active')) {
                loadDownloads();
            }
        }
        
        // Refresh downloads
        function refreshDownloads() {
            loadDownloads();
        }
        
        // Clear completed downloads
        function clearDownloads() {
            // This would need to be implemented on the server side
            alert('Clear downloads functionality would be implemented here');
        }
    </script>
</body>
</html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def api_get_folders(self):
        """Get available folders for downloads"""
        folders = [
            {"name": "Models - Checkpoints", "path": "models/checkpoints"},
            {"name": "Models - VAE", "path": "models/vae"},
            {"name": "Models - LoRA", "path": "models/loras"},
            {"name": "Models - Embeddings", "path": "models/embeddings"},
            {"name": "Models - ControlNet", "path": "models/controlnet"},
            {"name": "Models - CLIP", "path": "models/clip"},
            {"name": "Models - UNET", "path": "models/unet"},
            {"name": "Models - Upscale", "path": "models/upscale_models"},
            {"name": "Custom Nodes", "path": "custom_nodes"},
            {"name": "Input", "path": "input"},
            {"name": "Output", "path": "output"}
        ]
        
        self.send_json(folders)
    
    def api_get_files(self):
        """Get files in a directory"""
        path = urllib.parse.unquote(self.path.split('/api/files/')[1])
        # Clean up the path to handle double slashes and empty segments
        path = path.strip('/')
        full_path = os.path.join(self.base_path, path) if path else self.base_path
        
        try:
            if not os.path.exists(full_path):
                os.makedirs(full_path, exist_ok=True)
            
            files = []
            for item in os.listdir(full_path):
                item_path = os.path.join(full_path, item)
                is_dir = os.path.isdir(item_path)
                
                try:
                    size = 0 if is_dir else os.path.getsize(item_path)
                except (OSError, IOError):
                    # Handle files that can't be accessed
                    size = 0
                
                files.append({
                    "name": item,
                    "type": "directory" if is_dir else "file",
                    "size": size
                })
            
            files.sort(key=lambda x: (x["type"] != "directory", x["name"].lower()))
            self.send_json({"files": files})
            
        except PermissionError:
            self.send_json({"error": "Permission denied", "files": []}, 403)
        except FileNotFoundError:
            self.send_json({"error": "Directory not found", "files": []}, 404)
        except Exception as e:
            logger.error(f"Error listing files in {full_path}: {str(e)}")
            self.send_json({"error": str(e), "files": []}, 500)
    
    def api_download(self):
        """Start a file download"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        url = data.get('url')
        folder = data.get('folder')
        custom_filename = data.get('filename')
        
        if not url or not folder:
            self.send_json({"success": False, "error": "URL and folder are required"}, 400)
            return
        
        try:
            # Start download in background
            download_id = hashlib.md5(f"{url}{folder}{datetime.now()}".encode()).hexdigest()
            threading.Thread(
                target=self.download_file,
                args=(download_id, url, folder, custom_filename),
                daemon=True
            ).start()
            
            self.send_json({"success": True, "download_id": download_id})
            
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
    
    def download_file(self, download_id, url, folder, custom_filename=None):
        """Download file in background"""
        try:
            import requests
            
            # Determine filename
            if custom_filename:
                filename = custom_filename
            else:
                # Extract filename from URL
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename:
                    filename = f"download_{download_id}"
            
            # Create full path
            folder_path = os.path.join(self.base_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            file_path = os.path.join(folder_path, filename)
            
            # Store download info
            downloads_db[download_id] = {
                "id": download_id,
                "url": url,
                "folder": folder,
                "filename": filename,
                "status": "downloading",
                "progress": 0,
                "error": None
            }
            
            # Download file
            response = requests.get(url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = int((downloaded / total_size) * 100)
                            downloads_db[download_id]["progress"] = progress
            
            downloads_db[download_id]["status"] = "completed"
            downloads_db[download_id]["progress"] = 100
            
        except Exception as e:
            downloads_db[download_id]["status"] = "error"
            downloads_db[download_id]["error"] = str(e)
    
    def api_get_downloads(self):
        """Get all downloads"""
        self.send_json(list(downloads_db.values()))
    
    def api_move_file(self):
        """Move a file"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        old_path = os.path.join(self.base_path, data.get('oldPath', '').lstrip('/'))
        new_path = os.path.join(self.base_path, data.get('newPath', '').lstrip('/'))
        
        try:
            os.makedirs(os.path.dirname(new_path), exist_ok=True)
            shutil.move(old_path, new_path)
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
    
    def api_delete_file(self):
        """Delete a file or folder"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        path = data.get('path', '')
        name = data.get('name', '')
        full_path = os.path.join(self.base_path, path, name).replace('//', '/')
        
        try:
            if os.path.isdir(full_path):
                shutil.rmtree(full_path)
            else:
                os.remove(full_path)
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
    
    def api_create_folder(self):
        """Create a new folder"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode())
        
        path = data.get('path', '')
        name = data.get('name', '')
        full_path = os.path.join(self.base_path, path, name).replace('//', '/')
        
        try:
            os.makedirs(full_path, exist_ok=True)
            self.send_json({"success": True})
        except Exception as e:
            self.send_json({"success": False, "error": str(e)}, 500)
    
    def send_json(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

# Global downloads database
downloads_db = {}

def run_server(port=8189, base_path="/workspace/comfyui-data"):
    """Run the file manager server"""
    def handler(*args, **kwargs):
        return FileManagerHandler(*args, base_path=base_path, **kwargs)
    
    with socketserver.TCPServer(("", port), handler) as httpd:
        logger.info(f"File Manager Server running at http://0.0.0.0:{port}")
        logger.info(f"Managing files in: {base_path}")
        httpd.serve_forever()

if __name__ == "__main__":
    import sys
    
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8189
    base_path = sys.argv[2] if len(sys.argv) > 2 else "/workspace/comfyui-data"
    
    # Install required packages if not available
    try:
        import requests
    except ImportError:
        os.system("pip install requests")
        import requests
    
    run_server(port, base_path)
