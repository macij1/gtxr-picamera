import threading
from datetime import datetime, timedelta
import os
import time
from glob import glob
import gt_packet
import camera_utils
from try_ports import try_ports

"""
Listens for telecommands from the UART port
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
        self.gt_buffer_max_size = 20 # makes it a circular buffer
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

                # Circular buffer: if full, pop oldest
                if len(self.gt_buffer) >= self.gt_buffer_max_size:
                    print(f"Warnning, gt circular buffer filled up with max size {self.gt_buffer_max_size}")
                    self.gt_buffer.pop()
                self.gt_buffer.append(tc)

    # # Sends the file size to the GT serial port
    # # 8-byte integers represent the state of the camera, the number of video segments, and the latest segment size
    # def send_update(self):
    #     print("\nStarting telemetry thread")
    #     while True:
    #         try:
    #             time.sleep(30)
    #             print("Forming telemetry gt packet")
    #             busy_byte = (1 if self.camera_busy else 0).to_bytes(4, byteorder='big', signed=True)
    #             video_counter_bytes = self.video_counter.to_bytes(4, byteorder='big', signed=True)
    #             current_video_size = self.current_video_size.to_bytes(4, byteorder='big', signed=True)
    #             payload = self.TELEMETRY_OPCODE + busy_byte + video_counter_bytes + current_video_size 
    #             self.gt_port.send(payload)
    #         except Exception as e:
    #             print(f"Error in telemetry thread")
    #             print(e)
        
    # Continuously monitors the size of a file and saves timestamped logs to a file
    def monitor_size(self):
        print("\nStarting monitor thread")
        while True:
            try:
                time.sleep(5)
                print("Monitoring size")
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
                    
                # Send telemetry packet
                busy_byte = (1 if self.camera_busy else 0).to_bytes(4, byteorder='big', signed=True)
                video_counter_bytes = self.video_counter.to_bytes(4, byteorder='big', signed=True)
                current_video_size = self.current_video_size.to_bytes(4, byteorder='big', signed=True)
                payload = self.TELEMETRY_OPCODE + busy_byte + video_counter_bytes + current_video_size 
                self.gt_port.send(payload)
            except Exception as e:
                print("Error in monitor size thread")
                print(e)

    def start(self):
        picam = camera_utils.init_camera()
        stop_event = threading.Event()
        camera_thread = threading.Thread(target=camera_utils.record_h264_segments, args = (picam, self, 7200, stop_event))
        monitor_size_thread = threading.Thread(target=self.monitor_size)
        gt_packet_reader = threading.Thread(target=self.gt_packet_reader)

        if self.gt_port:
            gt_packet_reader.start()
            

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
                            monitor_size_thread.start()
                    elif tc is self.STOP_RECORDING_OPCODE:
                        if not self.camera_busy:
                            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Stop failed, camera not busy")
                        else:
                            print(f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}: Stopping video recording")
                            stop_event.set()
                            self.camera_busy = False
                            camera_thread.join()
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
