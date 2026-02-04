# GenX_FX_0: Comprehensive Documentation

## Project Overview

GenX_FX_0 is an advanced, AI-driven trading platform designed for the forex and gold markets. As an AI-powered system, it leverages machine learning predictions and sophisticated Expert Advisors (EAs) to deliver automated, real-time trading intelligence. The platform's core purpose is to provide automated signal generation, conduct multi-source market analysis, and execute trades with precision.

Built on Python 3.9+, GenX_FX_0 is a production-ready solution engineered for 24/7 operation. It integrates machine learning models with robust trading logic to analyze market data from multiple sources, identify trading opportunities, and manage risk. The system is designed for both traders seeking to deploy automated strategies out-of-the-box and developers looking for a powerful framework to build and test their own trading algorithms.

## Folder and File Structure

The GenX_FX_0 repository is organized into distinct directories, each serving a specific purpose within the platform's architecture.

### Top-Level Folders

*   **`api/`**: Contains the FastAPI application, which exposes RESTful endpoints for trading operations, signal retrieval, and system management.
*   **`core/`**: Houses the central trading logic, including the main `trading_engine.py`, strategy implementations, risk management rules, and market analysis tools.
*   **`expert-advisors/`**: Includes MetaTrader Expert Advisor (EA) files, such as `GenX_AI_EA.mq5` and `GenX_Gold_Master_EA.mq4`, which are designed to be used directly in the MT4/MT5 platforms.
*   **`ai_models/`**: Contains the machine learning models, including data preprocessing scripts, model training notebooks, and the prediction logic used for signal generation.
*   **`client/`**: The frontend application, built with React and TypeScript, providing a user interface for interacting with the platform.
*   **`deploy/`**: Holds deployment scripts and configuration files for various environments, including Docker, AWS, and Heroku.
*   **`config/`**: Stores configuration files for trading parameters, API keys, and system settings.
*   **`shared/`**: Contains shared code and utilities used across multiple components of the system.
*   **`utils/`**: A directory for miscellaneous utility scripts and helper functions.
*   **`tests/`**: Includes the test suite for the platform, with unit and integration tests for all major components.
*   **`services/`**: Contains modules for integrating with external services, such as broker APIs (ForexConnect, FXCM), data providers, and notification systems.
*   **`receiver_system/`**: Manages incoming data feeds and real-time market data processing.

### Key Files

*   **`.env.example`**: An example environment file. This should be copied to `.env` and filled with the necessary API keys and configuration secrets.
*   **`requirements.txt`**: Lists all the Python dependencies required to run the backend services.
*   **`Dockerfile`**: The primary Dockerfile for building a container image of the application.
*   **`docker-compose.yml`**: A Docker Compose file for orchestrating the multi-service deployment of the platform.
*   **`genx`**: The main command-line interface (CLI) tool for managing the system, from checking status to running backtests and deploying updates.
*   **`package.json`**: Defines the Node.js dependencies and scripts for the frontend application.

## Setup and Installation

Follow these steps to set up the GenX_FX_0 platform for development and local execution.

### Prerequisites

*   **System Requirements**:
    *   **Operating System**: Linux (Ubuntu recommended) or Windows.
    *   **Python**: Version 3.9+ with `pip` installed.
    *   **RAM/Disk**: Sufficient memory and disk space to run the database, backend, and frontend services.
*   **Git**: Required for cloning the repository.
*   **Docker**: (Optional) For containerized deployment.

### Installation Steps

1.  **Clone the Repository**:
    Open your terminal and clone the repository to your local machine:
    ```bash
    git clone https://github.com/Mouy-leng/GenX_FX.git
    cd GenX_FX_0
    ```

2.  **Create a Python Virtual Environment**:
    It is highly recommended to use a virtual environment to manage Python dependencies:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install Dependencies**:
    Install the required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables**:
    The system uses a `.env` file to manage sensitive information and environment-specific settings.
    *   Copy the example file:
        ```bash
        cp .env.example .env
        ```
    *   Open the `.env` file in a text editor and fill in the required values, including:
        *   **Broker API Keys**: Credentials for your trading broker (e.g., ForexConnect, FXCM).
        *   **Database Credentials**: Connection details for your database.
        *   **Cloud Service Keys**: AWS or GCP credentials if you plan to deploy to the cloud.
        *   **Firebase Credentials**: If using Firebase for authentication or other services.

5.  **Database and Broker Accounts**:
    Ensure you have active accounts with the necessary services, such as a ForexConnect-compatible broker and any cloud services (e.g., AWS) you intend to use.

### Docker Setup (Optional)

If you have Docker and Docker Compose installed, you can build and run the entire platform in a containerized environment.

1.  **Build the Docker Image**:
    ```bash
    docker build -t genx_fx .
    ```

2.  **Run with Docker Compose**:
    Use the `docker-compose.yml` file to launch all services:
    ```bash
    docker-compose up
    ```

## Usage Instructions and Examples

Once the system is installed and configured, you can use the command-line interface (CLI) and API to manage and interact with the platform.

### Command-Line Interface (CLI)

The `genx` CLI is the primary tool for controlling the system. Below are some common commands:

*   **Initialize the System**:
    This command sets up the necessary directories and default configuration files. It should be run once after the initial setup.
    ```bash
    ./genx init
    ```

*   **Check System Status**:
    To get a real-time overview of all running services, including the API, trading engine, and data receivers.
    ```bash
    ./genx status
    ```

*   **View Market Overview**:
    Fetches and displays a summary of the current market conditions for configured trading pairs.
    ```bash
    ./genx overview
    ```

*   **Generate Trading Signals**:
    Manually trigger the AI model to generate and output new trading signals.
    ```bash
    ./genx generate-signals
    ```

*   **Run a Backtest**:
    Execute a backtest of a specified trading strategy over a historical data range.
    ```bash
    ./genx backtest --strategy <strategy_name> --start-date YYYY-MM-DD --end-date YYYY-MM-DD
    ```

### API Usage

The FastAPI backend provides several RESTful endpoints for programmatic access.

*   **Get Trading Signals**:
    Retrieve the latest trading signals generated by the AI models.
    ```http
    GET /api/v1/signals
    ```

*   **Get Account Information**:
    Fetch the current status of your trading account, including balance and open positions.
    ```http
    GET /api/v1/account
    ```

*   **Execute a Trade**:
    Programmatically place a trade order.
    ```http
    POST /api/v1/orders
    {
      "symbol": "XAUUSD",
      "action": "BUY",
      "quantity": 0.01,
      "stop_loss": 1800.00,
      "take_profit": 1850.00
    }
    ```

## Key Modules, Functions, and Classes

The GenX_FX_0 platform is composed of several key modules that work together to deliver its core functionality.

*   **`core/trading_engine.py`**: This is the heart of the platform. The `TradingEngine` class is responsible for orchestrating the entire trading process, from signal evaluation to order execution and risk management. It connects to data sources, processes signals from the AI models, and interacts with broker APIs.

*   **`ai_models/`**: This directory contains the machine learning infrastructure. Key components include:
    *   **Signal Generation Logic**: Scripts and classes that process market data, apply ML models, and produce buy/sell signals.
    *   **Model Classes**: Python classes that define the architecture of the predictive models, such as neural networks or gradient boosting classifiers.
    *   **Data Handlers**: Utilities for fetching, cleaning, and preparing historical and real-time data for model training and inference.

*   **`api/`**: The FastAPI application defines all the RESTful API routes. Important route modules include:
    *   **Authentication Routes**: Handle user login, API key validation, and session management.
    *   **Signal APIs**: Endpoints for retrieving trading signals, which can be consumed by the frontend or external applications like MetaTrader EAs.
    *   **Trading Routes**: Endpoints for executing trades, checking account status, and managing open positions.

*   **`genx-cli/`**: This module contains the implementation of the `genx` command-line interface. Each command (e.g., `status`, `overview`, `init`) is typically mapped to a specific function that interacts with the core engine or other system components.

*   **`services/` and `receiver_system/`**: These directories manage interactions with external systems:
    *   **Broker Integrations**: Modules for connecting to different broker APIs (e.g., ForexConnect, FXCM) to fetch market data and execute trades.
    *   **Data Receivers**: Real-time data processing pipelines that consume data from WebSockets or other streaming sources and feed it into the trading engine.

## Developer and Contributor Notes

We welcome contributions to GenX_FX_0. To ensure a smooth and collaborative development process, please adhere to the following guidelines.

### Code of Conduct

All contributors are expected to read and abide by our **`CODE_OF_CONDUCT.md`**. We are committed to fostering an open, inclusive, and welcoming environment for everyone.

### Contribution Workflow

1.  **Fork the Repository**: Start by forking the official repository to your own GitHub account.
2.  **Create a Branch**: Create a new, descriptive branch for your feature or bug fix (e.g., `feature/new-indicator` or `fix/api-bug`).
3.  **Commit Changes**: Make your changes and commit them with clear, standardized messages.
4.  **Run Tests**: Before submitting, ensure all tests pass and add new tests for your changes where applicable.
    ```bash
    # Run backend tests
    python run_tests.py
    # Run frontend tests
    npm test
    ```
5.  **Open a Pull Request**: Push your branch to your fork and open a pull request against the main repository.

### Pull Request Guidelines

*   **Squash and Merge**: Pull requests are merged using the "Squash and Merge" strategy to maintain a clean git history. Please provide a clear and concise title for your pull request.
*   **Branch Protection and CI**: The main branch is protected, and all pull requests must pass required Continuous Integration (CI) checks before they can be merged. This ensures code quality and stability.