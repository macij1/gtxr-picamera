#!/bin/bash

if [ -z "$1" ]; then
    echo "Error: missing argument — video dir name required"
    exit 1
fi

scp -r gtxr@pi-netanyahu.local:/home/gtxr/gtxr-picamera/"$1" videos/"$1" 
exit 0