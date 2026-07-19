#!/usr/bin/env python3
"""
KIDO Build Script
Builds standalone executables for Windows, macOS, and Linux
"""

import os
import sys
import platform
import shutil
import subprocess
from pathlib import Path

def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous builds...")
    for dir_name in ['build', 'dist', '__pycache__', 'kido_core/__pycache__', 'kido_cli/__pycache__']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    for file_name in ['kido.spec']:
        if os.path.exists(file_name):
            os.remove(file_name)

def build_executable():
    """Build standalone executable using PyInstaller"""
    print("🔨 Building KIDO executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'], check=True)
    
    # Determine platform-specific settings
    system = platform.system()
    if system == 'Windows':
        exe_name = 'kido.exe'
        icon = None  # Add icon path if you have one: 'kido_icon.ico'
    elif system == 'Darwin':  # macOS
        exe_name = 'kido'
        icon = None  # Add icon path if you have one: 'kido_icon.icns'
    else:  # Linux
        exe_name = 'kido'
        icon = None
    
    # PyInstaller command
    cmd = [
        'pyinstaller',
        '--onefile',  # Single executable file
        '--name', exe_name,
        '--clean',  # Clean cache before building
        '--noconfirm',  # Don't ask for confirmation
    ]
    
    # Add icon if available
    if icon and os.path.exists(icon):
        cmd.extend(['--icon', icon])
    
    # Add console mode (no GUI window)
    cmd.append('--console')
    
    # Entry point
    cmd.append('kido_cli/cli.py')
    
    print(f"📦 Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print("❌ Build failed!")
        print(result.stderr)
        return False
    
    print("✅ Build successful!")
    return True

def create_distribution():
    """Create distribution package"""
    print("📦 Creating distribution package...")
    
    system = platform.system()
    dist_dir = Path('dist')
    
    if not dist_dir.exists():
        print("❌ No dist directory found. Build may have failed.")
        return False
    
    # Create examples directory in dist
    examples_dist = dist_dir / 'examples'
    if examples_dist.exists():
        shutil.rmtree(examples_dist)
    shutil.copytree('examples', examples_dist)
    
    # Copy README
    if os.path.exists('README.md'):
        shutil.copy('README.md', dist_dir / 'README.md')
    
    # Create platform-specific package
    if system == 'Windows':
        package_name = 'kido-windows.zip'
        print(f"📦 Creating {package_name}...")
        shutil.make_archive('kido-windows', 'zip', 'dist')
    elif system == 'Darwin':
        package_name = 'kido-macos.tar.gz'
        print(f"📦 Creating {package_name}...")
        shutil.make_archive('kido-macos', 'gztar', 'dist')
    else:
        package_name = 'kido-linux.tar.gz'
        print(f"📦 Creating {package_name}...")
        shutil.make_archive('kido-linux', 'gztar', 'dist')
    
    print(f"✅ Distribution package created: {package_name}")
    return True

def main():
    print("=" * 60)
    print("🧒 KIDO Build System")
    print("=" * 60)
    print()
    
    # Clean previous builds
    clean_build()
    print()
    
    # Build executable
    if not build_executable():
        sys.exit(1)
    print()
    
    # Create distribution
    if not create_distribution():
        sys.exit(1)
    print()
    
    print("=" * 60)
    print("✅ Build complete!")
    print("=" * 60)
    print()
    print("📁 Output files:")
    print("  - dist/kido (or kido.exe on Windows)")
    print("  - kido-*.zip or kido-*.tar.gz")
    print()
    print("🚀 To install:")
    print("  1. Extract the archive")
    print("  2. Add the directory to your PATH")
    print("  3. Run: kido version")
    print()

if __name__ == '__main__':
    main()
