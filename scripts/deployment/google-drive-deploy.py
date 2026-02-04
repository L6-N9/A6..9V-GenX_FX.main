import json
import os

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Google Drive API setup
SCOPES = ["https://www.googleapis.com/auth/drive"]
CLIENT_SECRET_FILE = "client_secret_723463751699-ukpjrov1tcb3eas5982g4cmvljt33ut4.apps.googleusercontent.com.json"


def authenticate_google_drive():
    """
    Authenticates with the Google Drive API using OAuth 2.0.
    It handles token creation and refreshing.

    Returns:
        A Google Drive API service object.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = Flow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
        flow.redirect_uri = "http://localhost:8080"
        auth_url, _ = flow.authorization_url(prompt="consent")
        print(f"Go to: {auth_url}")
        code = input("Enter authorization code: ")
        flow.fetch_token(code=code)
        creds = flow.credentials

        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def get_drive_info() -> dict:
    """
    Retrieves information about the user's Google Drive, including user details,
    storage quota, and a list of files.

    Returns:
        dict: A dictionary containing user, storage, and file information.
    """
    service = authenticate_google_drive()

    # Get user info
    about = service.about().get(fields="user,storageQuota").execute()

    # List files in root
    results = (
        service.files().list(pageSize=10, fields="files(id,name,mimeType)").execute()
    )
    files = results.get("files", [])

    return {
        "user": about.get("user"),
        "storage": about.get("storageQuota"),
        "files": files,
    }


def deploy_to_drive() -> bool:
    """
    Deploys the application to Google Drive by creating a deployment folder.

    Returns:
        bool: True if the deployment is successful, False otherwise.
    """
    try:
        info = get_drive_info()
        print(f"Connected to Google Drive: {info['user']['emailAddress']}")
        print(f"Storage used: {info['storage']['usage']} / {info['storage']['limit']}")

        # Create deployment folder
        service = authenticate_google_drive()
        folder_metadata = {
            "name": "GenX-FX-Deploy",
            "mimeType": "application/vnd.google-apps.folder",
        }
        folder = service.files().create(body=folder_metadata, fields="id").execute()
        print(f"Created deployment folder: {folder.get('id')}")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False


if __name__ == "__main__":
    deploy_to_drive()
