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
        "--prep-container-only",
        action="store_true",
        help="Prepare the container and exit before running the package build.",
    )
    parser.add_argument(
        "--force-container-build",
        action="store_true",
        help="Always build the container even if one is available upstream",
    )

    return parser
