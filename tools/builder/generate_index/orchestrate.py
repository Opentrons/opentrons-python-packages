"""generate_index.orchestrate: functions for generating the index"""

from pathlib import Path
from pkginfo import Wheel  # type: ignore
from shutil import copyfile
from glob import iglob
from itertools import chain
from typing import Iterable, Iterator, cast
from .root_index import generate as generate_root
from .package_leaf import generate as generate_leaf
from collections import defaultdict


def generate(index_root: Path, dist_root: Path) -> list[Path]:
    """
    Inspect a tree of package distributions and build an index in index_root for them.
    """
    return generate_for_distributions(index_root, distributions_from_tree(dist_root))


def distributions_from_tree(dist_root: Path) -> Iterator[Path]:
    """Inspect a dist tree and find distribution paths."""
    return (Path(pth) for pth in iglob(str(dist_root / "**" / "*.whl")))


def generate_for_distributions(
    index_root: Path, distributions: Iterable[Path]
) -> list[Path]:
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
    by_package = collate_to_packages(distributions)

    return (
        [index_root]
        + generate_simple_index_dir(
            index_root, package_dirs_from_names(index_root, by_package.keys())
        )
        + list(
            chain.from_iterable(
                [
                    generate_and_fill_package_dir(index_root, package, dists)
                    for package, dists in by_package.items()
                ]
            )
        )
    )


def simple_root_from_index_root(index_root: Path) -> Path:
    return index_root / "simple"


def package_dirs_from_names(
    root_path: Path, package_names: Iterable[str]
) -> Iterator[Path]:
    return (simple_root_from_index_root(root_path) / name for name in package_names)


def generate_simple_index_dir(
    index_root: Path, package_dirs: Iterable[Path]
) -> list[Path]:
    simple_root = simple_root_from_index_root(index_root)
    simple_root.mkdir(parents=True, exist_ok=True)
    root_index_contents = generate_root(index_root, package_dirs)
    root_index_path = simple_root / "index.html"
    with open(root_index_path, "w") as root_index:
        root_index.write(root_index_contents)
    return [simple_root, root_index_path]


def generate_and_fill_package_dir(
    index_root: Path, package_name: str, dists: set[Path]
) -> list[Path]:
    simple_root = simple_root_from_index_root(index_root)
    package_dir = simple_root / package_name
    package_dir.mkdir(parents=True, exist_ok=True)
    dists_in_package = list(copy_dists_to_leaf(package_dir, dists))
    leaf_index_contents = generate_leaf(simple_root, package_dir, dists_in_package)
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
    result: defaultdict[str, set[Path]] = defaultdict(
        # this cast is needed because I think mypy sees the set argument as a Type
        # rather than as the type constructor: Type[Set[Any]] rather than
        # Callable[Any, Set[Any]]
        default_factory=cast(set[Path], set)
    )
    for dist in distributions:
        result[Wheel(dist).name].add(dist)
    return result
