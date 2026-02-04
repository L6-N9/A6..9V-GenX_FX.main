#!/bin/bash

# Ensure we are in the script's directory and move to root
cd "$(dirname "$0")/.."

echo "==================================================="
echo "WARNING: This will RESET your local repository to"
echo "match the remote 'main' branch exactly."
echo ""
echo "1. All local changes will be LOST."
echo "2. All untracked files will be DELETED."
echo ""
echo "Make sure you have backed up any important work!"
echo "==================================================="
echo ""
read -p "Are you sure you want to proceed? (Type 'YES' to confirm): " confirm

if [ "$confirm" != "YES" ]; then
    echo "Operation cancelled."
    exit 1
fi

echo ""
echo "[1/3] Fetching latest changes from origin..."
git fetch origin

echo ""
echo "[2/3] Resetting working tree to origin/main..."
git reset --hard origin/main

echo ""
echo "[3/3] Cleaning untracked files..."
git clean -fd

echo ""
echo "==================================================="
echo "Reset Complete! Your working tree matches origin/main."
echo "==================================================="
