"""generate_index.package_leaf: generate metadata in a package leaf dir"""
from pathlib import Path
from hashlib import sha256
from typing import Iterable
from binascii import hexlify

from airium import Airium  # type: ignore[import]


def generate(
    index_root: Path, package_path: Path, distributions: Iterable[Path]
) -> str:
    """Generate a package leaf directory with index and hashes

    Params
    ------
    root: the path to the actual root of index, i.e. what gets served at /
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
                idx(f"{package_path.name} at Opentrons Python Package Index")
        with idx.body():
            for dist in distributions:
                digest = hexlify(sha256(open(dist, "rb").read()).digest())
                with idx.a(
                    href=(
                        str(Path("/") / (dist.relative_to(index_root)))
                        + f"#sha256={digest.decode()}"
                    )
                ):
                    idx(dist.name)
    return str(idx)
