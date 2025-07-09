#!/bin/bash

mkdir -p "/home/gtxr/gtxr-picamera/logs"
exec > "/home/gtxr/gtxr-picamera/logs/main_log.txt" 2>&1
set -x

# Absolute path to your project directory
PROJECT_DIR="/home/gtxr/gtxr-picamera"
TOP_LOG="/home/gtxr/gtxr-picamera/logs/main_log.txt"

# Navigate to the project directory
cd "$PROJECT_DIR"

# Activate the virtual environment
source "picamvenv/bin/activate"

# Check that the background process is running
if ! pgrep -f "task_manager.py" > /dev/null; then
    echo "$(date): Starting task manager" >> "$TOP_LOG"
    sudo python -u task_manager.py >> "$TOP_LOG" 2>&1 &
else
    echo "$(date): $SCRIPT already running" >> "$TOP_LOG"
fi
