"""builder.common.shellcommand: utilities for nicer shell processing"""

import subprocess
import io
import time
from typing import List, Optional


class ShellCommandFailed(RuntimeError):
    def __init__(
        self, command: str, returncode: int, message: str, output: str
    ) -> None:
        self.command = command
        self.returncode = returncode
        self.message = message
        self.output = output

    def __str__(self) -> str:
        return f"{self.message}: {self.command} returned code {self.returncode} "

    def __repr__(self) -> str:
        return f"<ShellCommandFailed: {self.command} returned {self.returncode}>"


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
        text=True,
    )
    if not proc.stdout:
        raise RuntimeError(f"failed to communicate with {name} process")
    accumulated = []
    try:
        while proc.poll() is None:
            # always read to prevent blocking on the pipe
            procwrote = proc.stdout.readline()
            accumulated.append(procwrote)
            # but only echo if verbose
            if verbose:
                output.write(procwrote)
                output.flush()
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        proc.terminate()
    if proc.returncode != 0:
        raise ShellCommandFailed(
            command=" ".join(args),
            returncode=proc.returncode,
            message=f"{name} failed",
            output="\n".join(accumulated),
        )
    return "\n".join(accumulated)
