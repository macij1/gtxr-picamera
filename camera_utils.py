from picamera2 import Picamera2
from datetime import datetime
import os

def init_camera():
    try:
        picam2 = Picamera2(0)
    except Exception as e:
        print("Error: camera not found:")
        print(f"\t{e}")
    config = picam2.create_video_configuration(main={"fps":60})
    picam2.configure(config)
    picam2.start()
    return picam2

def record_video(picam2, camera_manager):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("Starting recording")
    path = f"{camera_manager.main_video_path}video_{ts}.mp4"
    picam2.start_and_record_video(path, duration=7200) # default length = 2h

# Records video segments. By default, 1 min segments for a total of 2 hours
def record_video_segments(picam2, camera_manager, segment_length=60, total_duration=7200):
    start_time = datetime.now()
    elapsed = 0
    while elapsed < total_duration:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = f"{camera_manager.main_video_path}video_{ts}.mp4"
        print(f"Recording segment: {path}")
        picam2.start_and_record_video(path, duration=segment_length)
        camera_manager.current_video_size += os.path.getsize(path)
        elapsed = (datetime.now() - start_time).total_seconds()
    picam2.stop()
    return 0


def take_photo(picam2):
    path = "/"+ str(datetime.now()) + "-selfie.jpg"
    picam2.start_and_capture_file(path)
    return 0
