# CI Simplification Notes

This document explains the CI simplification implemented to address build reliability issues.

## Problem
The original CI setup had 6 workflow files with significant redundancy:
- `build-artifacts.yaml`
- `build-packages-dev.yaml` 
- `build-packages-prod.yaml`
- `build-packages-staging.yaml`
- `create-release.yaml`
- `tools.yaml`

This caused maintenance complexity and reliability issues.

## Solution

### Consolidated Workflows
Reduced to 3 focused workflows:

1. **`build-and-deploy.yaml`** - Main workflow that:
   - Builds packages once
   - Creates artifacts for download
   - Creates releases with wheel files
   - Deploys to appropriate environments (dev/staging/prod)

2. **`commit-wheels.yaml`** - Fallback workflow that:
   - Builds packages and commits wheels directly to repository
   - Creates issues when builds fail
   - Provides immediate access even when CI has issues

3. **`tools.yaml`** - Unchanged, handles build tools and container management

### Multiple Access Methods

Users now have several ways to install packages:

1. **One-line installer**:
   ```bash
   curl -sSL https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/install.sh | bash -s -- pandas
   ```

2. **Direct wheel download**:
   ```bash
   curl -L https://raw.githubusercontent.com/sgbaird/opentrons-python-packages/main/wheels/pandas-1.5.0-cp310-cp310-linux_armv7l.whl -o /tmp/pandas.whl
   pip install /tmp/pandas.whl
   ```

3. **CI artifacts and releases** (when CI runs successfully)

### Benefits

- **Simplified maintenance**: 50% fewer workflow files
- **Reduced redundancy**: Single build logic instead of duplicated across files
- **Improved reliability**: Multiple fallback options
- **Better user experience**: Immediate access to packages
- **Clear deployment flow**: Single workflow handles all environments based on triggers