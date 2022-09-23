"""external.run: interface for running the build from host shell"""
import argparse
import subprocess
import os
import sys
import io

from typing import List

import builder.common.args
import builder

ROOT_PATH = os.path.realpath(
    os.path.join(os.path.dirname(builder.__file__), os.path.pardir)
)
VOLUME_PATH = os.path.realpath(os.path.join(ROOT_PATH, os.path.pardir))


def run_from_cmdline() -> None:
    """
    Run as the main function from commandline.

    This function may write to stdout, and will swallow all exceptions and sys.exit
    if it gets them. It will also sys.exit if it succeeds. It should be called only
    from a command line wrapper.
    """
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        run_build(sys.argv, args, allow_sys_exit=True)
    except Exception as exc:
        if args.verbose:
            import traceback

            print("\n".join(traceback.format_exception(exc)), file=args.output)
        else:
            print(f"Build failed: {str(exc)}", file=args.output)


def run_build(
    argv: List[str], parsed_args: argparse.Namespace, /, allow_sys_exit: bool = False
) -> None:
    """
    Primary external interface - run the build.

    Parameters:
    argv: The sys.argv that should be used inside the container. In almost all cases
          this should be sys.argv.
    parsed_args: The result of calling build_arg_parser.parse_args(). This needs to
                 happen outside this function since if -h/--help is in the args, argparse
                 "helpfully" prints help and exits.
    allow_sys_exit (kw only): Allow this call to call sys.exit(). This is useful in a
                              direct command-line context and to be avoided otherwise.
    """
    container_str = _build_container(
        os.geteuid(), os.getegid(), parsed_args.output, allow_sys_exit
    )
    _run_build(container_str, argv[1:], parsed_args.output)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the common arguments used both inside and outside the container."""
    parser = argparse.ArgumentParser(description="Build the packages in this repo.")
    parser = builder.common.args.add_common_args(parser)
    return parser


def _container_image_name() -> str:
    version_no_metadata = builder.__version__.split("+")[0]
    return f"opentrons-python-packages-{version_no_metadata}"


def _container_build_invoke_cmd(effective_uid: int, effective_gid: int) -> List[str]:
    """Create the string used to invoke the container build"""
    return [
        "docker",
        "build",
        "-f",
        os.path.join(ROOT_PATH, "Dockerfile"),
        "-t",
        f"{_container_image_name()}",
        ROOT_PATH,
    ]


def _build_container(
    effective_uid: int, effective_gid: int, output: io.TextIOBase, allow_sys_exist: bool
) -> str:
    """Build the docker container and return a keyword usable to run it."""
    invoke_str = _container_build_invoke_cmd(effective_uid, effective_gid)
    print("Creating container", file=output)
    print(" ".join(invoke_str), file=output)
    proc = subprocess.Popen(
        invoke_str,
        bufsize=100,
        cwd=ROOT_PATH,
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
    print(f"Created container as {_container_image_name()}", file=output)
    return _container_image_name()


def _container_run_invoke_cmd(
    container_str: str, forwarded_argv: List[str]
) -> List[str]:
    """Build the string to run the container."""
    return [
        "docker",
        "run",
        "--rm",
        f"--volume={VOLUME_PATH}:/build-environment/python-package-index:rw,delegated",
        container_str,
    ] + forwarded_argv


def _run_build(
    container_str: str,
    forwarded_argv: List[str],
    output: io.TextIOBase,
    allow_sys_exit: bool = False,
) -> None:
    print("Running build", file=output)
    invoke_str = _container_run_invoke_cmd(container_str, forwarded_argv)
    print(" ".join(invoke_str), file=output)
    proc = subprocess.Popen(
        invoke_str,
        bufsize=100,
        cwd=ROOT_PATH,
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
