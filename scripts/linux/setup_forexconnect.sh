#!/bin/bash

# ForexConnect Installation Script
# This script installs ForexConnect API for Python on Ubuntu systems

set -e  # Exit on any error

echo "=== ForexConnect API Installation Script ==="
echo "This script will install ForexConnect API for Python using Python 3.7"
echo

# Check if running on Ubuntu
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    echo "Warning: This script is designed for Ubuntu. It may not work on other distributions."
fi

# Update system packages
echo "Step 1: Updating system packages..."
sudo apt update

# Install build dependencies
echo "Step 2: Installing build dependencies..."
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
    liblzma-dev git software-properties-common

# Install pyenv if not already installed
if ! command -v pyenv &> /dev/null; then
    echo "Step 3: Installing pyenv..."
    curl https://pyenv.run | bash
    
    # Add pyenv to PATH for current session
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init - bash)"
    
    # Add pyenv to shell profile
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
    echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
    echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc
else
    echo "Step 3: pyenv already installed, skipping..."
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init - bash)"
fi

# Install Python 3.7.17
echo "Step 4: Installing Python 3.7.17..."
if ! pyenv versions | grep -q "3.7.17"; then
    pyenv install 3.7.17
else
    echo "Python 3.7.17 already installed, skipping..."
fi

# Set Python 3.7.17 as local version
echo "Step 5: Setting Python 3.7.17 as local version..."
pyenv local 3.7.17

# Create virtual environment
echo "Step 6: Creating virtual environment..."
if [ ! -d "forexconnect_env_37" ]; then
    python -m venv forexconnect_env_37
else
    echo "Virtual environment already exists, skipping creation..."
fi

# Activate virtual environment and install ForexConnect
echo "Step 7: Installing ForexConnect and dependencies..."
source forexconnect_env_37/bin/activate
python -m pip install --upgrade pip
python -m pip install numpy pandas forexconnect

# Verify installation
echo "Step 8: Verifying installation..."
python -c "import forexconnect; print('ForexConnect version:', forexconnect.__version__ if hasattr(forexconnect, '__version__') else 'Unknown')"

echo
echo "=== Installation Complete! ==="
echo
echo "ForexConnect API has been successfully installed!"
echo "Python version: $(python --version)"
echo "ForexConnect package location: $(python -c 'import forexconnect; print(forexconnect.__file__)')"
echo
echo "To use ForexConnect in the future:"
echo "1. Navigate to this directory: $(pwd)"
echo "2. Activate the virtual environment: source forexconnect_env_37/bin/activate"
echo "3. Run your Python scripts that use ForexConnect"
echo
echo "Test the installation with: python test_forexconnect.py"
echo
echo "For FXCM account setup and API documentation, visit:"
echo "- https://github.com/fxcm/ForexConnectAPI"
echo "- https://www.fxcm.com/uk/api-trading/"