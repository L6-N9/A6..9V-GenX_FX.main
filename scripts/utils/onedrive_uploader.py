import json
import logging
import os
from pathlib import Path

import msal
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Try to import settings from api.config
try:
    from api.config import settings
except ImportError:
    settings = None
except Exception:
    # Catch pydantic validation errors or other issues
    settings = None

SCOPES = ["Files.ReadWrite.All", "User.Read"]
TOKEN_CACHE_FILE = "onedrive_token.json"


class OneDriveUploader:
    def __init__(self, client_id=None, tenant_id=None):
        self.client_id = client_id or self._get_config("ONEDRIVE_CLIENT_ID")
        self.tenant_id = tenant_id or self._get_config("ONEDRIVE_TENANT_ID") or "common"
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"

        if not self.client_id:
            logger.warning(
                "ONEDRIVE_CLIENT_ID is not set. Authentication will likely fail."
            )

        self.app = msal.PublicClientApplication(
            self.client_id or "placeholder-client-id",
            authority=self.authority,
            token_cache=self._load_cache(),
        )

    def _get_config(self, key):
        """Retrieve config from api.config or environment variables."""
        val = None
        if settings:
            val = getattr(settings, key, None)
        if not val:
            val = os.getenv(key)
        return val

    def _load_cache(self):
        cache = msal.SerializableTokenCache()
        if os.path.exists(TOKEN_CACHE_FILE):
            with open(TOKEN_CACHE_FILE, "r") as f:
                cache.deserialize(f.read())
        return cache

    def _save_cache(self):
        if self.app.token_cache.has_state_changed:
            with open(TOKEN_CACHE_FILE, "w") as f:
                f.write(self.app.token_cache.serialize())

    def authenticate(self):
        """Authenticates the user using Device Code Flow."""
        accounts = self.app.get_accounts()
        result = None

        if accounts:
            logger.info(f"Found account: {accounts[0]['username']}")
            result = self.app.acquire_token_silent(SCOPES, account=accounts[0])

        if not result:
            logger.info(
                "No suitable token found in cache. Starting Device Code Flow..."
            )
            flow = self.app.initiate_device_flow(scopes=SCOPES)
            if "user_code" not in flow:
                raise ValueError(
                    f"Failed to create device flow. Error: {json.dumps(flow, indent=4)}"
                )

            print(flow["message"])  # Print to stdout for user interaction

            result = self.app.acquire_token_by_device_flow(flow)

        if "access_token" in result:
            self._save_cache()
            return result["access_token"]
        else:
            logger.error(f"Authentication failed: {result.get('error')}")
            logger.error(f"Error description: {result.get('error_description')}")
            return None

    def upload_file(self, local_path: str, remote_folder: str = None):
        """Uploads a file to OneDrive."""
        remote_folder = (
            remote_folder or self._get_config("ONEDRIVE_FOLDER_NAME") or "GenX_Signals"
        )

        token = self.authenticate()
        if not token:
            return False

        if not os.path.exists(local_path):
            logger.error(f"File not found: {local_path}")
            return False

        filename = os.path.basename(local_path)

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/octet-stream",
        }

        upload_url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{remote_folder}/{filename}:/content"

        logger.info(f"Uploading {filename} to OneDrive ({remote_folder})...")

        with open(local_path, "rb") as f:
            response = requests.put(upload_url, headers=headers, data=f)

        if response.status_code in [200, 201]:
            logger.info(
                f"Successfully uploaded {filename}. File ID: {response.json().get('id')}"
            )
            return True
        else:
            logger.error(f"Failed to upload {filename}. Status: {response.status_code}")
            logger.error(response.text)
            return False


def sync_signals():
    uploader = OneDriveUploader()
    signal_dir = "signal_output"

    if not uploader.client_id:
        print("Error: ONEDRIVE_CLIENT_ID is not set.")
        print("Please configure it in .env or environment variables.")
        return

    if not os.path.exists(signal_dir):
        logger.warning(f"Signal directory '{signal_dir}' does not exist.")
        return

    # Upload only CSV files for now as per architecture
    csv_files = [f for f in os.listdir(signal_dir) if f.endswith(".csv")]
    if not csv_files:
        logger.info(f"No CSV files found in {signal_dir} to upload.")
        return

    for file in csv_files:
        uploader.upload_file(os.path.join(signal_dir, file))


if __name__ == "__main__":
    sync_signals()
