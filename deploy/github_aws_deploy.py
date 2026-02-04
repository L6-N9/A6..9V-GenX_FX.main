#!/usr/bin/env python3
"""
GitHub Token AWS Deployment Script
Uses GitHub API with token authentication for AWS deployment
"""

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional

import boto3
import docker
import requests
from botocore.exceptions import ClientError, NoCredentialsError
from docker.errors import DockerException

# GitHub token (provide via environment variable or --token argument)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Default values
DEFAULT_ENVIRONMENT = "production"
DEFAULT_AWS_REGION = "us-east-1"
DEFAULT_BRANCH = "main"


class Colors:
    """ANSI color codes for terminal output"""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"  # No Color


class GitHubAWSDployer:
    """Main deployment class for GitHub token-based AWS deployment"""

    def __init__(self, environment: str, region: str, branch: str, token: str):
        self.environment = environment
        self.region = region
        self.branch = branch
        self.token = token
        self.github_headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.deployment_id = None
        self.deployment_url = None

        # Initialize AWS and Docker clients
        self.aws_session = None
        self.docker_client = None
        self.ecr_client = None

    def print_status(self, message: str):
        """Print status message with blue color"""
        print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")

    def print_success(self, message: str):
        """Print success message with green color"""
        print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

    def print_warning(self, message: str):
        """Print warning message with yellow color"""
        print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

    def print_error(self, message: str):
        """Print error message with red color"""
        print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

    def check_github_token(self) -> bool:
        """Check if GitHub token is valid"""
        try:
            response = requests.get(
                "https://api.github.com/user", headers=self.github_headers
            )
            if response.status_code == 200:
                user_data = response.json()
                self.print_success(
                    f"GitHub authentication successful for user: {user_data['login']}"
                )
                return True
            else:
                self.print_error(
                    f"GitHub authentication failed: {response.status_code}"
                )
                return False
        except Exception as e:
            self.print_error(f"Failed to check GitHub token: {e}")
            return False

    def check_aws_credentials(self) -> bool:
        """Check if AWS credentials are configured"""
        try:
            self.aws_session = boto3.Session(region_name=self.region)
            sts_client = self.aws_session.client("sts")
            identity = sts_client.get_caller_identity()
            self.print_success(
                f"AWS credentials configured for account: {identity['Account']}"
            )
            return True
        except NoCredentialsError:
            self.print_error("AWS credentials not configured")
            return False
        except Exception as e:
            self.print_error(f"Failed to check AWS credentials: {e}")
            return False

    def setup_aws_from_github_secrets(self) -> bool:
        """Setup AWS credentials from GitHub repository secrets"""
        try:
            # Get repository secrets (requires admin access)
            repo_owner = self._get_repo_owner()
            repo_name = self._get_repo_name()

            # Note: GitHub API doesn't allow reading secrets directly
            # This would need to be done through GitHub CLI or environment variables
            self.print_warning("GitHub API doesn't allow direct secret reading")
            self.print_status("Please set AWS credentials as environment variables:")
            self.print_status("export AWS_ACCESS_KEY_ID=your_access_key")
            self.print_status("export AWS_SECRET_ACCESS_KEY=your_secret_key")
            self.print_status("export AWS_DEFAULT_REGION=us-east-1")
            return False

        except Exception as e:
            self.print_error(f"Failed to setup AWS from GitHub secrets: {e}")
            return False

    def _get_repo_owner(self) -> str:
        """Get repository owner from git remote"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()
            if "github.com" in remote_url:
                parts = remote_url.split("github.com/")[-1].split("/")
                return parts[0]
            return "unknown"
        except:
            return "unknown"

    def _get_repo_name(self) -> str:
        """Get repository name from git remote"""
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=True,
            )
            remote_url = result.stdout.strip()
            if "github.com" in remote_url:
                parts = remote_url.split("github.com/")[-1].split("/")
                return parts[1].replace(".git", "")
            return "unknown"
        except:
            return "unknown"

    def create_github_deployment(self) -> Optional[str]:
        """Create a GitHub deployment"""
        try:
            repo_owner = self._get_repo_owner()
            repo_name = self._get_repo_name()

            # Get current commit SHA
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
            )
            commit_sha = result.stdout.strip()

            deployment_data = {
                "ref": commit_sha,
                "environment": self.environment,
                "description": f"Deployment to AWS {self.environment}",
                "auto_merge": False,
                "required_contexts": [],
            }

            url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/deployments"
            response = requests.post(
                url, headers=self.github_headers, json=deployment_data
            )

            if response.status_code == 201:
                deployment = response.json()
                self.deployment_id = str(deployment["id"])
                self.print_success(
                    f"Created GitHub deployment with ID: {self.deployment_id}"
                )
                return self.deployment_id
            else:
                self.print_error(
                    f"Failed to create deployment: {response.status_code} - {response.text}"
                )
                return None

        except Exception as e:
            self.print_error(f"Failed to create GitHub deployment: {e}")
            return None

    def update_deployment_status(
        self, state: str, description: str, url: str = None
    ) -> bool:
        """Update GitHub deployment status"""
        if not self.deployment_id:
            self.print_warning("No deployment ID available")
            return False

        try:
            repo_owner = self._get_repo_owner()
            repo_name = self._get_repo_name()

            status_data = {"state": state, "description": description}

            if url:
                status_data["environment_url"] = url

            status_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/deployments/{self.deployment_id}/statuses"
            response = requests.post(
                status_url, headers=self.github_headers, json=status_data
            )

            if response.status_code == 201:
                self.print_success(f"Updated deployment status to: {state}")
                return True
            else:
                self.print_error(
                    f"Failed to update deployment status: {response.status_code}"
                )
                return False

        except Exception as e:
            self.print_error(f"Failed to update deployment status: {e}")
            return False

    def build_and_push_docker_images(self) -> bool:
        """Build and push Docker images to ECR"""
        try:
            # Initialize Docker client
            self.docker_client = docker.from_env()

            # Get ECR registry
            sts_client = self.aws_session.client("sts")
            account_id = sts_client.get_caller_identity()["Account"]
            ecr_registry = f"{account_id}.dkr.ecr.{self.region}.amazonaws.com"

            # Initialize ECR client
            self.ecr_client = self.aws_session.client("ecr")

            # Get ECR login token
            auth_response = self.ecr_client.get_authorization_token()
            username, password = (
                auth_response["authorizationData"][0]["authorizationToken"]
                .decode("base64")
                .split(":")
            )

            # Login to ECR
            self.docker_client.login(
                username=username, password=password, registry=ecr_registry
            )

            # Get current commit SHA for image tag
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
            )
            image_tag = result.stdout.strip()

            # Build and push main API image
            self.print_status("Building main API image...")
            image, logs = self.docker_client.images.build(
                path=".",
                dockerfile="Dockerfile.production",
                tag=f"{ecr_registry}/genx-api:{image_tag}",
            )

            # Tag as latest
            image.tag(f"{ecr_registry}/genx-api", "latest")

            # Push images
            self.docker_client.images.push(f"{ecr_registry}/genx-api:{image_tag}")
            self.docker_client.images.push(f"{ecr_registry}/genx-api:latest")

            self.print_success("Docker images built and pushed successfully")
            return True

        except DockerException as e:
            self.print_error(f"Docker error: {e}")
            return False
        except Exception as e:
            self.print_error(f"Failed to build and push Docker images: {e}")
            return False

    def deploy_to_aws(self) -> bool:
        """Deploy to AWS using existing deployment script"""
        try:
            self.print_status(f"Deploying to AWS {self.environment} environment...")

            # Run the existing AWS deployment script
            if os.path.exists("deploy/aws-deploy.sh"):
                os.chmod("deploy/aws-deploy.sh", 0o755)
                result = subprocess.run(
                    [
                        "./deploy/aws-deploy.sh",
                        "--region",
                        self.region,
                        "--environment",
                        self.environment,
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0:
                    self.print_success("AWS deployment completed successfully")
                    return True
                else:
                    self.print_error(f"AWS deployment failed: {result.stderr}")
                    return False
            else:
                self.print_error("AWS deployment script not found")
                return False

        except Exception as e:
            self.print_error(f"Failed to deploy to AWS: {e}")
            return False

    def get_deployment_url(self) -> Optional[str]:
        """Get the deployment URL from CloudFormation outputs"""
        try:
            stack_name = f"{self.environment}-genx-trading-platform"
            cloudformation = self.aws_session.client("cloudformation")

            response = cloudformation.describe_stacks(StackName=stack_name)

            for output in response["Stacks"][0]["Outputs"]:
                if output["OutputKey"] == "LoadBalancerDNS":
                    alb_dns = output["OutputValue"]
                    self.deployment_url = f"http://{alb_dns}"
                    self.print_success(f"Application URL: {self.deployment_url}")
                    return self.deployment_url

            self.print_warning("Could not retrieve deployment URL")
            return None

        except ClientError as e:
            self.print_error(f"AWS CloudFormation error: {e}")
            return None
        except Exception as e:
            self.print_error(f"Failed to get deployment URL: {e}")
            return None

    def health_check(self, url: str, max_attempts: int = 30) -> bool:
        """Perform health check on deployed application"""
        self.print_status(f"Performing health check on {url}...")

        for attempt in range(1, max_attempts + 1):
            try:
                response = requests.get(f"{url}/health", timeout=10)
                if response.status_code == 200:
                    self.print_success("Health check passed!")
                    return True
            except requests.RequestException:
                pass

            self.print_status(
                f"Health check attempt {attempt}/{max_attempts} failed, retrying in 10 seconds..."
            )
            time.sleep(10)

        self.print_error(f"Health check failed after {max_attempts} attempts")
        return False

    def deploy(self) -> bool:
        """Main deployment method"""
        self.print_status("Starting GitHub Token AWS Deployment")
        self.print_status(f"Environment: {self.environment}")
        self.print_status(f"Region: {self.region}")
        self.print_status(f"Branch: {self.branch}")

        # Step 1: Check GitHub token
        if not self.check_github_token():
            return False

        # Step 2: Check AWS credentials
        if not self.check_aws_credentials():
            if not self.setup_aws_from_github_secrets():
                return False

        # Step 3: Create GitHub deployment
        if not self.create_github_deployment():
            return False

        # Step 4: Update deployment status to in_progress
        self.update_deployment_status("in_progress", "Starting deployment to AWS")

        # Step 5: Build and push Docker images
        if not self.build_and_push_docker_images():
            self.update_deployment_status(
                "failure", "Failed to build and push Docker images"
            )
            return False

        # Step 6: Deploy to AWS
        if not self.deploy_to_aws():
            self.update_deployment_status("failure", "Failed to deploy to AWS")
            return False

        # Step 7: Get deployment URL
        deployment_url = self.get_deployment_url()

        # Step 8: Perform health check
        if deployment_url:
            if self.health_check(deployment_url):
                self.update_deployment_status(
                    "success", "Deployment successful and healthy", deployment_url
                )
                self.print_success("Deployment completed successfully!")
                self.print_success(f"Application URL: {deployment_url}")
                return True
            else:
                self.update_deployment_status(
                    "failure",
                    "Deployment completed but health check failed",
                    deployment_url,
                )
                self.print_error("Deployment completed but health check failed")
                return False
        else:
            self.update_deployment_status("success", "Deployment completed")
            self.print_success("Deployment completed successfully!")
            return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="GitHub Token AWS Deployment Script")
    parser.add_argument(
        "-e",
        "--environment",
        default=DEFAULT_ENVIRONMENT,
        help=f"Environment to deploy to (default: {DEFAULT_ENVIRONMENT})",
    )
    parser.add_argument(
        "-r",
        "--region",
        default=DEFAULT_AWS_REGION,
        help=f"AWS region (default: {DEFAULT_AWS_REGION})",
    )
    parser.add_argument(
        "-b",
        "--branch",
        default=DEFAULT_BRANCH,
        help=f"Git branch to deploy (default: {DEFAULT_BRANCH})",
    )
    parser.add_argument(
        "-t",
        "--token",
        help="GitHub personal access token (default: uses GITHUB_TOKEN env var)",
    )

    args = parser.parse_args()

    # Use provided token or environment variable
    token = args.token or GITHUB_TOKEN

    if not token:
        print(f"{Colors.RED}[ERROR]{Colors.NC} GitHub token not provided")
        print(
            "Please provide a token using --token or set GITHUB_TOKEN environment variable"
        )
        sys.exit(1)

    # Create deployer and run deployment
    deployer = GitHubAWSDployer(
        environment=args.environment,
        region=args.region,
        branch=args.branch,
        token=token,
    )

    success = deployer.deploy()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
