import socket
import time
from common.payloads import SensorPacket

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    print("[SENSOR] Sending data to base station...")
    while True:
        pkt = SensorPacket("sensor_1", time.time(), {"temp": 25.3}, seq)
        sock.sendto(pkt.to_json().encode(), (SERVER_IP, SERVER_PORT))
        seq += 1
        time.sleep(2)  # send every 2 seconds

if __name__ == "__main__":
    main()
