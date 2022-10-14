"""generate_index.orchestrate: functions for generating the index"""

from pathlib import Path
from pkginfo import Wheel  # type: ignore
from shutil import copyfile
from glob import iglob
from itertools import chain
from typing import Iterable, Iterator
from .root_index import generate as generate_root
from .package_leaf import generate as generate_leaf
from collections import defaultdict
from urllib.parse import urljoin


def generate(index_root_url: str, index_root: Path, dist_root: Path) -> list[Path]:
    """
    Inspect a tree of package distributions and build an index in index_root for them.
    """
    return generate_for_distributions(
        index_root_url, index_root, distributions_from_tree(dist_root)
    )


def distributions_from_tree(dist_root: Path) -> Iterator[Path]:
    """Inspect a dist tree and find distribution paths."""
    return (Path(pth) for pth in iglob(str(dist_root / "**" / "*.whl"), recursive=True))


def generate_for_distributions(
    index_root_url: str, index_root_path: Path, distributions: Iterable[Path]
) -> list[Path]:
    """
    Generate an index for a list of packages in a root path.

    Params
    ------
    index_root_url: a URL where the index will be hosted - necessary for writing
                    absolute urls to packages. This should be a domain or a domain
                    plus path under which the index as a whole will be served. This
                    will typically be under another /simple directory. For instance,
                    if you pass pypi.opentrons.com as index_root_url, everything
                    will be generated so that the index root is at
                    pypi.opentrons.com/simple/index.html, and packages are at
                    pypi.opentrons.com/simple/packagename/.
    index_root_path: The path to generate the index in. The index will be generated
                     such that if you run a static webserver with index_root as the
                     served directory, the resulting server will be PEP503 compliant.
                     That means files will be under index_root/simple/.
    distributions: A list of paths to package distributions. A package might have
                   multiple distributions.

    Returns
    -------
    A list of paths to each file and directory in the index, with the root as the first.
    """
    by_package = collate_to_packages(distributions)
    if not index_root_url.endswith("/"):
        index_root_url += "/"
    return (
        [index_root_path]
        + generate_simple_index_dir(
            index_root_url,
            index_root_path,
            package_dirs_from_names(index_root_path, by_package.keys()),
        )
        + list(
            chain.from_iterable(
                [
                    generate_and_fill_package_dir(
                        index_root_url, index_root_path, package, dists
                    )
                    for package, dists in by_package.items()
                ]
            )
        )
    )


def simple_root_from_index_root(index_root: Path) -> Path:
    return index_root / "simple"


def simple_url_from_index_url(index_url: str) -> str:
    if not index_url.endswith("/"):
        index_url += "/"
    return urljoin(index_url, "simple/")


def package_dirs_from_names(
    index_root_path: Path, package_names: Iterable[str]
) -> Iterator[Path]:
    return (
        simple_root_from_index_root(index_root_path) / name for name in package_names
    )


def generate_simple_index_dir(
    index_root_url: str, index_root_path: Path, package_dirs: Iterable[Path]
) -> list[Path]:
    simple_fs_root = simple_root_from_index_root(index_root_path)
    simple_fs_root.mkdir(parents=True, exist_ok=True)
    simple_url_root = simple_url_from_index_url(index_root_url)
    simple_root_index_contents = generate_root(
        simple_url_root, simple_fs_root, package_dirs
    )
    simple_root_index_path = simple_fs_root / "index.html"
    with open(simple_root_index_path, "w") as simple_root_index:
        simple_root_index.write(simple_root_index_contents)
    return [simple_fs_root, simple_root_index_path]


def generate_and_fill_package_dir(
    index_root_url: str, index_root_path: Path, package_name: str, dists: set[Path]
) -> list[Path]:
    simple_fs_root = simple_root_from_index_root(index_root_path)
    package_dir = simple_fs_root / package_name
    package_dir.mkdir(parents=True, exist_ok=True)
    dists_in_package = list(copy_dists_to_leaf(package_dir, dists))
    simple_root_url = simple_url_from_index_url(index_root_url)
    package_url = urljoin(simple_root_url, f"{package_dir.name}/")
    leaf_index_contents = generate_leaf(
        package_url,
        package_dir,
        dists_in_package,
    )
    leaf_index_path = package_dir / "index.html"
    with open(leaf_index_path, "w") as leaf_index:
        leaf_index.write(leaf_index_contents)
    return [package_dir, leaf_index_path] + dists_in_package


def copy_dists_to_leaf(package_dir: Path, dists: Iterable[Path]) -> Iterator[Path]:
    """Copy distribution files to the leaf directory"""
    for dist in dists:
        target_path = package_dir / dist.name
        copyfile(dist, target_path)
        yield target_path


def collate_to_packages(distributions: Iterable[Path]) -> dict[str, set[Path]]:
    """
    Turns the flat list of paths to distributions into a mapping of package names to
    a set of distributions for the package.
    """
    result: defaultdict[str, set[Path]] = defaultdict(set)
    for dist in distributions:
        result[Wheel(dist).name].add(dist)
    return result
