#!/usr/bin/env python3
# /// script
# requires-python = "==3.10.*"
# dependencies = [
#     "rich",
# ]
# ///

"""
Dependencies:
    - uv
    - Docker (with buildx configured)

Usage:
    uv run local.py
"""

import os
import subprocess
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live

# Create a console without timestamps or file logging
console = Console(log_time=False, log_path=False)

PACKAGES_PATH = Path(Path(__file__).parent, "packages")
if not PACKAGES_PATH.exists():
    console.log("[bold red]Error:[/bold red] The 'packages' directory does not exist.")
    exit(1)


def package_name_from_path(package_path: Path) -> str:
    """
    Generate a package name from its path.
    Example: If package is at packages/foo/1.0.0, returns 'foo:1.0.0'
    """
    return f"{package_path.parent.name}:{package_path.name}"


def test_package_name_from_path(package_path: Path) -> str:
    """
    Generate a test image tag for the package.
    Example: If package is at packages/foo/1.0.0, returns 'foo-test:1.0.0'
    """
    return f"{package_path.parent.name}-test:{package_path.name}"


def find_all_packages() -> list:
    """
    Find all package directories in the 'packages' directory.
    Returns:
        list: A list of Path objects representing each package directory.
    """
    package_parents = [d for d in PACKAGES_PATH.iterdir() if d.is_dir()]
    packages = [d for parent in package_parents for d in parent.iterdir() if d.is_dir()]
    if not packages:
        console.log(
            "[bold red]Error:[/bold red] No packages found in the 'packages' directory."
        )
        exit(1)
    console.log(f"[bold green]Found {len(packages)} package(s):[/bold green]")
    for package in packages:
        console.log(f" - {package_name_from_path(package)}")
    return packages


def run_command(command: list, cwd: str = None) -> bool:
    """
    Run a shell command and log its output.

    Args:
        command (list): List of command arguments.
        cwd (str or Path, optional): Working directory for the command.

    Returns:
        bool: True if the command succeeded, False otherwise.
    """
    console.log(
        f"[bold green]Running:[/bold green] {' '.join(command)} (cwd: {cwd or os.getcwd()})"
    )
    try:
        result = subprocess.run(
            command, cwd=cwd, check=True, text=True, capture_output=True
        )
        console.log(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        console.log(f"[bold red]Error:[/bold red] {e.stderr}")
        return False


def run_command_live(
    command: list, cwd: str = None, title: str = "Running Command"
) -> str:
    """
    Run a shell command with live output using Rich Live.

    Args:
        command (list): List of command arguments.
        cwd (str or Path, optional): Working directory for the command.
        title (str): Title for the live panel.

    Returns:
        str: The combined output of the command.

    Raises:
        RuntimeError: If the command fails.
    """
    output_lines = []
    live_panel = Panel(
        Text("", overflow="fold"), title=title, border_style="blue", expand=True
    )
    with Live(live_panel, refresh_per_second=4) as live:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        )
        for line in process.stdout:
            output_lines.append(line.rstrip())
            live.update(
                Panel(
                    Text("\n".join(output_lines), overflow="fold"),
                    title=title,
                    border_style="blue",
                    expand=True,
                )
            )
        process.wait()
        if process.returncode != 0:
            raise RuntimeError(
                f"Command {' '.join(command)} failed with exit code {process.returncode}"
            )
    return "\n".join(output_lines)


def create_output_directory(package: Path) -> None:
    """
    Create the output directory (package/output).

    Args:
        package (Path): The package directory.
    """
    output_dir = Path(package, "output")
    output_dir.mkdir(parents=True, exist_ok=True)
    console.log(f"[bold green]Output directory created at {output_dir}[/bold green]")


def build_docker_image(package: Path) -> str:
    """
    Build the Docker image and export the wheel using docker buildx.

    Args:
        package (Path): The package directory.

    Returns:
        str: The captured output from the Docker build command.
    """
    build_cmd = [
        "docker",
        "buildx",
        "build",
        "--platform",
        "linux/arm64",
        "-t",
        package_name_from_path(package),
        "--output",
        "type=local,dest=output",
        ".",
    ]
    console.log(
        f"[bold green]Building Docker image for {package_name_from_path(package)}...[/bold green]"
    )
    output = run_command_live(
        build_cmd,
        cwd=str(package),
        title=f"Docker Build: {package_name_from_path(package)}",
    )
    console.log(
        f"[green]Docker build completed for {package_name_from_path(package)}![/green]"
    )
    return output


def build_and_run_test_container(package: Path) -> str:
    """
    Build and run the Docker container to test the installation of the wheel.

    Args:
        package (Path): The package directory used to tag the Docker image.

    Returns:
        str: The combined output from the build and run test commands.
    """
    image_tag = test_package_name_from_path(package)
    build_cmd = ["docker", "build", "-f", "DockerfileTest", "-t", image_tag, "."]
    console.log(f"[bold green]Building Docker test image '{image_tag}'...[/bold green]")
    build_output = run_command_live(
        build_cmd, cwd=str(package), title=f"Test Build: {image_tag}"
    )
    console.log(f"[green]Docker test image '{image_tag}' built successfully![/green]")

    run_cmd = ["docker", "run", "--rm", image_tag]
    console.log(
        f"[bold green]Running Docker test container from image '{image_tag}'...[/bold green]"
    )
    run_output = run_command_live(
        run_cmd, cwd=str(package), title=f"Test Run: {image_tag}"
    )
    console.log(f"[green]Test container '{image_tag}' ran successfully![/green]")

    return f"{build_output}\n{run_output}"


def main():
    """
    Main process to build the packages and run tests.
    """
    console.rule("[bold blue]Build all packages[/bold blue]")
    packages = find_all_packages()

    for package in packages:
        console.log(
            f"\n[bold yellow]Processing package: {package_name_from_path(package)}[/bold yellow]"
        )
        create_output_directory(package)
        try:
            build_docker_image(package)
        except RuntimeError as e:
            console.log(f"[bold red]Error:[/bold red] {e}")
            continue

    console.rule("[bold blue]Build Process Completed Successfully! 🎉[/bold blue]")
    console.rule("[bold magenta]Running Tests for All Packages[/bold magenta]")

    for package in packages:
        package_name = package_name_from_path(package)
        console.print(
            f"[bold yellow]Running tests for package: {package_name}...[/bold yellow]"
        )
        try:
            test_output = build_and_run_test_container(package)
        except RuntimeError as e:
            test_output = f"Error running tests: {e}"
        wrapped_text = Text(test_output, overflow="fold")
        console.print(
            Panel(
                wrapped_text,
                title=f"Test: {package_name}",
                border_style="yellow",
                expand=True,
            )
        )

    console.rule("[bold magenta]All Tests Completed 🎉[/bold magenta]")


if __name__ == "__main__":
    main()
