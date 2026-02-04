# ForexConnect API Installation Guide

## Overview

ForexConnect is FXCM's trading API that allows you to programmatically interact with FXCM's trading platform. This guide shows you how to install ForexConnect for Python on Ubuntu systems.

## Important Notes

- **Python Version Compatibility**: ForexConnect currently supports Python 3.5, 3.6, and 3.7 only
- **Platform Support**: This guide is tested on Ubuntu 25.04, but should work on most Ubuntu/Debian systems
- **Dependencies**: Requires numpy and pandas

## Quick Installation (Automated)

Run the automated installation script:

```bash
chmod +x setup_forexconnect.sh
./setup_forexconnect.sh
```

## Manual Installation Steps

### 1. Install System Dependencies

```bash
sudo apt update
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
    liblzma-dev git software-properties-common
```

### 2. Install pyenv (Python Version Manager)

```bash
curl https://pyenv.run | bash

# Add to shell profile
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
echo '[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
echo 'eval "$(pyenv init - bash)"' >> ~/.bashrc

# Restart shell or source the profile
source ~/.bashrc
```

### 3. Install Python 3.7

```bash
pyenv install 3.7.17
pyenv local 3.7.17
```

### 4. Create Virtual Environment

```bash
python -m venv forexconnect_env_37
source forexconnect_env_37/bin/activate
```

### 5. Install ForexConnect and Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install numpy pandas forexconnect
```

### 6. Verify Installation

```bash
python test_forexconnect.py
```

## Package Information

- **Package**: forexconnect
- **Version**: 1.6.43 (as of this installation)
- **GitHub**: https://github.com/gehtsoft/forex-connect
- **Official FXCM API**: https://github.com/fxcm/ForexConnectAPI

## Basic Usage Example

```python
import forexconnect as fx

# Create session
session = fx.O2GSession()

# Set up login parameters (you need FXCM credentials)
session_descriptor = fx.O2GSessionDescriptor()
session_descriptor.setUrl("http://www.fxcorporate.com/Hosts.jsp")  # Demo server
session_descriptor.setUser("your_demo_username")
session_descriptor.setPassword("your_demo_password")
session_descriptor.setConnection("Demo")  # or "Real" for live trading

# Login to FXCM
session.login(session_descriptor)

# Your trading code here...

# Logout when done
session.logout()
```

## Getting FXCM Credentials

1. **Demo Account**: Visit https://www.fxcm.com/ and sign up for a free demo account
2. **Live Account**: Open a live trading account with FXCM
3. **API Access**: Ensure your account has API trading enabled

## Available Features

ForexConnect provides access to:

- Real-time market data
- Historical price data
- Order management (buy/sell orders)
- Account information
- Position management
- Trade execution
- Market analysis tools

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure you're using Python 3.7 and have numpy/pandas installed
2. **Connection Issues**: Verify your FXCM credentials and internet connection
3. **Platform Compatibility**: ForexConnect wheels are available for Linux x86_64 systems

### Python Version Issues

If you encounter issues with newer Python versions:

```bash
# Use pyenv to install and switch to Python 3.7
pyenv install 3.7.17
pyenv local 3.7.17
```

### Missing Dependencies

```bash
# Install all required dependencies
pip install numpy pandas forexconnect
```

## Files Created

- `forexconnect_env_37/` - Virtual environment with Python 3.7
- `test_forexconnect.py` - Test script to verify installation
- `setup_forexconnect.sh` - Automated installation script
- `.python-version` - pyenv local Python version file

## Next Steps

1. Test your installation with `python test_forexconnect.py`
2. Get FXCM demo account credentials
3. Study the FXCM API documentation
4. Start building your trading applications

## Support Resources

- **FXCM API Documentation**: https://www.fxcm.com/uk/api-trading/
- **GitHub Repository**: https://github.com/fxcm/ForexConnectAPI
- **FXCM Support**: Contact FXCM customer support for account-related issues
- **Community**: FXCM developer forums and GitHub issues

## License

ForexConnect API is proprietary software by Gehtsoft USA, LLC. Check the official license terms before use.

---

**Installation completed successfully!** You now have ForexConnect API ready for Python development.