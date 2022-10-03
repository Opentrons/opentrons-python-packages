"""build.build_wheel - utilities to build a single wheel"""
from .shell_environment import SDKSubshell
from pathlib import Path
from .types import GlobalBuildContext
import sys

def args_for_build_ext(
        source_dir: Path,
        build_dir: Path,
        dist_dir: Path
) -> list[str]:
    """args for build ext"""
    return [f'--build-lib={build_dir}',
            f'--build-temp={build_dir}']

def args_for_bdist_wheel(
        source_dir: Path,
        build_dir: Path,
        dist_dir: Path
) -> list[str]:
    """args for wheel"""
    return [f'--dist-dir={str(dist_dir)}', f'--bdist-dir={str(build_dir)}']

def args_for_command(
        command: str,
        source_dir: Path,
        build_dir: Path,
        dist_dir: Path) -> list[str]:
    """Different setup.py commands use different arguments. Look them up."""
    match command:
        case 'build_ext':
            return args_for_build_ext(source_dir, build_dir, dist_dir)
        case 'bdist_wheel':
            return args_for_bdist_wheel(source_dir, build_dir, dist_dir) + args_for_build_ext(source_dir, build_dir, dist_dir)
        case _:
            return []


def build_with_setup_py(
        command: str,
        source_dir: Path, build_dir: Path, dist_dir: Path, venv_dir: Path,
        build_dependencies: list[str],
        *, context: GlobalBuildContext) -> str:
    """Build a package."""
    context.write(f'Building package with python setup.py {command}')
    with SDKSubshell.scoped(
        source_dir,
        context.sdk_path,
        context.write,
        context.write_verbose
    ) as shell:
        shell.run(['python', '-m', 'venv', str(venv_dir)])
        shell.run(['source', str(venv_dir/'bin'/'activate')])
        # we have to allow importing from the system python path because
        # with the activated buildroot sdk, we'll be using the python in there,
        # and that python doesn't have ssl, and we need ssl to use pypi. things
        # still get installed to the venv.
        shell.run([f'PYTHONPATH={":".join(sys.path)}', 'python', '-m', 'pip', 'install'] + build_dependencies + ['wheel'])
        return shell.run(
            ['python',
             'setup.py',
             command] + args_for_command(command, source_dir, build_dir, dist_dir))
