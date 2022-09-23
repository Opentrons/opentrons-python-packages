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
    return parser
