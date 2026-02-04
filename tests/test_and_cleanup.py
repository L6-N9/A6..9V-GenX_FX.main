#!/usr/bin/env python3
"""
Test and Cleanup Script for GenX Trading Platform
Tests all systems and performs repository cleanup
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

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SystemTester:
    """
    A class for performing comprehensive system testing and cleanup for the
    GenX Trading Platform.
    """

    def __init__(self):
        """
        Initializes the SystemTester.
        """
        self.project_root = Path.cwd()
        self.test_results = {}

    def run_command(self, command: str, cwd: str = None) -> dict:
        """
        Runs a shell command and returns the results.

        Args:
            command (str): The command to run.
            cwd (str, optional): The working directory for the command. Defaults to None.

        Returns:
            dict: A dictionary containing the success status, stdout, stderr,
                  and return code of the command.
        """
        try:
            result = subprocess.run(
                command.split(),
                cwd=cwd or self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out", "returncode": -1}
        except Exception as e:
            return {"success": False, "error": str(e), "returncode": -1}

    def test_python_imports(self) -> dict:
        """
        Tests if all critical and optional Python modules can be imported.

        Returns:
            dict: A dictionary of results for each tested module.
        """
        logger.info("🐍 Testing Python imports...")

        critical_modules = ["pandas", "numpy", "typer", "rich", "requests"]

        optional_modules = ["sklearn", "xgboost", "tensorflow", "talib"]

        results = {}

        for module in critical_modules + optional_modules:
            try:
                __import__(module)
                results[module] = {
                    "status": "success",
                    "critical": module in critical_modules,
                }
                logger.info(f"  ✅ {module}")
            except ImportError as e:
                results[module] = {
                    "status": "failed",
                    "error": str(e),
                    "critical": module in critical_modules,
                }
                if module in critical_modules:
                    logger.error(f"  ❌ {module} (CRITICAL)")
                else:
                    logger.warning(f"  ⚠️ {module} (optional)")

        return results

    def test_cli_tools(self) -> dict:
        """
        Tests all available CLI tools.

        Returns:
            dict: A dictionary of results for each tested CLI tool.
        """
        logger.info("🎮 Testing CLI tools...")

        cli_tests = {
            "head_cli": "./genx --help",
            "amp_cli": "python3 amp_cli.py --help",
            "genx_cli": "python3 genx_cli.py --help",
        }

        results = {}

        for cli_name, command in cli_tests.items():
            logger.info(f"  Testing {cli_name}...")
            result = self.run_command(command)

            if result["success"]:
                logger.info(f"  ✅ {cli_name}")
                results[cli_name] = {"status": "success"}
            else:
                logger.error(f"  ❌ {cli_name}: {result.get('error', 'Failed')}")
                results[cli_name] = {"status": "failed", "error": result.get("error")}

        return results

    def test_amp_system(self) -> dict:
        """
        Tests the functionality of the AMP system.

        Returns:
            dict: A dictionary of results for each AMP system test.
        """
        logger.info("🤖 Testing AMP system...")

        amp_tests = {
            "auth_status": "python3 amp_cli.py auth --status",
            "amp_status": "python3 amp_cli.py status",
            "amp_overview": "./genx amp status",
        }

        results = {}

        for test_name, command in amp_tests.items():
            logger.info(f"  Testing {test_name}...")
            result = self.run_command(command)

            if result["success"]:
                logger.info(f"  ✅ {test_name}")
                results[test_name] = {
                    "status": "success",
                    "output": result["stdout"][:200],
                }
            else:
                logger.warning(f"  ⚠️ {test_name}: {result.get('error', 'Failed')}")
                results[test_name] = {"status": "failed", "error": result.get("error")}

        return results

    def test_file_structure(self) -> dict:
        """
        Tests the project's file and directory structure.

        Returns:
            dict: A dictionary containing the results of the file structure tests.
        """
        logger.info("📁 Testing file structure...")

        required_files = [
            "README.md",
            "requirements.txt",
            "main.py",
            "head_cli.py",
            "amp_cli.py",
            "genx_cli.py",
            "genx",
        ]

        required_dirs = [
            "ai_models",
            "api",
            "core",
            "services",
            "expert-advisors",
            "logs",
            "signal_output",
        ]

        results = {"files": {}, "directories": {}}

        # Test files
        for file_name in required_files:
            file_path = self.project_root / file_name
            if file_path.exists():
                results["files"][file_name] = {
                    "status": "exists",
                    "size": file_path.stat().st_size,
                }
                logger.info(f"  ✅ {file_name}")
            else:
                results["files"][file_name] = {"status": "missing"}
                logger.error(f"  ❌ {file_name}")

        # Test directories
        for dir_name in required_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                item_count = len(list(dir_path.iterdir()))
                results["directories"][dir_name] = {
                    "status": "exists",
                    "items": item_count,
                }
                logger.info(f"  ✅ {dir_name} ({item_count} items)")
            else:
                results["directories"][dir_name] = {"status": "missing"}
                logger.error(f"  ❌ {dir_name}")

        return results

    def cleanup_repository(self) -> dict:
        """
        Cleans up the repository by removing unnecessary files and directories.

        Returns:
            dict: A dictionary containing a list of removed items and their count.
        """
        logger.info("🧹 Cleaning up repository...")

        cleanup_patterns = [
            "__pycache__",
            "*.pyc",
            "*.pyo",
            "*.log",
            ".pytest_cache",
            "node_modules",
            ".DS_Store",
            "Thumbs.db",
            "*.tmp",
            "*.temp",
        ]

        cleanup_dirs = ["amp_env", "forexconnect_env_37"]

        removed_items = []

        # Remove cache directories and files
        for pattern in cleanup_patterns:
            for item in self.project_root.rglob(pattern):
                try:
                    if item.is_file():
                        item.unlink()
                        removed_items.append(str(item))
                    elif item.is_dir():
                        shutil.rmtree(item)
                        removed_items.append(str(item))
                except Exception as e:
                    logger.warning(f"Could not remove {item}: {e}")

        # Remove large directories
        for dir_name in cleanup_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    removed_items.append(str(dir_path))
                    logger.info(f"  ✅ Removed {dir_name}")
                except Exception as e:
                    logger.warning(f"Could not remove {dir_name}: {e}")

        logger.info(f"🧹 Cleanup completed: {len(removed_items)} items removed")
        return {"removed_items": removed_items, "count": len(removed_items)}

    def run_comprehensive_tests(self) -> dict:
        """
        Runs all system tests and generates a summary report.

        Returns:
            dict: A dictionary containing the results of all tests and a summary.
        """
        logger.info("🚀 Starting Comprehensive System Tests...")

        # Run all tests
        test_results = {
            "timestamp": datetime.now().isoformat(),
            "python_imports": self.test_python_imports(),
            "cli_tools": self.test_cli_tools(),
            "amp_system": self.test_amp_system(),
            "file_structure": self.test_file_structure(),
            "cleanup": self.cleanup_repository(),
        }

        # Generate summary
        summary = self.generate_test_summary(test_results)
        test_results["summary"] = summary

        # Save test report
        report_path = (
            self.project_root
            / "logs"
            / f'test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(test_results, f, indent=2)

        logger.info(f"📊 Test report saved: {report_path}")

        return test_results

    def generate_test_summary(self, test_results: dict) -> dict:
        """
        Generates a summary of the test results.

        Args:
            test_results (dict): A dictionary containing the results of all tests.

        Returns:
            dict: A dictionary summarizing the test results.
        """
        summary = {
            "overall_status": "PASS",
            "critical_failures": 0,
            "warnings": 0,
            "passed_tests": 0,
            "total_tests": 0,
        }

        # Count Python import results
        for module, result in test_results["python_imports"].items():
            summary["total_tests"] += 1
            if result["status"] == "success":
                summary["passed_tests"] += 1
            elif result.get("critical", False):
                summary["critical_failures"] += 1
                summary["overall_status"] = "FAIL"
            else:
                summary["warnings"] += 1

        # Count CLI test results
        for cli, result in test_results["cli_tools"].items():
            summary["total_tests"] += 1
            if result["status"] == "success":
                summary["passed_tests"] += 1
            else:
                summary["critical_failures"] += 1
                summary["overall_status"] = "FAIL"

        # Count file structure results
        for file_name, result in test_results["file_structure"]["files"].items():
            summary["total_tests"] += 1
            if result["status"] == "exists":
                summary["passed_tests"] += 1
            else:
                summary["warnings"] += 1

        # Calculate success rate
        if summary["total_tests"] > 0:
            summary["success_rate"] = summary["passed_tests"] / summary["total_tests"]
        else:
            summary["success_rate"] = 0

        return summary


def main() -> int:
    """
    The main function for the test and cleanup script.

    Returns:
        int: 0 if all tests pass, 1 otherwise.
    """
    logger.info("🧪 GenX Trading Platform - System Testing & Cleanup")
    logger.info("=" * 60)

    try:
        tester = SystemTester()
        results = tester.run_comprehensive_tests()

        # Print summary
        summary = results["summary"]
        logger.info("📊 Test Summary:")
        logger.info(f"   Overall Status: {summary['overall_status']}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1%}")
        logger.info(f"   Passed: {summary['passed_tests']}")
        logger.info(f"   Total: {summary['total_tests']}")
        logger.info(f"   Critical Failures: {summary['critical_failures']}")
        logger.info(f"   Warnings: {summary['warnings']}")

        if summary["overall_status"] == "PASS":
            logger.info("🎉 All critical tests passed!")
        else:
            logger.warning("⚠️ Some critical tests failed. Check the detailed report.")

        return 0 if summary["overall_status"] == "PASS" else 1

    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
