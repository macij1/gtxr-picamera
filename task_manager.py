import serial
import threading
import datetime
import os
import time

import gt_packet
from camera_utils import record_video

"""
Pseudo:
Constantly listen for commands from the UART port
Upon receival, parse and immediately complete the task
"""
class CameraManager():
    START_RECORDING_OPCODE = b"1"
    SELFIE_OPCODE = b"2" 
    REPORT_SIZE_OPCODE = b"3"
    STOP_RECORDING = b"4"
    current_video_size_mbs = 0 
    
    def __init__(self):
        self.gt_buffer = []
        self.serial_portname = "/dev/cu.usbmodem1201"
        self.main_video_path = "~/videos/"+ str(datetime.now()) + ".mp4"
        self.log_path = "~/logs/"+ str(datetime.now()) + "serial_log.txt"

        # Open serial port for UART communication with ADCS board
        try:
            self.gt_port = gt_packet.GTPacket(self.serial_portname, 115200)
        except Exception as e:
            print(f"Error: Failed to open Serial Port:{e}")
    
    # Read telecommand 
    def gt_packet_reader(self, payload : str):
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
        self.gt_buffer.append(tc)

    # Sends the file size through the GT serial port
    # An 8-byte integer represents the file size in bytes
    def send_update(self, serial_line : str):
        size_bytes = self.current_video_size_mb.to_bytes(8, byteorder='big')
        self.gt_port.send(self, size_bytes)
    
    # Continiously monitors the size of a file and saves timestamped logs to a file
    # Current size is saved for fats return if requested by a command
    def monitor_size(self, path):
        while True:
            time.sleep(10)
            if os.path.exists(path):
                self.current_video_size_mb = os.path.getsize(path) # size is saved in MB
                # Log sizze
                with open(self.log_path) as logfile:
                    size_str = f"Size: {float(self.current_video_size_mb)/(1024*1024):.1f} MB"
                    timestamp = datetime.now().isoformat()
                    entry = f"{timestamp} - Video size:{size_str}"
                    logfile.write(entry + "\n")
                    logfile.flush()

    def start(self):
        camera_thread = threading.thread(record_video, args=(self.main_video_path))
        monitor_size_thread = threading.thread(monitor_size, args=(self.main_video_path))
        gt_packet_reader = threading.thead(self.read_gt_packets, args=())

        gt_packet_reader.start()

        while True:
            try:
                tc = self.gt_buffer.pop()
                if tc:
                    # Log
                    with open(self.log_path) as logfile:
                        timestamp = datetime.now().isoformat()
                        entry = f"Running TC: {tc}"
                        logfile.write(entry + "\n")
                        logfile.flush()

                    # Manage Tasks
                    if tc is self.START_RECORDING_OPCODE:
                        # Start recording video and monitoring the 
                        camera_thread.start()
                        monitor_size_thread.start()
                    elif tc is self.REPORT_SIZE_OPCODE:
                        # Acquire cam data and use send_update()
                        self.send_update(str(self.current_video_size_mb))
                        

            except UnicodeDecodeError:
                print("Received malformed data")
            except KeyboardInterrupt:
                print("Exiting...")
                break
   
    



if __name__ == "__main__":
    cam_manager = CameraManager()
    cam_manager.start()