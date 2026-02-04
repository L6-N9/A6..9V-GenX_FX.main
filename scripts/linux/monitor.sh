#!/bin/bash
echo "=== GenX FX System Status ==="
echo "Date: $(date)"
echo

echo "🔄 Services:"
systemctl is-active genx-trading.service
systemctl is-active genx-web.service
echo

echo "💾 Disk Usage:"
df -h /
echo

echo "🧠 Memory Usage:"
free -h
echo

echo "⚡ CPU Usage:"
top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1"% used"}'
echo

echo "📊 Latest Signals:"
ls -la signal_output/ | tail -3
echo

echo "📈 AMP Status:"
source genx_env/bin/activate && python3 amp_cli.py status 2>/dev/null || echo "AMP not running"
