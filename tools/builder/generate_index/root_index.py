"""generate_index.root_index: generate the root page for the index"""
from pathlib import Path
from typing import Iterable

from airium import Airium  # type: ignore[import]


def generate(index_root: Path, package_dirs: Iterable[Path]) -> str:
    """Generate a PEP503 compliant simple index root html file.

    Params
    ------
    simple_root: the path to the actual root of the index, i.e. what gets served at /
    package_directory: the path to the package directory
    package_name: the canonical name of the package
    distributions: iterable of the files to serve for the package. these paths should be true
                   filesystem paths (we need to read the files to get their hex digests) and
                   should be in the package directory.

    Returns
    -------
    The generated html file
    """
    idx = Airium()
    idx("<!DOCTYPE html>")
    with idx.html():
        with idx.head():
            with idx.title():
                idx("Opentrons Python Package Index")
        with idx.body():
            for package in package_dirs:
                with idx.a(href=(str(Path("/") / (package.relative_to(index_root))))):
                    idx(package.name)
    return str(idx)
