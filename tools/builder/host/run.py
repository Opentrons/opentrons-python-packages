"""external.run: interface for running the build from host shell"""
import argparse
import os
import sys

from typing import List, NoReturn

import builder.common.args
from builder.common.shellcommand import ShellCommandFailed
import builder

from .containers import run_container, prep_container

ROOT_PATH = os.path.realpath(
    os.path.join(os.path.dirname(builder.__file__), os.path.pardir)
)


def run_from_cmdline() -> NoReturn:
    """
    Run as the main function from commandline.

    This function may write to stdout, and will swallow all exceptions and sys.exit
    if it gets them. It will also sys.exit if it succeeds. It should be called only
    from a command line wrapper.
    """
    parser = build_arg_parser()
    args = parser.parse_args()
    try:
        run_build(sys.argv, args)
    except ShellCommandFailed as scf:
        # Special handling for shell commands that fail: mostly they're not going to
        # be interesting especially if they're from the package build
        if "docker run" in scf.command or not args.verbose:
            print(f"{scf.message}", file=args.output)
        else:
            print(str(scf), file=args.output)
        if "docker run" in scf.command:
            sys.exit(1)
        else:
            sys.exit(2)
    except Exception as exc:
        if args.verbose:
            import traceback

            print("".join(traceback.format_exception(exc)), file=args.output)
        else:
            print(f"Build failed: {str(exc)}", file=args.output)
        sys.exit(2)
    sys.exit(0)


def run_build(argv: List[str], parsed_args: argparse.Namespace) -> None:
    """
    Primary external interface - run the build.

    Parameters:
    argv: The sys.argv that should be used inside the container. In almost all cases
          this should be sys.argv.
    parsed_args: The result of calling build_arg_parser.parse_args(). This needs to
                 happen outside this function since if -h/--help is in the args, argparse
                 "helpfully" prints help and exits.
    """
    if parsed_args.container_source == "any":
        force_container_build = False
        require_tag = False
    elif parsed_args.container_source == "build":
        force_container_build = True
        require_tag = False
    elif parsed_args.container_source == "pull":
        force_container_build = False
        require_tag = True
    else:
        raise RuntimeError("update handling of container source arg")
    container_str = prep_container(
        ROOT_PATH,
        parsed_args.output,
        pull_tag=parsed_args.container_tag,
        force_build=force_container_build,
        require_tag=require_tag,
        verbose=parsed_args.verbose,
    )
    if parsed_args.prep_container_only:
        return
    run_container(container_str, argv[1:], ROOT_PATH, parsed_args.output, True)


def build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the common arguments used both inside and outside the container."""
    parser = argparse.ArgumentParser(description="Build the packages in this repo.")
    parser = builder.common.args.add_common_args(parser)
    return parser
