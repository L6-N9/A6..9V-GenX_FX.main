#!/bin/bash

# Startup Script for GenX-FX Trading Platform

echo "🚀 Starting GenX-FX Trading Platform..."

# Check if database exists
if [ ! -f "genxdb_fx.db" ]; then
    echo "📊 Setting up database..."
    python3 setup_database.py
fi

# Start the API server
echo "🌐 Starting API server on port 8080..."
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8080 --reload
