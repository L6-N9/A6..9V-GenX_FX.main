#!/bin/bash
# AMP CLI Alias Script
# Usage: source amp_alias.sh
# Then use: amp <command>

# Function to run AMP CLI
amp() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "Activating AMP virtual environment..."
        source amp_env/bin/activate
    fi
    
    python3 amp_wrapper.py "$@"
}

# Export the function
export -f amp

echo "AMP CLI alias created!"
echo "Usage: amp <command>"
echo "Available commands:"
echo "  amp status     - Show AMP status"
echo "  amp run        - Run next job"
echo "  amp update     - Update configuration"
echo "  amp verify     - Verify installation"
echo "  amp --help     - Show all commands"