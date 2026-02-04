"""
Agent 2: Deploys the platform to Vercel and Railway.

This script generates the necessary configuration files for deploying
the application to Vercel and Railway.
"""

import json
import subprocess


def deploy_to_vercel():
    """
    Creates the necessary configuration files for deploying to Vercel.

    This function generates 'vercel.json' for build and routing configuration,
    and 'requirements-vercel.txt' for Python dependencies.
    """
    # Create vercel.json configuration
    vercel_config = {
        "version": 2,
        "builds": [
            {"src": "api/main.py", "use": "@vercel/python"},
            {"src": "dist/**", "use": "@vercel/static"},
        ],
        "routes": [
            {"src": "/api/(.*)", "dest": "/api/main.py"},
            {"src": "/(.*)", "dest": "/dist/$1"},
        ],
        "env": {"NODE_ENV": "production"},
    }

    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)

    # Create requirements.txt for Vercel
    requirements = ["fastapi==0.104.1", "uvicorn==0.24.0", "sqlite3"]

    with open("requirements-vercel.txt", "w") as f:
        for req in requirements:
            f.write(f"{req}\n")

    print("Agent 2: Vercel deployment configured")
    print("Files created: vercel.json, requirements-vercel.txt")
    print("Run: vercel --prod")


def deploy_to_railway():
    """
    Creates the 'railway.json' configuration file for deploying to Railway.
    """
    # Create railway.json
    railway_config = {
        "build": {"builder": "NIXPACKS"},
        "deploy": {"startCommand": "uvicorn api.main:app --host 0.0.0.0 --port $PORT"},
    }

    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)

    print("Agent 2: Railway deployment configured")
    print("File created: railway.json")


if __name__ == "__main__":
    deploy_to_vercel()
    deploy_to_railway()
