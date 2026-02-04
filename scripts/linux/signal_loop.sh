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
