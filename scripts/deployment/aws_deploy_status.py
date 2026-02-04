#!/usr/bin/env python3
"""
AWS Deployment Status Checker
Checks the current state of AWS deployment and provides guidance
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def check_aws_cli() -> bool:
    """
    Checks if the AWS CLI is installed and accessible in the system's PATH.

    Returns:
        bool: True if the AWS CLI is installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["aws", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_aws_credentials() -> bool:
    """
    Checks if AWS credentials are configured by calling 'aws sts get-caller-identity'.

    Returns:
        bool: True if credentials are valid, False otherwise.
    """
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_terraform() -> bool:
    """
    Checks if Terraform is installed and accessible in the system's PATH.

    Returns:
        bool: True if Terraform is installed, False otherwise.
    """
    try:
        result = subprocess.run(
            ["terraform", "--version"], capture_output=True, text=True, timeout=10
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def check_ssh_key() -> bool:
    """
    Checks if an SSH key file for the deployment exists in common locations.

    Returns:
        bool: True if an SSH key is found, False otherwise.
    """
    key_files = [
        "amp-trading-key",
        "amp-trading-key.pem",
        "aws/amp-trading-key",
        "aws/amp-trading-key.pem",
    ]
    return any(Path(key_file).exists() for key_file in key_files)


def check_aws_resources() -> Optional[Dict[str, Any]]:
    """
    Checks if AWS resources have been deployed by looking for 'instance_info.json'.

    Returns:
        Optional[Dict[str, Any]]: A dictionary with instance info if found, else None.
    """
    try:
        instance_info_file = Path("instance_info.json")
        if instance_info_file.exists():
            with open(instance_info_file, "r") as f:
                return json.load(f)
        return None
    except (json.JSONDecodeError, FileNotFoundError):
        return None


def show_deployment_status() -> Dict[str, Any]:
    """
    Displays the current AWS deployment status and returns a summary.

    Returns:
        Dict[str, Any]: A dictionary summarizing the deployment status.
    """
    print("🚀 AMP System AWS Deployment Status")
    print("=" * 50)
    print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\n📋 Prerequisites Check:")
    print("-" * 30)
    aws_cli_installed = check_aws_cli()
    print(f"   AWS CLI: {'✅ Installed' if aws_cli_installed else '❌ Not installed'}")
    aws_creds_configured = check_aws_credentials()
    print(
        f"   AWS Credentials: {'✅ Configured' if aws_creds_configured else '❌ Not configured'}"
    )
    terraform_installed = check_terraform()
    print(
        f"   Terraform: {'✅ Installed' if terraform_installed else '❌ Not installed'}"
    )
    ssh_key_exists = check_ssh_key()
    print(f"   SSH Key: {'✅ Found' if ssh_key_exists else '❌ Not found'}")

    print("\n🐳 AWS Resources:")
    print("-" * 20)
    instance_info = check_aws_resources()
    if instance_info:
        print("   EC2 Instance: ✅ Deployed")
        print(f"   Instance ID: {instance_info.get('instance_id', 'N/A')}")
        print(f"   Public IP: {instance_info.get('public_ip', 'N/A')}")
        print(f"   Key Name: {instance_info.get('key_name', 'N/A')}")
    else:
        print("   EC2 Instance: ❌ Not deployed")

    print("\n🔧 Configuration Files:")
    print("-" * 25)
    config_files = [
        "aws/amp-deploy.sh",
        "aws/terraform/main.tf",
        "aws/terraform/user_data.sh",
        "AWS_DEPLOYMENT_GUIDE.md",
    ]
    for config_file in config_files:
        print(
            f"   {config_file}: {'✅ Found' if Path(config_file).exists() else '❌ Missing'}"
        )

    return {
        "aws_cli": aws_cli_installed,
        "aws_creds": aws_creds_configured,
        "terraform": terraform_installed,
        "ssh_key": ssh_key_exists,
        "deployed": instance_info is not None,
        "instance_info": instance_info,
    }


def show_deployment_options():
    """Displays the available deployment options to the user."""
    print("\n🚀 Deployment Options:")
    print("=" * 25)

    print("1. 🎯 Automated Script Deployment (Recommended)")
    print("   - Simple and fast, one-command deployment.")
    print("   - Automatic configuration.")
    print("   Command: ./aws/amp-deploy.sh")

    print("\n2. 🏗️ Terraform Infrastructure as Code")
    print("   - Infrastructure as code, version controlled.")
    print("   - Reproducible deployments.")
    print("   Commands: cd aws/terraform/ && terraform init && terraform apply")

    print("\n3. 📖 Manual AWS Console Deployment")
    print("   - Step-by-step process with full control.")
    print("   - Follow: AWS_DEPLOYMENT_GUIDE.md")


def show_next_steps(status: Dict[str, Any]):
    """
    Displays recommended next steps based on the current deployment status.

    Args:
        status (Dict[str, Any]): The current deployment status dictionary.
    """
    print("\n📋 Next Steps:")
    print("=" * 15)

    if not status.get("aws_cli"):
        print("1. 🔧 Install AWS CLI.")
        print(
            "   Follow the official AWS guide: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
        )
    elif not status.get("aws_creds"):
        print("2. 🔑 Configure AWS Credentials.")
        print("   Run: aws configure")
    elif not status.get("ssh_key"):
        print("3. 🔐 Generate an SSH Key Pair.")
        print("   Run: ssh-keygen -t rsa -b 4096 -f amp-trading-key -N ''")
    elif not status.get("deployed"):
        print("4. 🚀 Deploy to AWS.")
        print("   Run: ./aws/amp-deploy.sh")
    else:
        print("✅ System Deployed!")
        show_access_info(status)


def show_free_tier_info():
    """Displays information about the AWS Free Tier."""
    print("\n💰 AWS Free Tier Information:")
    print("=" * 35)

    print("   - EC2: 750 hours/month of t2.micro or t3.micro (region dependent).")
    print("   - S3: 5GB of standard storage.")
    print("   - RDS: 750 hours of db.t2.micro instance.")
    print("   - Lambda: 1 million free requests per month.")
    print("\n💡 Cost Optimization Tips:")
    print(
        "   - Stop your EC2 instance when not in use: `aws ec2 stop-instances --instance-ids YOUR_ID`"
    )
    print("   - Set up AWS Budgets and billing alerts to monitor costs.")


def show_access_info(status: Dict[str, Any]):
    """
    Displays access information for a deployed instance.

    Args:
        status (Dict[str, Any]): The current deployment status dictionary.
    """
    if status.get("deployed") and status.get("instance_info"):
        instance_info = status["instance_info"]
        public_ip = instance_info.get("public_ip", "N/A")
        key_name = instance_info.get("key_name", "N/A")

        print("\n🔗 Access Information:")
        print("=" * 25)
        print(f"🌐 Public IP: {public_ip}")
        print(f"🔑 Key File: {key_name}.pem")
        print("\n📊 Access URLs:")
        print(f"   - API Docs: http://{public_ip}:8000/docs")
        print(f"   - Health Check: http://{public_ip}:8000/health")
        print("\n⚡ SSH Access:")
        print(f"   ssh -i {key_name}.pem ec2-user@{public_ip}")


def main():
    """Main function to run the status checker and show relevant info."""
    status = show_deployment_status()
    show_deployment_options()
    show_next_steps(status)
    show_free_tier_info()

    print("\n" + "=" * 50)
    print("🎯 Ready to deploy your AMP system to AWS!")
    print("📖 For detailed instructions, see: AWS_DEPLOYMENT_GUIDE.md")


if __name__ == "__main__":
    main()
