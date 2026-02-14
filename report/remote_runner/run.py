import argparse
import os
import sys
import concurrent.futures

import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from report.report_runner import run_config, extract_stats_and_timing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
run_ids = set()

def main() -> None:
    parser = argparse.ArgumentParser(description="Run configs remotely via coordination server")
    parser.add_argument("--thread-workers", type=int, default=os.cpu_count(), help="Number of worker threads")
    parser.add_argument("--api-host", type=str, required=True, help="API host URL, e.g. http://server:8000")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds for each policy run")
    args = parser.parse_args()

    api_host = args.api_host.rstrip("/")

    session = requests.Session()

    def worker(worker_id: int):
        while True:
            r = session.get(f"{api_host}/get-run", timeout=30)
            if r.status_code == 404:
                break # all done
            r.raise_for_status()
            run = r.json()
            run_id = run.get("run_id")

            if run_id in run_ids:
                print(f"Worker {worker_id} received duplicate run_id {run_id}, skipping...")
                continue
            run_ids.add(run_id)

            run = {k: v for k, v in run.items() if v != ""}

            print(f"Worker {worker_id} starting run {run_id}")
            _, _, result = run_config(0, run, timeout=args.timeout)
            stats, timing = extract_stats_and_timing(result)

            session.post(
                f"{api_host}/submit-results",
                json={"run_id": run_id, "stats": stats, "timing": timing},
            )
            print(f"Worker {worker_id} completed run {run_id}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.thread_workers) as executor:
        futures = []
        print(f"Starting {args.thread_workers} worker threads...")

        for i in range(args.thread_workers):
            futures.append(executor.submit(worker, i))
        
        concurrent.futures.wait(futures)


if __name__ == "__main__":
    main()