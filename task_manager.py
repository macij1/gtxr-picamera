import threading
from datetime import datetime, timedelta
import os
import time
from glob import glob
import camera_utils

"""
Listens for telecommands from the UART port
Upon receival, parse and immediately complete the task
"""
class CameraManager():
    
    def __init__(self):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.main_video_path = f"videos_{ts}/"
        self.size_log_path = f"logs/{ts}-size_log.txt"
        self.current_video_size = 0 
        self.video_counter = 0
        self.camera_busy = False

        if not os.path.exists(self.main_video_path):
            os.makedirs(self.main_video_path)
        if not os.path.exists("logs/"):
            os.makedirs("logs/")
        if not os.path.exists("photos/"):
            os.makedirs("photos/")
    
        
    # Logs every 3 seconds the state of the recording
    def monitor_size(self):
        print("\nStarting monitor thread")
        while True:
            try:
                time.sleep(3)
                # Get latest segment size
                files = glob(f"{self.main_video_path}*")
                if not files:
                    print("No files found in monitoring")
                    continue
                self.video_counter = len(files)
                latest_file = max(files, key=os.path.getctime)
                self.current_video_size = os.path.getsize(latest_file)

                # Log telemtry to SD card
                with open(self.size_log_path, "a") as logfile:
                    camera_state_str = f"Camera is busy" if self.camera_busy else f"Camera is free"
                    count_str = f"Number of recorded segments {float(self.video_counter):.1f}"
                    size_str = f"Latest segment size: {float(self.current_video_size):.1f} bytes"
                    timestamp = datetime.now().isoformat()
                    entry = f"{timestamp}: \t{count_str}\n\t{size_str}\n\t{camera_state_str}"
                    logfile.write(entry + "\n")
                    logfile.flush()
                    
            except Exception as e:
                print("Error in monitor size thread")
                print(e)

    def start(self):
        picam = camera_utils.init_camera()
        stop_event = threading.Event()
        camera_thread = threading.Thread(target=camera_utils.record_h264_segments, args = (picam, self, 7200, stop_event))
        monitor_size_thread = threading.Thread(target=self.monitor_size)
        
        try:
            # The camera starts recording by default
            with open(self.size_log_path, "a") as logfile:
                entry = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Starting camera routine"
                logfile.write(entry + "\n")
                logfile.flush()

            # Start recording video and monitoring its size
            self.camera_busy = True
            camera_thread.start()
            monitor_size_thread.start()

            return True
        except UnicodeDecodeError:
            print("Received malformed data")
            return False
        except KeyboardInterrupt:
            print("Exiting...")
            stop_event.set()
            self.camera_busy = False
            return False
        except Exception as e:
            print(e)
            return False



if __name__ == "__main__":
    print("Initializing Camera Manager")
    cam_manager = CameraManager()
    
    
    print("Camera Manager Ready, ROUTINE STARTED")
    res = cam_manager.start()
    while not res:
        print("Re-starting camera")
        time.sleep(5)
        res = cam_manager.start()



