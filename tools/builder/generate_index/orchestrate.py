"""generate_index.orchestrate: functions for generating the index"""

from pathlib import Path
from pkginfo import Wheel
from shutil import copyfile
from itertools import chain
from typing import Iterable, Iterator
from .root_index import generate as generate_root
from .package_leaf import generate as generate_leaf

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
    generated_paths: list[Path] = [index_root]
    by_package = collate_to_packages(distributions)
    generated_paths.extend(generate_simple_index_dir(index_root, by_package.keys()))
    simple_root = index_root / 'simple'
    simple_root.mkdir(parents=True, exist_ok=True)
    return [simple_root, generate_root(simple_root, by_package.keys())] + \
        list(chain.from_iterable([generate_and_fill_package_dir(simple_root, package, dists)
                         for package, dists in by_package.items()]))

def generate_simple_index_dir(index_root: Path, package_dirs: list[str]) -> list[Path]:
    simple_root = index_root / 'simple'
    simple_root.mkdir(parents=True, exist_ok=True)
    root_index_contents = generate_root(index_root, package_dirs)
    root_index_path = simple_root / 'index.html'
    with open(root_index_path, 'w') as root_index:
        root_index.write(root_index_contents)
    return [simple_root, root_index_path]

def generate_and_fill_package_dir(simple_root: Path, package_name: str, dists: set[Path]) -> list[Path]:
    package_dir = simple_root / package_name
    package_dir.mkdir(parents=True, exist_ok=True)
    dists_in_package = list(copy_dists_to_leaf(package_dir, dists))
    leaf_index_contents = generate_leaf(simple_root, package_name, dists_in_package)
    with open(package_dir / 'index.html', 'w') as leaf_index:
        leaf_index.write(leaf_index_contents)

def copy_dists_to_leaf(package_dir: Path, dists: Iterable[Path]) -> Iterator[Path]:
    """Copy distribution files to the leaf directory"""
    for dist in dists:
        target_path = package_dir / dist.name
        copyfile(dist, target_path)
        yield target_path


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
