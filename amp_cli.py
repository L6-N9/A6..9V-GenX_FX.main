#!/usr/bin/env python3
"""
AMP CLI - Automated Model Pipeline for GenX Trading Platform
Enhanced CLI with Typer for better user experience
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import typer
from rich.console import Console

# Force UTF-8 stdout/stderr to avoid Unicode issues on Windows consoles
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm
from rich.table import Table

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Typer app and Rich console
app = typer.Typer(help="AMP CLI - Automated Model Pipeline for GenX Trading Platform")
console = Console()


class AMPCLI:
    """
    A class to encapsulate the functionality of the AMP CLI.

    This class handles loading and saving configuration, managing plugins,
    and running various commands like updating, verifying, and testing.

    Attributes:
        project_root (Path): The root directory of the project.
        config_file (Path): The path to the main AMP configuration file.
        plugins_dir (Path): The directory where plugins are stored.
        env_file (Path): The path to the .env file.
    """

    def __init__(self):
        """Initializes the AMPCLI class."""
        self.project_root = Path.cwd()
        self.config_file = self.project_root / "amp_config.json"
        self.plugins_dir = self.project_root / "amp-plugins"
        self.env_file = self.project_root / ".env"

    def load_config(self) -> Dict:
        """
        Loads the AMP configuration from 'amp_config.json'.

        Returns:
            Dict: The loaded configuration, or a default config if the file doesn't exist.
        """
        if self.config_file.exists():
            with open(self.config_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {
            "api_provider": "gemini",
            "plugins": [],
            "services": [],
            "dependencies": [],
            "env_vars": {},
        }

    def save_config(self, config: Dict):
        """
        Saves the AMP configuration to 'amp_config.json'.

        Args:
            config (Dict): The configuration dictionary to save.
        """
        with open(self.config_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def update(
        self,
        env_file: Optional[str] = None,
        set_config: Optional[List[str]] = None,
        add_dependency: Optional[List[str]] = None,
        add_env: Optional[List[str]] = None,
        description: Optional[str] = None,
    ):
        """
        The main command to update the AMP configuration.

        Args:
            env_file (Optional[str]): Path to an environment file to load.
            set_config (Optional[List[str]]): Key-value pairs to set in the config.
            add_dependency (Optional[List[str]]): Dependencies to add.
            add_env (Optional[List[str]]): Environment variables to add.
            description (Optional[str]): A new description for the configuration.
        """
        with console.status("[bold green]Starting GenX Trading Platform AMP Update..."):
            config = self.load_config()

            if env_file:
                self._load_env_vars(env_file)
            if set_config:
                for setting in set_config:
                    if "=" in setting:
                        k, v = setting.split("=", 1)
                        config[k] = v
            if add_dependency:
                config.setdefault("dependencies", []).extend(add_dependency)
            if add_env:
                for env_var in add_env:
                    if "=" in env_var:
                        k, v = env_var.split("=", 1)
                        config.setdefault("env_vars", {})[k] = v
            if description:
                config["description"] = description

            self.save_config(config)
        console.print("✅ [bold green]Main AMP update complete!")

    def plugin_install(
        self,
        plugin_name: str,
        source: str = "genx-trading",
        enable_service: Optional[List[str]] = None,
        description: str = "",
    ):
        """
        Installs an AMP plugin by adding it to the configuration.

        Args:
            plugin_name (str): The name of the plugin to install.
            source (str): The source of the plugin.
            enable_service (Optional[List[str]]): Services to enable with this plugin.
            description (str): A description of the plugin.
        """
        with console.status(f"[bold blue]Installing AMP plugin: {plugin_name}..."):
            config = self.load_config()
            plugin_config = {
                "name": plugin_name,
                "source": source,
                "enabled": True,
                "services": enable_service or [],
                "description": description,
            }
            config.setdefault("plugins", []).append(plugin_config)
            self.save_config(config)
        console.print(f"✅ [bold green]Plugin '{plugin_name}' installed successfully!")

    def config_set(
        self,
        api_provider: Optional[str] = None,
        enable_sentiment_analysis: Optional[bool] = None,
        enable_social_signals: Optional[bool] = None,
        enable_news_feeds: Optional[bool] = None,
        enable_websocket_streams: Optional[bool] = None,
    ):
        """
        Sets various high-level configuration options for AMP services.

        Args:
            api_provider (Optional[str]): The main API provider to use.
            enable_sentiment_analysis (Optional[bool]): Toggles sentiment analysis.
            enable_social_signals (Optional[bool]): Toggles social media signals.
            enable_news_feeds (Optional[bool]): Toggles news feeds.
            enable_websocket_streams (Optional[bool]): Toggles WebSocket streams.
        """
        with console.status("[bold blue]Configuring services..."):
            config = self.load_config()

            if api_provider:
                config["api_provider"] = api_provider
            if enable_sentiment_analysis is not None:
                config["enable_sentiment_analysis"] = enable_sentiment_analysis
            if enable_social_signals is not None:
                config["enable_social_signals"] = enable_social_signals
            if enable_news_feeds is not None:
                config["enable_news_feeds"] = enable_news_feeds
            if enable_websocket_streams is not None:
                config["enable_websocket_streams"] = enable_websocket_streams

            self.save_config(config)
        console.print("🔧 [bold green]Service configuration complete!")

    def service_enable(self, service: List[str]):
        """
        Enables one or more services in the AMP configuration.

        Args:
            service (List[str]): A list of service names to enable.
        """
        config = self.load_config()
        enabled_services = set(config.setdefault("enabled_services", []))
        enabled_services.update(service)
        config["enabled_services"] = sorted(list(enabled_services))
        self.save_config(config)
        console.print(f"✅ [bold green]Services enabled: {', '.join(service)}")

    def verify(
        self,
        check_dependencies: bool = False,
        check_env_vars: bool = False,
        check_services: bool = False,
        check_api_keys: bool = False,
    ):
        """
        Verifies the installation and configuration of the AMP system.

        Args:
            check_dependencies (bool): If True, check for required Python packages.
            check_env_vars (bool): If True, check for required environment variables.
            check_services (bool): If True, check if enabled services exist.
            check_api_keys (bool): If True, check for essential API keys.
        """
        with console.status("[bold blue]Verifying installation..."):
            config = self.load_config()

            if check_dependencies:
                self._check_dependencies(config.get("dependencies", []))
            if check_env_vars:
                self._check_env_vars(config.get("env_vars", {}))
            if check_services:
                self._check_services(config.get("enabled_services", []))
            if check_api_keys:
                self._check_api_keys()

        console.print("✅ [bold green]Installation verification complete!")

    def test(self, all_tests: bool = False):
        """
        Runs automated tests.

        Args:
            all_tests (bool): If True, runs both Python and Node.js tests.
                              Otherwise, runs only Python tests.
        """
        if all_tests:
            with console.status("[bold blue]Running all tests..."):
                self._run_python_tests()
                self._run_node_tests()
        else:
            with console.status("[bold blue]Running Python tests..."):
                self._run_python_tests()

    def deploy(self):
        """Deploys the application to production by running the job runner."""
        with console.status("[bold blue]Deploying to production..."):
            try:
                import subprocess

                subprocess.run(
                    [sys.executable, "amp_job_runner.py", "deploy"], check=True
                )
            except subprocess.CalledProcessError:
                console.print("❌ [bold red]Deployment failed!")
            except FileNotFoundError:
                console.print("⚠️ [yellow]amp_job_runner.py not found.")

    def _load_env_vars(self, env_file: str):
        """Load environment variables from file"""
        if Path(env_file).exists():
            console.print(f"📄 [blue]Loading environment variables from {env_file}")

    def _check_dependencies(self, dependencies: List[str]):
        """Check if dependencies are installed"""
        console.print("📦 [blue]Checking dependencies...")
        table = Table(title="Dependencies Status")
        table.add_column("Package", style="cyan")
        table.add_column("Status", style="green")

        for dep in dependencies:
            try:
                if ">=" in dep:
                    package = dep.split(">=")[0]
                else:
                    package = dep
                __import__(package.replace("-", "_"))
                table.add_row(package, "✅ Installed")
            except ImportError:
                table.add_row(package, "❌ Not installed")

        console.print(table)

    def _check_env_vars(self, env_vars: Dict[str, str]):
        """Check environment variables"""
        console.print("🔑 [blue]Checking environment variables...")
        table = Table(title="Environment Variables Status")
        table.add_column("Variable", style="cyan")
        table.add_column("Status", style="green")

        for key, value in env_vars.items():
            if os.getenv(key):
                table.add_row(key, "✅ Set")
            else:
                table.add_row(key, "❌ Not set")

        console.print(table)

    def _check_services(self, services: List[str]):
        """Check services"""
        console.print("🔧 [blue]Checking services...")
        table = Table(title="Services Status")
        table.add_column("Service", style="cyan")
        table.add_column("Status", style="green")

        for service in services:
            service_file = self.project_root / "api" / "services" / f"{service}.py"
            if service_file.exists():
                table.add_row(service, "✅ Available")
            else:
                table.add_row(service, "❌ Not found")

        console.print(table)

    def _check_api_keys(self):
        """Check API keys"""
        console.print("🔑 [blue]Checking API keys...")
        table = Table(title="API Keys Status")
        table.add_column("API Key", style="cyan")
        table.add_column("Status", style="green")

        required_keys = ["GEMINI_API_KEY", "BYBIT_API_KEY", "BYBIT_API_SECRET"]

        for key in required_keys:
            if os.getenv(key):
                table.add_row(key, "✅ Set")
            else:
                table.add_row(key, "❌ Not set")

        console.print(table)

    def _run_python_tests(self):
        """Run Python tests"""
        try:
            import subprocess

            subprocess.run([sys.executable, "run_tests.py"], check=True)
            console.print("✅ [bold green]Python tests passed!")
        except subprocess.CalledProcessError:
            console.print("❌ [bold red]Python tests failed!")
        except FileNotFoundError:
            console.print("⚠️ [yellow]run_tests.py not found")

    def _run_node_tests(self):
        """Run Node.js tests"""
        try:
            import subprocess

            subprocess.run(["npm", "test"], check=True)
            console.print("✅ [bold green]Node.js tests passed!")
        except subprocess.CalledProcessError:
            console.print("❌ [bold red]Node.js tests failed!")
        except FileNotFoundError:
            console.print("⚠️ [yellow]npm not found")

    def _run_docker_deploy(self):
        """Run Docker deployment"""
        try:
            import subprocess

            subprocess.run(
                ["docker-compose", "-f", "docker-compose.production.yml", "up", "-d"],
                check=True,
            )
            console.print("✅ [bold green]Docker deployment successful!")
        except subprocess.CalledProcessError:
            console.print("❌ [bold red]Docker deployment failed!")
        except FileNotFoundError:
            console.print("⚠️ [yellow]docker-compose not found")

    def show_status(self):
        """Show current AMP status"""
        config = self.load_config()

        # Create status panel
        status_text = f"""
[bold cyan]API Provider:[/bold cyan] {config.get('api_provider', 'Not set')}
[bold cyan]Plugins Installed:[/bold cyan] {len(config.get('plugins', []))}
[bold cyan]Services Enabled:[/bold cyan] {len(config.get('enabled_services', []))}
        """

        console.print(
            Panel(
                status_text, title="[bold blue]AMP Status Report", border_style="blue"
            )
        )

        # Plugins table
        if config.get("plugins"):
            table = Table(title="Installed Plugins")
            table.add_column("Plugin", style="cyan")
            table.add_column("Source", style="blue")
            table.add_column("Status", style="green")
            table.add_column("Description", style="white")

            for plugin in config.get("plugins", []):
                status = "✅ Enabled" if plugin.get("enabled") else "❌ Disabled"
                table.add_row(
                    plugin["name"],
                    plugin.get("source", "N/A"),
                    status,
                    plugin.get("description", "No description"),
                )

            console.print(table)

        # Services table
        if config.get("enabled_services"):
            table = Table(title="Enabled Services")
            table.add_column("Service", style="cyan")

            for service in config.get("enabled_services", []):
                table.add_row(service)

            console.print(table)

        # Features table
        features = [
            ("Sentiment Analysis", "enable_sentiment_analysis"),
            ("Social Signals", "enable_social_signals"),
            ("News Feeds", "enable_news_feeds"),
            ("WebSocket Streams", "enable_websocket_streams"),
        ]

        table = Table(title="Features Status")
        table.add_column("Feature", style="cyan")
        table.add_column("Status", style="green")

        for feature_name, feature_key in features:
            status = "✅ Enabled" if config.get(feature_key) else "❌ Disabled"
            table.add_row(feature_name, status)

        console.print(table)


# Global AMP CLI instance
amp = AMPCLI()


@app.command()
def update(
    env_file: Optional[str] = typer.Option(None, "--env", help="Environment file"),
    set_config: Optional[List[str]] = typer.Option(
        None, "--set", help="Set configuration values"
    ),
    add_dependency: Optional[List[str]] = typer.Option(
        None, "--add-dependency", help="Add dependencies"
    ),
    add_env: Optional[List[str]] = typer.Option(
        None, "--add-env", help="Add environment variables"
    ),
    description: Optional[str] = typer.Option(
        None, "--description", help="Description"
    ),
):
    """Update AMP configuration"""
    amp.update(env_file, set_config, add_dependency, add_env, description)


@app.command()
def plugin_install(
    plugin_name: str = typer.Argument(..., help="Plugin name"),
    source: str = typer.Option("genx-trading", "--source", help="Plugin source"),
    enable_service: Optional[List[str]] = typer.Option(
        None, "--enable-service", help="Enable services"
    ),
    description: str = typer.Option("", "--description", help="Description"),
):
    """Install AMP plugin"""
    amp.plugin_install(plugin_name, source, enable_service, description)


@app.command()
def config_set(
    api_provider: Optional[str] = typer.Option(
        None, "--api-provider", help="API provider"
    ),
    enable_sentiment_analysis: Optional[bool] = typer.Option(
        None, "--enable-sentiment-analysis", help="Enable sentiment analysis"
    ),
    enable_social_signals: Optional[bool] = typer.Option(
        None, "--enable-social-signals", help="Enable social signals"
    ),
    enable_news_feeds: Optional[bool] = typer.Option(
        None, "--enable-news-feeds", help="Enable news feeds"
    ),
    enable_websocket_streams: Optional[bool] = typer.Option(
        None, "--enable-websocket-streams", help="Enable WebSocket streams"
    ),
):
    """Set AMP configuration"""
    amp.config_set(
        api_provider,
        enable_sentiment_analysis,
        enable_social_signals,
        enable_news_feeds,
        enable_websocket_streams,
    )


@app.command()
def service_enable(service: List[str] = typer.Argument(..., help="Services to enable")):
    """Enable services"""
    amp.service_enable(service)


@app.command()
def verify(
    check_dependencies: bool = typer.Option(
        False, "--check-dependencies", help="Check dependencies"
    ),
    check_env_vars: bool = typer.Option(
        False, "--check-env-vars", help="Check environment variables"
    ),
    check_services: bool = typer.Option(
        False, "--check-services", help="Check services"
    ),
    check_api_keys: bool = typer.Option(
        False, "--check-api-keys", help="Check API keys"
    ),
):
    """Verify installation"""
    amp.verify(check_dependencies, check_env_vars, check_services, check_api_keys)


@app.command()
def test(all_tests: bool = typer.Option(False, "--all", help="Run all tests")):
    """Run tests"""
    amp.test(all_tests)


@app.command()
def deploy():
    """Deploy to production"""
    amp.deploy()


@app.command()
def status():
    """Show AMP status"""
    amp.show_status()


@app.command()
def api_health(
    url: Optional[str] = typer.Option(
        None, "--url", help="Backend base URL, e.g. https://service.run.app"
    ),
):
    """Validate API /health endpoint"""
    try:
        import requests

        target = url or os.getenv("BACKEND_URL")
        if not target:
            console.print("⚠️ [yellow]Provide --url or set BACKEND_URL env var")
            raise typer.Exit(1)
        resp = requests.get(target.rstrip("/") + "/health", timeout=10)
        console.print(f"🔎 GET {resp.url} -> {resp.status_code}")
        try:
            console.print(resp.json())
        except Exception:
            console.print(resp.text)
    except Exception as e:
        console.print(f"❌ [bold red]API health check failed: {e}")


@app.command()
def run():
    """Run the next job"""
    console.print("🚀 [bold blue]AMP Job Runner - Starting Next Job")
    console.print("=" * 50)

    # Import and run the job runner
    try:
        from amp_job_runner import AMPJobRunner

        runner = AMPJobRunner()
        asyncio.run(runner.run_next_job())
    except ImportError:
        console.print(
            "❌ [bold red]AMP Job Runner not found. Please ensure amp_job_runner.py exists."
        )


@app.command()
def auth(
    token: Optional[str] = typer.Option(None, "--token", help="Authentication token"),
    logout: bool = typer.Option(False, "--logout", help="Logout current user"),
    status: bool = typer.Option(False, "--status", help="Show authentication status"),
):
    """Manage authentication"""
    try:
        from amp_auth import authenticate_user, check_auth, get_user_info, logout_user

        if logout:
            logout_user()
        elif status:
            if check_auth():
                user_info = get_user_info()
                console.print(
                    f"✅ [bold green]Authenticated as: {user_info['user_id']}"
                )
            else:
                console.print("❌ [bold red]Not authenticated")
        elif token:
            if authenticate_user(token):
                console.print("✅ [bold green]Authentication successful!")
            else:
                console.print("❌ [bold red]Authentication failed!")
        else:
            console.print(
                "Please provide a token with --token or use --status to check current auth"
            )

    except ImportError:
        console.print("❌ [bold red]Authentication module not found")


@app.command()
def schedule(
    start: bool = typer.Option(False, "--start", help="Start the scheduler"),
    stop: bool = typer.Option(False, "--stop", help="Stop the scheduler"),
    status: bool = typer.Option(False, "--status", help="Show scheduler status"),
    interval: Optional[int] = typer.Option(
        None, "--interval", help="Set job interval in minutes"
    ),
    enable: bool = typer.Option(False, "--enable", help="Enable scheduler"),
    disable: bool = typer.Option(False, "--disable", help="Disable scheduler"),
):
    """Manage automated job scheduling"""
    try:
        from amp_scheduler import (
            get_scheduler_status,
            start_scheduler,
            stop_scheduler,
            update_scheduler_config,
        )

        if start:
            console.print("🚀 [bold blue]Starting AMP Scheduler...")
            start_scheduler()
        elif stop:
            console.print("⏹️ [bold yellow]Stopping AMP Scheduler...")
            stop_scheduler()
        elif status:
            status_info = get_scheduler_status()
            console.print(f"📊 [bold blue]Scheduler Status:")
            console.print(f"   Running: {'✅' if status_info['is_running'] else '❌'}")
            console.print(
                f"   Enabled: {'✅' if status_info['config']['enabled'] else '❌'}"
            )
            console.print(
                f"   Interval: {status_info['config']['interval_minutes']} minutes"
            )
            if status_info["last_run"]:
                console.print(f"   Last Run: {status_info['last_run']}")
        elif interval:
            update_scheduler_config(interval_minutes=interval)
            console.print(
                f"✅ [bold green]Scheduler interval updated to {interval} minutes"
            )
        elif enable:
            update_scheduler_config(enabled=True)
            console.print("✅ [bold green]Scheduler enabled")
        elif disable:
            update_scheduler_config(enabled=False)
            console.print("❌ [bold red]Scheduler disabled")
        else:
            console.print(
                "Please specify an action: --start, --stop, --status, --interval, --enable, or --disable"
            )

    except ImportError:
        console.print("❌ [bold red]Scheduler module not found")


@app.command()
def monitor(
    dashboard: bool = typer.Option(
        False, "--dashboard", help="Show real-time dashboard"
    ),
    status: bool = typer.Option(False, "--status", help="Show system status"),
    report: bool = typer.Option(False, "--report", help="Generate monitoring report"),
    alerts: bool = typer.Option(False, "--alerts", help="Show active alerts"),
):
    """Monitor system performance and status"""
    try:
        from amp_monitor import display_dashboard, generate_report, get_system_status

        if dashboard:
            console.print("📊 [bold blue]Starting AMP Monitoring Dashboard...")
            display_dashboard()
        elif status:
            status_info = get_system_status()
            console.print(f"📊 [bold blue]System Status:")

            # Authentication
            auth = status_info["authentication"]
            console.print(
                f"   🔐 Auth: {'✅' if auth['status'] == 'authenticated' else '❌'}"
            )
            if auth.get("user_id"):
                console.print(f"   👤 User: {auth['user_id']}")

            # Scheduler
            scheduler = status_info["scheduler"]
            console.print(
                f"   ⏰ Scheduler: {'✅' if scheduler.get('is_running') else '❌'}"
            )

            # Jobs
            jobs = status_info["jobs"]
            console.print(
                f"   📊 Jobs: {jobs.get('total_jobs', 0)} (Success: {jobs.get('success_rate', 0.0):.1f}%)"
            )

            # Performance
            perf = status_info["performance"]
            uptime_hours = perf.get("uptime_seconds", 0) / 3600
            console.print(
                f"   ⚡ Uptime: {uptime_hours:.1f}h, Logs: {perf.get('logs_size_mb', 0)}MB"
            )

            # Alerts
            alerts_list = status_info["alerts"]
            if alerts_list:
                console.print(f"   🚨 Alerts: {len(alerts_list)} active")
            else:
                console.print(f"   ✅ No alerts")

        elif report:
            report_file = generate_report()
            if report_file:
                console.print(f"✅ [bold green]Report generated: {report_file}")
            else:
                console.print("❌ [bold red]Failed to generate report")
        elif alerts:
            status_info = get_system_status()
            alerts_list = status_info["alerts"]
            if alerts_list:
                console.print(f"🚨 [bold red]Active Alerts:")
                for alert in alerts_list:
                    level_icon = (
                        "🔴"
                        if alert["level"] == "critical"
                        else "🟡" if alert["level"] == "warning" else "🔵"
                    )
                    console.print(f"   {level_icon} {alert['message']}")
            else:
                console.print("✅ [bold green]No active alerts")
        else:
            console.print(
                "Please specify an action: --dashboard, --status, --report, or --alerts"
            )

    except ImportError:
        console.print("❌ [bold red]Monitor module not found")


def main():
    """Main function"""
    app()


if __name__ == "__main__":
    main()
