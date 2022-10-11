"""
builder.package_build - entrypoints for building python packages

This is the part of the builder package that actually builds python wheels,
using other internal components. This __init__ re-exports everything required
to import in a build.py for  a single package build.
"""
from typing import overload
from .types import GithubDevSource, GithubReleaseSDistSource
from .orchestrate import build_package


@overload
def github_source(
    *,
    org: str,
    repo: str,
    tag: str,
    sdist_archive: str,
    name: str | None = None,
) -> GithubReleaseSDistSource:
    pass


@overload
def github_source(
    *, org: str, repo: str, tag: str, name: str | None = None, path: str | None = None
) -> GithubDevSource:
    pass


def github_source(
    *,
    org: str,
    repo: str,
    tag: str,
    sdist_archive: str | None = None,
    name: str | None = None,
    path: str | None = None,
) -> GithubDevSource | GithubReleaseSDistSource:
    """
    Tell the system this package is fetched from github.

    Params
    ------
    org: str - the github org hosting the package, e.g. pandas-dev for pandas
    repo: str - the github repo with the package, e.g. pandas for pands
    tag: str - the tag for the release to use, e.g. v1.5.0 for pandas 1.5.0
    sdist_archive: str - if this repo posts an sdist as a github release artifact,
                         you can put the name of the sdist archive here and it will
                         be used instead of a full repo download. for pandas 1.5.0
                         downloaded using the sdist, this would be pandas-1.5.0.tar.gz
    path: Optional str - if downloading full repo archive, an optional path to a
                         subdirectory of this repo that has the actual code. the path
                         should be the directory containing the package metadata - the
                         pyproject.toml or setup.py or whatever.
    name: Optional str - a name for the source. If not specified, repo is used.
    """
    sourcename = name or repo
    if sdist_archive:
        return GithubReleaseSDistSource(
            name=sourcename, org=org, repo=repo, tag=tag, package_name=sdist_archive
        )
    return GithubDevSource(
        name=sourcename, org=org, repo=repo, tag=tag, package_source_path=path
    )


__all__ = ["github_source", "build_package"]
