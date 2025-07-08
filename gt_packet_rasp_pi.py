GT_HEADER_1 = 0x47  # 'G'
GT_HEADER_2 = 0x54  # 'T'
GT_MAX_PAYLOAD_SIZE = 255

WAIT_HEADER_1 = 0
WAIT_HEADER_2 = 1
WAIT_LENGTH = 2
WAIT_PAYLOAD = 3
WAIT_CRC_1 = 4
WAIT_CRC_2 = 5


def crc16_ccitt_false(data: bytes) -> int:
    """CRC-16-CCITT-FALSE implementation"""
    crc = 0xFFFF
    for byte in data:
        crc ^= (byte << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF  # keep crc 16-bit
    return crc


class GTPacketParser:
    def __init__(self):
        self.state = WAIT_HEADER_1
        self.payload_len = 0
        self.payload_pos = 0
        self.payload = bytearray()
        self.crc_bytes = bytearray(2)

    def reset(self):
        self.state = WAIT_HEADER_1
        self.payload_len = 0
        self.payload_pos = 0
        self.payload = bytearray()
        self.crc_bytes = bytearray(2)

    def read_byte(self, byte: int) -> (bool, bytes):
        """Feed one byte at a time. Returns (True, payload) on success."""
        if self.state == WAIT_HEADER_1:
            if byte == GT_HEADER_1:
                self.state = WAIT_HEADER_2

        elif self.state == WAIT_HEADER_2:
            if byte == GT_HEADER_2:
                self.state = WAIT_LENGTH
            else:
                self.state = WAIT_HEADER_1

        elif self.state == WAIT_LENGTH:
            if byte > GT_MAX_PAYLOAD_SIZE:
                self.reset()
            else:
                self.payload_len = byte
                self.payload = bytearray()
                self.payload_pos = 0
                self.state = WAIT_PAYLOAD

        elif self.state == WAIT_PAYLOAD:
            self.payload.append(byte)
            self.payload_pos += 1
            if self.payload_pos >= self.payload_len:
                self.state = WAIT_CRC_1

        elif self.state == WAIT_CRC_1:
            self.crc_bytes[0] = byte
            self.state = WAIT_CRC_2

        elif self.state == WAIT_CRC_2:
            self.crc_bytes[1] = byte
            expected_crc = crc16_ccitt_false(self.payload)
            received_crc = (self.crc_bytes[0] << 8) | self.crc_bytes[1]

            if expected_crc == received_crc:
                result = bytes(self.payload)
                self.reset()
                return True, result
            else:
                # CRC mismatch
                self.reset()

        return False, b''


def build_gt_packet(data: bytes) -> bytes:
    """Construct a GT packet from a data payload"""
    length = len(data)
    if length == 0 or length > GT_MAX_PAYLOAD_SIZE:
        raise ValueError("Invalid payload length")

    packet = bytearray()
    packet.append(GT_HEADER_1)
    packet.append(GT_HEADER_2)
    packet.append(length)
    packet.extend(data)

    crc = crc16_ccitt_false(data)
    packet.append((crc >> 8) & 0xFF)  # CRC high byte
    packet.append(crc & 0xFF)         # CRC low byte

    return bytes(packet)


if __name__ == "__main__":
    # Example driver code
    parser = GTPacketParser()

    # Example payload
    payload = b"Hello GT Packet!"
    print(f"Original payload: {payload}")

    # Build packet
    packet = build_gt_packet(payload)
    print(f"Built packet (hex): {packet.hex()}")

    # Simulate receiving the packet byte by byte
    print("\nFeeding bytes to parser...")
    for byte in packet:
        success, received_payload = parser.read_byte(byte)
        if success:
            print(f"Received full payload: {received_payload}")
            print(f"Payload matches original? {received_payload == payload}")