#!/usr/bin/env python3
"""
Create ujson fallback wheel for OT-2 environments where C compilation fails.

This creates a minimal ujson implementation that provides the ujson interface
using Python's standard library json module.
"""

import os
import tempfile
import subprocess
import shutil
from pathlib import Path

def create_ujson_fallback():
    """Create a minimal ujson fallback wheel"""
    
    # Create temporary directory for wheel building
    with tempfile.TemporaryDirectory() as tmpdir:
        pkg_dir = Path(tmpdir) / "ujson_package"
        pkg_dir.mkdir()
        
        # Create minimal ujson.py
        ujson_py = pkg_dir / "ujson.py"
        ujson_py.write_text('''"""
Minimal ujson fallback for ARM environments where compilation fails.
Provides ujson interface using standard library json.
"""
import json

# Expose standard json functions with ujson names  
dumps = json.dumps
loads = json.loads
dump = json.dump
load = json.load

# ujson-specific interface
def encode(obj, **kwargs):
    return json.dumps(obj, **kwargs)

def decode(s, **kwargs):
    return json.loads(s, **kwargs)

__version__ = "5.10.0"
''')
        
        # Create setup.py
        setup_py = pkg_dir / "setup.py"
        setup_py.write_text('''from setuptools import setup

setup(
    name="ujson",
    version="5.10.0", 
    py_modules=["ujson"],
    description="Minimal ujson fallback for ARM environments",
    long_description="Fallback ujson implementation using standard library json",
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers", 
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8", 
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
''')
        
        # Build the wheel
        print("Building ujson fallback wheel...")
        old_cwd = os.getcwd()
        try:
            os.chdir(pkg_dir)
            result = subprocess.run([
                "python3", "setup.py", "bdist_wheel", 
                "--plat-name", "linux_armv7l"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find the created wheel
                dist_dir = pkg_dir / "dist"
                wheels = list(dist_dir.glob("*.whl"))
                if wheels:
                    wheel_path = wheels[0]
                    print(f"✅ Created wheel: {wheel_path.name}")
                    
                    # Copy to current directory
                    output_path = Path(old_cwd) / wheel_path.name
                    shutil.copy2(wheel_path, output_path)
                    print(f"✅ Copied to: {output_path}")
                    return output_path
                else:
                    print("❌ No wheel file found in dist/")
                    return None
            else:
                print(f"❌ Build failed: {result.stderr}")
                return None
                
        finally:
            os.chdir(old_cwd)

if __name__ == "__main__":
    wheel_path = create_ujson_fallback()
    if wheel_path:
        print(f"\n🎉 ujson fallback wheel created successfully: {wheel_path}")
        print("\nTest the wheel:")
        print(f"pip install {wheel_path}")
        print('python3 -c "import ujson; print(ujson.dumps({\'test\': True}))"')
    else:
        print("\n❌ Failed to create ujson fallback wheel")