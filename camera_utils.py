from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from datetime import datetime
import time
import os
import subprocess

def init_camera():
    picam2 = Picamera2()
    config = picam2.create_video_configuration(
        main={"size": (1920, 1080)},  # Resolution
        controls={"FrameDurationLimits": (16666, 16666)}  # ~60fps
    )
    picam2.configure(config)
    picam2.start()  # Don't use show_preview on headless
    return picam2

def record_video(picam2, camera_manager, duration=120):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{camera_manager.main_video_path}video_{ts}.h264"

    print(f"Starting recording: {path}")
    encoder = H264Encoder()
    picam2.start_recording(encoder, path)
    time.sleep(duration)
    picam2.stop_recording()
    print("Recording successful")

def record_and_pipe_video(picam2, camera_manager, duration = 120):
    # Configuration
    width, height = 1920, 1080
    framerate = 30  # try 60 if you're confident in performance
    segment_length = 10  # seconds
    output_pattern = f"{camera_manager.main_video_path}video%03d.mp4"

    # Start ffmpeg subprocess for segmentation
    ffmpeg = subprocess.Popen([
        "ffmpeg",
        "-f", "h264",              # raw H.264 input
        "-framerate", str(framerate),
        "-i", "pipe:0",            # from stdin
        "-c", "copy",              # no re-encoding
        "-f", "segment",
        "-segment_time", str(segment_length),
        "-reset_timestamps", "1",
        output_pattern
    ], stdin=subprocess.PIPE)

    # Start recording
    print(f"Starting recording: {output_pattern}")
    encoder = H264Encoder()
    picam2.start_recording(encoder, ffmpeg.stdin)


    try:
        print("Recording... Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping recording.")
    finally:
        picam2.stop_recording()
        ffmpeg.stdin.close()
        ffmpeg.wait()


def record_video_segments(picam2, camera_manager, segment_length=60, total_duration=7200):
    encoder = H264Encoder()
    picam2.encoder = encoder

    start_time = datetime.now()
    elapsed = 0
    while elapsed < total_duration:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{camera_manager.main_video_path}video_{ts}.h264"
        print(f"Recording segment: {path}")
        picam2.start_recording(encoder, path)
        time.sleep(segment_length)
        picam2.stop_recording()
        camera_manager.current_video_size += os.path.getsize(path)
        elapsed = (datetime.now() - start_time).total_seconds()

    picam2.stop()
    return 0

def take_photo(picam2):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"picam_runtime/{ts}-selfie.jpg"
    picam2.capture_file(path)
    return path
