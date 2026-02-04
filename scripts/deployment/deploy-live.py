import os
import subprocess


def deploy_to_github_pages() -> bool:
    """
    Deploys the application to GitHub Pages.

    This function builds the frontend, creates a 'gh-pages' branch,
    and pushes the 'dist' directory to it.

    Returns:
        bool: True if deployment is successful, False otherwise.
    """
    # Create GitHub Pages deployment
    try:
        # Build for GitHub Pages
        subprocess.run(["npm", "run", "build"], check=True)

        # Create gh-pages branch and deploy
        commands = [
            "git checkout -b gh-pages",
            "git add dist/",
            'git commit -m "Deploy to GitHub Pages"',
            "git subtree push --prefix dist origin gh-pages",
        ]

        for cmd in commands:
            subprocess.run(cmd.split(), check=True)

        print("✅ Deployed to GitHub Pages")
        print("🌐 Live URL: https://mouy-leng.github.io/GenX_FX/")
        return True

    except Exception as e:
        print(f"❌ GitHub Pages deployment failed: {e}")
        return False


def deploy_to_netlify() -> bool:
    """
    Prepares the application for deployment to Netlify by creating a 'netlify.toml' file.

    Returns:
        bool: True after creating the configuration file.
    """
    # Create netlify.toml
    netlify_config = """
[build]
  publish = "dist"
  command = "npm run build"

[build.environment]
  NODE_ENV = "production"

[[redirects]]
  from = "/api/*"
  to = "/.netlify/functions/:splat"
  status = 200
"""

    with open("netlify.toml", "w") as f:
        f.write(netlify_config)

    print("✅ Netlify configuration created")
    print("📁 Upload dist/ folder to Netlify manually")
    return True


def start_local_production():
    """
    Starts the production server locally for testing.
    """
    # Start production server locally
    try:
        print("🚀 Starting local production server...")
        subprocess.run(["python", "api/main.py"], check=True)
    except KeyboardInterrupt:
        print("🛑 Server stopped")


if __name__ == "__main__":
    print("=== Live Deployment Options ===")
    print("1. GitHub Pages (Free)")
    print("2. Netlify (Free)")
    print("3. Local Production Server")

    choice = input("Choose deployment (1/2/3): ")

    if choice == "1":
        deploy_to_github_pages()
    elif choice == "2":
        deploy_to_netlify()
    elif choice == "3":
        start_local_production()
    else:
        print("Invalid choice")
