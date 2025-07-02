# Prefect 3.3.4 Support for OT-2

This directory contains the build configuration for Prefect 3.3.4, a workflow orchestration tool, compiled for the Opentrons OT-2 robot.

## Package Information

- **Package**: Prefect
- **Version**: 3.3.4
- **Source**: GitHub repository PrefectHQ/prefect
- **Build Type**: Pure Python package with compiled dependencies

## Build Configuration

The `build.py` file configures the build system to:

1. Download Prefect 3.3.4 source code from GitHub (tag `3.3.4`)
2. Build a wheel package using `bdist_wheel` command
3. Cross-compile for arm7hf architecture (OT-2 compatible)

## Dependencies with Native Components

Prefect has several runtime dependencies that include compiled components:

- `asyncpg` - PostgreSQL adapter with C extensions
- `cryptography` - Cryptographic library with native code
- `orjson` - Fast JSON library with Rust extensions  
- `pydantic-core` - Pydantic validation core with Rust extensions
- `ujson` - Fast JSON library with C extensions
- `websockets` - WebSocket library with C extensions

These dependencies are handled automatically by the build system and will be resolved from the package index or built separately if needed.

## Build Process

To build this package:

```bash
./build-packages --verbose --build-type packages-only
```

Or to build the package and generate a package index:

```bash
./build-packages --verbose --build-type both
```

The build system will:
1. Pull the Prefect source code from GitHub
2. Set up a cross-compilation environment using Buildroot SDK
3. Create a Python virtual environment with build dependencies
4. Build the wheel package for arm7hf architecture
5. Output the wheel to the dist/ directory
6. Generate a PEP 503 package index (if using `--build-type both`)

## Installation on OT-2

### Generic Instructions

Once built and deployed, the package can be installed on an OT-2 using:

```bash
pip install prefect --index-url <opentrons-package-index-url>
```

### For sgbaird/opentrons-python-packages Fork

**Important**: This fork does not have access to the upstream repository's AWS deployment infrastructure. You have several options for distribution:

#### Option 1: Install from GitHub Releases (Recommended)

The repository automatically creates GitHub releases with wheel files when code is pushed to the main branch:

```bash
# Find the latest release at: https://github.com/sgbaird/opentrons-python-packages/releases
# Then install directly on your OT-2:
curl -L https://github.com/sgbaird/opentrons-python-packages/releases/download/[RELEASE_TAG]/prefect-3.3.4-py3-none-any.whl \
  -o /tmp/prefect-3.3.4-py3-none-any.whl
pip install /tmp/prefect-3.3.4-py3-none-any.whl
```

**Example with a specific release:**
```bash
# Replace [RELEASE_TAG] with actual tag from releases page
curl -L https://github.com/sgbaird/opentrons-python-packages/releases/download/build-20241209-143022-a1b2c3d/prefect-3.3.4-py3-none-any.whl \
  -o /tmp/prefect-3.3.4-py3-none-any.whl
pip install /tmp/prefect-3.3.4-py3-none-any.whl
```

#### Option 2: Install from GitHub Artifacts

GitHub Actions artifacts require authentication to download via API. The easiest approach is:

**Manual approach (one-time setup):**
1. Go to https://github.com/sgbaird/opentrons-python-packages/actions
2. Find the latest successful workflow run for your branch
3. Download the `opentrons-packages-[commit-sha]` artifact manually
4. Extract the zip file to get the wheel file
5. Upload the wheel file to a simple HTTP server or cloud storage
6. Then on your OT-2:
   ```bash
   curl -L "https://your-server.com/prefect-3.3.4-py3-none-any.whl" \
     -o /tmp/prefect-3.3.4-py3-none-any.whl
**Verification for all methods:**
```bash
python -c "import prefect; print(f'Prefect {prefect.__version__} installed successfully')"
```
   ```

#### Option 3: Download from GitHub Artifacts (Manual Transfer)

If direct installation doesn't work, you can download the artifacts manually:

1. **Check the latest GitHub Actions run** at: https://github.com/sgbaird/opentrons-python-packages/actions
2. **Find the workflow run** for your branch/commit
3. **Download the artifacts** named `opentrons-packages-[commit-sha]`
4. **Extract the downloaded zip** to get the wheel files
5. **Transfer the wheel file** to your OT-2 robot
6. **Install on the OT-2**:
   ```bash
   pip install /path/to/prefect-3.3.4-py3-none-any.whl
   ```

#### Option 4: Manual Local Build
1. Build the package locally:
   ```bash
   ./build-packages --verbose --build-type packages-only
   ```

2. Transfer the generated wheel file from `dist/` to your OT-2 robot

3. Install directly on the OT-2:
   ```bash
   pip install /path/to/prefect-3.3.4-py3-none-any.whl
   ```

#### Option 5: Set Up Your Own Package Index

To deploy an automated package index like the upstream repo, you would need to:

1. **Set up cloud storage** (AWS S3, Google Cloud Storage, etc.)
2. **Configure GitHub Actions secrets** with your cloud credentials
3. **Modify the workflow files** (.github/workflows/*.yaml) to use your storage endpoints
4. **Update the deployment URLs** in the workflows

Example for AWS S3:
- Create an S3 bucket (e.g., `your-pypi-bucket`)
- Configure IAM roles/users with S3 permissions
- Update workflows to use your bucket: `s3://your-pypi-bucket`
- Packages would then be available at: `https://your-pypi-bucket.s3.amazonaws.com/simple/`

#### Option 6: Upstream Integration

If the upstream repository eventually merges your changes, packages would be available at:
- **Development**: `https://dev.pypi.opentrons.com/[branch-name]/simple/`
- **Production**: `http://pypi.opentrons.com/simple/`

## Notes

- Prefect is primarily a pure Python package, so the build should be straightforward
- The build system will handle cross-compilation of any C/Rust extensions in dependencies
- The package has been tested for syntax and import validation
- Network connectivity is required during the build process to download source code