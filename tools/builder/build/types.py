"""build.types - types for building everything"""

from dataclasses import dataclass
from typing import Protocol
import os

class HTTPFetchableSource(Protocol):
    def url() -> str:
        ...

    def archive_name() -> str:
        ...

class ShellBuild(Protocol):
    def command(self, path_to_unpacked: str) -> list[str]:
        ...

@dataclass
class SetupPyBuild:
    subcommand: str
    """The subcommand for setup.py, e.g. build_ext for pandas"""

    def command(self, path_to_unpacked: str) -> list[str]:
        return ['python', os.path.join(path_to_unpacked, 'setup.py'), self.subcommand]

@dataclass
class _GithubSource(_Source):
    org: str
    """The github org (e.g. pandas-dev for pandas)"""

    repo: str
    """The repository (e.g. pandas for pandas)"""

    tag: str
    """The tag name to pull for this version (e.g. v1.5.0 for pandas 1.5.0)"""

@dataclass
class GithubReleaseSDistSource(_GithubSource):
    """A package where you can download an sdist from a Github release post."""
    package_name: str
    """
    The package name used for the release archive (e.g. pandas-1.5.0.tar.gz
    for pandas 1.5.0)
    """

    def url(self) -> str:
        return f'https://github.com/{self.org}/{self.repo}/releases/download/{self.tag}/{self.package_name}'

    def archive_name(self) -> str:
        return self.package_name

@dataclass
class GithubDevSource(_GithubSource):
    """
    A package where the only way to get it is to download an archive of the Github
    repo at a tag.
    """
    package_source_path: str = '.'

    def url(self) -> str:
        return f'https://github.com/{self.org}/{self.repo}/archive/refs/tags/{self.tag}.zip'

    def archive_name(self) -> str:
        return f'{self.tag}.zip'
