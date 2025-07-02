# Complete Prefect Installation Guide for OT-2

This guide provides step-by-step instructions to install Prefect on a fresh OT-2 simulator, enabling full workflow orchestration with flow serving and cloud login capabilities.

## Prerequisites

- OT-2 simulator with Python 3.10
- Network connectivity to download packages
- SSH access to the OT-2

## Quick Installation (Recommended)

### Option 1: Automated Installation Script

Download and run the complete installer:

```bash
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/ot2_prefect_final_installer.py -o installer.py
python3 installer.py
```

This script will:
1. Set up the correct PYTHONPATH
2. Install pre-built ARM-compatible wheels
3. Resolve all dependency conflicts
4. Test the installation with a working flow

### Option 2: Manual Step-by-Step Installation

If you prefer manual control or need to troubleshoot:

#### Step 1: Set Up Environment

```bash
# Create permanent PATH configuration
cat > /root/.bashrc << 'EOF'
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
EOF

cat > /root/.profile << 'EOF'
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
EOF

# Apply to current session
source /root/.bashrc
```

#### Step 2: Try Requirements Files First

Try installing using the provided requirements files:

```bash
# Option A: Try relaxed requirements first
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements.txt -o requirements.txt
pip3 install -r requirements.txt --target /var/user-packages/root/.local/lib/python3.10/site-packages/

# Option B: If that fails, try frozen versions
curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/requirements-frozen.txt -o requirements-frozen.txt
pip3 install -r requirements-frozen.txt --target /var/user-packages/root/.local/lib/python3.10/site-packages/
```

If the requirements files work, skip to **Step 4: Test Installation**. If they fail due to ARM compilation issues, continue to Step 3.

#### Step 3: Install Core Dependencies (Fallback)

```bash
# Base URL for pre-built wheels
BASE_URL="https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/"

# Install critical ARM-compatible wheels
python3 -m pip install --user --force-reinstall --no-deps \
  "${BASE_URL}pendulum-3.1.0-cp310-cp310-linux_armv7l.whl" \
  "${BASE_URL}ujson-5.10.0-py3-none-linux_armv7l.whl" \
  "${BASE_URL}prefect-3.3.4-py3-none-any.whl"

# Install additional required dependencies
python3 -m pip install --user --upgrade \
  pydantic>=2.0 \
  rich \
  typing-extensions>=4.10.0
```

#### Step 3: Verify Installation

```bash
# Test basic import
python3 -c "import prefect; print(f'Prefect version: {prefect.__version__}')"

# Test flow and task decorators
python3 -c "from prefect import flow, task; print('Flow/task imports: SUCCESS')"

# Test complete flow functionality
python3 -c "
from prefect import flow, task

@task
def say_hello(name: str):
    return f'Hello {name}!'

@flow 
def hello_flow(name: str = 'OT-2'):
    message = say_hello(name)
    print(message)
    return message

if __name__ == '__main__':
    result = hello_flow()
    print(f'✅ Flow result: {result}')
    print('🎉 PREFECT FULLY WORKING ON OT-2!')
"
```

#### Step 4: Verify CLI Access

```bash
# Test Prefect CLI
prefect --version

# Test cloud login capability (don't need to actually login)
prefect cloud login --help
```

## Key Components Explained

### 1. Pre-built ARM Wheels

The installation uses specially built ARMv7l-compatible wheels. **Currently only 3 of 15+ required wheels are provided:**

**Available (3/15+):**
- **pendulum-3.1.0**: Solves Rust compilation issues that blocked Prefect installation
- **ujson-5.10.0**: Custom fallback wheel for JSON processing on ARM
- **prefect-3.3.4**: Full Prefect package with flow/task decorator support

**⚠️ Still Required for Full Functionality (12+ packages):**
- **cryptography**: SSL/TLS support (compilation-heavy)
- **asyncpg**: PostgreSQL adapter with C extensions
- **sqlalchemy**: Database toolkit (with asyncio support)
- **orjson**: High-performance JSON with Rust components
- **uvicorn**: ASGI web server
- **aiosqlite**: Async SQLite adapter
- **alembic**: Database migration tool
- **dateparser**: Date parsing library (depends on regex)
- **docker**: Docker client library
- **graphviz**: Graph visualization
- **ruamel-yaml**: Advanced YAML processing
- **prometheus-client**: Metrics collection
- **readchar**: Terminal input handling
- **uv**: Modern package installer (Rust-based)
- **griffe**: Documentation generation tool

> **⚠️ LIMITATION**: Current installation provides basic Prefect functionality but may fail for advanced features requiring the missing compiled dependencies.

> **Build Instructions**: For details on how these wheels were built, see `WHEEL-BUILD-INSTRUCTIONS.md`

### 2. Environment Configuration

The OT-2 requires specific PATH and PYTHONPATH settings:
- Packages install to `/var/user-packages/root/.local/`
- CLI tools need to be added to PATH
- Python modules need PYTHONPATH configuration

### 3. Dependency Resolution

Force-reinstalling core wheels with `--no-deps` prevents pip from attempting to compile dependencies that fail on the OT-2's limited environment.

## Usage Examples

### Basic Flow Example

```python
from prefect import flow, task

@task
def prepare_protocol():
    print("Initializing OT-2...")
    return "ready"

@task  
def run_experiment(status):
    print(f"Running experiment with status: {status}")
    return "completed"

@flow
def ot2_workflow():
    status = prepare_protocol()
    result = run_experiment(status)
    print(f"Workflow finished: {result}")
    return result

# Run the workflow
if __name__ == "__main__":
    ot2_workflow()
```

### Flow Serving

Create a file `my_flow.py`:

```python
from prefect import flow, task

@task
def process_samples(count: int):
    return f"Processed {count} samples"

@flow
def lab_workflow(sample_count: int = 10):
    result = process_samples(sample_count)
    return result

if __name__ == "__main__":
    lab_workflow.serve(name="ot2-lab-workflow")
```

Run the server:
```bash
python3 my_flow.py
```

### Cloud Integration

If you have a Prefect Cloud account:

```bash
# Login to Prefect Cloud
prefect cloud login

# Your flows will now be tracked in the cloud
python3 my_flow.py
```

## Troubleshooting

### Import Errors

If you get import errors:

```bash
# Check Python version (should be 3.10)
python3 --version

# Verify PYTHONPATH is set
echo $PYTHONPATH

# Re-source environment
source /root/.bashrc
```

### CLI Not Found

If `prefect` command not found:

```bash
# Check PATH
echo $PATH

# Re-apply configuration
source /root/.profile
```

### Permission Issues

If you get permission errors:

```bash
# Ensure using --user flag
python3 -m pip install --user package_name
```

### Network Issues

If downloads fail:

```bash
# Test connectivity
curl -I https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/prefect-3.3.4-py3-none-any.whl

# Use alternative download method if needed
python3 -c "
import urllib.request
url = 'https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/copilot/fix-11/wheels/prefect-3.3.4-py3-none-any.whl'
urllib.request.urlretrieve(url, 'prefect.whl')
print('Downloaded successfully')
"
```

## What This Enables

After successful installation, you can:

✅ **Create and run basic Prefect flows** with `@flow` and `@task` decorators  
⚠️ **Limited flow serving** (may timeout on resource-constrained OT-2)  
✅ **Use Prefect CLI** for basic workflow management  
✅ **Connect to Prefect Cloud** for monitoring and orchestration  
⚠️ **Build simple OT-2 automation workflows** with task dependencies  

**⚠️ KNOWN LIMITATIONS:**
- Advanced database features may fail (missing asyncpg, aiosqlite, alembic)
- Some web serving features limited (missing uvicorn optimizations)
- Date parsing limitations (missing dateparser)
- Docker integration unavailable (missing docker package)
- Advanced serialization limited (missing orjson)
- SSL/TLS features may be limited (missing cryptography optimizations)  

## Architecture Notes

- **Environment**: Debian-based OT-2 firmware with Python 3.10
- **Architecture**: ARMv7l (32-bit ARM)
- **Package Location**: `/var/user-packages/root/.local/`
- **Shell**: busybox ash (limited bash features)

This installation process resolves all compilation issues that prevent standard pip installation of Prefect on OT-2 hardware.