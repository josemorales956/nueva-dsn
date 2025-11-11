import socket
from common.payloads import SensorPacket

HOST = "127.0.0.1"
PORT = 5005

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    print(f"[BASE] Listening on {HOST}:{PORT}...")
    while True:
        data, addr = sock.recvfrom(4096)
        pkt = SensorPacket.from_json(data.decode())
        print(f"[BASE] Received from {pkt.node_id}: {pkt.data} at {pkt.timestamp}")

if __name__ == "__main__":
    main()
