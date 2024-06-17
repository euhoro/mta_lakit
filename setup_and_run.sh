#!/bin/bash

check_python310_installed() {
    if command -v python3.10 &> /dev/null; then
        echo "Python 3.10 is installed."
    else
        echo "Python 3.10 is not installed. Please install Python 3.10 and try again."
        exit 1
    fi
}

check_python310_installed

echo "Creating virtual environment..."
python3.10 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Starting FastAPI application..."
uvicorn main:app --reload
