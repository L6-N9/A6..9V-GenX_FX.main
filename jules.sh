#!/usr/bin/env bash
set -euo pipefail

# === CONFIG ===
# These variables are used throughout the script.
# Some, like DUCKDNS_TOKEN, should be handled securely (e.g., as environment variables).
DOMAIN="remote.genxfx.org"
DUCKDNS_DOMAIN="your-duckdns-subdomain.duckdns.org" # Default, can be overridden
DEVICE_IP="10.62.78.114"
BUILD_NUMBER="LI9-15.1.2.145SP08(OP001PF001AZ)"
HASHED_ID=$(echo -n "$BUILD_NUMBER" | openssl dgst -sha256 | awk '{print $2}')
FIREBASE_PROJECT="genxfx"
PRIVACY_EMAIL="189807f4de4d86bd181553d72ab3f.protect@withheldforprivacy.com"

# === STEP 1: Reverse Proxy Setup ===
# This function generates an Apache reverse proxy configuration.
# To use it, you would uncomment the scp and ssh lines and ensure you have
# passwordless SSH access to your server.
reverse_proxy() {
  echo "[*] Setting up reverse proxy for $DOMAIN -> $DEVICE_IP"
  cat > remote.conf <<EOF
<VirtualHost *:80>
  ServerName $DOMAIN
  ProxyPass / http://$DEVICE_IP:8000/
  ProxyPassReverse / http://$DEVICE_IP:8000/
</VirtualHost>
EOF
  echo "[*] Configuration file 'remote.conf' created."
  echo "[!] SCP and SSH commands are commented out for safety."
  # scp remote.conf user@server354.web-hosting.com:/etc/apache2/sites-available/
  # ssh user@server354.web-hosting.com "a2ensite remote && systemctl reload apache2"
}

# === STEP 2: Device Identity Hashing ===
# This function calculates and displays a unique hash for the device.
# It also pings an API endpoint with the hash in a header.
device_identity() {
  echo "[*] Device hash: $HASHED_ID"
  curl -H "X-Device-ID: $HASHED_ID" https://genxfx.org/api/agent-status || true
}

# === STEP 3: Firebase Session Schema ===
# This function generates a JSON schema for a Firebase session and provides
# the command to deploy Firestore rules. You must be logged into Firebase.
firebase_session() {
  echo "[*] Pushing session schema to Firebase"
  cat > session.json <<EOF
{
  "deviceid": "$HASHED_ID",
  "session_token": "$(uuidgen)",
  "timestamp": "$(date -Iseconds)",
  "notes_synced": true
}
EOF
  echo "[*] Session schema file 'session.json' created."
  echo "[!] Firebase command is commented out. Run 'firebase deploy --only firestore:rules' manually after login."
  # firebase deploy --only firestore:rules
}

# === STEP 4: GitHub OAuth + Device Verification ===
# This function displays a JavaScript snippet for device verification in an
# OAuth callback.
githuboauthcheck() {
  echo "[*] Reminder: Add this snippet to your OAuth callback"
  cat <<'JS'
if (req.headers['x-device-id'] !== expectedHash) {
  return res.status(403).send("Unauthorized device");
}
JS
}

# === STEP 5: LiteWriter Note Sync ===
# This function mounts a WebDAV share and syncs tasks to GitHub issues.
# It requires davfs2 to be installed and configured.
note_sync() {
  echo "[*] Mounting LiteWriter WebDAV and syncing tasks"
  mkdir -p /mnt/litewriter
  echo "[!] Mount command is commented out. You will need to configure /etc/davfs2/secrets."
  # sudo mount -t davfs http://$DOMAIN /mnt/litewriter || true
  echo "[!] Note sync logic is commented out."
  # grep -r "\[ \]" /mnt/litewriter | awk '{print $2}' > tasks.txt
  # while read -r task; do
    # gh issue create --title "New Task" --body "$task"
  # done < tasks.txt
}

# === STEP 6: VS Code Extension Hook ===
# This function provides the URL for a VS Code extension to poll for session status.
vscode_hook() {
  echo "[*] VS Code extension should poll Firebase at:"
  echo "https://firebase.genxfx.org/session-status"
}

# === STEP 7: Privacy Email Alerts ===
# This function sends an email alert using msmtp.
# You will need to configure msmtp with your email provider's details.
send_alert() {
  echo "[*] Sending fallback alert to $PRIVACY_EMAIL"
  echo "[!] msmtp command is commented out. You must configure msmtp first."
  # echo "Agent offline" | msmtp -a default "$PRIVACY_EMAIL"
}

# === STEP 8: GCP Multi-Project Deployment ===
# This function triggers the deployment of the application to multiple GCP projects.
deploy_gcp() {
  echo "[*] Triggering Multi-Project GCP Deployment..."
  if [ -f "./scripts/linux/deploy_to_all_gcp.sh" ]; then
    bash ./scripts/linux/deploy_to_all_gcp.sh
  else
    echo "[!] Error: Deployment script not found at ./scripts/linux/deploy_to_all_gcp.sh"
    return 1
  fi
}

# === DDNS Auto-Update (Free Tier) ===
# This function updates a DuckDNS record.
# Usage: ./jules.sh ddns <your-duckdns-domain>
ddns_update() {
  local domain="${1:-$DUCKDNS_DOMAIN}"
  if [ -z "${DUCKDNS_TOKEN:-}" ]; then
    echo "[!] Error: DUCKDNS_TOKEN environment variable is not set."
    echo "[!] Please set it to your DuckDNS token."
    return 1
  fi
  echo "[*] Updating DuckDNS record for $domain"
  curl -s "https://www.duckdns.org/update?domains=$domain&token=$DUCKDNS_TOKEN&ip="
}

# === COMMAND DISPATCH ===
case "${1:-}" in
  reverse-proxy) reverse_proxy ;;
  device-id) device_identity ;;
  firebase) firebase_session ;;
  github-oauth) githuboauthcheck ;;
  note-sync) note_sync ;;
  vscode) vscode_hook ;;
  alert) send_alert ;;
  deploy-gcp) deploy_gcp ;;
  ddns) ddns_update "${2:-}" ;;
  all)
    reverse_proxy
    device_identity
    firebase_session
    note_sync
    ;;
  *)
    echo "Usage: $0 {reverse-proxy|device-id|firebase|github-oauth|note-sync|vscode|alert|deploy-gcp|ddns|all}"
    ;;
esac