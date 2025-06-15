from picamera2 import Picamera2
import datetime

def init_camera():
    picam2 = Picamera2()
    config = picam2.create_preview_configuration()
    picam2.configure(config)
    picam2.start()
    return picam2

def record_video(picam2, path):
    picam2.start_and_record_video(path, duration=30) # default length = 30mins
    return 0


def take_photo(picam2):
    path = "~/photos/"+ str(datetime.now()) + ".jpg"
    picam2.start_and_capture_file(path)
    return 0