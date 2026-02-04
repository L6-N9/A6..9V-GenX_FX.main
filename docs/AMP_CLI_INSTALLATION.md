# AMP CLI Installation & Usage Guide

## ✅ **AMP CLI Successfully Installed!**

The AMP (Automated Model Pipeline) CLI has been successfully installed and configured for your GenX Trading Platform.

## 🚀 **Quick Start**

### **1. Activate AMP CLI**
```bash
source amp_alias.sh
```

### **2. Check Status**
```bash
amp status
```

### **3. Run Next Job**
```bash
amp run
```

## 📋 **Available Commands**

| Command | Description | Example |
|---------|-------------|---------|
| `amp status` | Show AMP status and configuration | `amp status` |
| `amp run` | Execute the next job | `amp run` |
| `amp update` | Update AMP configuration | `amp update --set api_provider=gemini` |
| `amp plugin-install` | Install AMP plugins | `amp plugin-install gemini-integration` |
| `amp config-set` | Set configuration options | `amp config-set --enable-sentiment-analysis` |
| `amp service-enable` | Enable services | `amp service-enable gemini_service` |
| `amp verify` | Verify installation | `amp verify --check-dependencies` |
| `amp test` | Run tests | `amp test --all` |
| `amp deploy` | Deploy to production | `amp deploy` |
| `amp --help` | Show all commands | `amp --help` |

## 🔧 **Current Configuration**

### **✅ Installed Plugins**
- **gemini-integration**: Google Gemini AI integration for market analysis
- **reddit-signals**: Reddit integration for social sentiment analysis
- **news-aggregator**: Multi-source news aggregation for market analysis
- **websocket-streams**: Multi-exchange WebSocket streams for real-time data

### **✅ Enabled Features**
- Sentiment Analysis
- Social Signals
- News Feeds
- WebSocket Streams

### **✅ API Provider**
- **Primary**: Gemini AI

## 📁 **File Structure**

```
GenX_FX/
├── amp_env/                    # Virtual environment
├── amp_cli.py                  # Main AMP CLI implementation
├── amp_wrapper.py              # CLI wrapper script
├── amp_alias.sh                # Shell alias script
├── amp_job_runner.py           # Job execution engine
├── amp_config.json             # AMP configuration
├── amp-plugins/                # Plugin definitions
│   ├── gemini-integration.md
│   ├── reddit-signals.md
│   ├── news-aggregator.md
│   └── websocket-streams.md
└── setup.py                    # Installation script
```

## 🎯 **Usage Examples**

### **Check Current Status**
```bash
amp status
```

### **Run Trading Pipeline**
```bash
amp run
```

### **Install New Plugin**
```bash
amp plugin-install new-plugin --source genx-trading --enable-service new_service
```

### **Update Configuration**
```bash
amp update --set api_provider=gemini --add-dependency websockets>=11.0
```

### **Verify Installation**
```bash
amp verify --check-dependencies --check-env-vars --check-services --check-api-keys
```

### **Run Tests**
```bash
amp test --all
```

## 🔍 **Troubleshooting**

### **If AMP CLI not found:**
```bash
source amp_alias.sh
```

### **If virtual environment not activated:**
```bash
source amp_env/bin/activate
```

### **If dependencies missing:**
```bash
pip install websockets google-generativeai praw newsapi-python
```

## 📊 **Job Reports**

Job reports are automatically generated and saved to:
```
logs/amp_job_report_YYYYMMDD_HHMMSS.json
```

## 🎉 **Success Indicators**

✅ **AMP CLI installed and working**
✅ **All 4 plugins configured**
✅ **Job runner functional**
✅ **Status reporting working**
✅ **Next job execution successful**

## 🚀 **Next Steps**

1. **Set API Keys**: Configure your API keys in `.env` file
2. **Install Dependencies**: `pip install websockets google-generativeai praw`
3. **Run Regular Jobs**: Use `amp run` for continuous execution
4. **Monitor Results**: Check logs directory for job reports
5. **Customize**: Modify `amp_config.json` for your specific needs

## 📞 **Support**

For issues or questions:
- Check the logs in `logs/` directory
- Review `amp_config.json` configuration
- Use `amp verify` to diagnose issues
- Check service files in `api/services/`

---

**🎯 AMP CLI is now ready for production use with your GenX Trading Platform!**