"""build.build_wheel - utilities to build a single wheel"""
from .shell_environment import SDKSubshell
from pathlib import Path
from .types import GlobalBuildContext
import re
from typing import Iterator


def args_for_build_ext(source_dir: Path, build_dir: Path, dist_dir: Path) -> list[str]:
    """args for build ext"""
    return [f"--build-lib={build_dir}", f"--build-temp={build_dir}"]


def args_for_bdist_wheel(
    source_dir: Path, build_dir: Path, dist_dir: Path
) -> list[str]:
    """args for wheel"""
    return [
        f"--dist-dir={str(dist_dir)}",
        f"--bdist-dir={str(build_dir)}",
        "--plat-name=linux_armv7l",
    ]


def args_for_command(
    command: str, source_dir: Path, build_dir: Path, dist_dir: Path
) -> list[str]:
    """Different setup.py commands use different arguments. Look them up."""

    match command:
        case "build_ext":
            return args_for_build_ext(source_dir, build_dir, dist_dir)
        case "bdist_wheel":
            return args_for_bdist_wheel(source_dir, build_dir, dist_dir)
        case _:
            return []
    return []


def update_build_dependencies(deps: list[str]) -> Iterator[str]:
    """some build dependencies need alteration to actually match what buildroot does."""
    for dep in deps:
        if dep.startswith("numpy"):
            # if the package requests numpy as a _build_ dependency, it is
            # probably because the package has cythonized components and uses the numpy
            # c api. For pandas 1.5.0 and newer packages, we need a more recent numpy
            # version that provides proper C API compatibility while still maintaining
            # backward compatibility for the target platform.
            yield "numpy>=1.19.0,<1.25"
        elif dep.startswith("Cython") and "=" not in dep:
            # If Cython is requested without version constraints, add reasonable defaults
            # for cross-compilation compatibility
            yield "Cython>=0.29.32,<3"
        else:
            yield dep


def build_with_setup_py(
    commands: list[str],
    source_dir: Path,
    build_dir: Path,
    dist_dir: Path,
    venv_dir: Path,
    build_dependencies: list[str],
    *,
    context: GlobalBuildContext,
) -> Path:
    """Build a package."""
    context.write(f'Building package with python setup.py {" ".join(commands)}')
    with SDKSubshell.scoped(
        source_dir,
        context.sdk_path,
        SDKSubshell.echo_wrap_prevent_double_newlines(context.write),
        SDKSubshell.echo_wrap_prevent_double_newlines(context.write_verbose),
    ) as shell:
        shell.run(["python", "-m", "venv", str(venv_dir)])
        shell.run(["source", str(venv_dir / "bin" / "activate")])
        # we have to allow importing from the system python path because
        # with the activated buildroot sdk, we'll be using the python in there,
        # and that python doesn't have ssl, and we need ssl to use pypi. things
        # still get installed to the venv if we don't provide a path that includes
        # site-packages.
        own_paths = [
            "/usr/local/lib/python3.10",
            "/usr/local/lib/python3.10/lib-dynload",
        ]
        shell.run(
            [f'PYTHONPATH={":".join(own_paths)}', "python", "-m", "pip", "install"]
            + [dep for dep in build_dependencies]
            + ["wheel"]
        )
        shell.initiate_python_environment(context.sdk_path)
        output = ""
        for command in commands:
            output += shell.run(
                ["python", "setup.py", command]
                + args_for_command(command, source_dir, build_dir, dist_dir)
            )
        wheelname = re.search(r"^creating.*?([\w\-\.]*\.whl).*$", output, re.MULTILINE)
        if not wheelname:
            context.write("Build failed: could not find wheelname")
            raise RuntimeError()
        return dist_dir / wheelname.group(1)
