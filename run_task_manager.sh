#!/bin/bash

mkdir -p "/home/gtxr/gtxr-picamera/logs"
exec > "/home/gtxr/gtxr-picamera/logs/main_log.txt" 2>&1
set -x

# Absolute path to your project directory
PROJECT_DIR="/home/gtxr/gtxr-picamera"
TOP_LOG_DIR="/home/gtxr/gtxr-picamera/logs/main_log.txt"

# Navigate to the project directory
cd "$PROJECT_DIR"

# Activate the virtual environment
source "picamvenv/bin/activate"

# Run your Python script
sudo python -u task_manager.py >> "$TOP_LOG_DIR" 2>&1 &
