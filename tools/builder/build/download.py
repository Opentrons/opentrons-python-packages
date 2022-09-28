"""
builder.build.download - tools to download package sources
"""

import os
import zipfile
import tarfile
import requests
from .types import HTTPFetchableSource

def fetch_source(source: HTTPFetchableSource, to_path: str) -> str:
    """Fetch a source to a specified download directory."""
    download_to = os.path.join(to_path, source.archive_name())
    with (requests.get(source.url(), stream=True) as response,
          open(download_to, 'wb') as writefile):
        response.raise_for_status()
        for chunk in response.iter_content(chunksize=None):
            writefile.write(chunk)
    return download_to

def unpack_source(path: str, archive: str, from_archive_path: str) -> list[str]:
    """Unpack a downloaded archive. Returns list of files at unpacked locations."""
    if '.tar' in archive:
        return _unpack_tar_to(path, archive, from_archive_path)
    else:
        return _unpack_zip_to(path, archive, from_archive_path)

def _verify_tar_member(
        path: str, member: tarfile.TarInfo) -> tarfile.TarInfo:
    unpack_to = os.path.realpath(os.path.join(path, member.name))
    try:
        common = os.path.commonpath(unpack_to, path)
    except ValueError:
        pass
    if common != unpack_to:
        raise RuntimeError(f'Will not unpack archive member {member.name}: outside unpack dir')
    # this archive member is trying to unpack itself somewhere above
    # the unpack location, i.e. contains a path traversal (possibly by
    # accident but we still can't allow it)

    if member.islnk() or member.issym():
        target_realpath = os.path.realpath(os.path.join(path, member.linkname))
        try:
            common = os.path.commonpath(unpack_to, target_realpath)
        except ValueError:
            pass
        if common != unpack_to:
            raise RuntimeError(f'Will not unpack archive member {member.name}: links outside unpack dir')
    if member.type not in (tarfile.REGTYPE, tarfile.LNKTYPE, tarfile.SYMTYPE, tarfile.DIRTYPE):
        raise RuntimeError(f'Cannot handle archive member of type {member.type}')
    return os.path.join(path, member.name)

def _unpack_member_to(
        tf: tarfile.TarFile,
        path: str,
        member: tarfile.TarInfo,
        from_archive_path: str) -> str | None:
    # make sure this is something we can unpack
    verified = _verify_tar_member(path, member)
    # if this member is not inside from_archive_path, don't extract it
    try:
        common = os.path.commonpath(verified.name, from_archive_path)
    except ValueError:
        pass
    if common != from_archive_path:
        return None
    destpath = os.path.join(path, os.path.relpath(from_archive_path, verified.name))
    # extract the member, which should be safe because we've passed this through
    # _verify_tar_member
    tf.extract(verified, destpath, set_attrs=True)
    return destpath

def _unpack_tar_to(path: str, archive: str, from_archive_path: str) -> list[str]:
    with tarfile.open(archive, 'r') as tf:
        verified = [member.name for member in tf.getmembers()]
        members = sorted(tf.getmembers(), key=lambda m: m.name, reverse=True)
        return [_unpack_member_to(tf, path, member, from_archive_path)
                for member in members]

def _unpack_zip_to(path: str, archive: str, from_archive_path: str) -> list[str]:
    unzipped: list[str] = []
    with zipfile.ZipFile(archive) as zf:
        for member in zf.infolist():
            # skip archive members not in the from_archive_path
            try:
                common = os.path.commonpath(member.name, from_archive_path)
            except ValueError:
                pass
            if common != from_archive_path:
                continue
            # and then just extract them, because zipfile extraction prevents
            # traversal unlike tarfile extraction
            unzipped.append(zf.extract(member, path=path))
    return unzipped
