"""build.types - types for building everything"""

from dataclasses import dataclass
from typing import Protocol
from io import TextIOBase
import os
from pathlib import Path


@dataclass
class BuildPaths:
    source_path: Path
    #: The path to the build source for a specific package
    build_path: Path
    #: The path to the build directory for a specific package
    dist_path: Path
    #: The path to the dist location for a specific package

    def prettyprint(self, prefix: str = "") -> str:
        return (
            f"{prefix}Build paths:\n"
            f"\t{prefix}source: {self.source_path}\n"
            f"\t{prefix}build: {self.build_path}\n"
            f"\t{prefix}dist: {self.dist_path}"
        )


@dataclass
class GlobalBuildContext:
    output: TextIOBase | None
    #: Where to write output
    verbose: bool
    #: Whether that output should be verbose
    sdk_path: Path
    #: The path to the buildroot sdk, containing setup_environment

    def write(self, logstr: str) -> None:
        if not self.output:
            return
        print(logstr, file=self.output)
        self.output.flush()

    def write_verbose(self, logstr: str) -> None:
        if not self.output:
            return
        if not self.verbose:
            return
        print(logstr, file=self.output)
        self.output.flush()

    def prettyprint(self, prefix: str = "") -> str:
        return (
            f"{prefix}Global build context:\n"
            f'\t{prefix}output: {getattr(self.output, "name", self.output)}\n'
            f"\t{prefix}verbose: {self.verbose}\n"
            f"\t{prefix}sdk path: {str(self.sdk_path)}"
        )


@dataclass
class PackageBuildContext:
    paths: BuildPaths
    #: The relevant paths for this specific package
    context: GlobalBuildContext
    #: Link up to the global build settings

    def prettyprint(self, prefix: str = "") -> str:
        next_pref = prefix + "\t"
        return (
            f"{prefix}Package build context:\n"
            f"{self.paths.prettyprint(next_pref)}\n"
            f"{self.context.prettyprint(next_pref)}"
        )


class HTTPFetchableSource(Protocol):
    @property
    def name(self) -> str:
        ...

    def url(self) -> str:
        ...

    def archive_name(self) -> str:
        ...


class ShellBuild(Protocol):
    def command(self, path_to_unpacked: str) -> list[str]:
        ...


@dataclass
class SetupPyBuild:
    subcommand: str
    """The subcommand for setup.py, e.g. build_ext for pandas"""

    def command(self, path_to_unpacked: str) -> list[str]:
        return ["python", os.path.join(path_to_unpacked, "setup.py"), self.subcommand]


@dataclass
class _GithubSource:
    name: str
    """A human-readable name for the package (e.g. pandas for pandas)"""

    org: str
    """The github org (e.g. pandas-dev for pandas)"""

    repo: str
    """The repository (e.g. pandas for pandas)"""

    tag: str
    """The tag name to pull for this version (e.g. v1.5.0 for pandas 1.5.0)"""

    def prettyprint(self, prefix: str = "") -> str:
        return (
            f"{prefix}\tname: {self.name}\n"
            f"{prefix}\torg: {self.org}\n"
            f"{prefix}\trepo: {self.repo}\n"
            f"{prefix}\ttag: {self.tag}"
        )


@dataclass
class GithubReleaseSDistSource(_GithubSource):
    """A package where you can download an sdist from a Github release post."""

    package_name: str
    """
    The package name used for the release archive (e.g. pandas-1.5.0.tar.gz
    for pandas 1.5.0)
    """

    def url(self) -> str:
        return f"https://github.com/{self.org}/{self.repo}/releases/download/{self.tag}/{self.package_name}"

    def archive_name(self) -> str:
        return self.package_name

    def prettyprint(self, prefix: str = "") -> str:
        return (
            f"{prefix}SDist from github:\n"
            f"{super().prettyprint(prefix)}\n"
            f"{prefix}\tURL: {self.url()}\n"
            f"{prefix}\tArchive file name: {self.archive_name()}\n"
        )


@dataclass
class GithubDevSource(_GithubSource):
    """
    A package where the only way to get it is to download an archive of the Github
    repo at a tag.
    """

    package_source_path: str | None = None

    def url(self) -> str:
        return f"https://github.com/{self.org}/{self.repo}/archive/refs/tags/{self.tag}.zip"

    def archive_name(self) -> str:
        return f"{self.tag}.zip"

    def prettyprint(self, prefix: str = "") -> str:
        return (
            f"{prefix}Dev source from github:\n"
            f"{super().prettyprint(prefix)}\n"
            f"{prefix}\tURL: {self.url()}\n"
            f"{prefix}\tarchive name: {self.archive_name()}"
        )
