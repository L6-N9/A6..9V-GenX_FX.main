#!/usr/bin/env python3
"""
AMP Monitoring Dashboard
Real-time monitoring and analytics for the AMP system
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from amp_auth import check_auth, get_user_info
from amp_scheduler import get_scheduler_status


class AMPMonitor:
    """
    A class for monitoring the real-time status and health of the AMP system.

    This class provides methods to check authentication, scheduler status,
    job history, performance metrics, and active alerts. It can also generate
    reports and display a live dashboard in the console.

    Attributes:
        logs_dir (Path): The directory where logs are stored.
        reports_dir (Path): The directory where reports are saved.
        monitor_config (Path): The path to the monitor's configuration file.
        config (Dict): The loaded monitoring configuration.
    """

    def __init__(self):
        """Initializes the AMPMonitor."""
        self.logs_dir = Path("logs")
        self.reports_dir = Path("reports")
        self.monitor_config = Path("amp_monitor_config.json")

        self.logs_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)

        self.config: Dict[str, Any] = {}
        self.load_config()

    def load_config(self):
        """Loads the monitoring configuration from a JSON file, or creates a default."""
        default_config = {
            "refresh_interval": 30,
            "retention_days": 7,
            "alerts_enabled": True,
            "metrics_enabled": True,
        }

        if self.monitor_config.exists():
            try:
                with open(self.monitor_config, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except json.JSONDecodeError:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        """Saves the current monitoring configuration to a JSON file."""
        try:
            with open(self.monitor_config, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving monitor config: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """
        Gets a comprehensive snapshot of the system's current status.

        Returns:
            Dict[str, Any]: A dictionary containing the status of all major components.
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "authentication": self.get_auth_status(),
            "scheduler": self.get_scheduler_status(),
            "jobs": self.get_job_status(),
            "performance": self.get_performance_metrics(),
            "alerts": self.get_active_alerts(),
        }

    def get_auth_status(self) -> Dict[str, Any]:
        """
        Gets the current authentication status.

        Returns:
            Dict[str, Any]: A dictionary with authentication status details.
        """
        try:
            if check_auth():
                user_info = get_user_info()
                return {
                    "status": "authenticated",
                    "user_id": user_info.get("user_id"),
                    "session_active": True,
                }
            else:
                return {
                    "status": "not_authenticated",
                    "user_id": None,
                    "session_active": False,
                }
        except Exception as e:
            return {"status": "error", "error": str(e), "session_active": False}

    def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Gets the current status of the job scheduler.

        Returns:
            Dict[str, Any]: A dictionary with scheduler status details.
        """
        try:
            return get_scheduler_status()
        except Exception as e:
            return {"error": str(e), "is_running": False}

    def get_job_status(self) -> Dict[str, Any]:
        """
        Gets the status of job executions by analyzing recent job reports.

        Returns:
            Dict[str, Any]: A dictionary summarizing the job history and success rate.
        """
        try:
            job_reports = sorted(
                self.logs_dir.glob("amp_job_report_*.json"),
                key=lambda x: x.stat().st_mtime,
                reverse=True,
            )

            if not job_reports:
                return {"total_jobs": 0, "last_job": None, "success_rate": 0.0}

            # Analyze recent jobs
            recent_jobs = []
            success_count = 0
            total_count = 0

            for report_file in job_reports[:10]:  # Last 10 jobs
                try:
                    with open(report_file, "r") as f:
                        job_data = json.load(f)

                    recent_jobs.append(
                        {
                            "job_id": job_data.get("job_id"),
                            "timestamp": job_data.get("timestamp"),
                            "status": job_data.get("status"),
                            "duration": job_data.get("duration"),
                        }
                    )

                    total_count += 1
                    if job_data.get("status") == "completed":
                        success_count += 1

                except Exception:
                    continue

            return {
                "total_jobs": total_count,
                "last_job": recent_jobs[0] if recent_jobs else None,
                "recent_jobs": recent_jobs[:5],
                "success_rate": (
                    (success_count / total_count * 100) if total_count > 0 else 0.0
                ),
            }

        except Exception as e:
            return {"error": str(e), "total_jobs": 0}

    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        Gets system performance metrics like uptime and disk usage.

        Returns:
            Dict[str, Any]: A dictionary with performance metrics.
        """
        try:
            uptime = timedelta(0)
            uptime_file = Path("logs/amp_startup.log")
            if uptime_file.exists():
                with open(uptime_file, "r") as f:
                    start_time_str = f.readline().strip()
                    if start_time_str:
                        try:
                            start_dt = datetime.fromisoformat(start_time_str)
                            uptime = datetime.now() - start_dt
                        except ValueError:
                            pass  # Ignore if timestamp is invalid

            logs_size = sum(
                f.stat().st_size for f in self.logs_dir.rglob("*") if f.is_file()
            )

            return {
                "uptime_seconds": int(uptime.total_seconds()),
                "logs_size_bytes": logs_size,
                "logs_size_mb": round(logs_size / (1024 * 1024), 2),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """
        Checks for and returns a list of active system alerts.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each representing an alert.
        """
        alerts = []
        try:
            if not check_auth():
                alerts.append(
                    {
                        "level": "critical",
                        "message": "User not authenticated",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            scheduler_status = get_scheduler_status()
            if not scheduler_status.get("is_running", False):
                alerts.append(
                    {
                        "level": "warning",
                        "message": "Scheduler not running",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            job_status = self.get_job_status()
            success_rate = job_status.get("success_rate", 100.0)
            if success_rate < 80.0 and job_status.get("total_jobs", 0) > 5:
                alerts.append(
                    {
                        "level": "warning",
                        "message": f"Low job success rate: {success_rate:.1f}%",
                        "timestamp": datetime.now().isoformat(),
                    }
                )
        except Exception as e:
            alerts.append(
                {
                    "level": "error",
                    "message": f"Monitoring error: {str(e)}",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        return alerts

    def generate_report(self) -> str:
        """
        Generates a comprehensive monitoring report and saves it to a JSON file.

        Returns:
            str: The path to the generated report file, or an empty string on failure.
        """
        status = self.get_system_status()
        report_file = (
            self.reports_dir
            / f"amp_monitor_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        try:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(status, f, indent=2)
            return str(report_file)
        except Exception as e:
            print(f"Error generating report: {e}")
            return ""

    def display_dashboard(self):
        """Displays a real-time monitoring dashboard in the console."""
        print("=" * 60)
        print("🚀 AMP SYSTEM MONITORING DASHBOARD")
        print("=" * 60)

        while True:
            try:
                # Clear screen (simple approach)
                print("\n" * 50)
                print("=" * 60)
                print("🚀 AMP SYSTEM MONITORING DASHBOARD")
                print(
                    f"📅 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                print("=" * 60)

                status = self.get_system_status()

                # Authentication Status
                auth = status["authentication"]
                print(f"\n🔐 AUTHENTICATION:")
                print(
                    f"   Status: {'✅ Authenticated' if auth['status'] == 'authenticated' else '❌ Not Authenticated'}"
                )
                if auth.get("user_id"):
                    print(f"   User ID: {auth['user_id']}")

                # Scheduler Status
                scheduler = status["scheduler"]
                print(f"\n⏰ SCHEDULER:")
                print(
                    f"   Running: {'✅ Yes' if scheduler.get('is_running') else '❌ No'}"
                )
                print(
                    f"   Enabled: {'✅ Yes' if scheduler.get('config', {}).get('enabled') else '❌ No'}"
                )
                if scheduler.get("config"):
                    print(
                        f"   Interval: {scheduler['config'].get('interval_minutes', 'N/A')} minutes"
                    )

                # Job Status
                jobs = status["jobs"]
                print(f"\n📊 JOBS:")
                print(f"   Total Jobs: {jobs.get('total_jobs', 0)}")
                print(f"   Success Rate: {jobs.get('success_rate', 0.0):.1f}%")
                if jobs.get("last_job"):
                    print(
                        f"   Last Job: {jobs['last_job']['job_id']} ({jobs['last_job']['status']})"
                    )

                # Performance
                perf = status["performance"]
                print(f"\n⚡ PERFORMANCE:")
                uptime_hours = perf.get("uptime_seconds", 0) / 3600
                print(f"   Uptime: {uptime_hours:.1f} hours")
                print(f"   Logs Size: {perf.get('logs_size_mb', 0)} MB")

                # Alerts
                alerts = status["alerts"]
                if alerts:
                    print(f"\n🚨 ALERTS:")
                    for alert in alerts:
                        level_icon = (
                            "🔴"
                            if alert["level"] == "critical"
                            else "🟡" if alert["level"] == "warning" else "🔵"
                        )
                        print(f"   {level_icon} {alert['message']}")
                else:
                    print(f"\n✅ No active alerts")

                print(f"\n{'=' * 60}")
                print("Press Ctrl+C to exit")

                # Wait for next update
                time.sleep(self.config.get("refresh_interval", 30))

            except KeyboardInterrupt:
                print("\n\n👋 Dashboard stopped")
                break
            except Exception as e:
                print(f"\n❌ Dashboard error: {e}")
                time.sleep(5)


# Global monitor instance
amp_monitor = AMPMonitor()


def get_system_status() -> Dict[str, Any]:
    """Get system status"""
    return amp_monitor.get_system_status()


def generate_report() -> str:
    """Generate monitoring report"""
    return amp_monitor.generate_report()


def display_dashboard():
    """Display monitoring dashboard"""
    amp_monitor.display_dashboard()
