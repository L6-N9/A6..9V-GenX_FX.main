"""
Agent 1: Configure production environment variables.

This script creates .env.production and .env.docker files with the
necessary environment variables for the production and Docker environments.
"""

import os

# Production environment configuration
prod_env = {
    "NODE_ENV": "production",
    "PORT": "8080",
    "API_URL": "https://genx-fx-api.vercel.app",
    "DATABASE_URL": "sqlite:///genxdb_fx.db",
    "CORS_ORIGIN": "https://genx-fx.vercel.app",
    "LOG_LEVEL": "info",
}

# Create production .env file
with open(".env.production", "w") as f:
    for key, value in prod_env.items():
        f.write(f"{key}={value}\n")

# Create Docker environment file
with open(".env.docker", "w") as f:
    f.write("NODE_ENV=production\n")
    f.write("PORT=8080\n")
    f.write("API_URL=http://localhost:8080\n")

print("Agent 1: Production environment variables configured")
print("Files created: .env.production, .env.docker")
