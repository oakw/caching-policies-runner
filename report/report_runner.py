import argparse
import json
import os
import subprocess
import tqdm
import re
import concurrent.futures
import threading
import random

TIME_TEMPLATE = "<user>%U</user><system>%S</system><elapsed>%e</elapsed><max-rss>%M</max-rss><exit-code>%x</exit-code><cpu>%P</cpu>"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_config(i, run, timeout=3600) -> tuple[int, dict, subprocess.CompletedProcess]:
    result = subprocess.run([
        "/usr/bin/time", "-f", TIME_TEMPLATE,
        'timeout', str(timeout),
        "python", f"{BASE_DIR}/../policy_runner.py",
        "--policy", run['policy'],
        "--model", run['model'],
        "--request-count", str(int(run.get('request_count', ''))),
        "--window-size", str(int(run.get('window_size', 100))),
        "--cache-size", str(int(run.get('cache_size', ''))),
        "--admission-threshold", str(int(run.get('admission_threshold', 2))),
        "--cms-epsilon", str(float(run.get('cms_epsilon', 0.1))),
        "--cms-delta", str(float(run.get('cms_delta', 0.1))),
        "--cms-width", str(int(run.get('cms_width', 100))),
        "--cms-depth", str(int(run.get('cms_depth', 10))),
        "--size-utility", str(run.get('size_utility', 'freq_over_size')),
        "--protected-fraction", str(float(run.get('protected_fraction', 0.5))),
        "--tiny-window-size", str(int(run.get('tiny_window_size', 100000))),
        "--latency-utility", str(run.get('latency_utility', 'freq_times_size_times_latency')),
        "--default-latency", str(float(run.get('default_latency', 1.0))),
        "--victim-sample-proportion", str(float(run.get('victim_sample_proportion', 1.0))),
    ], text=True, capture_output=True)

    if result.returncode != 0:
        print(f"ERROR: Run {run} failed with return code {result.returncode}")
        print(f"stdout: {result.stdout}")
        print(f"stderr: {result.stderr}")
        
    return (i, run, result)

def extract_stats_and_timing(result):
    stats = {
        'hits': 0,
        'misses': 0,
        'accesses': 0,
        'current_size': 0,
        'max_size': 0,
        'hit_object_size_sum': 0,
        'hit_response_time_sum': 0.0,
        'object_size_sum': 0,
        'response_time_sum': 0.0,
    }    
    timing = {}
    
    for line in (result.stderr + result.stdout).split('\n'):
        if 'Stats:' in line:
            # Extract hits, misses, accesses, size
            hits_match = re.search(r'hits=(\d+)', line)
            misses_match = re.search(r'misses=(\d+)', line)
            accesses_match = re.search(r'accesses=(\d+)', line)
            size_match = re.search(r'size=(\d+)/(\d+)', line)
            hit_object_size_sum_match = re.search(r'hit_object_size_sum=(\d+)', line)
            hit_response_time_sum_match = re.search(r'hit_response_time_sum=([\d.]+)', line)
            object_size_sum_match = re.search(r'total_object_size_sum=(\d+)', line)
            response_time_sum_match = re.search(r'total_response_time_sum=([\d.]+)', line)

            if hits_match:
                stats['hits'] = int(hits_match.group(1))
            if misses_match:
                stats['misses'] = int(misses_match.group(1))
            if accesses_match:
                stats['accesses'] = int(accesses_match.group(1))
            if size_match:
                stats['current_size'] = int(size_match.group(1))
                stats['max_size'] = int(size_match.group(2))
            if hit_object_size_sum_match:
                stats['hit_object_size_sum'] = int(hit_object_size_sum_match.group(1))
            if hit_response_time_sum_match:
                stats['hit_response_time_sum'] = float(hit_response_time_sum_match.group(1))
            if object_size_sum_match:
                stats['object_size_sum'] = int(object_size_sum_match.group(1))
            if response_time_sum_match:
                stats['response_time_sum'] = float(response_time_sum_match.group(1))

    for line in result.stderr.split('\n'):
        if '<user>' in line:
            user_match = re.search(r'<user>([\d.]+)</user>', line)
            system_match = re.search(r'<system>([\d.]+)</system>', line)
            elapsed_match = re.search(r'<elapsed>([^<]+)</elapsed>', line)
            max_rss_match = re.search(r'<max-rss>(\d+)</max-rss>', line)
            exit_code_match = re.search(r'<exit-code>(\d+)</exit-code>', line)
            cpu_match = re.search(r'<cpu>([^<]+)</cpu>', line)

            if user_match:
                timing['user_time'] = float(user_match.group(1))
            if system_match:
                timing['system_time'] = float(system_match.group(1))
            if elapsed_match:
                timing['elapsed_time'] = float(elapsed_match.group(1))
            if max_rss_match:
                timing['max_rss'] = int(max_rss_match.group(1))
            if exit_code_match:
                timing['exit_code'] = int(exit_code_match.group(1))
            if cpu_match:
                timing['cpu_percent'] = cpu_match.group(1).rstrip('%')
            break

    return stats, timing

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run policies defined in config.json and generate a report")
    parser.add_argument("--config-file", type=str, default=os.path.join(BASE_DIR, 'config.json'), help="Path to configuration JSON file")
    parser.add_argument("--run-repeats", type=int, default=1, help="Number of times to repeat each configuration for averaging")
    parser.add_argument("--thread-workers", type=int, default=max(1, (os.cpu_count() - 2)), help="Number of worker threads to use for running configurations in parallel")
    parser.add_argument("--emit-file", type=str, default=False, help="File to emit results to instead of stdout")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout in seconds for each policy run")
    args = parser.parse_args()

    CONFIG_FILE = args.config_file
    RUN_REPEATS = args.run_repeats
    THREAD_COUNT = args.thread_workers
    EMIT_FILE = args.emit_file
    TIMEOUT = args.timeout

    semaphore = threading.Semaphore(THREAD_COUNT)
        
    all_results = []
    with open (CONFIG_FILE, 'r') as file:
        config = json.load(file)
        config = random.sample(config, len(config))
        config = config * RUN_REPEATS

        with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
            futures = {executor.submit(run_config, i, run, TIMEOUT): (i, run) for i, run in enumerate(config)}

            for fut in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Running configurations"):
                i, run, result = fut.result()

                stats, timing = extract_stats_and_timing(result)

                if len(timing) == 0:
                    print(f"ERROR: Run {run} failed to produce timing info.")
                    print(f"stdout: {result.stdout}")
                    print(f"stderr: {result.stderr}")
                    exit(1)

                with semaphore:
                    if EMIT_FILE:
                        with open(EMIT_FILE, "a") as f:
                            f.write(json.dumps(dict(id=run.get('id', None), run=run, stats=stats, timing=timing), indent=2))

                all_results.append(dict(
                    run=run,
                    stats=stats,
                    timing=timing
                ))

    # Group results by configuration
    def group_key(run: dict):
        items = []
        for k in sorted(run.keys()):
            if k == "request_count":
                continue
            items.append((k, run[k]))
        return tuple(items)


    def group_label_for_table(run: dict) -> dict:
        result = {"policy": run.get("policy")}
        for key in sorted(run.keys()):
            if key != "policy" and key != "request_count":
                result[key] = run.get(key)
        return result

    def additional_attributes_for_run(run: dict) -> dict:
        result = {}
        for key in sorted(run.keys()):
            if key not in ["policy", "request_count", "model", "cache_size"]:
                result[key] = run.get(key)
        return result

    grouped_results = {}
    for result in all_results:
        key = group_key(result["run"])
        grouped_results.setdefault(key, []).append(result)

    # Calculate averages for each group
    averaged_results = []
    for key, results in grouped_results.items():
        run0 = results[0]["run"]

        avg_stats = {
            'object_size_sum': f"{results[0]['stats'].get('object_size_sum', 0):.2g}",
            'response_time_sum': f"{results[0]['stats'].get('response_time_sum', 0):.2g}"
        }

        for stat in ['hits', 'misses', 'accesses', 'current_size', 'hit_object_size_sum', 'hit_response_time_sum']:
            values = [r['stats'][stat] for r in results]
            avg_value = sum(values) / len(values)
            if not all(val == values[0] for val in values):
                # Indicate that there was variance with an asterisk
                avg_stats[stat] = f"{avg_value:.1f}*"
            else:
                avg_stats[stat] = f"{avg_value:.1f}"

        avg_timing = {
            'user_time': sum(r['timing']['user_time'] for r in results) / len(results),
            'system_time': sum(r['timing']['system_time'] for r in results) / len(results),
            'elapsed_time': sum(r['timing']['elapsed_time'] for r in results) / len(results),
            'max_rss': sum(r['timing']['max_rss'] for r in results) / len(results),
            'exit_code': results[0]['timing']['exit_code']
        }

        hits = float(avg_stats['hits'].rstrip('*'))
        accesses = float(avg_stats['accesses'].rstrip('*'))
        hit_response_time_sum = float(avg_stats['hit_response_time_sum'].rstrip('*'))
        user_time = avg_timing['user_time']
        
        hit_ratio = hits / accesses if accesses > 0 else 0
        cpu_per_access = user_time / accesses if accesses > 0 else 0
        cpu_per_hit = user_time / hits if hits > 0 else 0
        avg_hit_latency = hit_response_time_sum / hits if hits > 0 else 0
        lightweightness = hit_ratio / cpu_per_access if cpu_per_access > 0 else 0
        
        derived_metrics = {
            'hit_ratio': f"{hit_ratio:.2g}",
            'cpu_per_access': f"{cpu_per_access:.2g}",
            'cpu_per_hit': f"{cpu_per_hit:.2g}",
            'avg_hit_latency': f"{avg_hit_latency:.2g}",
            'lightweightness': f"{lightweightness:.2g}"
        }

        averaged_results.append({
            'run': group_label_for_table(run0),
            'stats': avg_stats,
            'timing': avg_timing,
            'derived': derived_metrics,
        })

    # Sort by policy, cache size, and model
    averaged_results.sort(key=lambda x: (x['run']['policy'], x['run']['cache_size'], x['run']['model']))

    md = "| Policy | Model | Cache Size | Args | Hits | Misses | Accesses | Total Object Size Sum | Total Response Time Sum | Hit Object Size Sum | Hit Response Time Sum | User Time | Elapsed Time | Max RSS | Exit Code | Hit Ratio | CPU per Access | CPU per Hit | Avg Hit Latency | Lightweightness"
    md += "\n|--------|-------|------------|---------------------|------|--------|----------|---------------------|---------------------|---------------------|----------------------|-----------|--------------|---------|-----------|----------|----------------|-------------|-----------------|-----------------"
    for result in averaged_results:
        md += (
            f"\n| {result['run'].get('policy')}"
            f" | {result['run'].get('model')}"
            f" | {result['run'].get('cache_size')}"
            f" | {json.dumps(additional_attributes_for_run(result['run']))}"
            f" | {result['stats']['hits']}"
            f" | {result['stats']['misses']}"
            f" | {result['stats']['accesses']}"
            f" | {result['stats']['object_size_sum']}"
            f" | {result['stats']['response_time_sum']}"
            f" | {result['stats']['hit_object_size_sum']}"
            f" | {result['stats']['hit_response_time_sum']}"
            f" | {result['timing']['user_time']}"
            f" | {result['timing']['elapsed_time']}"
            f" | {result['timing']['max_rss']}"
            f" | {result['timing']['exit_code']}"
            f" | {result['derived']['hit_ratio']}"
            f" | {result['derived']['cpu_per_access']}"
            f" | {result['derived']['cpu_per_hit']}"
            f" | {result['derived']['avg_hit_latency']}"
            f" | {result['derived']['lightweightness']}"
            " |"
        )

    with open(os.path.join(BASE_DIR, 'report.md'), 'w') as report_file:
        report_file.write("# Caching Policies Report\n\n")
        report_file.write("Last updated at: " + subprocess.getoutput("date") + "\n\n")
        report_file.write(md)
        report_file.write("\n")
        report_file.write(f"\n*Values marked with an asterisk (\\*) indicate variance across {RUN_REPEATS} runs.*\n")