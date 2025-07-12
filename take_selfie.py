import threading
from datetime import datetime, timedelta
import os
import time
from glob import glob
import gt_packet
import camera_utils
from try_ports import try_ports

class CameraManager():
    
    def __init__(self):
        self.gt_buffer = []
        self.serial_portname = ""
        self.camera_busy = False
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        if not os.path.exists("photos/"):
            os.makedirs("photos/")

    def start(self):
        picam = camera_utils.init_camera()
        stop_event = threading.Event()
        camera_thread = threading.Thread(target=camera_utils.record_h264_segments, args = (picam, self, 7200, stop_event))
            

        while True:
            try:
                if self.camera_busy:
                    print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Selfie failed, camera busy")
                else:
                    self.camera_busy = True
                    print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Taking a picture in ...")
                    for count in range(10):
                        print(f"{count}")
                    camera_utils.take_selfie(picam)
                    self.camera_busy = False
                    return

            except UnicodeDecodeError:
                print("Received malformed data")
            except KeyboardInterrupt:
                print("Exiting...")
                stop_event.set()
                self.camera_busy = False
                break
            except Exception as e:
                print(e)



if __name__ == "__main__":
    print("Initializing Camera Manager")
    cam_manager = CameraManager()
    
    print("Camera Manager Ready, ROUTINE STARTED")
    cam_manager.start()
    exit()
