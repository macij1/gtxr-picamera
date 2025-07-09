from picamera2 import Picamera2
from picamera2.encoders import H264Encoder
from picamera2.outputs import FileOutput
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

def take_selfie(picam2):
    """
    Captures a high-quality still image using the Pi Camera v1.2.
    The image is saved with a timestamp in the filename.
    """
    # Pi Camera v1.2 max resolution: 3280×2464
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"photos/selfie_{ts}.jpg"

    try:
        # Configure for still capture at max quality
        config = picam2.create_still_configuration(main={"size": (3280, 2464)})
        picam2.configure(config)
        picam2.start()
        picam2.capture_file(path)
        print(f"Selfie taken and saved to {path}")
    except Exception as e:
        print(f"Error, Photo Unsuccessful: {e}")


def record_and_pipe_video(picam2, camera_manager, duration=None, stop_event=None):
    # Configuration
    width, height = 1920, 1080
    framerate = 60
    segment_length = 10  # seconds
    output_pattern = f"{camera_manager.main_video_path}video%03d.mp4"

    # Start ffmpeg subprocess for segmentation
    ffmpeg = subprocess.Popen([
        "ffmpeg",
        "-f", "h264",
        "-framerate", str(framerate),
        "-i", "pipe:0",
        "-c", "copy",
        "-f", "segment",
        "-segment_time", str(segment_length),
        "-reset_timestamps", "1",
        output_pattern
    ], stdin=subprocess.PIPE)

    # Start recording
    print(f"Starting recording: {output_pattern}")
    encoder = H264Encoder()
    output = FileOutput(ffmpeg.stdin)

    picam2.start()
    picam2.start_recording(encoder, output)

    try:
        print("Recording... Press Ctrl+C to stop.")
        start_time = time.time()
        while True:
            time.sleep(5)
            if stop_event and stop_event.is_set():
                print("Stop event received. Ending recording.")
                break
            if duration and (time.time() - start_time) >= duration:
                print("Duration reached. Ending recording.")
                break
    except KeyboardInterrupt:
        print("Stopping recording due to keyboard interrupt.")
    finally:
        picam2.stop_recording()
        ffmpeg.stdin.close()
        ffmpeg.wait()

def record_h264_segments(picam2, camera_manager, duration=7200, stop_event=None):
    
    encoder = H264Encoder()
    picam2.start()
    i = 0
    start_time = time.time()
    try:
        while not (stop_event and stop_event.is_set()):
            filename = f"{camera_manager.main_video_path}video_{i}.h264"
            print(f"Recording segment: {filename}")
            picam2.start_recording(encoder, filename)
            time.sleep(segment_length)
            picam2.stop_recording()
            i += 1
            if i > 100 and duration and (time.time() - start_time) >= duration: 
                print("Duration reached. Ending recording.")
                break
    except KeyboardInterrupt:
        print("Stopping recording due to keyboard interrupt.")
    finally:
        picam2.stop_recording()
        picam2.stop()


####### Deprecated functionalities:

# Video in one single take, deprecated
def record_video(picam2, camera_manager, duration=120):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{camera_manager.main_video_path}video_{ts}.h264"
    try:
        print(f"Starting recording: {path}")
        encoder = H264Encoder()
        picam2.start_recording(encoder, path)
        time.sleep(duration)
        picam2.stop_recording()
        print("Recording successful")
    except Exception as e:
        print(f"Error, Photo Unsuccessful: {e}")



