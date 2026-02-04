# Jules Environment Setup Guide

This repository contains optimized setup scripts for the Jules environment. These scripts leverage the pre-installed tools in Jules VMs to ensure a fast and consistent setup.

## 🚀 Quick Start

To set up the environment in Jules:

1.  Go to your repo in Jules.
2.  Click **"Configuration"**.
3.  Paste the content of `jules_setup.sh` (for full setup) or `jules_setup_minimal.sh` (for basic Node.js) into the **"Initial Setup"** field.
4.  Click **"Run and Snapshot"**.

## 📂 Included Scripts

### 1. `jules_setup.sh` (Comprehensive)
*   **Best for:** Full-stack applications (Python + Node.js), complex environments.
*   **What it does:**
    *   Installs project dependencies (`pnpm install`, `pip install`).
    *   Installs additional system tools (if configured).
    *   Runs linters (`ESLint`, `Ruff`, `Black`).
    *   Runs tests (`Vitest`, `Pytest`).
    *   Prepares the environment for a snapshot.

### 2. `jules_setup_minimal.sh` (Minimal)
*   **Best for:** Simple Node.js projects, quick prototypes.
*   **What it does:**
    *   Installs `firebase-tools` and Google AI SDKs.
    *   Installs project dependencies.
    *   Runs basic checks.

## 🛠️ Pre-installed Tools in Jules
Jules VMs come equipped with the following, so you **do not** need to install them:
*   **Node.js:** v22, v20, v18
*   **Python:** v3.12, v3.10
*   **Docker:** v28.2.2
*   **Linters:** ESLint, Prettier, Ruff, Black
*   **Testing:** Pytest, Jest (via npm)

## 📝 Best Practices
*   **Use `pnpm`:** This project uses `pnpm` for package management. The setup scripts are configured accordingly.
*   **Lockfiles:** Ensure `pnpm-lock.yaml` and `requirements.txt` are up to date to guarantee reproducible builds.
*   **Snapshots:** Using the "Initial Setup" feature in Jules creates a snapshot, speeding up future environment starts.
