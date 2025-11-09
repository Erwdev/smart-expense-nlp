#!/bin/bash

echo "========================================"
echo "Smart Expense NLP - Local Setup"
echo "========================================"
echo

echo "[1/4] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create venv"
    exit 1
fi

echo "[2/4] Activating virtual environment..."
source venv/bin/activate

echo "[3/4] Upgrading pip..."
pip install --upgrade pip

echo "[4/4] Installing dependencies..."
pip install -r requirements-dev.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo
echo "========================================"
echo "✅ Setup complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Activate venv: source venv/bin/activate"
echo "2. Run API: uvicorn src.api.main:app --reload"
echo "3. Jupyter: jupyter notebook"
echo
echo "For Docker: docker-compose up"
echo "========================================"