"""generate_index.root_index: generate the root page for the index"""
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin

from airium import Airium  # type: ignore[import]


def generate(
    simple_root_url: str, simple_root_path: Path, package_dirs: Iterable[Path]
) -> str:
    """Generate a PEP503 compliant simple index root html file.

    Params
    ------
    simple_root_url: the url of the index's simple api, e.g. pypi.opentrons.com/simple
    simple_root_path: the path to the actual root of the simple index, i.e. what gets served
                     at the simple_root_url, i.e. /path/to/opentrons-python-packages/index/simple
    package_directory: the path to the package directory, i.e.
                     /path/to/opentrons-python-packages/index/simple/package
    package_name: the canonical name of the package, i.e. pandas for pandas
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
                with idx.a(
                    href=str(
                        urljoin(
                            simple_root_url, str(package.relative_to(simple_root_path))
                        )
                    )
                ):
                    idx(package.name)
    return str(idx)
