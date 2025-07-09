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
        self.main_video_path = f"videos/"
        timestamp = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
        self.size_log_path = f"logs/{timestamp}-size_log.txt"
        self.current_video_size = 0 
        self.video_counter = 0
        self.camera_busy = False

        if not os.path.exists("videos/"):
            os.makedirs("videos/")
        if not os.path.exists("logs/"):
            os.makedirs("logs/")
        if not os.path.exists("photos/"):
            os.makedirs("photos/")

        self.gt_port = None

        # Open serial port for UART communication with ADCS board
        while True:
            try:
                portname = try_ports()
                if portname: 
                    self.serial_portname = portname
                    self.gt_port = gt_packet.GTPacket(self.serial_portname, 115200)
                    break
                else:
                    print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Error in serial port opening: All ports were unsuccessful")
                    time.sleep(5)
                    continue
            except Exception as e:
                print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Error in serial port opening: {e}")
            print("Waiting 5 secs")
            time.sleep(5)

    
    # Read telecommand 
    def gt_packet_reader(self):
        while True:
            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Started packet reader")
            # Blocking serial read
            payload = self.gt_port.receive()
            tc = None
            if self.START_RECORDING_OPCODE in payload:
                tc =  self.START_RECORDING_OPCODE
            elif self.SELFIE_OPCODE in payload:
                tc = self.SELFIE_OPCODE
            elif self.STOP_RECORDING_OPCODE in payload:
                tc = self.STOP_RECORDING_OPCODE
            else:
                print("Error, found no tc in payload")
            if tc:
                print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Found TC: {tc} in payload")
                self.gt_buffer.append(tc)

    # Sends the file size to the GT serial port
    # 8-byte integers represent the state of the camera, the number of video segments, and the latest segment size
    def send_update(self, serial_line : str):
        while True:
            try:
                time.sleep(5)
                busy_byte = (1 if self.camera_busy else 0).to_bytes(4, byteorder='big', signed=True)
                video_counter_bytes = self.video_counter.to_bytes(4, byteorder='big', signed=True)
                current_video_size = self.current_video_size.to_bytes(4, byteorder='big', signed=True)
                payload = self.TELEMETRY_OPCODE + busy_byte + video_counter_bytes + current_video_size 
                self.gt_port.send(payload)
            except Exception as e:
                print(f"Error: Send unsuccessful of telemetry reporting")
        
    # Continuously monitors the size of a file and saves timestamped logs to a file
    def monitor_size(self):
        while True:
            try:
                time.sleep(5)
                # Get latest segment size
                files = glob(f"{self.main_video_path}video%03d.mp4")
                if not files:
                    return 0
                latest_file = max(files, key=os.path.getctime)
                self.current_video_size =  os.path.getsize(latest_file)
                # Log size
                with open(self.size_log_path, "a") as logfile:
                    size_str = f"Latest segment size: {float(self.current_video_size):.1f} bytes"
                    timestamp = datetime.now().isoformat()
                    entry = f"{timestamp} - Video size:{size_str}"
                    logfile.write(entry + "\n")
                    logfile.flush()
            except Exception as e:
                print("Error in monitor size thread")
                print(e)

    def start(self):
        picam = camera_utils.init_camera()
        stop_event = threading.Event()
        camera_thread = threading.Thread(target=camera_utils.record_and_pipe_video, args = (picam, self, 7200, stop_event))
        monitor_size_thread = threading.Thread(target=self.monitor_size)
        gt_packet_reader = threading.Thread(target=self.gt_packet_reader)

        if self.gt_port:
            gt_packet_reader.start()

        while True:
            try:
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
                            monitor_size_thread.start()
                    elif tc is self.STOP_RECORDING_OPCODE:
                        print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Stopping video recording")
                        stop_event.set()
                        self.camera_busy = False
                    elif tc is self.SELFIE_OPCODE:
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
