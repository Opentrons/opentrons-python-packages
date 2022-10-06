from pathlib import Path
from unittest import mock
from builder.package_build.download import unpack_source
from builder.package_build.types import GlobalBuildContext


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


def test_verify_tar_member() -> None:
    pass
