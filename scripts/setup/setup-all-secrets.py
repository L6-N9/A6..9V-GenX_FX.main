import os

"""
Security note:
- Do NOT hardcode tokens/keys in this repository.
- Do NOT write real secrets to `.env` in git. Use `.env.example` as a template.
"""

ENV_TEMPLATE = """
# Copy to `.env` (this file is gitignored) and fill values.
# Never commit real credentials.

# GitHub / GitLab / Cursor
GITHUB_TOKEN=
GITLAB_TOKEN=
CURSOR_CLI_API_KEY=

# AMP
AMP_TOKEN=

# Trading / AI / Messaging
BYBIT_API_KEY=
BYBIT_SECRET=
FXCM_USERNAME=
FXCM_PASSWORD=
GEMINI_API_KEY=
TELEGRAM_BOT_TOKEN=
DISCORD_BOT_TOKEN=
""".strip() + "\n"

with open(".env.example", "w", encoding="utf-8") as f:
    f.write(ENV_TEMPLATE)

print("Wrote .env.example (template only).")
