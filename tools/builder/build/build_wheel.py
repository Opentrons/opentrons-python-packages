"""build.build_wheel - utilities to build a single wheel"""
import sys
from .types import ShellBuild
from builder.common.shellcommand import run_simple

def build_with_setup_py(command: str, source_dir: str, build_dir: str) -> str:
    """Build a package."""
    run_simple(['python', 'setup.py', command], 'build {buildable}', sys.stdout, cwd=in_dir)
