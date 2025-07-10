import threading
from datetime import datetime, timedelta
import os
import time
from glob import glob
import gt_packet
import camera_utils
from try_ports import try_ports

"""
Pseudo:
Constantly listen for commands from the UART port
Upon receival, parse and immediately complete the task
"""
class CameraManager():
    # Constants
    START_RECORDING_OPCODE = b'\x01'
    SELFIE_OPCODE = b'\x02'
    STOP_RECORDING_OPCODE = b'\x03'
    TELEMETRY_OPCODE = b'\x04'
    
    def __init__(self):
        self.gt_buffer = []
        self.serial_portname = ""
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

        self.gt_port = None
        self.gt_buffer.append(self.START_RECORDING_OPCODE)

    def start(self):
        picam = camera_utils.init_camera()
        stop_event = threading.Event()
        camera_thread = threading.Thread(target=camera_utils.record_h264_segments, args = (picam, self, 7200, stop_event))
            

        while True:
            try:
                time.sleep(2)
                if self.gt_buffer:
                    tc = self.gt_buffer.pop()
                    print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Running TC: {tc}")
                    # Log tc
                    with open(self.size_log_path, "a") as logfile:
                        entry = f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')} Running TC: {tc}"
                        logfile.write(entry + "\n")
                        logfile.flush()

                    # Manage Tasks
                    if tc is self.START_RECORDING_OPCODE:
                        if self.camera_busy:
                            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Camera busy, tc ignored")
                        else:
                            # Start recording video and monitoring its size
                            self.camera_busy = True
                            camera_thread.start()
                    elif tc is self.STOP_RECORDING_OPCODE:
                        if not self.camera_busy:
                            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Stop failed, camera not busy")
                        else:
                            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Stopping video recording")
                            stop_event.set()
                            self.camera_busy = False
                    elif tc is self.SELFIE_OPCODE:
                        if self.camera_busy:
                            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Selfie failed, camera busy")
                        else:
                            self.camera_busy = True
                            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Taking a picture")
                            time.sleep(3) # 3 second delay
                            camera_utils.take_selfie(picam)
                            self.camera_busy = False


            except UnicodeDecodeError:
                print("Received malformed data")
            except KeyboardInterrupt:
                print("Exiting...")
                break
            except Exception as e:
                print(e)



if __name__ == "__main__":
    print("Initializing Camera Manager")
    cam_manager = CameraManager()
    
    print("Camera Manager Ready, ROUTINE STARTED")
    cam_manager.start()
