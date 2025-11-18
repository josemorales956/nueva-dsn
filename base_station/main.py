# base_station/main.py
# Author: Jose Morales
# Initial version of base station main code to receive sensor packets
import socket, json, traceback
from common.payloads import SensorPacket
from base_station.db_sqlite import init_db, insert_reading


HOST = "127.0.0.1"   # local for now; later bind to 0.0.0.0 on Jetson
PORT = 5005
ACK_PORT = 5006      # we'll reply to the sender's source port, but define anyway

def main():
    print(f"[BASE] starting on {HOST}:{PORT}")
    init_db() #initialize database

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST, PORT))
    # waits and listens for incoming packets
    while True:
        buf, addr = sock.recvfrom(8192)
        try:
            pkt = SensorPacket.from_bytes(buf)  # Decode the raw bytes into a structured SensorPacket object.
            insert_reading(pkt.node_id, pkt.timestamp, pkt.seq, json.dumps(pkt.data))  # Stores node_id, timestamp, sequence number, and sensor data.
            print(f"[BASE] #{pkt.seq} from {pkt.node_id}  data={pkt.data}")
            # send ACK: {"ack": seq, "node": node_id}
            ack = json.dumps({"ack": pkt.seq, "node": pkt.node_id}).encode("utf-8") 
            sock.sendto(ack, addr)
        except Exception as e:
            print(f"[BASE] drop from {addr}: {e}") # If a packet is malformed or fails to parse, print the error
            traceback.print_exc()

if __name__ == "__main__":
    main()
