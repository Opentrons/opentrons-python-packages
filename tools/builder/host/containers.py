"""Code for managing the containers to build the repo."""
import subprocess
import io
import os
from typing import List

import builder

CONTAINER_NAME = "ghcr.io/opentrons/python-package-builder"


def run_container(
    container_str: str,
    forwarded_argv: List[str],
    root_path: str,
    output: io.TextIOBase,
) -> None:
    """Run the container with a forwarded argv.

    container_str: a string suitable for passing to `docker run` that identifies
                   a container image.
    forwarded_argv: the arguments to pass to the container
    root_path: the path to the root of the packages repo
    output: an output file stream for capturing the container
    """
    print("Running build", file=output)
    invoke_str = _container_run_invoke_cmd(container_str, forwarded_argv, root_path)
    print(" ".join(invoke_str), file=output)
    proc = subprocess.Popen(
        invoke_str,
        bufsize=100,
        cwd=root_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if not proc.stdout:
        raise RuntimeError("failed to communicate with builder process")
    try:
        while proc.poll() is None:
            output.write(proc.stdout.read().decode())
            output.flush()
    except KeyboardInterrupt:
        proc.terminate()
    if proc.returncode != 0:
        raise RuntimeError(f"Build failed with {proc.returncode}")


def prep_container(root_path: str, force_build: bool, output: io.TextIOBase) -> str:
    """Prepare the container for the build.

    Params
    ------
    root_path: the path to the root of the packages repo
    force_build: if True, always build the container even if one is available
                 to pull
    output: file stream to send output logs to.

    For now, this just builds the container. In the future, it might pull
    it from a container repo instead.
    """
    _ = force_build
    return build_container(root_path, output)


def build_container(root_path: str, output: io.TextIOBase) -> str:
    """Build the docker container for the build locally.

    Params
    ------
    root_path: str, the absolute path to the root of the package repo
    output: file stream to send logs to

    """
    return _build_container(os.geteuid(), os.getegid(), root_path, output)


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
    effective_uid: int, effective_gid: int, root_path: str, output: io.TextIOBase
) -> str:
    """Build the docker container and return a keyword usable to run it."""
    invoke_str = _container_build_invoke_cmd(effective_uid, effective_gid, root_path)
    print("Creating container", file=output)
    print(" ".join(invoke_str), file=output)
    proc = subprocess.Popen(
        invoke_str,
        bufsize=100,
        cwd=root_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if not proc.stdout:
        raise RuntimeError("failed to communicate with builder process")
    try:
        while proc.poll() is None:
            output.write(proc.stdout.read().decode())
            output.flush()
    except KeyboardInterrupt:
        proc.terminate()
    if proc.returncode != 0:
        raise RuntimeError(f"Container build failed with {proc.returncode}")
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
