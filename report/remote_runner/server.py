from __future__ import annotations

import os
import random
import sqlite3
import threading
import time
import uuid
from typing import Any, List

from flask import Flask, jsonify, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH") or os.path.join(BASE_DIR, "db.sqlite3")

CONFIG_COLUMNS: List[str] = [
    "id",
    "admission_threshold",
    "cache_size",
    "cms_delta",
    "cms_epsilon",
    "default_latency",
    "latency_utility",
    "model",
    "policy",
    "protected_fraction",
    "request_count",
    "size_utility",
    "tau",
    "tiny_window_size",
    "window_size",
    "expected_count",
]

app = Flask(__name__)
_db_lock = threading.Lock()

def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = _connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS configs (
            id TEXT PRIMARY KEY,
            """ + ",\n".join([f"{col} TEXT" for col in CONFIG_COLUMNS if col != "id"]) + """
        );

        CREATE TABLE IF NOT EXISTS runs (
            run_id TEXT PRIMARY KEY,
            config_id TEXT NOT NULL,
            created_at REAL NOT NULL,
            finished_at REAL,
            stats_json TEXT,
            timing_json TEXT,
            FOREIGN KEY(config_id) REFERENCES configs(id)
        );

        CREATE INDEX IF NOT EXISTS idx_runs_config_id ON runs(config_id);
        """
    )
    conn.commit()
    conn.close()


def _json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)


@app.get("/get-run")
def get_run():
    with _db_lock:
        conn = _connect()

        rows = conn.execute(
            """
            SELECT c.*, COALESCE(r.completed, 0) AS completed
            FROM configs c
            LEFT JOIN (
                SELECT config_id, COUNT(*) AS completed
                FROM runs
                WHERE finished_at IS NOT NULL
                GROUP BY config_id
            ) r ON r.config_id = c.id
            WHERE COALESCE(r.completed, 0) < c.expected_count
            """
        ).fetchall()

        if not rows:
            conn.close()
            return ("", 204)

        min_completed = min(int(r["completed"]) for r in rows)
        candidates = [r for r in rows if int(r["completed"]) == min_completed]
        chosen = random.choice(candidates)

        run_id = str(uuid.uuid4())
        conn.execute(
            "INSERT INTO runs(run_id, config_id, created_at) VALUES(?,?,?)",
            (run_id, chosen["id"], time.time()),
        )
        conn.commit()
        conn.close()

    run = {k: chosen[k] for k in chosen.keys() if k != "completed"}
    run["run_id"] = run_id
    return jsonify(run)


@app.post("/submit-results")
def submit_results():
    payload = request.get_json(force=True, silent=False) or {}
    run_id = payload.get("run_id")
    stats = payload.get("stats")
    timing = payload.get("timing")

    conn = _connect()
    conn.execute(
        "UPDATE runs SET finished_at=?, stats_json=?, timing_json=? WHERE run_id=?",
        (time.time(), _json_dumps(stats), _json_dumps(timing), run_id),
    )
    conn.commit()
    conn.close()

    return jsonify({"ok": True})


def main() -> None:
    import argparse

    _init_db()

    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    app.run(host=args.host, port=args.port, threaded=True)

if __name__ == "__main__":
    main()
