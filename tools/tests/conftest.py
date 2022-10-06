"""Conftest for all builder tests"""
from pathlib import Path
from glob import glob
from shutil import copytree

import pytest

TEST_DATA_DIR = Path(__file__).parent / "test_data"


@pytest.fixture
def run_path(tmpdir: str) -> Path:
    return Path(tmpdir)


@pytest.fixture
def build_path(run_path: Path) -> Path:
    return run_path / "build"


@pytest.fixture
def dist_path(run_path: Path) -> Path:
    dist_tree_root = run_path / "dist"
    copytree(TEST_DATA_DIR / "dist", dist_tree_root)
    return dist_tree_root


@pytest.fixture
def index_path(run_path: Path) -> Path:
    index_tree_root = run_path / "index"
    copytree(TEST_DATA_DIR / "index", index_tree_root)
    return index_tree_root


@pytest.fixture
def downloaded_artifacts() -> list[Path]:
    return list((TEST_DATA_DIR / "download").iterdir())


@pytest.fixture
def downloaded_source_zip() -> Path:
    return TEST_DATA_DIR / "download" / "some-test-zip.zip"


@pytest.fixture
def downloaded_sdist_tar() -> Path:
    return TEST_DATA_DIR / "download" / "some-test-tar.tar.gz"


@pytest.fixture
def package_names(dist_path: Path) -> list[str]:
    return [str(package.name) for package in dist_path.iterdir()]


@pytest.fixture
def dist_files(dist_path: Path) -> set[Path]:
    files = {Path(pth) for pth in glob(str(dist_path / "**" / "*.whl"), recursive=True)}
    return files
