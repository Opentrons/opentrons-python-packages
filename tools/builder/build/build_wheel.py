"""build.build_wheel - utilities to build a single wheel"""
from .shell_environment import SDKSubshell
from pathlib import Path
from .types import GlobalBuildContext

def build_with_setup_py(command: str, source_dir: Path, build_dir: Path,
                        dist_dir: Path,
                        *, context: GlobalBuildContext) -> str:
    """Build a package."""
    context.write(f'Building package with python setup.py {command}')
    with SDKSubshell.scoped(
        source_dir,
        context.sdk_path,
        context.write,
        context.write_verbose
    ) as shell:
        shell.run(['python', '-c', 'import sys; print(sys.path)'])
        return shell.run(
            ['python',
             'setup.py',
             command,
             f'--dist-dir={str(dist_dir)}',
             f'--build-base={str(build_dir)}'])
