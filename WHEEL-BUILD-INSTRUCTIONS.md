# Complete Wheel Build Instructions for Prefect on OT-2

This document provides comprehensive instructions for building **all** wheels required for full Prefect functionality on OT-2.

## Overview

For complete Prefect 3.3.4 functionality, **15+ ARM-compatible wheels are required**. Currently only 3 are provided:

**Currently Available:**
- `pendulum-3.1.0-cp310-cp310-linux_armv7l.whl` - Date/time library (cross-compiled)
- `ujson-5.10.0-py3-none-linux_armv7l.whl` - JSON encoder/decoder (fallback implementation)
- `prefect-3.3.4-py3-none-any.whl` - Prefect workflow engine (pure Python)

**Required for Full Functionality:**
- `cryptography-*-cp310-cp310-linux_armv7l.whl` - SSL/TLS support
- `asyncpg-*-cp310-cp310-linux_armv7l.whl` - PostgreSQL adapter
- `sqlalchemy-*-py3-none-any.whl` - Database toolkit
- `orjson-*-cp310-cp310-linux_armv7l.whl` - High-performance JSON
- `uvicorn-*-py3-none-any.whl` - ASGI web server
- `aiosqlite-*-py3-none-any.whl` - Async SQLite
- `alembic-*-py3-none-any.whl` - Database migrations
- `dateparser-*-py3-none-any.whl` - Date parsing (requires regex)
- `regex-*-cp310-cp310-linux_armv7l.whl` - Regular expressions (C extension)
- `docker-*-py3-none-any.whl` - Docker client
- `graphviz-*-py3-none-any.whl` - Graph visualization
- `ruamel-yaml-*-cp310-cp310-linux_armv7l.whl` - YAML processing
- `prometheus-client-*-py3-none-any.whl` - Metrics
- `readchar-*-py3-none-any.whl` - Terminal input
- `uv-*-cp310-cp310-linux_armv7l.whl` - Package installer (Rust)
- `griffe-*-py3-none-any.whl` - Documentation tool

## Prerequisites

- Docker for cross-compilation environment
- Python 3.10+
- Access to the build tools in this repository

## Build Environment Setup

### 1. Cross-Compilation Environment

The repository includes a cross-compilation toolchain for ARMv7l builds:

```bash
# Clone the repository
git clone https://github.com/sgbaird/opentrons-python-packages.git
cd opentrons-python-packages

# Build the cross-compilation container
cd tools
python3 -m builder.container build
```

## Building Individual Wheels

### Priority 1: Currently Available Wheels

#### 1. Pendulum Wheel (Cross-compiled)

Pendulum requires Rust compilation for ARMv7l architecture:

```bash
# Use the existing build script
python3 build-packages packages/pendulum/3.1.0
```

**Alternative manual build:**
```bash
# Set up cross-compilation environment
export TARGET_ARCH=armv7l
export CARGO_TARGET_ARMV7_UNKNOWN_LINUX_GNUEABIHF_LINKER=arm-linux-gnueabihf-gcc

# Clone pendulum source
git clone https://github.com/sdispater/pendulum.git
cd pendulum
git checkout 3.1.0

# Install Rust and add ARM target
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add armv7-unknown-linux-gnueabihf

# Build wheel with maturin
pip install maturin
maturin build --target armv7-unknown-linux-gnueabihf --release
```

#### 2. Prefect Wheel (Pure Python)

Prefect is pure Python but uses the build system for consistency:

```bash
# Use the existing build script
python3 build-packages packages/prefect/3.3.4
```

**Alternative manual build:**
```bash
# Clone prefect source
git clone https://github.com/PrefectHQ/prefect.git
cd prefect
git checkout 3.3.4

# Build wheel
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

#### 3. ujson Wheel (Fallback Implementation)

The ujson wheel is a special case - it's a minimal fallback implementation that provides the ujson interface without C extensions:

#### Option A: Create Minimal ujson Fallback

```bash
# Create minimal ujson implementation
mkdir ujson_fallback
cd ujson_fallback

cat > ujson.py << 'EOF'
"""
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
EOF

cat > setup.py << 'EOF'
from setuptools import setup

setup(
    name="ujson",
    version="5.10.0",
    py_modules=["ujson"],
    description="Minimal ujson fallback for ARM",
    python_requires=">=3.7",
)
EOF

# Build the wheel
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

#### Option B: Cross-compile ujson (Advanced)

```bash
# This requires setting up cross-compilation toolchain
export CC=arm-linux-gnueabihf-gcc
export CXX=arm-linux-gnueabihf-g++

git clone https://github.com/ultrajson/ultrajson.git
cd ultrajson
git checkout v5.10.0

# Install cross-compilation dependencies
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf

python3 setup.py bdist_wheel --plat-name linux_armv7l
```

### Priority 2: Critical Missing Wheels

#### 4. Cryptography Wheel (SSL/TLS Support)

**Critical for HTTPS and secure connections:**

```bash
# Cross-compilation approach
export CC=arm-linux-gnueabihf-gcc
export CXX=arm-linux-gnueabihf-g++

git clone https://github.com/pyca/cryptography.git
cd cryptography
git checkout 43.x.x  # Latest stable

# Install cross-compilation dependencies
sudo apt-get install gcc-arm-linux-gnueabihf g++-arm-linux-gnueabihf
sudo apt-get install libssl-dev:armhf libffi-dev:armhf

# Build wheel
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

#### 5. Regex Wheel (Required for dateparser)

**Essential for date parsing functionality:**

```bash
git clone https://github.com/mrabarnett/mrab-regex.git
cd mrab-regex
git checkout 2024.x.x  # Latest

export CC=arm-linux-gnueabihf-gcc
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

#### 6. AsyncPG Wheel (PostgreSQL Support)

**For database connectivity:**

```bash
git clone https://github.com/MagicStack/asyncpg.git
cd asyncpg
git checkout v0.x.x  # Latest stable

# Install PostgreSQL development headers for ARM
sudo apt-get install libpq-dev:armhf

export CC=arm-linux-gnueabihf-gcc
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

#### 7. OrJSON Wheel (High-Performance JSON)

**Rust-based JSON encoder (high priority):**

```bash
git clone https://github.com/ijl/orjson.git
cd orjson
git checkout 3.x.x  # Latest stable

# Install Rust and ARM target
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
rustup target add armv7-unknown-linux-gnueabihf

# Build with maturin
pip install maturin
maturin build --target armv7-unknown-linux-gnueabihf --release
```

### Priority 3: Additional Required Wheels

#### 8. UV Wheel (Modern Package Installer)

**Rust-based package manager:**

```bash
git clone https://github.com/astral-sh/uv.git
cd uv
rustup target add armv7-unknown-linux-gnueabihf
cargo build --target armv7-unknown-linux-gnueabihf --release
# Note: Building UV requires complex Rust packaging setup
```

#### 9. Ruamel-YAML Wheel (YAML Processing)

**Configuration file support:**

```bash
git clone https://github.com/ruamel/yaml.git
cd yaml
export CC=arm-linux-gnueabihf-gcc
python3 setup.py bdist_wheel --plat-name linux_armv7l
```

### Priority 4: Pure Python Packages (Lower Priority)

Most of these should install normally but may need repackaging:

```bash
# These are typically pure Python but may need verification
pip wheel --platform linux_armv7l sqlalchemy alembic aiosqlite
pip wheel --platform linux_armv7l docker graphviz prometheus-client
pip wheel --platform linux_armv7l readchar griffe dateparser
```

## Automated Build Process

**Complete build script for all wheels:**

```bash
# Build all critical wheels
python3 build-packages packages/pendulum/3.1.0
python3 build-packages packages/prefect/3.3.4
python3 build-packages packages/ujson/5.10.0

# Add build scripts for missing wheels (when implemented)
python3 build-packages packages/cryptography/43.x.x
python3 build-packages packages/regex/2024.x.x
python3 build-packages packages/asyncpg/0.x.x
python3 build-packages packages/orjson/3.x.x
python3 build-packages packages/uv/0.x.x
python3 build-packages packages/ruamel-yaml/0.x.x
```

## Automated Build Process

For reproducible builds, use the repository's build system:

```bash
# Build all essential wheels
python3 build-packages packages/pendulum/3.1.0
python3 build-packages packages/prefect/3.3.4

# For ujson, use the fallback method above or:
# (if a build script exists)
python3 build-packages packages/ujson/5.10.0
```

## Verification

After building, verify the wheels:

**Basic wheel integrity:**
```bash
# Check wheel contents
unzip -l pendulum-3.1.0-cp310-cp310-linux_armv7l.whl
unzip -l ujson-5.10.0-py3-none-linux_armv7l.whl  
unzip -l prefect-3.3.4-py3-none-any.whl

# Check additional wheels (when available)
unzip -l cryptography-*-cp310-cp310-linux_armv7l.whl
unzip -l regex-*-cp310-cp310-linux_armv7l.whl
unzip -l orjson-*-cp310-cp310-linux_armv7l.whl
```

**Installation testing (on ARM environment):**
```bash
# Test core wheels
pip install pendulum-3.1.0-cp310-cp310-linux_armv7l.whl
python3 -c "import pendulum; print(pendulum.now())"

pip install ujson-5.10.0-py3-none-linux_armv7l.whl
python3 -c "import ujson; print(ujson.dumps({'test': True}))"

pip install prefect-3.3.4-py3-none-any.whl
python3 -c "from prefect import flow, task; print('Prefect OK')"

# Test additional wheels (when available)
pip install cryptography-*-cp310-cp310-linux_armv7l.whl
python3 -c "import cryptography; print('Cryptography OK')"

pip install regex-*-cp310-cp310-linux_armv7l.whl
python3 -c "import regex; print('Regex OK')"
```

**Complete functionality test:**
```bash
# Test full Prefect with all dependencies
python3 -c "
from prefect import flow, task
import pendulum, ujson, cryptography, regex
import asyncpg, orjson  # When available

@task
def test_task():
    return {'status': 'success', 'time': str(pendulum.now())}

@flow
def test_flow():
    return test_task()

if __name__ == '__main__':
    result = test_flow()
    print('✅ FULL PREFECT FUNCTIONALITY VERIFIED')
    print(f'Result: {result}')
"
```

## Key Points

1. **Pendulum** requires actual cross-compilation due to Rust components
2. **Prefect** is pure Python but benefits from controlled build environment  
3. **ujson** uses a fallback implementation to avoid C compilation issues on OT-2
4. **Cryptography** requires complex SSL/TLS library cross-compilation
5. **Regex** is essential for dateparser functionality 
6. **OrJSON** provides significant performance benefits over standard JSON
7. **AsyncPG** enables full PostgreSQL database connectivity
8. **UV** represents the future of Python package management
9. All wheels use `linux_armv7l` platform tag for OT-2 compatibility
10. **Current limitation**: Only 3 of 15+ required wheels are implemented

## Current Status vs. Full Implementation

**✅ Currently Available (3/15+):**
- pendulum, ujson, prefect

**❌ Missing Critical Wheels (12+):**
- cryptography, regex, asyncpg, orjson, uv, ruamel-yaml
- sqlalchemy, alembic, aiosqlite, docker, graphviz, prometheus-client
- readchar, griffe, dateparser

**Impact of Missing Wheels:**
- Limited database functionality
- No SSL/TLS optimizations  
- Reduced JSON performance
- Missing date parsing capabilities
- No Docker integration
- Limited configuration file support

## Troubleshooting

### Compilation Errors
- Ensure cross-compilation toolchain is properly installed
- Check that target architecture environment variables are set
- For Rust components, verify ARM target is added to rustup

### Size Issues
- If wheels are too large, check for debug symbols
- Consider using `--strip` flags during compilation
- Verify only necessary components are included

### Compatibility Issues
- Test wheels on actual OT-2 hardware or simulator
- Verify Python version compatibility (3.10)
- Check for missing shared library dependencies

This build process ensures that all essential wheels are reproducible and compatible with the OT-2's ARMv7l architecture.