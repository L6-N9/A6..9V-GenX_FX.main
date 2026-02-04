# Gitea Act Runner Setup Script for Windows
# This script automates the installation and registration of act_runner for forge.mql5.io

$RunnerVersion = "0.2.10"
$GiteaInstance = "https://forge.mql5.io"
$RunnerName = "genx-windows-runner"
$Labels = "windows-latest:host,ubuntu-latest:docker://node:20-bullseye"

# Use RegistrationToken from environment or prompt
$RegistrationToken = $env:REGISTRATION_TOKEN
if (-not $RegistrationToken) {
    $RegistrationToken = Read-Host "🔑 Enter your Gitea runner registration token"
}

if (-not $RegistrationToken) {
    Write-Error "Registration token is required."
    exit 1
}

Write-Host "🚀 Starting Gitea Act Runner setup for Windows..." -ForegroundColor Cyan

# 1. Prerequisite check: Docker (optional on Windows as it can run on host)
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Warning "Docker not found. Windows host labels will still work, but docker labels will fail."
}

# 2. Download act_runner
$Binary = "act_runner-$RunnerVersion-windows-amd64.exe"
$Url = "https://gitea.com/gitea/act_runner/releases/download/v$RunnerVersion/$Binary"
$OutFile = "act_runner.exe"

if (-not (Test-Path $OutFile)) {
    Write-Host "📥 Downloading act_runner v$RunnerVersion..."
    Invoke-WebRequest -Uri $Url -OutFile $OutFile
}

# 3. Use existing config if available, else generate
if (-not (Test-Path config.yaml) -and (Test-Path runner_config.yaml)) {
    Write-Host "⚙️ Using provided runner_config.yaml..."
    Copy-Item runner_config.yaml config.yaml
} elseif (-not (Test-Path config.yaml)) {
    Write-Host "⚙️ Generating default configuration..."
    .\act_runner.exe generate-config | Out-File -FilePath config.yaml -Encoding utf8
}

# 4. Register the runner
Write-Host "📝 Registering runner with $GiteaInstance..."
.\act_runner.exe register `
    --instance "$GiteaInstance" `
    --token "$RegistrationToken" `
    --name "$RunnerName" `
    --labels "$Labels" `
    --no-interactive

Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "To start the runner, run:"
Write-Host "  .\act_runner.exe daemon --config config.yaml"
Write-Host ""
Write-Host "Note: To run as a service, consider using NSSM (Non-Sucking Service Manager)."
