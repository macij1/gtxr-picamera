#!/bin/bash

mkdir -p "/home/gtxr/gtxr-picamera/logs"
exec | "/home/gtxr/gtxr-picamera/logs/picture.txt" 2>&1
set -x

# Absolute path to your project directory
PROJECT_DIR="/home/gtxr/gtxr-picamera"
date=$(date +%Y-%m-%d)
TOP_LOG="/home/gtxr/gtxr-picamera/logs/main_log_${date}.txt"

# Navigate to the project directory
cd "$PROJECT_DIR"

# Activate the virtual environment
source "picamvenv/bin/activate"

# Check that the background process is running
echo "$(date): Killing camera task manager" | "$TOP_LOG"
sudo pkill -f "task"

echo "$(date): Running selfie script" | "$TOP_LOG"
sudo /home/gtxr/gtxr-picamera/picamvenv/bin/python -u take_selfie.py

echo "$(date): Re-starting the video recording" | "$TOP_LOG"
nohup sudo /bin/bash /home/gtxr/gtxr-picamera/run_task_manager.sh &

exit 0

