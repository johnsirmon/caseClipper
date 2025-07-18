#!/usr/bin/env python3
"""
Simple build script for CaseClipSaver
Creates a standalone executable using PyInstaller
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_exe():
    """Build standalone executable"""
    print("Building CaseClipSaver executable...")
    
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Clean previous builds
    if Path("dist").exists():
        shutil.rmtree("dist")
    if Path("build").exists():
        shutil.rmtree("build")
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "CaseClipSaver",
        "--add-data", "config.json;.",
        "--hidden-import", "plyer.platforms.win.notification",
        "caseclipsaver.py"
    ]
    
    print("Running PyInstaller...")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("Build successful!")
        print(f"Executable created: {Path('dist/CaseClipSaver.exe').absolute()}")
        
        # Copy config file to dist directory
        shutil.copy("config.json", "dist/config.json")
        print("Config file copied to dist directory")
        
    except subprocess.CalledProcessError as e:
        print(f"Build failed: {e}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return False
    
    return True

def test_exe():
    """Test the built executable"""
    exe_path = Path("dist/CaseClipSaver.exe")
    if exe_path.exists():
        print(f"Testing executable: {exe_path}")
        print("Note: The executable will run in system tray mode")
        print("Use Ctrl+C to stop if needed")
        
        try:
            subprocess.run([str(exe_path)], timeout=5)
        except subprocess.TimeoutExpired:
            print("Executable started successfully (timed out as expected)")
        except Exception as e:
            print(f"Error testing executable: {e}")
    else:
        print("Executable not found!")

if __name__ == "__main__":
    if build_exe():
        print("\nBuild completed successfully!")
        print("Files created:")
        print("- dist/CaseClipSaver.exe")
        print("- dist/config.json")
        print("\nYou can now run the standalone executable.")
    else:
        print("Build failed!")
        sys.exit(1)