"""
builder.container.run: run the build inside a container
"""
import argparse
import io
from pathlib import Path
from builder.common import args
from builder import __version__
from builder.package_build.orchestrate import discover_build_packages_sync
from builder.package_build.types import GlobalBuildContext
from builder.common.shellcommand import ShellCommandFailed
import sys


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
    repo_base = Path(parsed_args.package_repo_base)

    try:
        run_build(
            Path(parsed_args.package_repo_base) / "packages",
            Path(parsed_args.buildroot_sdk_base),
            _ensure_path(repo_base, Path(parsed_args.build_tree_root)),
            _ensure_path(repo_base, Path(parsed_args.dist_tree_root)),
            parsed_args.output,
            parsed_args.verbose,
        )
    except ShellCommandFailed as scf:
        # Invert the usual verbosity logic here because if we're verbose, then
        # we already printed all the output as it happened; if we're not, then
        # we should make sure the user can see it.
        if not parsed_args.verbose:
            print(
                f"{scf.message}: {scf.returncode}: {''.join(scf.output)}",
                file=parsed_args.output,
            )
        else:
            print(f"{scf.message}: {scf.returncode}", file=parsed_args.output)
        sys.exit(1)
    except Exception as exc:
        if parsed_args.verbose:
            import traceback

            print("".join(traceback.format_exception(exc)), file=parsed_args.output)
        else:
            print(f"Build failed: {str(exc)}", file=parsed_args.output)
        sys.exit(2)
    sys.exit(0)


def _ensure_path(repo_base: Path, possibly_relative: Path) -> Path:
    if possibly_relative.is_absolute():
        return possibly_relative
    return (repo_base / possibly_relative).resolve()


def run_build(
    package_tree_root: Path,
    buildroot_sdk_base: Path,
    build_tree_root: Path,
    dist_tree_root: Path,
    output: io.TextIOBase,
    verbose: bool,
) -> None:
    """Run the build.

    Params
    ------

    package_tree_root: path to the tree of packages, each containing a build.py
    buildroot_sdk_base: path to the unzipped location of the buildroot sdk, containing
                        setup_environment
    build_tree_root: path to the tree of build directories
    dist_tree_root: path to the tree where distributables should go
    output: a text io that can be used to write build logs
    verbose: whether those logs should be verbose
    """
    print(f"Building with tools version {__version__}")
    context = GlobalBuildContext(
        output=output, verbose=verbose, sdk_path=buildroot_sdk_base
    )

    discover_build_packages_sync(
        package_tree_root, build_tree_root, dist_tree_root, context=context
    )
