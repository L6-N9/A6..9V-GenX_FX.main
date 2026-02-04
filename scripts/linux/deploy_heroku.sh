#!/bin/bash

# Heroku Deployment Script for GenX-FX Trading Platform
# This script sets up Heroku deployment with PostgreSQL database and SSH key configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up Heroku deployment for GenX-FX Trading Platform${NC}"

# Heroku token
HEROKU_TOKEN="HRKU-AAdx7OW4VQYFLAyNbE0_2jze4VpJbaTHK8sxEv1XDN3w_____ws77zaRyPXX"

# Check if Heroku CLI is installed
if ! command -v heroku &> /dev/null; then
    echo -e "${YELLOW}Installing Heroku CLI...${NC}"
    curl https://cli-assets.heroku.com/install.sh | sh
fi

# Check if we have SSH key
if [ ! -f ~/.ssh/id_rsa ]; then
    echo -e "${YELLOW}Generating SSH key for Heroku...${NC}"
    ssh-keygen -t rsa -b 4096 -C "heroku-deployment@genx-fx.com" -f ~/.ssh/id_rsa -N ""
    echo -e "${GREEN}✅ SSH key generated${NC}"
fi

# Add SSH key to SSH agent
echo -e "${YELLOW}Adding SSH key to agent...${NC}"
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa

# Login to Heroku
echo -e "${YELLOW}Logging into Heroku...${NC}"
heroku auth:token $HEROKU_TOKEN

# Create Heroku app with timestamp
APP_NAME="genx-fx-$(date +%s)"
echo -e "${YELLOW}Creating Heroku app: $APP_NAME${NC}"

# Create the app
heroku create $APP_NAME --json

# Add PostgreSQL addon
echo -e "${YELLOW}Adding PostgreSQL database...${NC}"
heroku addons:create heroku-postgresql:mini --app $APP_NAME

# Wait for database to be ready
echo -e "${YELLOW}Waiting for database to be ready...${NC}"
sleep 10

# Set environment variables
echo -e "${YELLOW}Setting environment variables...${NC}"
heroku config:set ENVIRONMENT=production --app $APP_NAME
heroku config:set SECRET_KEY=$(openssl rand -hex 32) --app $APP_NAME
heroku config:set PYTHON_VERSION=3.11.7 --app $APP_NAME

# Get database URL
DATABASE_URL=$(heroku config:get DATABASE_URL --app $APP_NAME)
echo -e "${GREEN}Database URL: $DATABASE_URL${NC}"

# Add SSH key to Heroku
echo -e "${YELLOW}Adding SSH key to Heroku...${NC}"
heroku keys:add ~/.ssh/id_rsa.pub --app $APP_NAME

# Stage all changes
echo -e "${YELLOW}Staging changes...${NC}"
git add .

# Commit changes
echo -e "${YELLOW}Committing changes...${NC}"
git commit -m "Setup Heroku deployment with PostgreSQL database" || echo "No changes to commit"

# Add Heroku remote
echo -e "${YELLOW}Adding Heroku remote...${NC}"
heroku git:remote -a $APP_NAME

# Deploy to Heroku
echo -e "${YELLOW}Deploying to Heroku...${NC}"
git push heroku main

# Run database setup
echo -e "${YELLOW}Setting up database schema...${NC}"
heroku run python setup_database.py --app $APP_NAME

# Test the application
echo -e "${YELLOW}Testing application...${NC}"
heroku run python -c "from api.main import app; print('✅ Application test successful')" --app $APP_NAME

# Open the application
echo -e "${GREEN}Opening application in browser...${NC}"
heroku open --app $APP_NAME

echo -e "${GREEN}✅ Heroku deployment complete!${NC}"
echo -e "${GREEN}App URL: https://$APP_NAME.herokuapp.com${NC}"
echo -e "${GREEN}Database URL: $DATABASE_URL${NC}"

# Save deployment info
cat > heroku_deployment_info.txt << EOF
Heroku Deployment Information
============================
App Name: $APP_NAME
App URL: https://$APP_NAME.herokuapp.com
Database URL: $DATABASE_URL
Environment: production
Deployment Date: $(date)

SSH Key Location: ~/.ssh/id_rsa
Heroku Token: $HEROKU_TOKEN

Useful Commands:
- View logs: heroku logs --tail --app $APP_NAME
- Run commands: heroku run <command> --app $APP_NAME
- Open app: heroku open --app $APP_NAME
- Scale dynos: heroku ps:scale web=1 --app $APP_NAME
- Database console: heroku pg:psql --app $APP_NAME
- Database info: heroku pg:info --app $APP_NAME

API Endpoints:
- Health check: https://$APP_NAME.herokuapp.com/health
- API docs: https://$APP_NAME.herokuapp.com/docs
- ReDoc: https://$APP_NAME.herokuapp.com/redoc
EOF

echo -e "${GREEN}📝 Deployment information saved to heroku_deployment_info.txt${NC}"
echo -e "${BLUE}🔑 SSH key is ready for secure connections${NC}"
echo -e "${BLUE}🗄️  PostgreSQL database is configured and ready${NC}"