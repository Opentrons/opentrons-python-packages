"""generate_index.orchestrate: functions for generating the index"""

from pathlib import Path
from pkginfo import Wheel

def generate_for_packages(
        index_root: Path, distributions: list[Path]) -> list[Path]:
    """
    Generate an index for a list of packages in a root path.

    Params
    ------
    index_root: The path to generate the index in. The index will be generated such that
                if you run a static webserver with index_root as the served directory,
                the resulting server will be PEP503 compliant. That means files will be
                under index_root/simple/.
    distributions: A list of paths to package distributions. A package might have
                   multiple distributions.

    Returns
    -------
    A list of paths to each file and directory in the index, with the root as the first.
    """
    pass


def collate_to_packages(
        distributions: list[Path]) -> dict[str, set[Path]]:
    """
    Turns the flat list of paths to distributions into a mapping of package names to
    a set of distributions for the package.
    """
    result: dict[str, set[Path]] = {}
    for dist in distributions:
        result[Wheel(dist).name].add(dist)
    return result
