import socket, time, pathlib, json, argparse
from common.payloads import make_fake_packet

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005
ACK_TIMEOUT_S = 1.0
RETRY_LIMIT = 3
QUEUE_FILE = pathlib.Path(__file__).with_name("outbox.jsonl")

def send_packet(sock, pkt_bytes, addr):
    sock.sendto(pkt_bytes, addr)
    sock.settimeout(ACK_TIMEOUT_S)
    try:
        ack, _ = sock.recvfrom(2048)
        obj = json.loads(ack.decode("utf-8"))
        return obj.get("ack")
    except Exception:
        return None

def enqueue(pkt_bytes):
    with QUEUE_FILE.open("ab") as f:
        f.write(pkt_bytes + b"\n")

def flush_queue(sock, addr):
    if not QUEUE_FILE.exists():
        return
    lines = QUEUE_FILE.read_bytes().splitlines()
    if not lines:
        return
    remaining = []
    for line in lines:
        acked = send_packet(sock, line, addr)
        if acked is None:
            remaining.append(line)
    # rewrite remaining
    with QUEUE_FILE.open("wb") as f:
        for r in remaining:
            f.write(r + b"\n")


def run(node_id: str, period: float):
    addr = (SERVER_IP, SERVER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq = 0
    print(f"[{node_id}] sending to {SERVER_IP}:{SERVER_PORT} every {period}s")
    while True:
        # try to flush any buffered packets first
        flush_queue(sock, addr)

        pkt = make_fake_packet(node_id, seq)
        pkt_bytes = pkt.to_bytes()

        # try with retries; if still no ACK, enqueue
        acked = None
        for _ in range(RETRY_LIMIT):
            acked = send_packet(sock, pkt_bytes, addr)
            if acked == seq:
                break
            time.sleep(0.1)

        if acked != seq:
            print(f"[{node_id}] no ACK for seq {seq} → buffering")
            enqueue(pkt_bytes)
        else:
            print(f"[{node_id}] sent seq {seq}")

        seq += 1
        time.sleep(period)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--node", required=True, help="node id (e.g., sensor_1)")
    ap.add_argument("--period", type=float, default=2.0, help="send period seconds")
    args = ap.parse_args()
    run(args.node, args.period)