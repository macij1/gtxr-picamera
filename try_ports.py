import serial
import os

# List of possible serial ports
possible_ports = [
    "/dev/serial0",
    "/dev/serial1",
    "/dev/ttyAMA0",
    "/dev/ttyS0",
    "/dev/ttyS1",
    "/dev/ttyS2",
    "/dev/serial1",
    "/dev/ttyUSB0",
    "/dev/ttyUSB1",
    "/dev/ttyUSB2",
    "/dev/ttyACM0",
    "/dev/ttyACM1",
    "/dev/ttyACM2",
    "/dev/cu.usbmodem1101",
    "/dev/cu.usbmodem1201",
    "/dev/cu.usbmodem1301",
    "/dev/cu.usbmodem1401",
    "/dev/pts/1",
    "/dev/pts/2",
    "/dev/pts/3",
    "/dev/pts/4",
    "/dev/pts/5",
    "/dev/ttyGS0"
]

# Serial connection settings
baudrate = 115200  # Change if needed
timeout = 1        # Seconds

def try_ports():
    ser = None
    for port in possible_ports:
        try:
            if os.path.exists(port):
                ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
                print(f"Connected to serial port: {port}")
                ser.close()
                return port
        except Exception as e:
            # print(f"Failed to open {port}: {e}")
            continue
    else:
        return None
