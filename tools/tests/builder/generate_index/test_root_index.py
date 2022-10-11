from pathlib import Path
import os
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from builder.generate_index import root_index


def test_generate(index_path: Path) -> None:
    package_dirs = [index_path / dirname for dirname in os.listdir(index_path)]
    index = root_index.generate("http://localhost/simple", index_path, package_dirs)
    soup = BeautifulSoup(index, "html.parser")
    assert soup.title and soup.title.string
    assert "Opentrons Python Package Index" in soup.title.string
    package_links: set[Path] = set()
    packages = set(package_dirs)
    for link in soup.find_all("a"):
        href = link.get("href").strip()
        parsed = urlparse(href)
        assert parsed.netloc == "localhost"
        assert parsed.path.startswith("/simple")
        package_links.add(index_path / Path(parsed.path).relative_to("/"))
    assert packages == package_links
