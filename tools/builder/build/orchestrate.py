from .types import GithubDevSource, GithubReleaseSDistSource
from .download import fetch_source, unpack_source
from .build_wheel import build_with_setup_py
import sys
import os

def build_package(
        source: GithubDevSource | GithubReleaseSDistSource,
        setup_py_command: str,
        /,
        work_path: str | None,
        ) -> str:
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
    setup_py_command: The command to use with setup.py to build the package.

    Returns
    -------
    The path to the built wheel.
    """
    work = _work_dir(work_path)
    download_dir = os.path.join(work, 'download')
    build_dir = os.path.join(work, 'build')
    unpack_dir = os.path.join(work, 'unpack')
    for dirname in (download_dir, build_dir, unpack_dir):
        os.makedirs(dirname, exist_ok=True)
    fetched = fetch_source(source, download_dir)
    unpacked = unpack_source(
        unpack_dir,
        os.path.join(download_dir, source.archive_name()),
        getattr(source, 'package_source_path', '.'))
    wheelfile = build_with_setup_py(setup_py_command, unpack_dir, build_dir)
    return wheelfile

def _work_dir(path_opt: str | None) -> str:
    if path_opt is None:
        try:
            # if we have a __main__ module, this is a non-interactive
            # session and we can use whatever that path is; this supports
            # when someone runs python build.py in a package directory
            return os.path.dir(sys.modules['__main__'].__file__)
        except (KeyError, AttributeError):
            # if we can't figure that out, just use the interpreter's
            # working directory
            return os.cwd()
    return path_opt
