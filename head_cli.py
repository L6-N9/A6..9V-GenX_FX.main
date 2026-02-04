#!/usr/bin/env python3
"""
Head CLI - Unified Command Line Interface for GenX Trading Platform
Wraps all existing CLI tools into a single, organized interface
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Union

import typer
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table
from rich.tree import Tree

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Typer app and Rich console
app = typer.Typer(
    help="🚀 GenX Trading Platform - Head CLI",
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
)
console = Console()


class HeadCLI:
    """
    The main class for the Head CLI, which acts as a unified interface for
    all other CLI tools in the GenX Trading Platform.
    """

    def __init__(self):
        """
        Initializes the HeadCLI, defining the available CLI modules.
        """
        self.project_root = Path.cwd()
        self.available_clis = {
            "amp": {
                "file": "amp_cli.py",
                "description": "Automated Model Pipeline - AI trading models and authentication",
                "commands": [
                    "update",
                    "plugin-install",
                    "config-set",
                    "verify",
                    "test",
                    "deploy",
                    "status",
                    "auth",
                    "schedule",
                    "monitor",
                ],
            },
            "genx": {
                "file": "genx_cli.py",
                "description": "GenX FX - Complete trading system management",
                "commands": [
                    "status",
                    "init",
                    "config",
                    "logs",
                    "tree",
                    "excel",
                    "forexconnect",
                ],
            },
            "chat": {
                "file": "simple_amp_chat.py",
                "description": "Interactive chat with AMP trading system",
                "commands": ["interactive"],
            },
        }

    def run_cli_command(
        self, cli_name: str, command: str, args: List[str] = None
    ) -> int:
        """
        Runs a command from a specific CLI module as a subprocess.

        Args:
            cli_name (str): The name of the CLI module to use.
            command (str): The command to execute.
            args (List[str], optional): A list of additional arguments for the command. Defaults to None.

        Returns:
            int: The exit code of the subprocess.
        """
        if cli_name not in self.available_clis:
            console.print(f"❌ [red]Unknown CLI: {cli_name}[/red]")
            return 1

        cli_info = self.available_clis[cli_name]
        cli_file = self.project_root / cli_info["file"]

        if not cli_file.exists():
            console.print(f"❌ [red]CLI file not found: {cli_file}[/red]")
            return 1

        # Build command
        cmd = ["python3", str(cli_file)]
        if command != "interactive":
            cmd.append(command)
        if args:
            cmd.extend(args)

        try:
            # Run the command
            if cli_name == "chat" and command == "interactive":
                # For interactive chat, use subprocess.run without capture
                return subprocess.run(cmd).returncode
            else:
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.stdout:
                    console.print(result.stdout)
                if result.stderr:
                    console.print(f"[red]{result.stderr}[/red]")
                return result.returncode
        except Exception as e:
            console.print(f"❌ [red]Error running command: {e}[/red]")
            return 1

    def show_overview(self):
        """
        Shows a system overview, including available CLI tools and a quick
        status check.
        """
        console.print(
            Panel.fit(
                "[bold blue]🚀 GenX Trading Platform - Head CLI[/bold blue]\n"
                "[dim]Unified interface for all trading system components[/dim]",
                border_style="blue",
            )
        )

        # Show available CLIs
        table = Table(title="📋 Available CLI Tools", show_header=True)
        table.add_column("CLI", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_column("Status", style="green")

        for cli_name, cli_info in self.available_clis.items():
            cli_file = self.project_root / cli_info["file"]
            status = "✅ Available" if cli_file.exists() else "❌ Missing"
            table.add_row(cli_name, cli_info["description"], status)

        console.print(table)

        # Quick status check
        console.print("\n[bold yellow]🔍 Quick System Check:[/bold yellow]")

        # Check AMP authentication
        try:
            result = subprocess.run(
                ["python3", "amp_cli.py", "auth", "--status"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and "Authenticated as:" in result.stdout:
                console.print("🔐 AMP Authentication: ✅ [green]Active[/green]")
            else:
                console.print("🔐 AMP Authentication: ❌ [red]Not authenticated[/red]")
        except Exception:
            console.print("🔐 AMP Authentication: ⚠️ [yellow]Unknown[/yellow]")

        # Check key files
        key_files = [".env", "requirements.txt", "main.py"]
        for file_name in key_files:
            file_path = self.project_root / file_name
            status = "✅" if file_path.exists() else "❌"
            console.print(f"📄 {file_name}: {status}")


# Create CLI app instance
head_cli = HeadCLI()


@app.command()
def overview():
    """
    Shows a system overview and status.
    """
    head_cli.show_overview()


@app.command()
def amp(
    command: str = typer.Argument(help="AMP command to run"),
    args: Optional[List[str]] = typer.Argument(None, help="Additional arguments"),
):
    """
    Runs AMP CLI commands for AI models, authentication, and monitoring.
    """
    console.print(f"🤖 [blue]Running AMP command:[/blue] {command}")
    if args:
        console.print(f"   [dim]Args: {' '.join(args)}[/dim]")

    exit_code = head_cli.run_cli_command("amp", command, args)
    if exit_code != 0:
        raise typer.Exit(exit_code)


@app.command()
def genx(
    command: str = typer.Argument(help="GenX command to run"),
    args: Optional[List[str]] = typer.Argument(None, help="Additional arguments"),
):
    """
    Runs GenX CLI commands for system management, ForexConnect, and Excel.
    """
    console.print(f"⚙️ [green]Running GenX command:[/green] {command}")
    if args:
        console.print(f"   [dim]Args: {' '.join(args)}[/dim]")

    exit_code = head_cli.run_cli_command("genx", command, args)
    if exit_code != 0:
        raise typer.Exit(exit_code)


@app.command()
def chat():
    """
    Starts an interactive chat with the AMP trading system.
    """
    console.print("💬 [cyan]Starting AMP Chat...[/cyan]")
    exit_code = head_cli.run_cli_command("chat", "interactive")
    if exit_code != 0:
        raise typer.Exit(exit_code)


@app.command()
def status():
    """
    Shows a comprehensive system status by running the status commands
    from both the AMP and GenX CLIs.
    """
    console.print("📊 [bold]System Status Report[/bold]")
    console.print("=" * 50)

    # AMP Status
    console.print("\n🤖 [blue]AMP Status:[/blue]")
    head_cli.run_cli_command("amp", "status")

    # GenX Status
    console.print("\n⚙️ [green]GenX Status:[/green]")
    head_cli.run_cli_command("genx", "status")


@app.command()
def auth(
    action: str = typer.Option("status", help="Auth action: status, login, logout"),
    token: Optional[str] = typer.Option(None, help="Authentication token for login"),
):
    """
    Manages authentication as a shortcut to the AMP auth commands.
    """
    if action == "login" and token:
        head_cli.run_cli_command("amp", "auth", ["--token", token])
    elif action == "logout":
        head_cli.run_cli_command("amp", "auth", ["--logout"])
    else:
        head_cli.run_cli_command("amp", "auth", ["--status"])


@app.command()
def init():
    """
    Initializes the GenX trading system.
    """
    console.print("🚀 [bold]Initializing GenX Trading System...[/bold]")
    head_cli.run_cli_command("genx", "init")


@app.command()
def logs(source: str = typer.Option("genx", help="Log source: genx, amp, all")):
    """
    Views system logs from a specified source.
    """
    if source == "all":
        console.print("📋 [yellow]All System Logs:[/yellow]")
        head_cli.run_cli_command("genx", "logs")
    elif source == "genx":
        console.print("📋 [green]GenX Logs:[/green]")
        head_cli.run_cli_command("genx", "logs")
    else:
        console.print(f"📋 [blue]Logs for {source}:[/blue]")
        head_cli.run_cli_command(source, "logs")


@app.command()
def monitor():
    """
    Monitors system performance using AMP monitoring.
    """
    console.print("📊 [blue]System Monitoring:[/blue]")
    head_cli.run_cli_command("amp", "monitor", ["--status"])


@app.command()
def tree():
    """
    Shows the project structure tree.
    """
    console.print("🌳 [green]Project Structure:[/green]")
    head_cli.run_cli_command("genx", "tree")


@app.command()
def help_all():
    """
    Shows a complete help guide for all available CLI tools.
    """
    console.print(
        Panel.fit(
            "[bold]🆘 Complete Help Guide[/bold]\n"
            "[dim]Available commands across all CLI tools[/dim]",
            border_style="yellow",
        )
    )

    for cli_name, cli_info in head_cli.available_clis.items():
        console.print(
            f"\n[bold]{cli_name.upper()} CLI:[/bold] {cli_info['description']}"
        )

        if cli_name == "chat":
            console.print("  • interactive - Start interactive chat")
        else:
            for cmd in cli_info["commands"]:
                console.print(f"  • {cmd}")

        console.print(f"  [dim]Direct access: python3 {cli_info['file']} --help[/dim]")

    console.print(f"\n[bold yellow]Head CLI Commands:[/bold yellow]")
    console.print("  • overview - System overview")
    console.print("  • status - Complete system status")
    console.print("  • auth - Authentication management")
    console.print("  • chat - Interactive AMP chat")
    console.print("  • init - Initialize system")
    console.print("  • logs - View logs")
    console.print("  • monitor - System monitoring")
    console.print("  • tree - Project structure")


@app.callback()
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", help="Show version"),
):
    """
    The main callback for the Head CLI, which provides a unified interface
    for all trading system components.
    """
    if version:
        console.print("GenX Trading Platform Head CLI v1.0.0")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        # Show overview if no command provided
        head_cli.show_overview()


if __name__ == "__main__":
    app()
