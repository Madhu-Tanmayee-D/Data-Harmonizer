#!/bin/bash

# Dataset Harmonization Platform - Startup Script for Linux/Mac

echo ""
echo "============================================"
echo "Dataset Harmonization Platform - Startup"
echo "============================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

echo "[1/4] Checking Python version..."
python3 --version

echo ""
echo "[2/4] Installing/Updating dependencies..."
pip3 install -r requirements.txt

echo ""
echo "[3/4] Initializing database..."
python3 database.py

echo ""
echo "[4/4] Starting application..."
echo ""
echo "============================================"
echo "Opening Streamlit app at http://localhost:8501"
echo "============================================"
echo ""
echo "Press CTRL+C to stop the application"
echo ""

streamlit run app.py --server.port=8501
