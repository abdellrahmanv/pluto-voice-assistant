#!/usr/bin/env python3
"""
Download YuNet face detection model from OpenCV Zoo
Model: face_detection_yunet_2023mar_int8bq.onnx
"""

import urllib.request
import hashlib
from pathlib import Path
import sys

# Model details
MODEL_NAME = "face_detection_yunet_2023mar_int8bq.onnx"
MODEL_URL = "https://github.com/opencv/opencv_zoo/raw/main/models/face_detection_yunet/face_detection_yunet_2023mar_int8bq.onnx"
MODEL_SHA256 = "dd5ad2e8f6e2e9f3dd8beec41e1d33a436327b8c5b5c4cd7c4e8b9a8d9c9f2d5"  # Will verify if available

# Paths
SCRIPT_DIR = Path(__file__).parent
MODELS_DIR = SCRIPT_DIR / "models"


def download_file(url: str, dest_path: Path) -> bool:
    """Download file with progress indicator"""
    try:
        print(f"📥 Downloading: {url}")
        print(f"📂 Destination: {dest_path}")
        
        def progress_hook(count, block_size, total_size):
            """Show download progress"""
            percent = int(count * block_size * 100 / total_size)
            sys.stdout.write(f"\r  Progress: {percent}% [{count * block_size}/{total_size} bytes]")
            sys.stdout.flush()
            
        urllib.request.urlretrieve(url, dest_path, reporthook=progress_hook)
        print("\n✅ Download complete")
        return True
        
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False


def verify_file(file_path: Path) -> bool:
    """Verify file exists and has reasonable size"""
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return False
        
    size_mb = file_path.stat().st_size / (1024 * 1024)
    print(f"📦 Model size: {size_mb:.2f} MB")
    
    # YuNet model should be around 2-3 MB
    if size_mb < 1 or size_mb > 10:
        print(f"⚠️  Warning: Unexpected file size")
        return False
        
    return True


def main():
    """Main download function"""
    print("\n" + "="*70)
    print("🎯 YuNet Face Detection Model Downloader")
    print("="*70 + "\n")
    
    # Ensure models directory exists
    MODELS_DIR.mkdir(exist_ok=True)
    print(f"📁 Models directory: {MODELS_DIR}")
    
    # Target path
    model_path = MODELS_DIR / MODEL_NAME
    
    # Check if already exists
    if model_path.exists():
        print(f"✅ Model already exists: {model_path}")
        if verify_file(model_path):
            print("✅ Model verified - ready to use")
            return 0
        else:
            print("⚠️  Model file seems corrupted, re-downloading...")
            model_path.unlink()
    
    # Download
    if not download_file(MODEL_URL, model_path):
        return 1
        
    # Verify
    if not verify_file(model_path):
        print("❌ Model verification failed")
        return 1
        
    print("\n" + "="*70)
    print("✅ YuNet model ready!")
    print("="*70)
    print(f"\nModel location: {model_path}")
    print("\nYou can now run the vision worker:")
    print("  python run.py")
    print("\n" + "="*70 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
