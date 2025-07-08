import serial
import threading
from datetime import datetime, timedelta
import os
import time

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
    REPORT_SIZE_OPCODE = b'\x03'
    STOP_RECORDING = b'\x04'

    
    current_video_size = 0 
    camera_busy = False
    
    def __init__(self):
        self.gt_buffer = []
        self.serial_portname = "/dev/pts/4"
        timestamp_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        self.main_video_path = f"picam_runtime/"
        self.size_log_path = f"picam_runtime/{timestamp_str}-size_log.txt"
        if not os.path.exists("picam_runtime/"):
            os.makedirs("picam_runtime/")  # Create the directory if it doesn't exist
            
        self.gt_port = None
        open_port_tries = 12 # 1 min

        # Open serial port for UART communication with ADCS board
        for i in range(open_port_tries):
            try:
                portname = try_ports()
                if portname: 
                    portname = self.serial_portname
                    self.gt_port = gt_packet.GTPacket(self.serial_portname, 115200)
                    break
                else:
                    print(f"Error in serial port opening: All ports were unsuccessful")
                    continue
            except Exception as e:
                print(f"Error in serial port opening: {e}")
            print("Waiting 5 secs")
            time.sleep(5)

        # Fall back to emergency recording
        if self.gt_port == None:
            print("Emergency Recording Started: no serial ports found")
            self.gt_buffer.append(self.START_RECORDING_OPCODE)
        else:
            print("Manager initialized correctly")
    
    # Read telecommand 
    def gt_packet_reader(self):
        while True:
            print("Started packet reader")
            # Blocking serial read
            payload = self.gt_port.receive()
            tc = None
            if self.START_RECORDING_OPCODE in payload:
                tc =  self.START_RECORDING_OPCODE
            elif self.SELFIE_OPCODE in payload:
                tc = self.SELFIE_OPCODE
            elif self.REPORT_SIZE_OPCODE in payload:
                tc = self.REPORT_SIZE_OPCODE
            elif self.STOP_RECORDING in payload:
                tc = self.STOP_RECORDING
             # Do additional parsing if necessary
            print(f"Found TC: {tc} in serial read")
            if tc:
                self.gt_buffer.append(tc)

    # Sends the file size through the GT serial port
    # An 8-byte integer represents the file size in bytes
    def send_update(self, serial_line : str):
        try:
            size_bytes = self.current_video_size.to_bytes(8, byteorder='big')
            self.gt_port.send(size_bytes)
        except Exception as e:
            print("Error: Send unsucessful of current video size")
    
    # Continuously monitors the size of a file and saves timestamped logs to a file
    # Current size is saved for fats return if requested by a command
    def monitor_size(self):
        while True:
            try:
                time.sleep(30)
                if os.path.exists(self.size_log_path):
                    self.current_video_size = os.path.getsize(self.size_log_path) # size is saved in MB
                    # Log size
                    with open(self.size_log_path, "a") as logfile:
                        size_str = f"Size: {float(self.current_video_size):.1f} bytes"
                        timestamp = datetime.now().isoformat()
                        entry = f"{timestamp} - Video size:{size_str}"
                        logfile.write(entry + "\n")
                        logfile.flush()
            except Exception as e:
                print("Error in monitor size thread")
                print(e)

    def start(self):
        picam = camera_utils.init_camera()
        camera_thread = threading.Thread(target=camera_utils.record_video_segments, args = (picam, self))
        monitor_size_thread = threading.Thread(target=self.monitor_size)
        gt_packet_reader = threading.Thread(target=self.gt_packet_reader)
        
        if self.gt_port:
            gt_packet_reader.start()
            
        # Mechanism to fall back to emergency recording if serial port is silent
        routine_started = False
        routine_start_time = datetime.now()
        while True:
            try:

                if not routine_start_time and datetime.now() - routine_started == timedelta(minutes=2):
                    self.gt_buffer.append(self.START_RECORDING_OPCODE)

                if self.gt_buffer:
                    routine_started = True
                    tc = self.gt_buffer.pop()
                    print(f"Running TC: {tc}")
                    # Log
                    with open(self.size_log_path, "a") as logfile:
                        timestamp = datetime.now().isoformat()
                        entry = f"Running TC: {tc}"
                        logfile.write(entry + "\n")
                        logfile.flush()

                    # Manage Tasks
                    if tc is self.START_RECORDING_OPCODE:
                        if self.camera_busy:
                            print("Camera busy, tc ignored")
                        else:
                            # Start recording video and monitoring its size
                            print("debug")
                            self.camera_busy = True
                            camera_thread.start()
                            monitor_size_thread.start()
                    elif tc is self.REPORT_SIZE_OPCODE:
                        print(f"Reporting video file size:{self.current_video_size}")
                        # Acquire cam data and use send_update()
                        self.send_update(str(self.current_video_size))
                        

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
