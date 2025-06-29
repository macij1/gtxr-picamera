#!/bin/bash

set -e  # Exit on error

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y python3-picamera2 --no-install-recommends

echo "Creating Python virtual environment with system packages..."
python3 -m venv picamvenv --system-site-packages

echo "Activating virtual environment..."
source picamvenv/bin/activate

echo "Installing Python packages..."
pip install --upgrade pip

# These are part of the standard library — don't need to install:
# pip install time
# pip install os

pip install pyserial
pip install crcmod

# Optional: mock-serial (commented out)
# pip install mock-serial

# Re-run apt install in case needed again (redundant)
sudo apt install -y python3-picamera2 --no-install-recommends

echo "Setup complete. Environment 'picamvenv' is ready and activated."