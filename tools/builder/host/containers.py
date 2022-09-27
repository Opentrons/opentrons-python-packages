"""Code for managing the containers to build the repo."""
import subprocess
import io
import os
from typing import List, Optional

import builder
from builder.common.shellcommand import run_simple

CONTAINER_NAME = "ghcr.io/opentrons/python-package-builder"
DEFAULT_TAG = "main"


def run_container(
    container_str: str,
    forwarded_argv: List[str],
    root_path: str,
    output: io.TextIOBase,
    verbose: bool = False,
) -> None:
    """Run the container with a forwarded argv.

    container_str: a string suitable for passing to `docker run` that identifies
                   a container image.
    forwarded_argv: the arguments to pass to the container
    root_path: the path to the root of the packages repo
    output: an output file stream for capturing the container
    """
    print("Running build", file=output)
    run_simple(
        _container_run_invoke_cmd(container_str, forwarded_argv, root_path),
        name="container build",
        output=output,
        verbose=verbose,
    )
    print("Build complete", file=output)


def prep_container(
    root_path: str,
    output: io.TextIOBase,
    pull_tag: Optional[str] = None,
    require_tag: bool = False,
    force_build: bool = False,
    verbose: bool = False,
) -> str:
    """Prepare the container for the build.

    Params
    ------
    root_path: the path to the root of the packages repo
    output: file stream to send output logs to.
    pull_tag: the tag to pull from ghcr. if pull_tag is not specified,
              this will use "latest". if require_tag is True, a failure
              to pull will cause an error; otherwise fall back to a local build.
              if force_build is True, do not attempt to push, but instead always
              build. Specifying both force_build=True and require_tag=True is
              an error.
    require_tag: if True, raise an error if the specified tag cannot be pulled.
    force_build: if True, always build the container even if one is available
                 to pull
    """
    if pull_tag is None:
        tag = DEFAULT_TAG
    else:
        tag = pull_tag
    if not force_build:
        try:
            return pull_container(tag, output, verbose=verbose)
        except RuntimeError:
            output.write(f"Failed to pull {tag}")
            pass
    if require_tag:
        raise RuntimeError(f"Could not pull {tag}")
    return build_container(root_path, output, verbose=verbose)


def pull_container(tag: str, output: io.TextIOBase, verbose: bool = False) -> str:
    """
    pull a version of the build container from ghci.

    Params
    ------

    tag: the tag to pull. main will be the latest push to main, dev-(branchname)
    might work if the branch is active. latest will be the latest released version.
    an explicit version tag will also work.
    """
    container_name = f"{CONTAINER_NAME}:{tag}"
    print(f"Attempting to pull {container_name}", file=output)
    pull_cmd = ["docker", "pull", container_name]
    run_simple(pull_cmd, name="pull", output=output, verbose=verbose)

    ls_result = subprocess.run(
        ["docker", "images", "-q", container_name], capture_output=True, check=True
    )

    images = ls_result.stdout.decode().strip().split("\n")
    if len(images) > 1:
        output.write(f"Found {len(images)} images, using first")
    elif len(images) == 0:
        raise RuntimeError("Could not find image after pull")
    print(f"Pulled {container_name} as {images[0]}", file=output)
    return images[0]


def build_container(
    root_path: str, output: io.TextIOBase, verbose: bool = False
) -> str:
    """Build the docker container for the build locally.

    Params
    ------
    root_path: str, the absolute path to the root of the package repo
    output: file stream to send logs to

    """
    return _build_container(
        os.geteuid(), os.getegid(), root_path, output, verbose=verbose
    )


def _container_image_specific() -> str:
    version_no_metadata = builder.__version__.split("+")[0]
    return f"{CONTAINER_NAME}:{version_no_metadata}"


def _container_image_latest() -> str:
    return f"{CONTAINER_NAME}:latest"


def _container_build_invoke_cmd(
    effective_uid: int, effective_gid: int, root_path: str
) -> List[str]:
    """Create the string used to invoke the container build"""
    return [
        "docker",
        "build",
        "-f",
        os.path.join(root_path, "Dockerfile"),
        "-t",
        f"{_container_image_specific()}",
        "-t",
        f"{_container_image_latest()}",
        root_path,
    ]


def _build_container(
    effective_uid: int,
    effective_gid: int,
    root_path: str,
    output: io.TextIOBase,
    verbose: bool = False,
) -> str:
    """Build the docker container and return a keyword usable to run it."""
    print("Creating container", file=output)
    invoke_str = _container_build_invoke_cmd(effective_uid, effective_gid, root_path)
    run_simple(
        invoke_str,
        name="build container",
        output=output,
        cwd=root_path,
        verbose=verbose,
    )
    print(f"Created container: {_container_image_specific()}", file=output)
    return _container_image_specific()


def _container_run_invoke_cmd(
    container_str: str, forwarded_argv: List[str], root_path: str
) -> List[str]:
    """Build the string to run the container."""
    volume_path = os.path.realpath(os.path.join(root_path, os.path.pardir))
    return [
        "docker",
        "run",
        "--rm",
        f"--volume={volume_path}:/build-environment/python-package-index:rw,delegated",
        container_str,
    ] + forwarded_argv
