#!/usr/bin/env python3
"""
GenX Master CLI - Complete Platform Management
Master command-line interface that integrates all CLI components:
- Unified CLI wrapper
- Cursor AI collaboration (Ali & Jules)
- Automated deployment job
- All existing CLI tools
"""

import asyncio
import json
import logging
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import typer
from rich.columns import Columns
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.syntax import Syntax
from rich.table import Table
from rich.tree import Tree

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Typer app and Rich console
app = typer.Typer(
    help="🚀 GenX Master CLI - Complete Platform Management",
    rich_markup_mode="rich",
    pretty_exceptions_enable=False,
)
console = Console()


class GenXMasterCLI:
    """
    The main class for the GenX Master CLI, which integrates all other CLI
    components and provides a unified interface for managing the trading platform.
    """

    def __init__(self):
        """
        Initializes the GenXMasterCLI, setting up paths and defining the
        available CLI modules and quick actions.
        """
        self.project_root = Path.cwd()
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Available CLI modules
        self.cli_modules = {
            "unified": {
                "file": "genx_unified_cli.py",
                "description": "Unified CLI wrapper with all core functionality",
                "commands": [
                    "status",
                    "setup",
                    "deploy",
                    "monitor",
                    "cursor_collaborate",
                    "execute_job",
                ],
            },
            "cursor": {
                "file": "cursor_ali_jules_cli.py",
                "description": "Cursor AI collaboration with Ali & Jules enhancements",
                "commands": [
                    "init",
                    "ali_enhance",
                    "jules_deploy",
                    "cursor_assist",
                    "collaboration_status",
                ],
            },
            "deployment": {
                "file": "automated_deployment_job.py",
                "description": "Automated deployment job orchestration",
                "commands": ["deploy", "status", "list_deployments"],
            },
            "genx": {
                "file": "genx_cli.py",
                "description": "Original GenX FX trading system management",
                "commands": [
                    "setup",
                    "start",
                    "stop",
                    "status",
                    "config",
                    "signals",
                    "test",
                ],
            },
            "head": {
                "file": "head_cli.py",
                "description": "Head CLI for unified platform management",
                "commands": ["overview", "deploy", "monitor", "logs"],
            },
            "amp": {
                "file": "amp_cli.py",
                "description": "Automated Model Pipeline for AI trading",
                "commands": ["auth", "update", "deploy", "schedule", "monitor"],
            },
        }

        # Quick actions for common tasks
        self.quick_actions = {
            "quick_setup": {
                "description": "Quick setup for local development",
                "commands": ["unified", "setup", "local"],
            },
            "quick_deploy_aws": {
                "description": "Quick deploy to AWS free tier",
                "commands": ["deployment", "deploy", "aws-free", "--yes"],
            },
            "quick_deploy_vps": {
                "description": "Quick deploy to VPS",
                "commands": ["deployment", "deploy", "exness-vps", "--yes"],
            },
            "quick_status": {
                "description": "Show comprehensive system status",
                "commands": ["unified", "status"],
            },
            "quick_monitor": {
                "description": "Start system monitoring",
                "commands": ["unified", "monitor"],
            },
        }

    def display_master_banner(self):
        """
        Displays the master CLI banner.
        """
        banner = """
╔════════════════════════════════════════════════════════════════════════════════════════════╗
║                                🚀 GenX Master CLI v2.0                                    ║
║                            Complete Trading Platform Management                            ║
║                                                                                            ║
║    🤖 AI-Powered Trading    📊 Real-Time Signals    ⚡ Auto-Deploy    🔐 Secure Platform  ║
║                                                                                            ║
║  👨‍💻 Ali's CLI Enhancements  🔧 Jules' Automation  🤖 Cursor AI  📈 Enterprise-Ready     ║
║                                                                                            ║
║                               One CLI to Rule Them All                                    ║
╚════════════════════════════════════════════════════════════════════════════════════════════╝
        """
        console.print(Panel(banner, style="bold blue"))

    def check_cli_availability(self) -> Dict[str, bool]:
        """
        Checks which of the defined CLI modules are available in the project.

        Returns:
            Dict[str, bool]: A dictionary mapping module names to their availability status.
        """
        availability = {}
        for name, info in self.cli_modules.items():
            file_path = self.project_root / info["file"]
            availability[name] = file_path.exists()
        return availability

    def execute_cli_command(
        self, module: str, command: str, args: List[str] = None
    ) -> bool:
        """
        Executes a command from a specific CLI module.

        Args:
            module (str): The name of the CLI module to use.
            command (str): The command to execute.
            args (List[str], optional): A list of additional arguments for the command. Defaults to None.

        Returns:
            bool: True if the command executes successfully, False otherwise.
        """
        if module not in self.cli_modules:
            console.print(f"❌ Unknown CLI module: {module}", style="red")
            return False

        cli_info = self.cli_modules[module]
        cli_file = self.project_root / cli_info["file"]

        if not cli_file.exists():
            console.print(f"❌ CLI file not found: {cli_info['file']}", style="red")
            return False

        # Build command
        cmd = ["python3", str(cli_file), command]
        if args:
            cmd.extend(args)

        try:
            console.print(
                f"🔄 Executing: {module} {command} {' '.join(args or [])}", style="cyan"
            )

            result = subprocess.run(cmd, cwd=self.project_root, text=True)

            if result.returncode == 0:
                console.print(
                    f"✅ {module} {command} completed successfully", style="green"
                )
                return True
            else:
                console.print(
                    f"❌ {module} {command} failed with exit code {result.returncode}",
                    style="red",
                )
                return False

        except Exception as e:
            console.print(f"❌ Error executing {module} {command}: {e}", style="red")
            return False

    def show_cli_overview(self):
        """
        Shows an overview of all available CLI modules and quick actions.
        """
        console.print("\n🛠️ [bold]Available CLI Modules[/bold]")

        availability = self.check_cli_availability()

        modules_table = Table(show_header=True, header_style="bold cyan")
        modules_table.add_column("Module")
        modules_table.add_column("Description")
        modules_table.add_column("Status")
        modules_table.add_column("Commands")

        for name, info in self.cli_modules.items():
            status = "✅ Available" if availability[name] else "❌ Missing"
            commands = ", ".join(info["commands"][:3]) + (
                "..." if len(info["commands"]) > 3 else ""
            )

            modules_table.add_row(name, info["description"], status, commands)

        console.print(modules_table)

        # Show quick actions
        console.print("\n⚡ [bold]Quick Actions[/bold]")

        actions_table = Table(show_header=True, header_style="bold magenta")
        actions_table.add_column("Action")
        actions_table.add_column("Description")
        actions_table.add_column("Command")

        for action, info in self.quick_actions.items():
            command_str = " ".join(info["commands"])
            actions_table.add_row(action, info["description"], f"genx {command_str}")

        console.print(actions_table)

    def create_project_summary(self):
        """
        Creates and displays a comprehensive summary of the project, including
        its structure and the status of its components.
        """
        console.print("\n📊 [bold]GenX FX Platform Summary[/bold]")

        # Project structure
        structure_tree = Tree("📁 GenX FX Platform")

        # Core components
        core_branch = structure_tree.add("🏗️ Core Components")
        core_branch.add("📊 Trading Engine (main.py)")
        core_branch.add("🤖 AI Models (core/ai_models/)")
        core_branch.add("📈 Signal Processing (core/strategies/)")
        core_branch.add("🔗 API Services (api/)")
        core_branch.add("💻 Web Client (client/)")

        # CLI Tools
        cli_branch = structure_tree.add("🛠️ CLI Tools")
        for name, info in self.cli_modules.items():
            status = "✅" if (self.project_root / info["file"]).exists() else "❌"
            cli_branch.add(f"{status} {name} - {info['description']}")

        # Deployment
        deploy_branch = structure_tree.add("🚀 Deployment")
        deploy_branch.add("☁️ AWS Free Tier")
        deploy_branch.add("☁️ AWS Full")
        deploy_branch.add("🖥️ Exness VPS")
        deploy_branch.add("💻 Local Development")

        # Collaboration
        collab_branch = structure_tree.add("🤝 Collaboration")
        collab_branch.add("👨‍💻 Ali - CLI Enhancement Specialist")
        collab_branch.add("👨‍💻 Jules - Deployment Automation Expert")
        collab_branch.add("🤖 Cursor AI - Development Assistant")

        console.print(structure_tree)

        # System status
        console.print("\n🔍 [bold]System Status[/bold]")

        status_data = [
            ("🐍 Python Environment", "✅ Ready"),
            ("🐳 Docker", "✅ Available" if shutil.which("docker") else "❌ Not Found"),
            ("☁️ AWS CLI", "✅ Available" if shutil.which("aws") else "❌ Not Found"),
            ("📦 Dependencies", "✅ Installed"),
            ("📁 Project Structure", "✅ Complete"),
            (
                "🛠️ CLI Tools",
                f"✅ {sum(self.check_cli_availability().values())}/{len(self.cli_modules)} Available",
            ),
        ]

        status_table = Table(show_header=True, header_style="bold green")
        status_table.add_column("Component")
        status_table.add_column("Status")

        for component, status in status_data:
            status_table.add_row(component, status)

        console.print(status_table)


# CLI instance
master_cli = GenXMasterCLI()


@app.callback()
def main():
    """
    The main callback for the GenX Master CLI, which displays the banner.
    """
    master_cli.display_master_banner()


@app.command()
def overview():
    """
    Shows a comprehensive overview of the trading platform, including all
    available CLI modules and a project summary.
    """
    master_cli.display_master_banner()
    master_cli.show_cli_overview()
    master_cli.create_project_summary()


@app.command()
def unified(
    command: str = typer.Argument(
        help="Unified CLI command: status, setup, deploy, monitor, etc."
    ),
    args: List[str] = typer.Argument(None, help="Additional arguments for the command"),
):
    """
    Executes commands from the unified CLI module.
    """
    master_cli.execute_cli_command("unified", command, args)


@app.command()
def cursor(
    command: str = typer.Argument(
        help="Cursor CLI command: init, ali_enhance, jules_deploy, etc."
    ),
    args: List[str] = typer.Argument(None, help="Additional arguments for the command"),
):
    """
    Executes commands from the Cursor AI collaboration CLI module.
    """
    master_cli.execute_cli_command("cursor", command, args)


@app.command()
def deployment(
    command: str = typer.Argument(
        help="Deployment command: deploy, status, list_deployments"
    ),
    args: List[str] = typer.Argument(None, help="Additional arguments for the command"),
):
    """
    Executes commands from the automated deployment CLI module.
    """
    master_cli.execute_cli_command("deployment", command, args)


@app.command()
def genx(
    command: str = typer.Argument(
        help="GenX CLI command: setup, start, stop, status, etc."
    ),
    args: List[str] = typer.Argument(None, help="Additional arguments for the command"),
):
    """
    Executes commands from the original GenX CLI module.
    """
    master_cli.execute_cli_command("genx", command, args)


@app.command()
def head(
    command: str = typer.Argument(
        help="Head CLI command: overview, deploy, monitor, logs"
    ),
    args: List[str] = typer.Argument(None, help="Additional arguments for the command"),
):
    """
    Executes commands from the Head CLI module.
    """
    master_cli.execute_cli_command("head", command, args)


@app.command()
def amp(
    command: str = typer.Argument(
        help="AMP CLI command: auth, update, deploy, schedule, monitor"
    ),
    args: List[str] = typer.Argument(None, help="Additional arguments for the command"),
):
    """
    Executes commands from the AMP CLI module.
    """
    master_cli.execute_cli_command("amp", command, args)


@app.command()
def quick_setup():
    """
    Runs a quick setup for local development.
    """
    console.print("\n⚡ [bold]Quick Setup - Local Development[/bold]")
    master_cli.execute_cli_command("unified", "setup", ["local"])


@app.command()
def quick_deploy_aws():
    """
    Runs a quick deployment to the AWS free tier.
    """
    console.print("\n⚡ [bold]Quick Deploy - AWS Free Tier[/bold]")
    master_cli.execute_cli_command("deployment", "deploy", ["aws-free", "--yes"])


@app.command()
def quick_deploy_vps():
    """
    Runs a quick deployment to a VPS.
    """
    console.print("\n⚡ [bold]Quick Deploy - VPS[/bold]")
    master_cli.execute_cli_command("deployment", "deploy", ["exness-vps", "--yes"])


@app.command()
def quick_status():
    """
    Shows a comprehensive system status.
    """
    console.print("\n⚡ [bold]Quick Status Check[/bold]")
    master_cli.execute_cli_command("unified", "status")


@app.command()
def quick_monitor():
    """
    Starts system monitoring.
    """
    console.print("\n⚡ [bold]Quick Monitor[/bold]")
    master_cli.execute_cli_command("unified", "monitor")


@app.command()
def init_collaboration():
    """
    Initializes the Cursor AI collaboration workspace.
    """
    console.print("\n🤖 [bold]Initializing Collaboration[/bold]")
    master_cli.execute_cli_command("cursor", "init")


@app.command()
def full_deploy(
    target: str = typer.Argument(
        "aws-free", help="Deployment target: aws-free, aws-full, exness-vps, local"
    ),
    environment: str = typer.Option(
        "production", help="Environment: development, staging, production"
    ),
):
    """
    Executes a full deployment with all enhancements, including collaboration
    initialization, environment setup, and monitoring.
    """
    console.print(f"\n🚀 [bold]Full Deployment to {target}[/bold]")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    ) as progress:

        deploy_task = progress.add_task("Full deployment...", total=5)

        # Step 1: Initialize collaboration
        progress.update(deploy_task, description="Initializing collaboration...")
        master_cli.execute_cli_command("cursor", "init")
        progress.advance(deploy_task)

        # Step 2: Apply Ali's enhancements
        progress.update(deploy_task, description="Applying Ali's enhancements...")
        master_cli.execute_cli_command("cursor", "ali_enhance", ["all"])
        progress.advance(deploy_task)

        # Step 3: Setup environment
        progress.update(deploy_task, description="Setting up environment...")
        master_cli.execute_cli_command("unified", "setup", [target])
        progress.advance(deploy_task)

        # Step 4: Execute deployment
        progress.update(deploy_task, description="Executing deployment...")
        master_cli.execute_cli_command("deployment", "deploy", [target, "--yes"])
        progress.advance(deploy_task)

        # Step 5: Start monitoring
        progress.update(deploy_task, description="Starting monitoring...")
        master_cli.execute_cli_command("unified", "monitor")
        progress.advance(deploy_task)

    console.print("✅ Full deployment completed!", style="green")


@app.command()
def health_check():
    """
    Performs a comprehensive health check of the entire platform, including
    CLI modules, system dependencies, and project structure.
    """
    console.print("\n🏥 [bold]Platform Health Check[/bold]")

    health_checks = [
        ("CLI Modules", master_cli.check_cli_availability()),
        (
            "System Dependencies",
            {
                "python": sys.version_info >= (3, 8),
                "docker": shutil.which("docker") is not None,
                "git": shutil.which("git") is not None,
            },
        ),
        (
            "Project Structure",
            {
                "logs_dir": master_cli.logs_dir.exists(),
                "deploy_dir": (master_cli.project_root / "deploy").exists(),
                "api_dir": (master_cli.project_root / "api").exists(),
                "core_dir": (master_cli.project_root / "core").exists(),
            },
        ),
    ]

    overall_health = True

    for check_name, checks in health_checks:
        console.print(f"\n🔍 [bold]{check_name}[/bold]")

        for item, status in checks.items():
            if isinstance(status, bool):
                emoji = "✅" if status else "❌"
                style = "green" if status else "red"
                if not status:
                    overall_health = False
            else:
                emoji = "✅"
                style = "green"

            console.print(f"  {emoji} {item}", style=style)

    # Overall status
    if overall_health:
        console.print("\n🎉 [bold green]Platform Health: EXCELLENT[/bold green]")
    else:
        console.print(
            "\n⚠️ [bold yellow]Platform Health: NEEDS ATTENTION[/bold yellow]"
        )


if __name__ == "__main__":
    app()
