import sqlite3, pathlib, time
DB_PATH = pathlib.Path(file).with_name("readings.sqlite").as_posix()

DDL = """
CREATE TABLE IF NOT EXISTS readings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  node_id TEXT NOT NULL,
  ts REAL NOT NULL,
  seq INTEGER NOT NULL,
  data_json TEXT NOT NULL,
  received_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_readings_node_ts ON readings(node_id, ts);
"""

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL;")
    return conn

def init_db():
    with get_conn() as c:
        for stmt in DDL.strip().split(";"):
            s = stmt.strip()
            if s:
                c.execute(s)

def insert_reading(node_id: str, ts: float, seq: int, data_json: str):
    with get_conn() as c:
        c.execute(
            "INSERT INTO readings(node_id, ts, seq, data_json, received_at) VALUES(?,?,?,?,?)",
            (node_id, ts, seq, data_json, time.time()),
        )