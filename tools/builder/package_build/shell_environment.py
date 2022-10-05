"""shell_environment - utils for running commands through the shell."""
import subprocess
from pathlib import Path
from contextlib import contextmanager
from io import TextIOBase
from dataclasses import dataclass
from typing import Callable, TypeVar, Type, Iterator, cast
import shlex
import re
import time
from functools import wraps
from builder.common.shellcommand import ShellCommandFailed

_SubshellType = TypeVar("_SubshellType", bound="SDKSubshell")
EchoFunc = Callable[[str], None]


@dataclass
class _SubshellHandles:
    stdin: TextIOBase
    stdout: TextIOBase


class SDKSubshell:
    """
    Manages a concurrently-running subshell with the buildroot SDK
    active. Since the SDK manipulates the shell environment, we need
    to either activate it every time or keep a consistent subshell
    for each package.

    Make an instance of this class for each package build.

    Use the classmethod build to build this class so the SDK gets activated
    correctly.
    """

    _result_re = re.compile(r"^xxxresultxxx:xxx(-?\d+)xxx$", flags=re.MULTILINE)

    @staticmethod
    def echo_wrap_prevent_double_newlines(echoer: EchoFunc) -> EchoFunc:
        @wraps(echoer)
        def _remove_nl_wrapper(logstr: str) -> None:
            if logstr.endswith("\n"):
                logstr = logstr[:-1]
            echoer(logstr)

        return _remove_nl_wrapper

    @classmethod
    @contextmanager
    def scoped(
        cls: Type[_SubshellType],
        in_directory: Path,
        sdk_path: Path,
        echo: EchoFunc | None = None,
        echo_verbose: EchoFunc | None = None,
    ) -> Iterator[_SubshellType]:
        """
        Provides a context manager entry for the shell instance that automatically
        stops it when the context is left. For a persistent version without a context
        manager use persistent().
        """
        instance = cls.persistent(in_directory, sdk_path, echo, echo_verbose)
        try:
            yield instance
        finally:
            instance.stop()

    @classmethod
    def persistent(
        cls: Type[_SubshellType],
        in_directory: Path,
        sdk_path: Path,
        echo: EchoFunc | None = None,
        echo_verbose: EchoFunc | None = None,
    ) -> _SubshellType:
        """
        Build a persistent subshell that can be passed around. Must be stopped
        explicitly. For a scoped instance that is a context manager, use scoped().
        """
        subshell = cls(in_directory, echo, echo_verbose)
        subshell._initiate_sdk(sdk_path)
        return subshell

    def stop(self) -> None:
        """stops the running shell"""
        self._proc.terminate()
        while self._proc.poll():
            time.sleep(0.1)

    def run(self, cmd: list[str]) -> str:
        return "\n".join(self._guarded_shellcall(shlex.join(cmd)))

    def initiate_python_environment(self, sdk_path: Path) -> None:
        """
        Prepare the shell environment for building python.

        This _must_ be called _before_ you try and build packages and _after_
        any python-side prep (activating venvs, installing dependencies) because
        it messes with extremely core python behavior in the shell.
        """
        sysroot = sdk_path / "arm-buildroot-linux-gnueabihf" / "sysroot"
        sysconfigdata_name = "_sysconfigdata__linux_arm-linux-gnueabihf"
        pythonpath = sysroot / "usr" / "lib" / "python3.10"
        self._guarded_shellcall("export _PYTHON_HOST_PLATFORM=linux-x86_64-linux-gnu")
        self._guarded_shellcall(
            f"export _PYTHON_SYSCONFIGDATA_NAME={sysconfigdata_name}"
        )
        self._guarded_shellcall(f"export PYTHONPATH={pythonpath}")
        self._guarded_shellcall("export SETUPTOOLS_USE_DISTUTILS=stdlib")
        self._guarded_shellcall(f"export _python_sysroot={sysroot}")
        self._guarded_shellcall("export _python_prefix=/usr")
        self._guarded_shellcall("export _python_exec_prefix=/usr")
        self._guarded_shellcall("export PYTHONNOUSERSITE=1")

    def _shellcall(
        self,
        cmd: str,
        handles: _SubshellHandles,
        *,
        command_echo_is_verbose: bool = False,
    ) -> tuple[int, list[str]]:
        """Run a call in the shell and check that it succeeded.

        return code detection only really works if the return code of cmd is
        relevant to the main thing that happens in cmd. that means that cmd shouldn't
        have || clauses and really should just have one actual command.

        Returns a tuple of (call retcode, stdout + stderr)
        """
        if cmd.endswith("\n"):
            cmd = cmd[:-1]
        cmd += ' ; echo "xxxresultxxx:xxx$?xxx"\n'
        if command_echo_is_verbose:
            self._echo_verbose(cmd)
        else:
            self._echo(cmd)
        handles.stdin.write(cmd)
        stdout_lines: list[str] = []
        while True:
            stdout = handles.stdout.readline()
            self._echo_verbose(stdout)
            stdout_lines.append(stdout)
            if match := self._result_re.search(stdout):
                return int(match.group(1)), stdout_lines

    def _guarded_shellcall(
        self, cmd: str, *, command_echo_is_verbose: bool = False
    ) -> list[str]:
        """run a shellcall and return its result. raise if the call failed."""
        with self._guard() as handles:
            result, stdout = self._shellcall(
                cmd, handles, command_echo_is_verbose=command_echo_is_verbose
            )
            if result != 0:
                stdout_log = "".join(stdout[:-1])
                raise ShellCommandFailed(
                    command=cmd,
                    returncode=result,
                    message="command failed",
                    output=stdout_log,
                )
            return stdout

    def _initiate_sdk(self, sdk_path: Path) -> None:
        self._guarded_shellcall(
            f"source {sdk_path}/environment-setup", command_echo_is_verbose=True
        )

    def __init__(
        self,
        in_directory: Path,
        echo: EchoFunc | None,
        echo_verbose: EchoFunc | None,
    ) -> None:
        self._proc = subprocess.Popen(
            ["/usr/bin/env", "bash", "-i"],
            cwd=in_directory,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            stdin=subprocess.PIPE,
            bufsize=1,
            text=True,
        )
        self._echo: EchoFunc = echo or (lambda _: None)
        self._echo_verbose: EchoFunc = echo or (lambda _: None)

    @contextmanager
    def _guard(self) -> Iterator[_SubshellHandles]:
        """Makes sure that the process is open and exposes typed handles
        to (in order) stdin, stdout, stderr"""
        if self._proc.poll() is not None:
            raise RuntimeError("Subshell closed")
        yield _SubshellHandles(
            stdin=cast(TextIOBase, self._proc.stdin),
            stdout=cast(TextIOBase, self._proc.stdout),
        )
