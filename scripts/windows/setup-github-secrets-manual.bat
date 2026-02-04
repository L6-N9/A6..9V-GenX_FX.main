@echo off
echo GenX FX GitHub Secrets Manual Setup Helper
echo ==========================================

echo.
echo The provided token doesn't have sufficient permissions.
echo You need to create a new GitHub token with these permissions:
echo.
echo   - repo (Full control of private repositories)
echo   - workflow (Update GitHub Action workflows)  
echo   - admin:repo_hook (Admin access to repository hooks)
echo.

echo Opening GitHub settings pages...
echo.

echo 1. Creating new token...
start "" "https://github.com/settings/tokens/new?scopes=repo,workflow,admin:repo_hook&description=GenX-FX-Secrets-Manager"

timeout /t 5

echo 2. Repository secrets page...
start "" "https://github.com/Mouy-leng/GenX_FX/settings/secrets/actions"

timeout /t 3

echo 3. Repository variables page...
start "" "https://github.com/Mouy-leng/GenX_FX/settings/variables/actions"

timeout /t 3

echo 4. Environments page...
start "" "https://github.com/Mouy-leng/GenX_FX/settings/environments"

echo.
echo ========================================
echo MANUAL SETUP CHECKLIST:
echo ========================================
echo.
echo [ ] 1. Create new GitHub token with proper permissions
echo [ ] 2. Set up Repository Secrets (see GITHUB_SECRETS_SETUP_GUIDE.md)
echo [ ] 3. Set up Repository Variables  
echo [ ] 4. Create Environments (development, staging, production)
echo [ ] 5. Set up Environment-specific secrets
echo [ ] 6. Test CI/CD pipeline
echo.
echo See GITHUB_SECRETS_SETUP_GUIDE.md for complete instructions.
echo.

pause