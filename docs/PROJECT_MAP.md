# Project Map: GenX FX Trading Platform

## Overview
GenX FX is a comprehensive, AI-powered trading system for Forex, Cryptocurrency, and Gold. It operates as a monorepo containing a Python FastAPI backend, a Node.js Express server, and a React frontend.

## Directory Structure

### Root
- **`package.json`**: Manages dependencies for the Node.js backend and React frontend. Defines scripts for running the system (`npm run dev`).
- **`requirements.txt`**: Python dependencies for the FastAPI backend and AI models.
- **`vite.config.ts`**: Configuration for the Vite frontend build tool.
- **`vitest.config.ts`**: Configuration for the Vitest test runner.

### Backend (Python)
Located in `api/` and supporting directories.
- **`api/`**: Main FastAPI application (`main.py`). Handles trading logic, AI predictions, and system management.
- **`core/`**: Core trading logic, strategies, indicators, and risk management.
- **`ai_models/`**: Machine learning models (Ensemble, LSTM, CNN, XGBoost) and feature engineering.
- **`utils/`**: Shared utilities for logging and validation.

### Backend (Node.js)
Located in `services/server/`.
- **`services/server/index.ts`**: Entry point for the Express server.
- **`services/server/routes.ts`**: API routes.
- **`services/server/db.ts`**: Database connection (Drizzle ORM).
- **`services/server/vite.ts`**: Vite integration middleware.

### Frontend
Located in `client/`.
- **`client/src/`**: React source code.
- **`client/src/App.tsx`**: Main application component.
- **`client/index.html`**: HTML entry point.

### Trading Bots
- **`expert-advisors/`**: Contains MetaTrader 4 (`.mq4`) and MetaTrader 5 (`.mq5`) Expert Advisors.

### Deployment & DevOps
- **`deploy/`**: Scripts for AWS, Docker, and other platforms.
- **`scripts/`**: Utility scripts for setup and maintenance.
- **`.github/workflows/`**: CI/CD pipelines.

## Architecture & Data Flow

1.  **Dual Backend**:
    -   **Python (Port 8000)**: Handles heavy lifting—AI inference, complex trading logic, broker integration.
    -   **Node.js (Port 5000)**: Handles real-time data, WebSocket connections, and serves as a proxy/middleware in some contexts.

2.  **Frontend**:
    -   **React (Vite, Port 5173)**: Consumes APIs from both backends. Proxies are configured in `vite.config.ts` to route requests to appropriate backends.

3.  **AI & Data**:
    -   Data flows from brokers -> Python Backend -> AI Models -> Predictions -> Trading Execution.
    -   Real-time updates flow via WebSockets to the Frontend.

## Key Scripts

-   `npm run dev`: Starts all services concurrently (Frontend, Node Server, Python API).
-   `npm run build`: Builds the frontend and compiles TypeScript.
-   `python run_tests.py`: Runs Python tests.
-   `npm test`: Runs Frontend/Node tests.
