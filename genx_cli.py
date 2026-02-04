#!/usr/bin/env python3
"""
GenX FX CLI - Comprehensive Trading System Management
Complete command-line interface for managing the GenX FX trading platform
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
from typing import Dict, List, Optional, Union

import typer
from rich.console import Console
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
    help="GenX FX CLI - Complete Trading System Management", rich_markup_mode="rich"
)
console = Console()


class GenXCLI:
    """
    A class to handle the core logic of the GenX FX CLI.
    """

    def __init__(self):
        """
        Initializes the GenXCLI class, setting up paths to important files and directories.
        """
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "amp_config.json"
        self.env_file = self.project_root / ".env"
        self.requirements_file = self.project_root / "requirements.txt"
        self.signal_output_dir = self.project_root / "signal_output"

        # Core directories
        self.core_dir = self.project_root / "core"
        self.api_dir = self.project_root / "api"
        self.client_dir = self.project_root / "client"
        self.logs_dir = self.project_root / "logs"

    def load_config(self) -> Dict:
        """
        Loads the system configuration from the amp_config.json file.

        Returns:
            Dict: The system configuration as a dictionary.
        """
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {}

    def load_env_template(self) -> Dict:
        """
        Loads the environment variable template from the .env.example file.

        Returns:
            Dict: A dictionary of environment variables from the template.
        """
        env_example = self.project_root / ".env.example"
        if env_example.exists():
            env_vars = {}
            with open(env_example, "r") as f:
                for line in f:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.strip().split("=", 1)
                        env_vars[key] = value
            return env_vars
        return {}

    def get_system_status(self) -> Dict:
        """
        Gathers a comprehensive status of the system, including directories,
        files, dependencies, and services.

        Returns:
            Dict: A dictionary containing the system status information.
        """
        status = {
            "project_root": str(self.project_root),
            "directories": {},
            "files": {},
            "environment": {},
            "dependencies": {},
            "services": {},
            "forexconnect": {},
        }

        # Check directories
        key_dirs = [
            "core",
            "api",
            "client",
            "signal_output",
            "logs",
            "config",
            "ai_models",
        ]
        for dir_name in key_dirs:
            dir_path = self.project_root / dir_name
            status["directories"][dir_name] = {
                "exists": dir_path.exists(),
                "path": str(dir_path),
                "items": len(list(dir_path.iterdir())) if dir_path.exists() else 0,
            }

        # Check important files
        key_files = [
            ".env",
            ".env.example",
            "requirements.txt",
            "main.py",
            "amp_config.json",
            "package.json",
        ]
        for file_name in key_files:
            file_path = self.project_root / file_name
            status["files"][file_name] = {
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
                "modified": (
                    datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                    if file_path.exists()
                    else None
                ),
            }

        # Check Python environment
        try:
            import pandas

            status["dependencies"]["pandas"] = pandas.__version__
        except ImportError:
            status["dependencies"]["pandas"] = None

        try:
            import openpyxl

            status["dependencies"]["openpyxl"] = openpyxl.__version__
        except ImportError:
            status["dependencies"]["openpyxl"] = None

        try:
            import forexconnect

            status["forexconnect"]["available"] = True
            status["forexconnect"]["module_path"] = forexconnect.__file__
        except ImportError:
            status["forexconnect"]["available"] = False

        # Check ForexConnect environment
        fc_env = self.project_root / "forexconnect_env_37"
        if fc_env.exists():
            status["forexconnect"]["env_path"] = str(fc_env)
            status["forexconnect"]["env_exists"] = True
        else:
            status["forexconnect"]["env_exists"] = False

        return status


# CLI Commands
@app.command()
def status():
    """Show comprehensive system status"""
    cli = GenXCLI()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Analyzing system status...", total=1)
        status_info = cli.get_system_status()
        progress.update(task, completed=1)

    # Display system overview
    console.print(
        Panel.fit(
            "[bold green]GenX FX Trading System Status[/bold green]",
            subtitle=f"Project Root: {status_info['project_root']}",
        )
    )

    # Directories table
    dir_table = Table(title="📁 Project Directories")
    dir_table.add_column("Directory", style="cyan")
    dir_table.add_column("Status", style="green")
    dir_table.add_column("Items", justify="right")
    dir_table.add_column("Path", style="dim")

    for name, info in status_info["directories"].items():
        status_icon = "✅" if info["exists"] else "❌"
        dir_table.add_row(
            name,
            f"{status_icon} {'Exists' if info['exists'] else 'Missing'}",
            str(info["items"]) if info["exists"] else "N/A",
            info["path"],
        )

    console.print(dir_table)
    console.print()

    # Files table
    file_table = Table(title="📄 Important Files")
    file_table.add_column("File", style="cyan")
    file_table.add_column("Status", style="green")
    file_table.add_column("Size", justify="right")
    file_table.add_column("Last Modified", style="dim")

    for name, info in status_info["files"].items():
        status_icon = "✅" if info["exists"] else "❌"
        size_str = f"{info['size']:,} bytes" if info["exists"] else "N/A"
        modified_str = info["modified"][:19] if info["modified"] else "N/A"

        file_table.add_row(
            name,
            f"{status_icon} {'Exists' if info['exists'] else 'Missing'}",
            size_str,
            modified_str,
        )

    console.print(file_table)
    console.print()

    # Dependencies and ForexConnect
    deps_table = Table(title="🔧 Dependencies & ForexConnect")
    deps_table.add_column("Component", style="cyan")
    deps_table.add_column("Status", style="green")
    deps_table.add_column("Version/Details", style="dim")

    # Python dependencies
    for dep, version in status_info["dependencies"].items():
        status_icon = "✅" if version else "❌"
        version_str = version if version else "Not installed"
        deps_table.add_row(dep, f"{status_icon}", version_str)

    # ForexConnect
    fc_info = status_info["forexconnect"]
    fc_status = "✅ Available" if fc_info["available"] else "❌ Not available"
    fc_details = fc_info.get("module_path", "Not found")
    deps_table.add_row("ForexConnect", fc_status, fc_details)

    if fc_info["env_exists"]:
        deps_table.add_row("FC Environment", "✅ Found", fc_info["env_path"])
    else:
        deps_table.add_row("FC Environment", "❌ Missing", "forexconnect_env_37/")

    console.print(deps_table)


@app.command()
def init():
    """Initialize or setup the GenX FX system"""
    cli = GenXCLI()

    console.print(
        Panel.fit(
            "[bold green]GenX FX System Initialization[/bold green]",
            subtitle="Setting up your trading system",
        )
    )

    # Create essential directories
    essential_dirs = ["signal_output", "logs", "config", "ai_models", "data"]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("Creating directories...", total=len(essential_dirs))

        for dir_name in essential_dirs:
            dir_path = cli.project_root / dir_name
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                console.print(f"  ✅ Created: {dir_name}/")
            else:
                console.print(f"  ✅ Exists: {dir_name}/")
            progress.advance(task)

    # Create .env file if it doesn't exist
    if not cli.env_file.exists():
        env_example = cli.project_root / ".env.example"
        if env_example.exists():
            shutil.copy2(env_example, cli.env_file)
            console.print("  ✅ Created .env from .env.example")
        else:
            console.print("  ⚠️ No .env.example found to copy")

    console.print("\n[bold green]✅ Initialization complete![/bold green]")
    console.print("Next steps:")
    console.print("  1. Run: [cyan]genx config[/cyan] to configure API keys")
    console.print("  2. Run: [cyan]genx excel demo[/cyan] to test signal generation")
    console.print(
        "  3. Run: [cyan]genx forexconnect test[/cyan] to test FXCM connection"
    )


@app.command()
def config():
    """Configure API keys and system settings"""
    cli = GenXCLI()

    console.print(
        Panel.fit(
            "[bold green]GenX FX Configuration[/bold green]",
            subtitle="Configure API keys and settings",
        )
    )

    env_template = cli.load_env_template()

    # Show current configuration status
    config_table = Table(title="🔧 Configuration Status")
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Status", style="green")
    config_table.add_column("Current Value", style="dim")

    # Check important environment variables
    important_vars = [
        "FXCM_USERNAME",
        "FXCM_PASSWORD",
        "FXCM_CONNECTION_TYPE",
        "GEMINI_API_KEY",
        "TRADING_ENABLED",
        "RISK_PERCENTAGE",
    ]

    for var in important_vars:
        current_value = os.getenv(var, env_template.get(var, "Not set"))
        is_set = var in os.environ
        status_icon = "✅" if is_set else "❌"

        # Mask sensitive values
        display_value = current_value
        if "PASSWORD" in var or "KEY" in var or "SECRET" in var:
            if is_set and current_value != "Not set":
                display_value = (
                    f"{current_value[:4]}***{current_value[-4:]}"
                    if len(current_value) > 8
                    else "***"
                )

        config_table.add_row(var, f"{status_icon}", display_value)

    console.print(config_table)
    console.print()

    if Confirm.ask("Would you like to configure settings now?"):
        # FXCM Configuration
        console.print("\n[bold yellow]📊 FXCM ForexConnect Configuration[/bold yellow]")

        current_username = os.getenv(
            "FXCM_USERNAME", env_template.get("FXCM_USERNAME", "")
        )
        username = Prompt.ask("FXCM Username", default=current_username)

        password = Prompt.ask("FXCM Password", password=True)

        connection_type = Prompt.ask(
            "Connection Type", choices=["Demo", "Real"], default="Demo"
        )

        # Trading Configuration
        console.print("\n[bold yellow]⚖️ Risk Management Configuration[/bold yellow]")

        trading_enabled = Confirm.ask("Enable live trading?", default=False)
        risk_percentage = Prompt.ask("Risk percentage per trade", default="2.0")

        # Write to .env file
        env_content = []
        if cli.env_file.exists():
            with open(cli.env_file, "r") as f:
                env_content = f.readlines()

        # Update or add variables
        updated_vars = {
            "FXCM_USERNAME": username,
            "FXCM_PASSWORD": password,
            "FXCM_CONNECTION_TYPE": connection_type,
            "TRADING_ENABLED": str(trading_enabled).lower(),
            "RISK_PERCENTAGE": risk_percentage,
        }

        # Simple .env update (you might want to use a proper .env library)
        with open(cli.env_file, "w") as f:
            f.write("# GenX FX Trading System Configuration\n")
            f.write(f"# Updated: {datetime.now().isoformat()}\n\n")

            for key, value in updated_vars.items():
                f.write(f"{key}={value}\n")

            f.write("\n# Add other configuration from .env.example as needed\n")

        console.print("\n[bold green]✅ Configuration saved to .env[/bold green]")


# Excel command group
excel_app = typer.Typer(help="Excel signal generation and management")
app.add_typer(excel_app, name="excel")


@excel_app.command("demo")
def excel_demo(count: int = typer.Option(10, help="Number of signals to generate")):
    """Generate demo Excel signals"""
    console.print(
        f"[bold green]📊 Generating {count} demo Excel signals...[/bold green]"
    )

    try:
        # Run the demo generator
        import subprocess

        result = subprocess.run(
            [sys.executable, "demo_excel_generator.py"],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd()),
        )

        if result.returncode == 0:
            console.print(
                "[bold green]✅ Excel demo completed successfully![/bold green]"
            )
            console.print(result.stdout)
        else:
            console.print("[bold red]❌ Excel demo failed![/bold red]")
            console.print(result.stderr)

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")


@excel_app.command("live")
def excel_live(count: int = typer.Option(10, help="Number of signals to generate")):
    """Generate Excel signals with live ForexConnect data"""
    console.print(
        f"[bold green]📊 Generating {count} live Excel signals...[/bold green]"
    )

    try:
        # Run the live generator
        result = subprocess.run(
            [sys.executable, "excel_forexconnect_integration.py"],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd()),
        )

        if result.returncode == 0:
            console.print(
                "[bold green]✅ Live Excel generation completed![/bold green]"
            )
            console.print(result.stdout)
        else:
            console.print("[bold red]❌ Live Excel generation failed![/bold red]")
            console.print(result.stderr)

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")


@excel_app.command("view")
def excel_view():
    """View generated Excel files"""
    cli = GenXCLI()

    excel_files = list(cli.signal_output_dir.glob("*.xlsx"))

    if not excel_files:
        console.print("[yellow]No Excel files found in signal_output/[/yellow]")
        return

    table = Table(title="📊 Generated Excel Files")
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified", style="dim")
    table.add_column("Action", style="green")

    for file_path in excel_files:
        size = file_path.stat().st_size
        modified = datetime.fromtimestamp(file_path.stat().st_mtime)

        table.add_row(
            file_path.name,
            f"{size:,} bytes",
            modified.strftime("%Y-%m-%d %H:%M"),
            "Ready to open",
        )

    console.print(table)
    console.print(f"\n📂 Files location: {cli.signal_output_dir}")


# ForexConnect command group
forexconnect_app = typer.Typer(help="ForexConnect API management")
app.add_typer(forexconnect_app, name="forexconnect")


@forexconnect_app.command("test")
def forexconnect_test():
    """Test ForexConnect connection"""
    console.print("[bold green]🔌 Testing ForexConnect connection...[/bold green]")

    try:
        # Test ForexConnect availability
        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import forexconnect; print('ForexConnect module available')",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print("✅ ForexConnect module: Available")

            # Test actual connection
            result = subprocess.run(
                [sys.executable, "test_forexconnect.py"],
                capture_output=True,
                text=True,
                cwd=str(Path.cwd()),
            )

            console.print("📊 Connection test output:")
            console.print(result.stdout)

            if result.stderr:
                console.print("[yellow]Warnings/Errors:[/yellow]")
                console.print(result.stderr)

        else:
            console.print("❌ ForexConnect module: Not available")
            console.print("💡 Try running: source forexconnect_env_37/bin/activate")

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")


@forexconnect_app.command("status")
def forexconnect_status():
    """Show ForexConnect installation status"""
    cli = GenXCLI()

    console.print("[bold green]📊 ForexConnect Status[/bold green]")

    # Check ForexConnect environment
    fc_env = cli.project_root / "forexconnect_env_37"

    table = Table(title="ForexConnect Installation")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Details", style="dim")

    if fc_env.exists():
        table.add_row("Environment", "✅ Found", str(fc_env))

        # Check if module is available
        fc_python = fc_env / "bin" / "python"
        if fc_python.exists():
            table.add_row("Python Binary", "✅ Available", str(fc_python))

        # Check ForexConnect module
        try:
            result = subprocess.run(
                [
                    str(fc_python),
                    "-c",
                    "import forexconnect; print(forexconnect.__file__)",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                table.add_row(
                    "ForexConnect Module", "✅ Available", result.stdout.strip()
                )
            else:
                table.add_row("ForexConnect Module", "❌ Error", result.stderr.strip())

        except Exception as e:
            table.add_row("ForexConnect Module", "❌ Error", str(e))
    else:
        table.add_row("Environment", "❌ Missing", "forexconnect_env_37/ not found")

    console.print(table)


@app.command()
def logs():
    """View system logs"""
    cli = GenXCLI()

    log_files = list(cli.logs_dir.glob("*.log")) if cli.logs_dir.exists() else []

    if not log_files:
        console.print("[yellow]No log files found in logs/[/yellow]")
        return

    table = Table(title="📋 System Logs")
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Modified", style="dim")

    for log_file in log_files:
        size = log_file.stat().st_size
        modified = datetime.fromtimestamp(log_file.stat().st_mtime)

        table.add_row(
            log_file.name, f"{size:,} bytes", modified.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)

    if log_files and Confirm.ask("View latest log file?"):
        latest_log = max(log_files, key=lambda f: f.stat().st_mtime)

        console.print(f"\n[bold]📄 {latest_log.name}[/bold] (last 20 lines):")
        console.print(
            Panel(
                "\n".join(latest_log.read_text().split("\n")[-20:]),
                title=latest_log.name,
                border_style="dim",
            )
        )


@app.command()
def tree():
    """Show project structure tree"""
    cli = GenXCLI()

    console.print("[bold green]🌳 GenX FX Project Structure[/bold green]")

    tree = Tree("GenX_FX/")

    # Add main directories
    for item in sorted(cli.project_root.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            branch = tree.add(f"📁 {item.name}/")

            # Add some key files in each directory
            try:
                for subitem in sorted(
                    list(item.iterdir())[:5]
                ):  # Limit to first 5 items
                    if subitem.is_file():
                        branch.add(f"📄 {subitem.name}")
                    elif subitem.is_dir():
                        branch.add(f"📁 {subitem.name}/")

                if len(list(item.iterdir())) > 5:
                    branch.add("...")

            except PermissionError:
                branch.add("❌ Permission denied")

    # Add important root files
    important_files = [
        ".env",
        ".env.example",
        "requirements.txt",
        "main.py",
        "README.md",
    ]
    for file_name in important_files:
        file_path = cli.project_root / file_name
        if file_path.exists():
            tree.add(f"📄 {file_name}")

    console.print(tree)


@app.command("onedrive-sync")
def onedrive_sync():
    """Sync signals to OneDrive"""
    console.print("[bold green]☁️ Syncing signals to OneDrive...[/bold green]")

    try:
        import onedrive_uploader

        # Call the sync function directly
        # This ensures stdout (like auth code) is visible to the user
        onedrive_uploader.sync_signals()

        console.print("[bold green]✅ OneDrive sync process finished.[/bold green]")

    except Exception as e:
        console.print(f"[bold red]❌ Error: {e}[/bold red]")


@app.command("verify-vps")
def verify_vps():
    """Run comprehensive VPS verification checks"""
    console.print("[bold green]🔍 Running VPS verification checks...[/bold green]")

    try:
        # Run the verification script
        result = subprocess.run(
            [sys.executable, "scripts/deployment/verify-setup.py"],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd()),
        )

        console.print(result.stdout)
        if result.stderr:
            console.print("[yellow]Warnings/Errors during verification:[/yellow]")
            console.print(result.stderr)

        if result.returncode == 0:
            console.print("\n[bold green]✅ VPS verification completed![/bold green]")
        else:
            console.print("\n[bold red]❌ VPS verification found issues![/bold red]")

    except Exception as e:
        console.print(f"[bold red]❌ Error running verification: {e}[/bold red]")


if __name__ == "__main__":
    app()
