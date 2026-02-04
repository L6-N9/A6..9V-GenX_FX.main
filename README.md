# 🚀 GenX FX Trading Platform

**An advanced, AI-powered platform for Forex, Cryptocurrency, and Gold trading.**

[![Python](https://img.shields.io/badge/Python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/A6-9V/A6..9V-GenX_FX.main)

---

## 🎯 Overview

GenX FX is a comprehensive, AI-powered trading system that combines machine learning, real-time market analysis, and automated execution capabilities. The platform is designed for both traders who want to use pre-built Expert Advisors (EAs) and for developers who want to build, test, and deploy their own automated strategies.

## ✨ Key Features

-   🤖 **AI-Powered Signals**: Utilizes advanced machine learning models, including an ensemble predictor, to generate high-quality trading signals.
-   📊 **Professional Expert Advisors**: Comes with pre-built EAs for MetaTrader 4 and 5, specializing in Gold and major Forex pairs, with sophisticated risk management.
-   🌐 **24/7 Cloud Operation**: Designed for continuous, 24/7 operation and is ready for deployment on cloud platforms like Google Cloud and AWS.
-   ⚡ **Real-Time Integration**: Features live data feeds through WebSocket and REST APIs for instant trade execution and real-time analysis.
-   🔗 **Multi-Broker Support**: Integrates with various brokers via ForexConnect, FXCM, and Exness, providing flexibility and choice.
-   📈 **Advanced Signal Generation**: Generates ML-based trading signals and exports them to Excel, CSV, or JSON formats for consumption by EAs or other tools.
-   📱 **Multi-Channel Notifications**: Send trading signals and alerts to Telegram, Discord, and WhatsApp groups for real-time team updates.
-   🛠️ **Unified CLI**: A powerful and unified command-line interface (`genx`) for all major operations, from system status checks to automated deployments and AI model training.

---

## 🚀 Getting Started

There are two main ways to get started with GenX FX, depending on your goals.

### For Traders: Using a Pre-Built Expert Advisor

This is the fastest and easiest way to start trading, especially with the specialized Gold Master EA.

1.  **Download the EA**:
    -   Navigate to the `expert-advisors/` directory.
    -   Download the `GenX_Gold_Master_EA.mq4` file.

2.  **Install in MetaTrader 4**:
    -   Open your MT4 terminal.
    -   Go to `File > Open Data Folder`.
    -   Navigate to the `MQL4/Experts/` directory.
    -   Copy the downloaded `.mq4` file into this directory.

3.  **Configure and Run**:
    -   Restart MT4 or refresh the "Expert Advisors" list in the Navigator panel.
    -   Drag the "GenX\_Gold\_Master\_EA" onto a chart (e.g., XAUUSD).
    -   Configure the settings as described in the [Gold Master EA Guide](GOLD_MASTER_EA_GUIDE.md).
    -   Enable "AutoTrading" on your MT4 terminal and start trading.

### For Developers: Full System Setup

This option allows you to run the entire backend, API, and AI models for development and customization.

1.  **Clone the Repository**:
    ```bash
    git clone https://github.com/A6-9V/A6..9V-GenX_FX.main.git
    cd A6..9V-GenX_FX.main
    ```

2.  **Install Dependencies**:
    The project uses both Python and Node.js.
    ```bash
    pip install -r requirements.txt
    npm install
    ```

3.  **Set Up Environment Variables**:
    -   Copy the `.env.example` file to a new file named `.env`.
    -   Fill in the required API keys and configuration details for the services you plan to use (e.g., FXCM, Gemini, etc.). See the [API Key Setup Guide](API_KEY_SETUP.md) for more details.

4.  **Initialize the System**:
    Use the unified CLI to initialize the system, which will create necessary directories and default configurations.
    ```bash
    python genx_cli.py init
    ```

5.  **Run the System**:
    The platform includes a concurrent runner for the frontend and backend services.
    ```bash
    npm run dev
    ```
    This command will start the FastAPI backend and the React frontend simultaneously. You can then access the platform at `http://localhost:3000`.

---

## 🏗️ System Architecture

The GenX FX platform is a monorepo containing several key components:

-   **`api/`**: The main backend powered by **FastAPI**. It serves REST endpoints for trading, predictions, and system management.
-   **`core/`**: The core trading logic, including strategies, indicators, pattern detection, risk management, and the main trading engine.
-   **`ai_models/`**: Contains the machine learning models (e.g., `EnsemblePredictor`) and the logic for generating predictions.
-   **`client/`**: The web-based frontend built with **React** and **TypeScript**.
-   **`services/`**: Contains various services for interacting with external APIs like FXCM, Reddit, and Google Gemini, as well as WebSocket and spreadsheet managers.
-   **`expert-advisors/`**: Contains the MetaTrader 4 (MQ4) and MetaTrader 5 (MQ5) Expert Advisor files.
-   **`utils/`**: Shared utilities for logging, configuration management, and model validation.
-   **`deploy/`**: Deployment scripts for various cloud platforms, including AWS and Exness VPS.

---

## 🛠️ Development and Testing

### Running Tests

The repository includes a comprehensive test suite for both the Python backend and the frontend.

-   **Python Tests (pytest)**:
    ```bash
    python run_tests.py
    ```
-   **JavaScript/TypeScript Tests (Vitest)**:
    ```bash
    npm test
    ```

### Code Style and Linting

-   **Python**: The project follows PEP 8 standards. We recommend using a formatter like Black.
-   **TypeScript/JavaScript**: The project uses Prettier and ESLint for code formatting and linting.
    ```bash
    npm run lint
    ```

---

## 📚 Documentation

For more detailed information, please refer to the following guides in the repository:

-   **[GETTING_STARTED.md](GETTING_STARTED.md)**: A complete guide to setting up the full system from scratch.
-   **[GOLD_MASTER_EA_GUIDE.md](GOLD_MASTER_EA_GUIDE.md)**: A comprehensive guide for the specialized gold trading EA.
-   **[SYSTEM_ARCHITECTURE_GUIDE.md](SYSTEM_ARCHITECTURE_GUIDE.md)**: An in-depth look at the system's design and architecture.
-   **[API_KEY_SETUP.md](API_KEY_SETUP.md)**: Instructions for configuring the necessary API keys for all services.
-   **[WHATSAPP_INTEGRATION_GUIDE.md](WHATSAPP_INTEGRATION_GUIDE.md)**: Guide for setting up WhatsApp notifications and group integration.

### 🚀 Deployment Guides

-   **[DEPLOYMENT_SETUP_INSTRUCTIONS.md](DEPLOYMENT_SETUP_INSTRUCTIONS.md)**: **NEW!** Master guide for forge.mql5.io and VPS deployment
-   **[docs/FORGE_MQL5_DEPLOYMENT.md](docs/FORGE_MQL5_DEPLOYMENT.md)**: Complete guide for forge.mql5.io integration with deploy keys
-   **[docs/VPS_QUICK_START.md](docs/VPS_QUICK_START.md)**: Quick reference for rapid VPS deployment with Docker
-   **[docs/REPOSITORY_SECRETS_SETUP.md](docs/REPOSITORY_SECRETS_SETUP.md)**: Comprehensive secrets and credentials configuration
-   **[AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)**: Step-by-step guide to deploying the platform on AWS

---

## 🤝 Contributing

We welcome contributions from the community! Please follow these steps to contribute:

1.  Fork the repository.
2.  Create a new feature branch: `git checkout -b feature/your-amazing-feature`
3.  Commit your changes: `git commit -m 'Add your amazing feature'`
4.  Push to the branch: `git push origin feature/your-amazing-feature`
5.  Open a Pull Request.

Please make sure to read our [Contributing Guidelines](CODE_OF_CONDUCT.md) and [Security Policy](SECURITY.md) before submitting your changes.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.