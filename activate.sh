#!/bin/bash
# Script to activate the virtual environment
# Usage: source activate.sh

if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
    echo "Python location: $(which python)"
    echo "To deactivate, run: deactivate"
else
    echo "❌ Virtual environment not found. Run: python -m venv .venv"
    echo "Then run: source activate.sh"
fi
