# Deployment Guide

This guide provides instructions for deploying the GenX Trading Platform to DigitalOcean using the provided GitHub Actions workflow.

## Deployment Options

This project includes two primary deployment methods, both orchestrated through the `.github/workflows/deploy.yml` file:

1.  **DigitalOcean App Platform:** A fully managed platform that simplifies building, deploying, and scaling applications.
2.  **DigitalOcean VPS (Droplet):** A virtual private server that provides more control over the environment.

## Prerequisites

Before deploying, ensure you have the following:

*   A DigitalOcean account.
*   A DigitalOcean personal access token with `write` scope.
*   A registered domain name (optional, but recommended for production).
*   API keys for the various services used by the platform (see `README.md` for a full list).

## Deployment to DigitalOcean App Platform

The App Platform deployment is automatically triggered when you push to the `main` branch. The workflow will:

1.  **Run tests:** Ensure the code is working as expected.
2.  **Build a Docker image:** Create a production-ready Docker image.
3.  **Push the image to GitHub Container Registry:** Store the image for deployment.
4.  **Deploy to App Platform:** Create a new deployment on the App Platform.

### Configuration

You will need to configure the following secrets and variables in your GitHub repository settings:

*   `DIGITALOCEAN_ACCESS_TOKEN`: Your DigitalOcean personal access token.
*   `DIGITALOCEAN_APP_ID`: The ID of your DigitalOcean App.
*   `APP_URL`: The URL of your deployed application (e.g., `https://your-app.ondigitalocean.app`).
*   `DISCORD_WEBHOOK`: The webhook URL for deployment notifications.

You will also need to set the required environment variables for the application in the DigitalOcean App Platform UI.

## Deployment to DigitalOcean VPS (Droplet)

The VPS deployment is also triggered on pushes to `main`. It uses `ssh` to connect to your Droplet and deploy the application.

### Configuration

You will need to configure the following secrets in your GitHub repository settings:

*   `VPS_HOST`: The IP address of your DigitalOcean Droplet.
*   `VPS_USERNAME`: The username for your Droplet (e.g., `root`).
*   `VPS_SSH_KEY`: The private SSH key for your Droplet.
*   `VPS_PORT`: The SSH port for your Droplet (usually `22`).

The workflow passes the necessary API keys and other secrets to the `docker-compose.production.yml` file on the VPS.

### Manual Deployment

To deploy manually, you can follow these steps:

1.  **SSH into your Droplet:**
    ```bash
    ssh your-user@your-droplet-ip
    ```
2.  **Clone the repository:**
    ```bash
    git clone https://github.com/Mouy-leng/GenX-EA_Script.git
    cd GenX-EA_Script
    ```
3.  **Create a `.env` file:**
    ```bash
    cp .env.example .env
    ```
4.  **Fill in the `.env` file with your API keys and other secrets.**
5.  **Run the deployment script:**
    ```bash
    sudo bash deploy/setup-vps.sh
    ```

This script will install Docker, Docker Compose, and other dependencies, and then start the application using `docker-compose`.
