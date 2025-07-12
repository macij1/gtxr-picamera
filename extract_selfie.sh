#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: missing argument — photo name required"
    exit 1
fi

scp gtxr@pi-netanyahu.local:/home/gtxr/gtxr-picamera/photos/"$1" ./photos/"$1" 
exit 0