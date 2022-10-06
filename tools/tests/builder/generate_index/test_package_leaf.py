from pathlib import Path
import os
from binascii import unhexlify
from hashlib import sha256

import pytest
from bs4 import BeautifulSoup

from builder.generate_index import package_leaf


@pytest.fixture
def index_pyudev_package_dir(index_path: Path) -> Path:
    return index_path / "pyudev"


@pytest.fixture
def index_pyudev_distributions(index_pyudev_package_dir: Path) -> list[Path]:
    return [
        index_pyudev_package_dir / fname
        for fname in os.listdir(index_pyudev_package_dir)
    ]


def test_generate(
    index_path: Path,
    index_pyudev_package_dir: Path,
    index_pyudev_distributions: list[Path],
) -> None:
    index = package_leaf.generate(
        index_path, index_pyudev_package_dir, index_pyudev_distributions
    )
    soup = BeautifulSoup(index, "html.parser")
    assert soup.title and soup.title.string
    assert "pyudev" in soup.title.string
    dists = {str(dist.name) for dist in index_pyudev_distributions}
    dist_links: set[tuple[str, Path, str]] = set()
    for link in soup.find_all("a"):
        href = link.get("href")
        assert "#" in href
        path, shasum = href.split("#")
        dist_links.add((link.string.strip(), Path(path.strip()), shasum))
    # all dists have their name in their href
    assert {link[0] for link in dist_links} == dists
    for link in dist_links:
        # link text matches the href target
        assert link[0] == link[1].name
        # href target is correct and hash is right
        distfile = open(index_path / link[1].relative_to(Path("/")), "rb")
        assert sha256(distfile.read()).digest() == unhexlify(
            link[2].split("=")[1].encode()
        )
