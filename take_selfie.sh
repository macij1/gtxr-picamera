#!/bin/bash

# Setup paths
PROJECT_DIR="/home/gtxr/gtxr-picamera"
date=$(date +%Y-%m-%d_%H-%M-%S)
TOP_LOG="$PROJECT_DIR/logs/main_log_${date}.txt"

# Ensure logs dir exists
mkdir -p "$PROJECT_DIR/logs"

# Redirect all output (stdout + stderr) to both terminal and log
exec > >(tee -a "$TOP_LOG") 2>&1
set -x  # Show commands as they run

cd "$PROJECT_DIR" || exit 1

# Activate virtual environment
source "picamvenv/bin/activate"

# Kill any existing task manager
echo "$(date): Killing camera task manager"
sudo pkill -f "task"

# Run selfie capture
echo "$(date): Running selfie script"
sudo "$PROJECT_DIR/picamvenv/bin/python" -u take_selfie.py

# Restart task manager in background
echo "$(date): Re-starting the video recording"
nohup sudo /bin/bash "$PROJECT_DIR/run_task_manager.sh"

exit 0
