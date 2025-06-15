import serial
import threading
import datetime
import os
import time

from camera_utils import record_video

"""
Pseudo:
Constantly listen for commands from the UART port
Upon receival, parse and immediately complete the task
"""

current_video_size = 0

def parse_serial(serial_line : str):
    # TODO
    return "record"

def send_update(serial_line : str):
    while True:
        try:
            msg = input(serial_line)
            ser.write((msg + '\n').encode('utf-8'))
        except:
            break

# Continiously monitors the size of a file and saves timestamped logs to a file
# Current size is saved for fats return if requested by a command
def monitor_size(path):
    while True:
        time.sleep(10)
        if os.path.exists(path):
            current_video_size = float(os.path.getsize(path))
            with open("~/logs/video_size.txt", "a") as logfile:
                size_str = f"Size: {current_video_size / 1024:.1f} KB"
                timestamp = datetime.now().isoformat()
                entry = f"{timestamp} - {size_str}"
                logfile.write(entry + "\n")
                logfile.flush()

if __name__ == "__main__":
    main_video_path = "~/videos/"+ str(datetime.now()) + ".mp4"

    camera_thread = threading.thread(record_video, args=(main_video_path))
    monitor_size_thread = threading.thread(record_video, args=(main_video_path))

    # Open serial port for UART communication with ADCS board
    with serial.Serial('/dev/cu.usbmodem1201', 115200, timeout=1) as ser, open("~/logs/serial_log.txt", "a") as logfile:
        while True:
            try:
                # x = ser.read()          # read one byte
                # s = ser.read(10)        # read up to ten bytes (timeout)
                # line = ser.readline()   # read a '\n' terminated line
                line = ser.readline().decode('utf-8').strip() # TODO
                if line:
                    # Log all commands
                    timestamp = datetime.now().isoformat()
                    entry = f"{timestamp} - {line}"
                    logfile.write(entry + "\n")
                    logfile.flush()
                    command = parse_serial(line)

                    # Manage Tasks
                    if command is "start":
                        # Start recording video and monitoring the 
                        camera_thread.start()
                        monitor_size_thread.start()
                    elif command is "report":
                        # Acquire cam data and use send_update()
                        send_update(str(current_video_size))
                        

            except UnicodeDecodeError:
                print("Received malformed data")
            except KeyboardInterrupt:
                print("Exiting...")
                break
            
    