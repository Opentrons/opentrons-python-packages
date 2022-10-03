"""common.args: common code that builds arguments"""

import sys
import argparse


def add_common_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--output",
        "-o",
        action="store",
        type=argparse.FileType("w"),
        default=sys.stdout,
        help="Where to write build logging output (- for stdout)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Whether verbose output should be written",
    )
    parser.add_argument(
        "--container-tag",
        action="store",
        default="main",
        help="Container tag to pull. default: main",
    )
    parser.add_argument(
        "--container-source",
        action="store",
        choices=["build", "pull", "any"],
        default="any",
        help=(
            "How to get the build container. build: do not attempt "
            "to pull, but build locally. pull: always pull, and fail "
            "if the tag cannot be pulled. any: try to pull, but build "
            "if the pull fails. default: any"
        ),
    )
    parser.add_argument(
        "--prep-container-only",
        action="store_true",
        help="Prepare the container and exit before running the package build.",
    )
    parser.add_argument(
        "--dist-tree-root",
        action="store",
        default="./dist",
        help="Location for the tree of package distributables",
    )
    parser.add_argument(
        "--build-tree-root",
        action="store",
        default="./build",
        help="Location for the tree of package build areas",
    )

    return parser
