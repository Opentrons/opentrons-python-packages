#!/usr/bin/env python3
"""
Python-only installer for OT-2 systems that don't have bash
Usage: python install.py PACKAGE_NAME
"""

import sys
import urllib.request
import subprocess
import tempfile
import os
import shutil

def main():
    if len(sys.argv) != 2:
        print("Usage: python install.py PACKAGE_NAME")
        print("")
        print("Available packages:")
        print("  pandas        - Data analysis library")
        print("  prefect       - Full workflow orchestration framework")
        print("  prefect-client- Lightweight workflow orchestration (recommended for OT-2)")
        print("  pendulum      - Date/time manipulation library (required for Prefect)")
        print("")
        print("Example:")
        print("  python install.py pandas")
        print("  python install.py prefect-client")
        print("  python install.py prefect")
        print("  python install.py pendulum")
        sys.exit(1)
    
    package_name = sys.argv[1]
    repo_url = "https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/79767ae/wheels"
    
    # Map package names to wheel files
    wheel_map = {
        "pandas": "pandas-1.5.0-cp310-cp310-linux_armv7l.whl",
        "prefect": "prefect-3.3.4-py3-none-any.whl", 
        "prefect-client": "prefect_client-3.4.6-py3-none-any.whl",
        "pendulum": "pendulum-3.1.0-cp310-cp310-linux_armv7l.whl"
    }
    
    if package_name not in wheel_map:
        print(f"Error: Unknown package '{package_name}'")
        sys.exit(1)
    
    wheel_file = wheel_map[package_name]
    
    if package_name == "pendulum":
        print("Installing ARMv7l-compatible pendulum wheel for Opentrons OT-2...")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="opentrons-packages-")
    
    try:
        print(f"Downloading {package_name}...")
        wheel_url = f"{repo_url}/{wheel_file}"
        wheel_path = os.path.join(temp_dir, wheel_file)
        
        # Download the wheel
        urllib.request.urlretrieve(wheel_url, wheel_path)
        
        print(f"Installing {package_name}...")
        # Install using pip
        result = subprocess.run([sys.executable, "-m", "pip", "install", wheel_path], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Successfully installed {package_name}!")
            print("Installation output:")
            print(result.stdout)
        else:
            print(f"Installation failed:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
        
    finally:
        # Clean up
        print("Cleaning up...")
        shutil.rmtree(temp_dir, ignore_errors=True)

if __name__ == "__main__":
    main()