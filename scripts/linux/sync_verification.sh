#!/bin/bash

echo "============================================"
echo "GenX_FX Repository Sync Verification"
echo "============================================"
echo

echo "[1] Checking current directory..."
echo "Current directory: $(pwd)"

echo
echo "[2] Checking if this is a Git repository..."
if ! git status &>/dev/null; then
    echo "ERROR: This is not a Git repository or Git is not installed"
    echo "Please make sure you're in the GenX_FX folder and Git is installed"
    exit 1
fi

echo "[3] Current Git status:"
git status

echo
echo "[4] Current branch and remote info:"
git branch -vv

echo
echo "[5] Fetching latest changes from GitHub..."
git fetch origin

echo
echo "[6] Checking remote repository URL:"
git remote get-url origin

echo
echo "[7] Current commit hash (LOCAL):"
LOCAL_HASH=$(git rev-parse HEAD)
echo $LOCAL_HASH

echo
echo "[8] Latest commit hash (REMOTE main):"
REMOTE_HASH=$(git rev-parse origin/main)
echo $REMOTE_HASH

echo
echo "[9] Expected commit hash (reference):"
EXPECTED_HASH="a7c541b4058014610b70c3e6a115ae6673dd53da"
echo $EXPECTED_HASH

echo
echo "[10] Comparison check:"
if [ "$LOCAL_HASH" = "$EXPECTED_HASH" ]; then
    echo "✅ SUCCESS: Your device is FULLY SYNCED with the repository!"
    echo "✅ Local commit matches the expected commit hash"
elif [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
    echo "✅ SUCCESS: Your device is synced with the remote main branch!"
    echo "✅ You have the latest version"
else
    echo "⚠️  WARNING: Your device may need updates"
    echo "Expected: $EXPECTED_HASH"
    echo "Current:  $LOCAL_HASH"
    echo "Remote:   $REMOTE_HASH"
    echo
    echo "To sync your device, run:"
    echo "  git checkout main"
    echo "  git pull origin main"
fi

echo
echo "[11] Recent commits (last 5):"
git log --oneline -5

echo
echo "============================================"
echo "Verification Complete"
echo "============================================"