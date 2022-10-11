import pytest
from io import StringIO
from pathlib import Path
from builder.package_build.types import GlobalBuildContext, BuildPaths
from typing import Protocol


class PathsBuilder(Protocol):
    def __call__(self, package_name: str) -> BuildPaths:
        ...


@pytest.fixture
def paths_builder(build_path: Path, dist_path: Path) -> PathsBuilder:
    def builder(package_name: str) -> BuildPaths:
        return BuildPaths(
            source_path=(build_path / package_name / "unpack"),
            build_path=(build_path / package_name / "build"),
            dist_path=(dist_path / package_name),
        )

    return builder


@pytest.fixture
def global_context() -> GlobalBuildContext:
    return GlobalBuildContext(StringIO(), True, Path("fake-sdk-path"))
