# FXCM ForexConnect Integration Guide

## Overview

This document provides comprehensive instructions for integrating FXCM's ForexConnect API with the GenX trading system's spreadsheet output functionality. The integration enables real-time market data retrieval and account information to be exported to Excel/CSV files for MT4/5 Expert Advisors.

## Architecture

```
FXCM ForexConnect API → Data Provider → Spreadsheet Manager → Excel/CSV Output
```

### Components

1. **FXCMForexConnectProvider**: Real-time data provider using ForexConnect API
2. **MockFXCMForexConnectProvider**: Mock provider for testing without credentials
3. **SpreadsheetManager**: Handles output to various formats (Excel, CSV, JSON, MT4/5)
4. **Configuration System**: Secure credential management with environment variables

## Installation

### Prerequisites

- Python 3.7 (Required by ForexConnect)
- Ubuntu/Debian Linux system
- FXCM Demo or Live account credentials

### Step 1: Install Python 3.7

```bash
# Install pyenv for Python version management
curl https://pyenv.run | bash

# Add pyenv to your shell
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"

# Install build dependencies
sudo apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
    libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
    liblzma-dev git

# Install Python 3.7
pyenv install 3.7.17
pyenv local 3.7.17
```

### Step 2: Install ForexConnect and Dependencies

```bash
# Create virtual environment
python -m venv forexconnect_env
source forexconnect_env/bin/activate

# Install ForexConnect and dependencies
pip install --upgrade pip
pip install numpy pandas forexconnect openpyxl aiohttp

# Verify installation
python -c "import forexconnect as fx; print('ForexConnect installed successfully!')"
```

### Step 3: Configure Environment Variables

```bash
# Set FXCM credentials (NEVER commit these to git!)
export FXCM_USERNAME='your_demo_username'
export FXCM_PASSWORD='your_demo_password'
export FXCM_CONNECTION_TYPE='Demo'
export FXCM_URL='http://fxcorporate.com/Hosts.jsp'
```

## Configuration

### Config File Structure

```json
{
  "fxcm_forexconnect": {
    "enabled": true,
    "use_mock": false,
    "username": "${FXCM_USERNAME}",
    "password": "${FXCM_PASSWORD}",
    "connection_type": "${FXCM_CONNECTION_TYPE}",
    "url": "${FXCM_URL}",
    "timeout": 30,
    "retry_attempts": 3,
    "auto_reconnect": true,
    "auto_select_server": true
  },
  "data_provider": {
    "symbols": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD"],
    "timeframes": ["M15", "H1", "H4", "D1"],
    "refresh_interval": 30
  },
  "spreadsheet": {
    "output_directory": "signal_output",
    "formats": {
      "excel": true,
      "csv": true,
      "json": true,
      "mt4_csv": true,
      "mt5_csv": true
    },
    "include_account_info": true,
    "include_market_data": true
  }
}
```

## Usage

### Basic Connection Test

```python
#!/usr/bin/env python3
import os
import forexconnect as fx

# Get credentials from environment
username = os.getenv('FXCM_USERNAME')
password = os.getenv('FXCM_PASSWORD')
connection_type = os.getenv('FXCM_CONNECTION_TYPE', 'Demo')
url = os.getenv('FXCM_URL', 'http://fxcorporate.com/Hosts.jsp')

# Create connection
forex_connect = fx.ForexConnect()
session = forex_connect.login(
    user_id=username,
    password=password,
    url=url,
    connection=connection_type
)

if session:
    print("✓ Connected to FXCM successfully!")
    
    # Get live prices
    offers_table = forex_connect.get_table(forex_connect.OFFERS)
    if offers_table and offers_table.size() > 0:
        offer = offers_table.get_row(0)
        print(f"Sample: {offer.instrument} - Bid: {offer.bid}, Ask: {offer.ask}")
    
    # Logout
    session.logout()
else:
    print("✗ Failed to connect to FXCM")
```

### Integration with Spreadsheet System

```python
from core.data_sources.fxcm_forexconnect_provider import FXCMForexConnectProvider
from core.spreadsheet_manager import SpreadsheetManager

# Initialize providers
config = {
    "username": os.getenv('FXCM_USERNAME'),
    "password": os.getenv('FXCM_PASSWORD'),
    "connection_type": "Demo",
    "url": "http://fxcorporate.com/Hosts.jsp"
}

# Create data provider
data_provider = FXCMForexConnectProvider(config)
await data_provider.connect()

# Get live prices
symbols = ["EURUSD", "GBPUSD", "USDJPY"]
prices = await data_provider.get_live_prices(symbols)

# Create spreadsheet manager
spreadsheet_config = {
    "output_directory": "signal_output",
    "formats": {"excel": True, "csv": True, "mt4_csv": True}
}
spreadsheet_manager = SpreadsheetManager(spreadsheet_config)
await spreadsheet_manager.initialize()

# Convert prices to signals format and update spreadsheet
market_signals = []
for symbol, price_data in prices.items():
    signal = {
        'Magic': f'MKT_{symbol}',
        'Symbol': symbol,
        'Action': 'MARKET_DATA',
        'Bid': price_data['bid'],
        'Ask': price_data['ask'],
        'Spread': price_data['spread'],
        'Timestamp': price_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    }
    market_signals.append(signal)

# Update spreadsheet
await spreadsheet_manager.update_signals(market_signals)
```

## Testing

### Run Mock Tests (No Credentials Required)

```bash
# Test with mock data provider
python test_fxcm_spreadsheet_integration.py --mock
```

### Run Real Connection Tests

```bash
# Set credentials first
export FXCM_USERNAME='your_username'
export FXCM_PASSWORD='your_password'
export FXCM_CONNECTION_TYPE='Demo'

# Test with real FXCM connection
python test_fxcm_spreadsheet_integration.py --real
```

### Simple Connection Test

```bash
# Test basic ForexConnect functionality
python test_fxcm_credentials_removed.py
```

## Output Files

The integration generates multiple output formats:

### Excel Files
- `signal_output/genx_signals.xlsx` - Formatted Excel with charts and styling
- Contains: Account info, live prices, trading signals, performance metrics

### CSV Files
- `signal_output/genx_signals.csv` - General CSV format
- `signal_output/MT4_Signals.csv` - MT4 EA optimized format
- `signal_output/MT5_Signals.csv` - MT5 EA optimized format

### JSON Files
- `signal_output/genx_signals.json` - JSON format for API integration

### Sample MT4 CSV Format
```csv
Magic,Symbol,Action,Lots,OpenPrice,StopLoss,TakeProfit,Comment
1001,EURUSD,BUY,0.10,1.08456,1.08356,1.08656,GenX Signal 1
1002,GBPUSD,SELL,0.15,1.26789,1.26889,1.26589,GenX Signal 2
```

## API Reference

### FXCMForexConnectProvider Methods

```python
# Connection management
await provider.connect() -> bool
await provider.disconnect()
await provider.health_check() -> bool

# Data retrieval
await provider.get_live_prices(symbols: List[str]) -> Dict[str, Dict]
await provider.get_historical_data(symbol: str, timeframe: str, count: int) -> pd.DataFrame
await provider.get_account_summary() -> Dict[str, Any]

# Information
provider.get_supported_symbols() -> List[str]
provider.get_supported_timeframes() -> List[str]
```

### Supported Symbols
- EURUSD, GBPUSD, USDJPY, USDCHF
- AUDUSD, USDCAD, NZDUSD
- EURGBP, EURJPY, GBPJPY

### Supported Timeframes
- M1, M5, M15, M30 (Minutes)
- H1, H4 (Hours)
- D1, W1 (Daily, Weekly)

## Error Handling

### Common Issues and Solutions

1. **"Login failed. Incorrect user name or password"**
   - Check credentials are correct
   - Verify demo account is active
   - Try different URL (HTTPS vs HTTP)

2. **"ForexConnect module not available"**
   - Ensure Python 3.7 is being used
   - Reinstall ForexConnect: `pip install forexconnect`
   - Check virtual environment is activated

3. **"Demo account might be expired"**
   - FXCM demo accounts expire after 30 days
   - Create new demo account at FXCM website
   - Verify account activation via email

4. **Spreadsheet files not created**
   - Check output directory permissions
   - Verify required packages: `pip install openpyxl pandas`
   - Check disk space availability

## Security Considerations

1. **Never commit credentials to git**
   - Use environment variables only
   - Add `.env` files to `.gitignore`
   - Use configuration templates with placeholders

2. **Credential management**
   ```bash
   # Good - using environment variables
   export FXCM_USERNAME='demo_user'
   
   # Bad - hardcoded in scripts
   username = "demo_user"  # DON'T DO THIS
   ```

3. **Log security**
   - Disable sensitive data logging in production
   - Set `log_sensitive_data: false` in config
   - Review log files before sharing

## Deployment

### Production Deployment

1. **Use encrypted credential storage**
2. **Set up log rotation**
3. **Configure monitoring and alerting**
4. **Implement graceful error handling**
5. **Set up automated backups of signal files**

### Docker Deployment

```dockerfile
FROM python:3.7-slim

# Install ForexConnect dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy application
COPY . /app
WORKDIR /app

# Run application
CMD ["python", "main.py", "--mode", "live"]
```

## Performance Optimization

1. **Automatic Server Selection**: Enable `auto_select_server` in the configuration to automatically select the server with the lowest latency. This can improve connection speed and reliability.
2. **Data Caching**: Cache frequently requested data
3. **Connection Pooling**: Reuse connections when possible
4. **Batch Operations**: Group multiple API calls
5. **Async Operations**: Use asyncio for concurrent operations
6. **Memory Management**: Clean up old data regularly

## Monitoring and Logging

### Key Metrics to Monitor
- Connection uptime
- API response times
- Data refresh rates
- Error rates
- File generation success

### Log Levels
- INFO: Normal operations
- WARNING: Recoverable issues
- ERROR: Failed operations
- DEBUG: Detailed troubleshooting

## Support and Troubleshooting

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py --mode=live --debug
```

### Health Check
```bash
# Check system health
python -c "
from core.data_sources.fxcm_forexconnect_provider import FXCMForexConnectProvider
import asyncio
import os

config = {
    'username': os.getenv('FXCM_USERNAME'),
    'password': os.getenv('FXCM_PASSWORD'),
    'connection_type': 'Demo',
    'url': 'http://fxcorporate.com/Hosts.jsp'
}

async def health_check():
    provider = FXCMForexConnectProvider(config)
    connected = await provider.connect()
    if connected:
        healthy = await provider.health_check()
        print(f'Health check: {'PASS' if healthy else 'FAIL'}')
        await provider.disconnect()
    else:
        print('Health check: FAIL - Could not connect')

asyncio.run(health_check())
"
```

## License and Disclaimer

This integration is provided as-is for educational and development purposes. Trading involves risk, and you should never trade with money you cannot afford to lose. Always test thoroughly in a demo environment before using with real accounts.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

For questions or support, please open an issue in the repository.