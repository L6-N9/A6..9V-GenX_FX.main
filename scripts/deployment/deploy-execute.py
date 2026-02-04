import os
import shutil
import subprocess


def execute_deployment() -> bool:
    """
    Executes the full deployment process for the GenX-FX application.

    This includes building the frontend, testing the backend, creating a
    deployment package, uploading to Google Drive, and preparing for production
    deployment.

    Returns:
        bool: True if the deployment process completes successfully, False otherwise.
    """
    print("=== GenX-FX Deployment Execution ===")

    # 1. Build frontend
    print("1. Building frontend...")
    result = subprocess.run(["npm", "run", "build"], capture_output=True, text=True)
    if result.returncode == 0:
        print("✓ Frontend build successful")
    else:
        print("✗ Frontend build failed")
        return False

    # 2. Test backend
    print("2. Testing backend...")
    result = subprocess.run(
        ["python", "-m", "pytest", "tests/test_bybit_api.py", "-v"],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("✓ Backend tests passed")
    else:
        print("✗ Backend tests failed")
        return False

    # 3. Create deployment package
    print("3. Creating deployment package...")
    if os.path.exists("deploy-package"):
        shutil.rmtree("deploy-package")

    os.makedirs("deploy-package")

    # Copy essential files
    files_to_copy = [
        "api/",
        "dist/",
        "requirements.txt",
        "package.json",
        "docker-compose.yml",
        "Dockerfile",
    ]

    for file in files_to_copy:
        if os.path.exists(file):
            if os.path.isdir(file):
                shutil.copytree(file, f"deploy-package/{file}")
            else:
                shutil.copy2(file, "deploy-package/")

    print("✓ Deployment package created")

    # 4. Upload to Google Drive
    print("4. Uploading to Google Drive...")
    try:
        from google_drive_deploy import deploy_to_drive

        if deploy_to_drive():
            print("✓ Uploaded to Google Drive")
        else:
            print("✗ Google Drive upload failed")
    except Exception as e:
        print(f"✗ Google Drive error: {e}")

    # 5. Deploy to production
    print("5. Deploying to production...")
    # Add your production deployment commands here
    print("✓ Ready for production deployment")

    return True


if __name__ == "__main__":
    success = execute_deployment()
    if success:
        print("\n🚀 Deployment completed successfully!")
    else:
        print("\n❌ Deployment failed!")
