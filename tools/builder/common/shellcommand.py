"""builder.common.shellcommand: utilities for nicer shell processing"""

import subprocess
import io
import time
from typing import List, Optional


def run_simple(
    args: List[str],
    name: str,
    output: io.TextIOBase,
    cwd: Optional[str] = None,
    verbose: bool = False,
) -> str:
    """Run a shell command simple enough to run with the list-args subprocess Popen.

    Should stream the output of the process to output. Raises RuntimeError if the
    process fails, and cancels the process and propagates KeyboardInterrupt.
    """
    if verbose:
        print(" ".join(args), file=output)
    proc = subprocess.Popen(
        args,
        bufsize=100,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if not proc.stdout:
        raise RuntimeError(f"failed to communicate with {name} process")
    accumulated = b""
    try:
        while proc.poll() is None:
            # always read to prevent blocking on the pipe
            procwrote = proc.stdout.read()
            accumulated += procwrote
            # but only echo if verbose
            if verbose:
                output.write(procwrote.decode())
                output.flush()
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        proc.terminate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"{name} failed with {proc.returncode}: {accumulated.decode()}"
        )
    return accumulated.decode()
