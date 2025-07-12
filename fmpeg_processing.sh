#!/bin/bash

# Define video directories here:
DIRS=("long_video")

for DIR in "${DIRS[@]}"
do
    echo "Processing $DIR"

    cd "$DIR" || { echo "Directory $DIR not found"; continue; }

    ls video*.h264 | sort | sed "s/^/file '/;s/$/'/" > files.txt

    ffmpeg -r 110 -f concat -safe 0 -i files.txt -c:v libx264 -preset slow -crf 18 "$DIR"_slowmo.mp4

    ffmpeg -i "$DIR"_slowmo.mp4 -vf "setpts=(1/4)*PTS" -an "$DIR"_realtime.mp4

    cd ..
done

