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
