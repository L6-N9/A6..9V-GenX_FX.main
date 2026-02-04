# Jules Memory Dump

This document contains the retained memory and context for the AI assistant Jules, covering project details, technical constraints, and learned patterns.

## Project Context
- **Repository**: Monorepo for 'GenX FX AI Trading Platform'.
- **Components**:
    - Python FastAPI backend (`api/`, port 8000).
    - Node.js Express server (`services/server/`, port 5000).
    - React Frontend (`client/`, port 5173).
    - AI Models (`ai_models/`).
    - MQL5 Expert Advisors (`expert-advisors/`).
- **Dependencies**:
    - Frontend dependencies managed in root `package.json` (`pnpm`).
    - Python version: 3.12.12.
    - Python dependencies: `requirements.txt` (includes `pybit>=5.0.0`, `msal`, `typer`, `rich`, `pydantic-settings`).
- **Command Standards**:
    - Build: `pnpm build`.
    - Dev: `pnpm dev` (runs `services/server/index.ts` and `uvicorn api.main:app` concurrently).
    - Frontend Dev: `pnpm client`.
    - Test: `python run_tests.py && pnpm test`.
    - Lint: `pnpm lint` (requires install first).
    - Package Manager: `pnpm` (strongly preferred over npm/yarn).
    - CLI: `amp` CLI flags (e.g., `--enabled`) must be used without values.

## Technical Details & Constraints
- **Networking**:
    - Vite proxies `/api`, `/health`, `/socket.io` to Node (5000).
    - Vite proxies `/api/v1`, `/trading-pairs` to Python (8000).
    - `api/main.py` has strict CORS allowing specific origins (e.g., `http://localhost:5000`) and uses `TrustedHostMiddleware`.
    - `services/server/vite.ts` must use relative imports to root.
- **Security**:
    - Symmetric encryption: `utils/encryption.py` using `cryptography.fernet.Fernet` (`CRYPTION_KEY`).
    - Key Generation: `scripts/generate_encryption_key.py`.
- **Frontend**:
    - No `package.json` in `client/` (uses root).
    - Types: `client/src/vite-env.d.ts` required for `import.meta.env`.
    - Libraries: `lucide-react` (icons), `react-hook-form`, `react-router-dom` v6.
    - **UX/Accessibility Standards**:
        - Numeric inputs: `inputMode="numeric"`, specific `autoComplete`.
        - Navigation: `NavLink` used. Active: blue/bold/underline. Inactive: `text-gray-600`.
        - Accessibility: 'Skip to main content' link required in `App.tsx`. Status indicators must use icons (not just color). Interactive elements need `focus-visible`.
    - Verification: Create temporary Playwright scripts in `verification/`.
- **Backend (Python)**:
    - Configuration: Uses `pydantic-settings` in `api/config.py`. `.env` manages Core, Exness, Captain, Database, etc.
    - `ConfigManager` (`utils/config_manager.py`) defaults to 'exness' but supports 'captain'.
    - `run_tests.py` sets `TESTING=1` and mock DB URLs.
    - `setup_database.py` and `config/trading_config.json` include `BTCUSD`, `BTCXAU`.
- **Backend (Node)**:
    - Uses TypeScript and Drizzle ORM.
    - Proxies requests to Python backend manually in `services/server/index.ts`.
- **Expert Advisors**:
    - `EXNESS_GenX_Trader.mq5`: `UseAI=true` default. Weekday trading logic (`TradeOnWeekends`).
- **Integrations**:
    - **Telegram**: Bot `@GenX_FX_bot`.
    - **OneDrive**: `onedrive_uploader.py` (MSAL Device Code Flow), `genx_cli.py onedrive-sync`. Token in `onedrive_token.json`.
    - **GitHub**: `scripts/create_gist.py`.
    - **FXCM**: `excel_forexconnect_integration.py` (requires `FXCM_PASSWORD`).

## Environment & Infrastructure
- **Git**: Shallow clones cause merge issues. `scripts/reset-github-tree.bat/.sh` available.
- **Deployment**:
    - AWS resources in `deploy/`.
    - `update-cicd-pipeline.py` (needs `pyyaml`) regenerates workflows.
    - `amp-update-command.sh` for updates.
- **Local Environment (User)**:
    - User: `keamouyleng` (Docker/GitHub).
    - Machine 'NuNa' Path: `D:\GenX_FX`.
    - Exness MT5: `"C:\Program Files\MetaTrader 5 EXNESS\Terminal.exe"`.
- **VPS**:
    - Singapore VPS details (IP: 192.168.18.6, SSID: LengA6-9V).

## Links & Resources
- **Dropbox (Memory)**: [Link 1](https://www.dropbox.com/scl/fo/wmsuv2bpkgosp1jli5tc5/AOKGX65h1csk9PcFapBwpJk?rlkey=1h8e0od7q2ijbwdvkvg5qsvrs&st=1d4kjv2w&dl=0)
- **Dropbox (Memory 2)**: [Link 2](https://www.dropbox.com/scl/fo/wmsuv2bpkgosp1jli5tc5/AOKGX65h1csk9PcFapBwpJk?rlkey=1h8e0od7q2ijbwdvkvg5qsvrs&st=wi1idcs3&dl=0)
- **Drive Link**: https://1drv.ms/f/c/8F247B1B46E82304/IgDpUzdplXkDTpiyCkdNDZpXASUMJEccVuNGxAaY3MxB1sA
- **OneDrive Vault**: Password = 369369
- **Proton Drive**: [Link](https://drive.proton.me/urls/2D7WAV1B70#C5LasdZntV7P)
- **NotebookLM**: [Link](https://notebooklm.google.com/notebook/35d7301f-8fa7-4bd0-b7b8-e492060404de)
- **Samsung Cloud Note**: [Link](https://groupshare.samsungcloud.com/invitation/notecoedit/hpXmILJ1xT)
- **Github API**: https://docs.github.com/api/article/body?pathname=/en/enterprise-server@3.19/admin/all-releases
- **OpenAI Codex**: https://github.com/openai/codex

## System Verification Log (2026-01-29)
- **Scalping Service**: Verified presence in `api/services/scalping_service.py` and passing tests.
- **VPS Configuration**: Verified `vps-config/` directory structure.
- **Encryption**: Verified `logging` usage in `utils/encryption.py`.
- **Bolt Optimizations**: Verified symbol lookup optimization in `api/routers/predictions.py`.
- **Status**: Main branch is fully up-to-date with recent feature branches. Redeployment triggered.

## System Verification Log (2026-02-04)
- **System Update**: Verified system update to version `LI9-15.1.2.145SP08(OP001PF001AZ)`.
- **Security Patch**: Updated Google Security Patch to January 1, 2026.
- **Fixes**: Resolved SD card recognition issues and optimized system stability and performance.
- **Documentation**: Added update screenshot to `docs/images/system_update_20260204.jpg`.
- **Status**: Updated `jules.sh` with the new build number.
