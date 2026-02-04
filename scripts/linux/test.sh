#!/bin/bash

# Run server tests
echo "Running server tests..."
npm test

# Run python tests
echo "Running python tests..."
export TA_INCLUDE_PATH=/usr/include
export TA_LIBRARY_PATH=/usr/lib
pip install --no-cache-dir -r services/python/requirements.txt
python -m unittest discover services/python/tests
