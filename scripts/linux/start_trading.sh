#!/bin/bash
# Simple GenX FX Trading Startup Script for Container Environment

echo "🚀 Starting GenX FX Trading System..."

# Activate virtual environment
source genx_env/bin/activate

# Create necessary directories
mkdir -p logs
mkdir -p backups

# Start web server in background for signal distribution
echo "🌐 Starting web server for signal distribution..."
python3 -m http.server 8080 --directory signal_output > logs/web_server.log 2>&1 &
WEB_PID=$!
echo "Web server started (PID: $WEB_PID)"

# Create signal generation loop
echo "📊 Starting automatic signal generation..."
cat > signal_loop.sh << 'EOF'
#!/bin/bash
source genx_env/bin/activate
while true; do
    echo "$(date): Generating signals..." >> logs/signals.log
    python3 demo_excel_generator.py >> logs/signals.log 2>&1
    
    # Try to run AMP if available
    python3 amp_cli.py run --once >> logs/amp.log 2>&1 || echo "$(date): AMP run failed" >> logs/amp.log
    
    # Wait 5 minutes
    sleep 300
done
EOF

chmod +x signal_loop.sh

# Start signal generation loop in background
nohup ./signal_loop.sh > logs/signal_loop.log 2>&1 &
SIGNAL_PID=$!
echo "Signal generation started (PID: $SIGNAL_PID)"

# Save PIDs for later management
echo $WEB_PID > logs/web_server.pid
echo $SIGNAL_PID > logs/signal_loop.pid

# Create status monitoring script
cat > status.sh << 'EOF'
#!/bin/bash
echo "=== GenX FX Trading System Status ==="
echo "Date: $(date)"
echo

# Check if processes are running
WEB_PID=$(cat logs/web_server.pid 2>/dev/null)
SIGNAL_PID=$(cat logs/signal_loop.pid 2>/dev/null)

echo "🌐 Web Server:"
if kill -0 $WEB_PID 2>/dev/null; then
    echo "  ✅ Running (PID: $WEB_PID)"
    echo "  📡 URL: http://34.71.143.222:8080"
else
    echo "  ❌ Not running"
fi

echo "📊 Signal Generation:"
if kill -0 $SIGNAL_PID 2>/dev/null; then
    echo "  ✅ Running (PID: $SIGNAL_PID)"
else
    echo "  ❌ Not running"
fi

echo
echo "📁 Latest Signal Files:"
ls -la signal_output/ 2>/dev/null | tail -5

echo
echo "📈 Recent Activity:"
echo "Signal generation:"
tail -3 logs/signals.log 2>/dev/null || echo "  No logs yet"

echo
echo "💾 System Resources:"
df -h . | grep -v Filesystem
free -h | grep -v "Swap:"
EOF

chmod +x status.sh

# Create stop script
cat > stop_trading.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping GenX FX Trading System..."

# Read PIDs
WEB_PID=$(cat logs/web_server.pid 2>/dev/null)
SIGNAL_PID=$(cat logs/signal_loop.pid 2>/dev/null)

# Kill processes
if [ ! -z "$WEB_PID" ] && kill -0 $WEB_PID 2>/dev/null; then
    kill $WEB_PID
    echo "Web server stopped"
fi

if [ ! -z "$SIGNAL_PID" ] && kill -0 $SIGNAL_PID 2>/dev/null; then
    kill $SIGNAL_PID
    echo "Signal generation stopped"
fi

# Clean up PID files
rm -f logs/web_server.pid logs/signal_loop.pid

echo "✅ Trading system stopped"
EOF

chmod +x stop_trading.sh

# Generate initial signals
echo "📊 Generating initial signals..."
python3 demo_excel_generator.py

echo "✅ GenX FX Trading System is now running!"
echo
echo "📋 Management Commands:"
echo "  📊 Check Status:    ./status.sh"
echo "  🛑 Stop System:     ./stop_trading.sh"
echo "  🔄 Restart:         ./stop_trading.sh && ./start_trading.sh"
echo
echo "📡 Access Points:"
echo "  🌐 Web Interface:   http://34.71.143.222:8080"
echo "  📈 MT4 Signals:     http://34.71.143.222:8080/MT4_Signals.csv"
echo "  📈 MT5 Signals:     http://34.71.143.222:8080/MT5_Signals.csv"
echo "  📊 Excel File:      http://34.71.143.222:8080/genx_signals.xlsx"
echo
echo "📝 Log Files:"
echo "  📊 Signals:         tail -f logs/signals.log"
echo "  🌐 Web Server:      tail -f logs/web_server.log"
echo "  🔄 AMP:             tail -f logs/amp.log"
echo
echo "🎉 Your trading system is generating signals every 5 minutes!"