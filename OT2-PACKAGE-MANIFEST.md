# OT-2 Prefect Dependencies - Complete Package List

This file contains the exact versions of all packages that were successfully installed to make Prefect work on the OT-2 simulator.

## Custom Installed Packages (61 packages)

The following packages were installed in `/var/user-packages/root/.local/lib/python3.10/site-packages/`:

```
aiosqlite==0.21.0
alembic==1.16.2
annotated_types==0.7.0
anyio==4.9.0
apprise==1.9.3
asgi_lifespan==2.1.0
cachetools==6.1.0
certifi==2025.6.15
cloudpickle==3.1.1
colorama==0.4.6
coolname==2.2.0
dateparser==1.2.1
docker==7.1.0
fastapi==0.115.13
fsspec==2025.5.1
graphviz==0.21
griffe==1.7.3
h11==0.16.0
httpcore==1.0.9
httpx==0.28.1
humanize==4.12.3
importlib_metadata==8.7.0
jinja2==3.1.6
jinja2_humanize_extension==0.4.0
jsonpatch==1.33
jsonpointer==3.0.0
mako==1.3.10
markdown==3.8
markdown_it_py==3.0.0
mdurl==0.1.2
oauthlib==3.2.2
opentelemetry_api==1.34.1
orjson==3.10.18
pathspec==0.12.1
pendulum==3.1.0
prefect==3.3.4
prefect_client==3.4.6
prometheus_client==0.22.1
pydantic==2.11.7
pydantic_core==2.33.2
pydantic_extra_types==2.10.5
pydantic_settings==2.9.1
python_slugify==8.0.4
python_socks==2.7.1
readchar==4.2.1
referencing==0.36.2
requests==2.32.4
requests_oauthlib==2.0.0
rfc3339_validator==0.1.4
rich==14.0.0
rpds_py==0.25.1
ruamel.yaml==0.18.14
shellingham==1.5.4
sqlalchemy==2.0.41
starlette==0.46.2
text_unidecode==1.3
toml==0.10.2
tomli==2.2.1
typer==0.16.0
typing_extensions==4.14.0
typing_inspection==0.4.1
tzlocal==5.3.1
ujson==5.10.0
urllib3==2.4.0
uv==0.7.13
websockets==15.0.1
zipp==3.23.0
```

## System Package Upgrades

These packages were upgraded in the main system Python environment:

```
certifi==2025.6.15     # (upgraded from system version)
pendulum==3.1.0        # (new installation)
requests==2.32.4       # (upgraded from system version)
ujson==5.10.0          # (custom fallback implementation)
urllib3==2.4.0         # (upgraded from system version)
```

## Manual Installations

These packages were manually installed in `/root/.local/lib/python3.10/site-packages/`:

```
aiosqlite              # SQLite async adapter
asyncpg                # PostgreSQL async adapter
cryptography           # Cryptographic functions
```

## Critical ARM-Compatible Wheels Required

The following 3 wheels are essential and must be pre-compiled for ARMv7l:

1. **pendulum-3.1.0**: Date/time handling library with complex C dependencies
2. **ujson-5.10.0**: High-performance JSON library (fallback implementation provided)
3. **prefect-3.3.4**: Main workflow orchestration package

## Environment Configuration

The following environment variables must be set:

```bash
export PATH="/var/user-packages/root/.local/bin:$PATH"
export PYTHONPATH="/var/user-packages/root/.local/lib/python3.10/site-packages:$PYTHONPATH"
```

## Installation Notes

- Total packages installed: 61 custom + 3 manual + 5 system upgrades = **69 packages**
- Installation location uses custom path to avoid system conflicts
- Several packages required fallback implementations due to ARM compilation issues
- Environment configuration enables permanent CLI access to `prefect` command
- All installations are persistent across reboots and SSH sessions