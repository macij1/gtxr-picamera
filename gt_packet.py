import serial
import struct
import crcmod
import time

# Packet structure:
# <header byte 1><header byte 2><payload length><data/opcode><crc byte 1><crc byte 2>
HEADER = bytes([0x47, 0x54])  # 'GT'
CRC_FUNC = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0) # CRC-16-CCITT-FALSE

class GTPacket:
    def __init__(self, port, baudrate=115200, timeout=None):
        self.ser = serial.Serial(port, baudrate, timeout=timeout)

    def build_packet(self, data: bytes) -> bytes:
        length = len(data)
        crc = CRC_FUNC(data)
        crc_bytes = struct.pack('>H', crc)
        return HEADER + bytes([length]) + data + crc_bytes

    def send(self, data: bytes):
        packet = self.build_packet(data)
        self.ser.write(packet)
        print(f"Sent: {packet.hex()}")

    def receive(self):
        while True:
            print("it1")
            byte = self.ser.read(1)
            if byte == b'\x47':  # look for first header byte
                print("byte1")
                second = self.ser.read(1)
                if second == b'\x54':
                    print("byte2")
                    length = self.ser.read(1)
                    if not length:
                        print("not length")
                        continue
                    length_val = length[0]
                    payload = self.ser.read(length_val)
                    crc = self.ser.read(2)
                    if len(payload) != length_val or len(crc) != 2:
                        print("Invalid packet size")
                        continue

                    calc_crc = CRC_FUNC(payload)
                    recv_crc = struct.unpack('>H', crc)[0]
                    if calc_crc == recv_crc:
                        print(f"Received valid packet: {payload.hex()}")
                        return payload
                    else:
                        print(f"CRC mismatch! Expected {calc_crc:04X}, got {recv_crc:04X}")
                else:
                    continue
            print("it")

    def close(self):
        self.ser.close()

if __name__ == "__main__":
    from mock_serial import MockSerial

    device = MockSerial()
    device.open()

    gt = GTPacket(port="/dev/pts/3")

    try:
        # Prepare a mock serial device
        device.stub(receive_bytes=gt.build_packet(b'\x01\x02'), send_bytes=gt.build_packet(b'\x01'))  # Mock packet: GT + length 2 + data 01+  CRC

        # Send command with opcode/data
        print("Sending:")
        gt.send(b'\x03')
        time.sleep(5)

        # Wait for a response
        # response = gt.receive()
        # print(f"Parsed Response: {response}")
    except Exception as e:
        print(e)
    finally:
        
        gt.close()
