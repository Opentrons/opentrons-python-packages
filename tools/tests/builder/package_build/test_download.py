from pathlib import Path
from unittest import mock
import os
import tarfile
import zipfile

from builder.package_build.download import unpack_source
from builder.package_build.types import GlobalBuildContext

from .conftest import PathsBuilder


def test_unpack_source_selects_tar_extractor(
    downloaded_sdist_tar: Path, global_context: GlobalBuildContext
) -> None:
    with mock.patch("builder.package_build.download._unpack_tar_to") as unpack_tar:
        unpack_tar.return_value = [Path("/tarfilecontents")]
        unpack_source(
            Path("/test/extract"),
            downloaded_sdist_tar,
            Path("."),
            context=global_context,
        )
        unpack_tar.assert_called_once()


def test_unpack_source_selects_zip_extractor(
    downloaded_source_zip: Path, global_context: GlobalBuildContext
) -> None:
    with mock.patch("builder.package_build.download._unpack_zip_to") as unpack_zip:
        unpack_zip.return_value = [Path("zipfilecontents")]
        unpack_source(
            Path("/test/extract"),
            downloaded_source_zip,
            Path("."),
            context=global_context,
        )
        unpack_zip.assert_called_once()


def test_tar_unpack_happypath(
    downloaded_sdist_tar: Path,
    global_context: GlobalBuildContext,
    paths_builder: PathsBuilder,
) -> None:
    paths = paths_builder("test-tar")
    files = [
        paths.source_path / Path(member.name)
        for member in tarfile.open(downloaded_sdist_tar, "r").getmembers()
    ]
    unpack_source(
        paths.source_path, downloaded_sdist_tar, Path("."), context=global_context
    )
    file_set = set(files)
    unpacked_set: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(paths.source_path):
        for element_name in filenames + dirnames:
            unpacked_set.add(Path(dirpath) / element_name)

    assert file_set == unpacked_set


def test_zip_unpack_happypath(
    downloaded_source_zip: Path,
    global_context: GlobalBuildContext,
    paths_builder: PathsBuilder,
) -> None:
    paths = paths_builder("test-zip")
    files = [
        paths.source_path / Path(member.filename)
        for member in zipfile.ZipFile(downloaded_source_zip).infolist()
    ]
    unpack_source(
        paths.source_path, downloaded_source_zip, Path("."), context=global_context
    )
    file_set = set(files)
    unpacked_set: set[Path] = set()
    for dirpath, dirnames, filenames in os.walk(paths.source_path):
        for element_name in filenames + dirnames:
            unpacked_set.add(Path(dirpath) / element_name)
    assert file_set == unpacked_set
