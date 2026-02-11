import argparse
import os
import concurrent.futures

import requests
import tqdm

from ..report_runner import run_config, extract_stats_and_timing

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run configs remotely via coordination server")
    parser.add_argument("--thread-workers", type=int, default=max(1, (os.cpu_count() or 1) // 2), help="Number of worker threads")
    parser.add_argument("--api-host", type=str, required=True, help="API host URL, e.g. http://server:8000")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds for each policy run")
    args = parser.parse_args()

    api_host = args.api_host.rstrip("/")

    session = requests.Session()

    def worker(worker_id: int):
        while True:
            r = session.get(f"{api_host}/get-run", timeout=30)
            r.raise_for_status()
            run = r.json()
            run_id = run.get("run_id")

            _, _, result = run_config(0, run, timeout=args.timeout)
            stats, timing = extract_stats_and_timing(result)

            session.post(
                f"{api_host}/submit-results",
                json={"run_id": run_id, "stats": stats, "timing": timing},
            )

    total_done = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.thread_workers) as executor:
        futures = [executor.submit(worker, i) for i in range(args.thread_workers)]
        for fut in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Workers"):
            total_done += fut.result()


if __name__ == "__main__":
    main()