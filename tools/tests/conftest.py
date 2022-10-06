"""Conftest for all builder tests"""
from pathlib import Path
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
    return run_path / "dist"


@pytest.fixture
def downloaded_artifacts() -> list[Path]:
    return list((TEST_DATA_DIR / "download").iterdir())


@pytest.fixture
def downloaded_source_zip() -> Path:
    return TEST_DATA_DIR / "download" / "some-test-zip.zip"


@pytest.fixture
def downloaded_sdist_tar() -> Path:
    return TEST_DATA_DIR / "download" / "some-test-tar.tar.gz"
