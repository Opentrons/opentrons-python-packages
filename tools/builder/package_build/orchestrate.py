from .types import (
    GithubDevSource,
    GithubReleaseSDistSource,
    GlobalBuildContext,
    PackageBuildContext,
    BuildPaths,
)
from .download import fetch_source, unpack_source
from .build_wheel import build_with_setup_py
from typing import Iterator

from pathlib import Path


def discover_build_packages_sync(
    package_root: Path,
    build_root: Path,
    dist_root: Path,
    *,
    context: GlobalBuildContext,
) -> None:
    for _ in discover_build_packages(
        package_root, build_root, dist_root, context=context
    ):
        pass


def discover_build_packages(
    package_root: Path,
    build_root: Path,
    dist_root: Path,
    *,
    context: GlobalBuildContext,
) -> Iterator[None]:
    context.write("Building all packages")
    yield from build_packages(
        discover_packages(package_root, build_root, dist_root, context=context),
        context=context,
    )


def discover_packages(
    package_root: Path,
    build_root: Path,
    dist_root: Path,
    *,
    context: GlobalBuildContext,
) -> Iterator[BuildPaths]:
    """
    Discover package sources and build a list of directories for
    the build.

    Params
    ------
    package_root: path to a directory containing package source specs
    build_root: path to a directory where packages should be built
    dist_root: path to a directory where package distributions should go
    """
    resolved_root = package_root.resolve()
    builds = [path.parent for path in resolved_root.rglob("build.py")]
    context.write("Discovering packages")
    for build in builds:
        build_path = build_root / (build.relative_to(resolved_root)) / ""
        dist_path = dist_root / (build.relative_to(resolved_root)) / ""
        paths = BuildPaths(
            source_path=build, build_path=build_path, dist_path=dist_path
        )
        context.write_verbose(
            f"Discovered package at {build}, building in {build_path}, dist to {dist_path}"
        )
        yield paths


def build_packages(
    packages: Iterator[BuildPaths], *, context: GlobalBuildContext
) -> Iterator[None]:
    for package in packages:
        discover_build_package(package, context=context)
        yield


def discover_build_package(package: BuildPaths, *, context: GlobalBuildContext) -> None:
    context.write(f"Building package in directory {package.source_path}")
    package_context = PackageBuildContext(paths=package, context=context)
    package_build_file = package.source_path / "build.py"
    build_obj = compile(package_build_file.open().read(), package_build_file, "exec")
    injected_globals = globals()
    injected_globals["opentrons_package_build_context"] = package_context
    exec(build_obj, injected_globals)


# This function is called by the exec'd build_package call in build.py
# package build files. It relies on having the build paths in the globals.
def build_package(
    source: GithubDevSource | GithubReleaseSDistSource,
    setup_py_commands: list[str] | None = None,
    build_dependencies: list[str] | None = None,
) -> Path:
    """
    Build a package. The main entry point for package builds.

    Params
    ------
    source: A source type. Best provided by using a top-level callable like
            github_source
    work_path: The path to build the package in. Subdirectories for download,
               unpack, and build results will be made automatically inside it.
               If None, automatically detect from the path in which python
               was run.
    setup_py_command: The command to use with setup.py to build the package. If
                      not specified, build_wheel.
    build_dependencies: any python dependencies required for the build.

    Returns
    -------
    The path to the built wheel.
    """
    global opentrons_package_build_context
    # this is injected as a global because this function gets called from an exec'd file
    context: PackageBuildContext = opentrons_package_build_context  # type: ignore[name-defined]
    context.context.write_verbose(
        f"building package {source.name}:\n"
        f"{context.prettyprint()}\n"
        f"{source.prettyprint()}"
    )
    context.paths.build_path.mkdir(parents=True, exist_ok=True)
    context.paths.dist_path.mkdir(parents=True, exist_ok=True)

    download_dir = context.paths.build_path / "download/"
    build_dir = context.paths.build_path / "build/"
    unpack_dir = context.paths.build_path / "unpack/"
    venv_dir = context.paths.build_path / "venv"

    commands = setup_py_commands or ["bdist_wheel"]

    for dirname in (download_dir, build_dir, unpack_dir, venv_dir):
        dirname.mkdir(exist_ok=True)

    fetched = fetch_source(source, download_dir, context=context.context)
    context.context.write(f"Fetched to {fetched}")
    unpacked = unpack_source(
        unpack_dir,
        download_dir / source.archive_name(),
        getattr(source, "package_source_path", None) or Path("."),
        context=context.context,
    )
    context.context.write(f"Unpacked to {str(unpacked)}")
    wheelfile = build_with_setup_py(
        commands,
        unpacked,
        build_dir,
        context.paths.dist_path,
        venv_dir,
        build_dependencies or [],
        context=context.context,
    )
    context.context.write(f"Built {wheelfile}")
    return wheelfile
