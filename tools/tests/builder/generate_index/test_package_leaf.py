from pathlib import Path
import os
from binascii import unhexlify
from hashlib import sha256
from urllib.parse import urlparse, ParseResult

import pytest
from bs4 import BeautifulSoup

from builder.generate_index import package_leaf


@pytest.fixture
def index_pyudev_package_dir(index_path: Path) -> Path:
    return index_path / "simple" / "pyudev"


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
        "http://localhost/simple/pyudev/",
        index_path,
        index_pyudev_package_dir,
        index_pyudev_distributions,
    )
    soup = BeautifulSoup(index, "html.parser")
    assert soup.title and soup.title.string
    assert "pyudev" in soup.title.string
    dists = {str(dist.name) for dist in index_pyudev_distributions}
    dist_links: set[tuple[str, ParseResult]] = set()
    for link in soup.find_all("a"):
        href = link.get("href")
        parsed = urlparse(href)
        dist_links.add((link.string.strip(), parsed))
    # all dists have their name in their href
    assert {urlparse(link[0]).path for link in dist_links} == dists
    for link in dist_links:
        assert link[1].netloc == "localhost"
        assert link[1].path.startswith("/simple/pyudev/")
        # link text matches the href target
        assert link[0] == Path(link[1].path).name
        # href target is correct and hash is right
        distfile = open(index_path / Path(link[1].path).relative_to("/"), "rb")
        algo, digest = link[1].fragment.split("=")
        assert algo == "sha256"
        assert sha256(distfile.read()).digest() == unhexlify(digest.encode())
