# /// script
# requires-python = "==3.10.*"
# dependencies = [
#     "rich",
# ]
# ///

#### RUN ME WITH ####
'''
uv run go.py
'''
#####################
import subprocess
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.text import Text

console = Console()

def main():
    cmd = (
        'docker buildx build --platform linux/arm64 -t test-pyscard . && '
        'docker run --platform linux/arm64 --rm test-pyscard'
    )

    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    output_panel = Panel("", title="[bold cyan]Docker Build and Run[/bold cyan]", border_style="cyan")
    output_text = Text()

    with Live(output_panel, console=console, refresh_per_second=4):
        for line in iter(process.stdout.readline, ''):
            output_text.append(line, style="white")
            output_panel.renderable = output_text

    process.stdout.close()
    return_code = process.wait()

    if return_code:
        console.print(f"\n[bold red]Command exited with code {return_code}[/bold red]")
        exit(return_code)
    else:
        console.print("\n[bold green]Docker command completed successfully![/bold green]")

if __name__ == '__main__':
    main()
