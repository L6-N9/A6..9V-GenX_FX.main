@echo off
echo 🔧 GenX FX VS Code Issues Fix
echo ===============================

echo 📍 Current Python version:
python --version

echo 📦 Upgrading pip...
python -m pip install --upgrade pip

echo 🔧 Installing essential packages...
pip install --upgrade setuptools wheel

echo 📚 Installing Python language server...
pip install python-lsp-server[all]

echo 🧹 Installing code formatters...
pip install black flake8 isort

echo 🧪 Installing testing tools...
pip install pytest pytest-cov

echo 📊 Installing type checking...
pip install mypy

echo 🔍 Checking for missing dependencies...
pip install --upgrade -r requirements.txt

echo ✅ VS Code Python environment fixed!
echo 🔄 Please restart VS Code now.

pause