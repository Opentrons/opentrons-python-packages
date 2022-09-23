"""
builder.container.run: run the build inside a container
"""
import argparse
import io
import subprocess
from pathlib import Path
from builder.common import args
from builder import __version__


def run_from_cmdline() -> None:
    """
    Run the build as a main function from a command line call.

    That means it may write to sys.stdout and may call sys.exit.
    """
    parser = argparse.ArgumentParser("Build the packages.")
    parser.add_argument(
        "--package-repo-base",
        type=str,
        help="Path to the build environment inside the container",
    )
    parser.add_argument(
        "--buildroot-sdk-base",
        type=str,
        help="Path to the downloaded and relocated sdk",
    )
    parser = args.add_common_args(parser)
    parsed_args = parser.parse_args()
    run_build(
        Path(parsed_args.package_repo_base),
        Path(parsed_args.buildroot_sdk_base),
        parsed_args.output,
        parsed_args.verbose,
    )


def _envmap_from_printenv(printenv_result: str) -> dict[str, str]:
    printenv_lines = iter(printenv_result.split("\n"))
    while next(printenv_lines).strip() != "__OT_OUTPUT__":
        continue
    environ_map: dict[str, str] = {}
    for line in printenv_lines:
        thisline = line.strip()
        if not thisline:
            continue
        lineparts = thisline.split("=")
        environ_map[lineparts[0]] = "=".join(lineparts[1:])
    return environ_map


def activate_environment(
    buildroot_sdk_base: Path, output: io.TextIOBase, verbose: bool
) -> dict[str, str]:
    print("Capturing buildroot SDK environment", file=output)
    cmd = [
        "/bin/bash",
        "-c",
        f'. {str(buildroot_sdk_base / "environment-setup")} && echo __OT_OUTPUT__ && printenv',
    ]
    if verbose:
        print(" ".join(cmd), file=output)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Buildroot SDK environment activation failed: {result.returncode}: {result.stderr} {result.stdout}"
        )
    if verbose:
        print(result.stdout, file=output)
    environ_map = _envmap_from_printenv(result.stdout)
    if verbose:
        print(f"Harvested buildroot SDK environ vars: {environ_map}", file=output)
    return environ_map


def run_build(
    package_repo_base: Path,
    buildroot_sdk_base: Path,
    output: io.TextIOBase,
    verbose: bool,
) -> None:
    """Run the build."""
    print(f"Building with tools version {__version__}")
    environ = activate_environment(buildroot_sdk_base, output, verbose)
    testfile = package_repo_base / "test.c"
    print(f"Building tiny little test file: {testfile.open().read()}", file=output)
    # There is some awful stuff going on with subprocess not really handling shell
    # calls with environment specs very well. Making the call one big string works
    # where the argslist approach does not.
    compile_args = " ".join(
        [
            f'PATH={environ["PATH"]}',
            "$CC",
            "-v",
            "$CFLAGS",
            str(package_repo_base / "test.c"),
            "-o",
            str(package_repo_base / "test.out"),
        ]
    )
    if verbose:
        print(" ".join(compile_args))
    result = subprocess.run(
        compile_args,
        cwd=str(package_repo_base),
        shell=True,
        env=environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if verbose:
        print(f"Build result: {result.stdout!r}", file=output)
    if result.returncode != 0:
        raise RuntimeError(
            f"Compile failed: {result.returncode}: {result.stdout!r}: {result.stderr!r}"
        )
    check_args = ["file", str(package_repo_base / "test.out")]
    if verbose:
        print(" ".join(check_args))
    result = subprocess.run(check_args, check=True, capture_output=True)
    print(result.stdout, file=output)
    assert b"ARM" in result.stdout
