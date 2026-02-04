#!/usr/bin/env python3
"""
Docker Deployment Verification Script
Checks the current state of your AMP system Docker setup
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


def check_file_exists(file_path: str) -> bool:
    """
    Checks if a file exists at the given path.

    Args:
        file_path (str): The path to the file.

    Returns:
        bool: True if the file exists, False otherwise.
    """
    return Path(file_path).exists()


def check_docker_installed() -> bool:
    """
    Checks if Docker is installed and running.

    Returns:
        bool: True if Docker is installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["docker", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_docker_compose_installed() -> bool:
    """
    Checks if Docker Compose is installed.

    Returns:
        bool: True if Docker Compose is installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["docker-compose", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_docker_image_exists(image_name: str) -> bool:
    """
    Checks if a Docker image exists locally.

    Args:
        image_name (str): The name of the Docker image.

    Returns:
        bool: True if the image exists, False otherwise.
    """
    try:
        result = subprocess.run(
            ["docker", "images", "-q", image_name],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return bool(result.stdout.strip())
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def get_git_status() -> Dict:
    """
    Gets the current Git status, including branch, commit, and remote URL.

    Returns:
        Dict: A dictionary containing the Git status.
    """
    try:
        # Get current branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        current_branch = (
            branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        )

        # Get latest commit
        commit_result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        latest_commit = (
            commit_result.stdout.strip() if commit_result.returncode == 0 else "unknown"
        )

        # Get remote URL
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        remote_url = (
            remote_result.stdout.strip() if remote_result.returncode == 0 else "unknown"
        )

        return {"branch": current_branch, "commit": latest_commit, "remote": remote_url}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"branch": "unknown", "commit": "unknown", "remote": "unknown"}


def verify_setup():
    """
    Verifies the complete Docker setup by checking for required tools,
    configuration files, and Docker images.
    """
    print("🐳 Docker Deployment Setup Verification")
    print("=" * 50)

    # Check Docker installation
    print("\n📋 System Requirements:")
    docker_installed = check_docker_installed()
    print(f"   Docker: {'✅ Installed' if docker_installed else '❌ Not installed'}")

    docker_compose_installed = check_docker_compose_installed()
    print(
        f"   Docker Compose: {'✅ Installed' if docker_compose_installed else '❌ Not installed'}"
    )

    # Check Git status
    print("\n📦 Git Repository Status:")
    git_status = get_git_status()
    print(f"   Branch: {git_status['branch']}")
    print(f"   Latest Commit: {git_status['commit']}")
    print(f"   Remote: {git_status['remote']}")

    # Check Docker configuration files
    print("\n🔧 Docker Configuration Files:")
    docker_files = [
        "Dockerfile.production",
        "docker-compose.amp.yml",
        "requirements-amp.txt",
        ".github/workflows/docker-image.yml",
    ]

    for file_path in docker_files:
        exists = check_file_exists(file_path)
        print(f"   {file_path}: {'✅ Found' if exists else '❌ Missing'}")

    # Check AMP CLI files
    print("\n⚡ AMP CLI System:")
    amp_files = [
        "amp_cli.py",
        "amp_job_runner.py",
        "amp_scheduler.py",
        "amp_monitor.py",
        "amp_auth.py",
    ]

    for file_path in amp_files:
        exists = check_file_exists(file_path)
        print(f"   {file_path}: {'✅ Found' if exists else '❌ Missing'}")

    # Check Docker image
    print("\n🐳 Docker Image Status:")
    image_name = "keamouyleng/genx-fx:latest"
    image_exists = check_docker_image_exists(image_name)
    print(
        f"   {image_name}: {'✅ Available locally' if image_exists else '❌ Not found locally'}"
    )

    # Summary and next steps
    print("\n" + "=" * 50)
    print("📊 SUMMARY:")

    if all(check_file_exists(f) for f in docker_files) and all(
        check_file_exists(f) for f in amp_files
    ):
        print("✅ All Docker configuration files are present")
        print("✅ AMP CLI system is complete")

        if docker_installed and docker_compose_installed:
            print("✅ Docker tools are installed")

            if not image_exists:
                print("\n🚀 NEXT STEPS:")
                print("1. Configure GitHub Secrets:")
                print(
                    "   - Go to: https://github.com/Mouy-leng/GenX_FX/settings/secrets/actions"
                )
                print("   - Add DOCKER_USERNAME: lengkundee01@gmail.com")
                print("   - Add DOCKER_PASSWORD: KML12345@#$01")
                print("\n2. Push to trigger build:")
                print(
                    "   git push origin cursor/check-docker-and-container-registration-status-5116"
                )
                print("\n3. Monitor build:")
                print("   https://github.com/Mouy-leng/GenX_FX/actions")
            else:
                print("✅ Docker image is available locally")
                print("\n🚀 Ready to deploy:")
                print("   docker-compose -f docker-compose.amp.yml up -d")
        else:
            print("❌ Docker tools need to be installed")
    else:
        print("❌ Some configuration files are missing")
        print("   Please ensure all Docker and AMP files are present")


if __name__ == "__main__":
    verify_setup()
