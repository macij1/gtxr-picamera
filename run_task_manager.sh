#!/bin/bash

# Absolute path to your project directory
PROJECT_DIR="/gtxr-picamera"
TOP_LOG_DIR="/gtxr-picamera/toplog.txt"

# Navigate to the project directory
cd "$PROJECT_DIR"

# Activate the virtual environment
source "$PROJECT_DIR/picamvenv/bin/activate"

# Run your Python script
sudo python -u task_manager.py >> "$TOP_LOG_DIR" 2>&1