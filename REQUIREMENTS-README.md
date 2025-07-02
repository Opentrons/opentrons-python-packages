# Prefect Requirements for OT-2 Installation

This directory contains two requirements files to help with Prefect installation on OT-2 devices:

## Files

- **`requirements.txt`** - Relaxed version constraints for easier installation
- **`requirements-frozen.txt`** - Exact versions that were successfully tested on OT-2

## Installation Methods

### Option 1: Try pip first (recommended)
```bash
pip install -r requirements.txt
```

### Option 2: Use frozen versions if needed
```bash
pip install -r requirements-frozen.txt
```

## Important Notes

### Packages That May Need Custom Steps

Some packages in these requirements may still fail to install via pip on ARM devices due to compilation issues. Based on our testing, the following packages commonly require custom ARM wheels or alternative installation methods:

#### Critical packages that may need pre-compiled wheels:
- `pendulum` - Date/time library with C dependencies
- `ujson` - High-performance JSON (fallback implementation provided)
- `sqlalchemy` - Database toolkit (may need specific version)
- `pydantic-core` - Core validation library with Rust components

#### Optional packages that may fail but have workarounds:
- `orjson` - Alternative high-performance JSON (not in core requirements)
- `cryptography` - May be needed for advanced features
- `asyncpg` - PostgreSQL adapter (only needed for PostgreSQL backends)

### Fallback Installation

If standard pip installation fails, refer to:
1. **`ot2_prefect_final_installer.py`** - Automated installer with ARM wheel support
2. **`OT2-PREFECT-INSTALLATION-GUIDE.md`** - Complete manual installation guide
3. **`wheels/`** directory - Pre-compiled ARM wheels for problematic packages

### Environment Setup

After installing packages, ensure proper environment configuration:

```bash
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
```

## Package Count
- Total core packages: 40
- Successfully tested on: OT-2 ARMv7l architecture
- Python version: 3.10

## Usage

These requirements enable:
- ✅ Prefect flow and task decorators (`@flow`, `@task`)
- ✅ Flow execution and orchestration
- ✅ Prefect CLI commands (`prefect cloud login`, `prefect serve`)
- ✅ Cloud integration and monitoring
- ✅ Basic workflow serving capabilities

For complete installation instructions, see `OT2-PREFECT-INSTALLATION-GUIDE.md`.