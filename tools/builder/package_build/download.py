"""
builder.package_build.download - tools to download package sources
"""

import os
import zipfile
import tarfile
import requests
from pathlib import Path
from .types import HTTPFetchableSource, GlobalBuildContext


def fetch_source(
    source: HTTPFetchableSource, to_path: Path, *, context: GlobalBuildContext
) -> Path:
    """Fetch a source to a specified download directory."""
    context.write(f"Fetching {source.name} from {source.url()}")
    download_to = to_path / source.archive_name()
    with (
        requests.get(source.url(), stream=True) as response,
        open(download_to, "wb") as writefile,
    ):
        response.raise_for_status()
        for chunk in response.iter_content(chunk_size=None):
            writefile.write(chunk)
    return download_to


def unpack_source(
    path: Path, archive: Path, from_archive_path: Path, *, context: GlobalBuildContext
) -> Path:
    """Unpack a downloaded archive. Returns the path to the actual content - if the
    top level of the archive that is unpacked (either the top level, or from_archive_path)
    is a directory, the returned path includes that directory."""
    if ".tar" in archive.name:
        return _unpack_tar_to(path, archive, from_archive_path, context=context)
    else:
        return _unpack_zip_to(path, archive, from_archive_path, context=context)


def _verify_tar_member(
    path: Path, member: tarfile.TarInfo, *, context: GlobalBuildContext
) -> tarfile.TarInfo:
    unpack_to = Path(os.path.realpath(path / Path(member.name).name))
    try:
        common = Path(os.path.commonpath([unpack_to, path]))
    except ValueError:
        pass
    if common != path:
        raise RuntimeError(
            f"Will not unpack archive member {member.name} to {unpack_to}: outside unpack dir: {common}"
        )
    # this archive member is trying to unpack itself somewhere above
    # the unpack location, i.e. contains a path traversal (possibly by
    # accident but we still can't allow it)
    dest = path / member.name
    match member.type:
        case tarfile.LNKTYPE | tarfile.SYMTYPE:
            target_realpath = Path(os.path.realpath(path / member.linkname))
            try:
                common = Path(os.path.commonpath([unpack_to, target_realpath]))
            except ValueError:
                pass
            if common != unpack_to:
                raise RuntimeError(
                    f"Will not unpack archive member {member.name}: links outside unpack dir"
                )
            context.write_verbose(f"unpack: {dest} (symlink to {target_realpath} ok")
        case tarfile.REGTYPE:
            context.write_verbose(f"unpack: {dest} file ok")
        case tarfile.DIRTYPE:
            context.write_verbose(f"unpack: {dest} directory ok")
        case _:
            raise RuntimeError(
                f"Cannot handle archive member of type {str(member.type)}"
            )
    return member


def _unpack_member_to(
    tf: tarfile.TarFile,
    path: Path,
    member: tarfile.TarInfo,
    from_archive_path: Path,
    *,
    context: GlobalBuildContext,
) -> Path | None:
    # make sure this is something we can unpack
    verified = _verify_tar_member(path, member, context=context)
    # if this member is not inside from_archive_path, don't extract it
    try:
        common = Path(os.path.commonpath([verified.name, from_archive_path]))
    except ValueError:
        pass
    if common != from_archive_path:
        return None
    destpath = path / Path(verified.name).relative_to(from_archive_path)
    context.write_verbose(f"unpack: {path} -> {destpath}")
    tf.extract(verified, path, set_attrs=True)
    return destpath


def _unpack_tar_to(
    path: Path, archive: Path, from_archive_path: Path, *, context: GlobalBuildContext
) -> Path:
    context.write(f"Untarring {archive} to {path}")
    with tarfile.open(archive, "r") as tf:
        members = sorted(tf.getmembers(), key=lambda m: m.name, reverse=True)
        unpacked = [
            _unpack_member_to(tf, path, member, from_archive_path, context=context)
            for member in members
        ]
        return Path(
            os.path.commonpath(
                [unpacked_file for unpacked_file in unpacked if unpacked_file]
            )
        )


def _unpack_zip_to(
    path: Path, archive: Path, from_archive_path: Path, *, context: GlobalBuildContext
) -> Path:
    context.write(f"Unzipping {archive} to {path}")
    unzipped: list[Path] = []
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            # skip archive members not in the from_archive_path
            try:
                common = Path(os.path.commonpath([member.filename, from_archive_path]))
            except ValueError:
                pass
            if common != from_archive_path:
                continue
            # and then just extract them, because zipfile extraction prevents
            # traversal unlike tarfile extraction
            context.write_verbose(
                f"unpack: {member.filename} -> {path/member.filename}"
            )
            unzipped.append(Path(zf.extract(member, path=path)))
    return Path(os.path.commonpath(unzipped))
