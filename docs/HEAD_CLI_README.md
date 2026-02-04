# GenX Trading Platform - Head CLI

🚀 **Unified Command Line Interface** for the GenX Trading Platform

The Head CLI wraps all existing CLI tools into a single, organized interface, making it easy to manage your entire trading system from one place.

## Quick Start

```bash
# Run the head CLI directly
python3 head_cli.py overview

# Or use the convenient launcher script
./genx overview
```

## Available CLI Tools

| CLI | Description | Status |
|-----|-------------|--------|
| **AMP** | Automated Model Pipeline - AI trading models and authentication | ✅ Available |
| **GenX** | GenX FX - Complete trading system management | ✅ Available |
| **Chat** | Interactive chat with AMP trading system | ✅ Available |

## Head CLI Commands

### System Overview & Status
```bash
./genx overview        # Show system overview
./genx status          # Complete system status report
./genx auth            # Check authentication status
./genx monitor         # System performance monitoring
```

### AMP (Automated Model Pipeline) Commands
```bash
./genx amp status                    # AMP system status
./genx amp auth --status             # Check AMP authentication
./genx amp auth --token YOUR_TOKEN   # Login to AMP
./genx amp auth --logout             # Logout from AMP
./genx amp monitor --status          # AMP monitoring
./genx amp deploy                    # Deploy AMP to production
```

### GenX FX Commands
```bash
./genx genx status              # GenX system status
./genx genx init                # Initialize GenX system
./genx genx config              # Configure API keys and settings
./genx genx logs                # View GenX logs
./genx genx tree                # Show project structure
./genx genx excel               # Excel signal management
./genx genx forexconnect        # ForexConnect API management
```

### Interactive Chat
```bash
./genx chat                     # Start interactive chat with AMP
```

### Logs & Monitoring
```bash
./genx logs                     # View GenX logs (default)
./genx logs --source amp        # View AMP logs
./genx logs --source all        # View all logs
./genx tree                     # Show project structure tree
```

### Help & Documentation
```bash
./genx help-all                 # Complete help for all CLI tools
./genx --help                   # Head CLI help
./genx --version                # Show version
```

## Direct CLI Access

You can still access individual CLIs directly if needed:

```bash
# AMP CLI
python3 amp_cli.py --help
python3 amp_cli.py status

# GenX CLI  
python3 genx_cli.py --help
python3 genx_cli.py status

# Interactive Chat
python3 simple_amp_chat.py
```

## Example Workflows

### 1. Initial Setup
```bash
./genx overview                 # Check system overview
./genx init                     # Initialize the system
./genx auth --token YOUR_TOKEN  # Authenticate with AMP
./genx status                   # Verify everything is working
```

### 2. Daily Operations
```bash
./genx auth                     # Check authentication
./genx status                   # System status check
./genx chat                     # Interactive trading analysis
./genx monitor                  # Performance monitoring
```

### 3. Development & Debugging
```bash
./genx tree                     # View project structure
./genx logs                     # Check logs
./genx genx config              # Update configuration
./genx amp verify               # Verify AMP installation
```

## Features

- 🎯 **Unified Interface**: All CLI tools accessible from one place
- 🔐 **Authentication Management**: Easy AMP login/logout
- 📊 **System Monitoring**: Comprehensive status and performance monitoring  
- 💬 **Interactive Chat**: Direct communication with AMP trading system
- 📋 **Rich Output**: Beautiful, colored terminal output using Rich
- 🛠️ **Easy Setup**: Simple launcher script for quick access
- 📚 **Comprehensive Help**: Built-in documentation for all commands

## Architecture

```
head_cli.py (Head CLI)
├── amp_cli.py (AMP CLI)
├── genx_cli.py (GenX CLI)
├── simple_amp_chat.py (Chat Interface)
└── genx (Launcher Script)
```

The Head CLI acts as a wrapper that:
- Routes commands to appropriate underlying CLIs
- Provides unified authentication management
- Offers system-wide status monitoring
- Maintains consistent command structure

## Installation

No additional installation required. The Head CLI uses the same dependencies as the existing CLI tools:

```bash
# Install dependencies (if not already installed)
pip3 install --break-system-packages typer rich requests pyyaml python-dotenv
```

## Configuration

The Head CLI inherits configuration from the underlying systems:
- AMP authentication via `amp_auth.json`
- GenX configuration via `amp_config.json`
- Environment variables from `.env` files

---

**🚀 You now have a unified command center for your entire GenX Trading Platform!**

Use `./genx help-all` to see all available commands across all CLI tools.