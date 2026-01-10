import json
import os
import subprocess
import tqdm
import re
import concurrent.futures

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUN_REPEATS = 1

TIME_TEMPLATE = "<user>%U</user><system>%S</system><elapsed>%e</elapsed><max-rss>%M</max-rss><exit-code>%x</exit-code><cpu>%P</cpu>"

HALF_PROCESSORS = max(1, (os.cpu_count() or 1) // 2)

all_results = []
with open (os.path.join(BASE_DIR, 'config.json'), 'r') as file:
    config = json.load(file)
    config = config * RUN_REPEATS

    def run_config(i, run):
        result = subprocess.run([
            "/usr/bin/time", "-f", TIME_TEMPLATE,
            "python", f"{BASE_DIR}/../policy_runner.py",
            "--policy", run['policy'],
            "--model", run['model'],
            "--request-count", str(int(run.get('request_count', ''))),
            "--window-size", str(int(run.get('window_size', 100))),
            "--cache-size", str(int(run.get('cache_size', ''))),
        ], text=True, capture_output=True)
        return (i, run, result)

    with concurrent.futures.ThreadPoolExecutor(max_workers=HALF_PROCESSORS) as executor:
        futures = {executor.submit(run_config, i, run): (i, run) for i, run in enumerate(config)}

        for fut in tqdm.tqdm(concurrent.futures.as_completed(futures), total=len(futures), desc="Running configurations"):
            i, run, result = fut.result()

            # Parse stats from stdout
            stats = {}
            for line in (result.stderr + result.stdout).split('\n'):
                if 'Stats:' in line:
                    # Extract hits, misses, accesses, size
                    hits_match = re.search(r'hits=(\d+)', line)
                    misses_match = re.search(r'misses=(\d+)', line)
                    accesses_match = re.search(r'accesses=(\d+)', line)
                    size_match = re.search(r'size=(\d+)/(\d+)', line)
                    hit_object_size_sum_match = re.search(r'hit_object_size_sum=(\d+)', line)
                    hit_response_time_sum_match = re.search(r'hit_response_time_sum=([\d.]+)', line)

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

            # Parse timing info from stderr using regex
            timing = {}
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

            if len(stats) == 0 or len(timing) == 0:
                print(f"ERROR: Run {run} failed to produce stats or timing info.")
                print(f"stdout: {result.stdout}")
                print(f"stderr: {result.stderr}")
                exit(1)

            all_results.append(dict(
                run=run,
                stats=stats,
                timing=timing
            ))

# Group results by configuration (policy, model, cache_size)
grouped_results = {}
for result in all_results:
    key = (result['run']['policy'], result['run']['model'], result['run']['cache_size'])
    if key not in grouped_results:
        grouped_results[key] = []
    grouped_results[key].append(result)

# Calculate averages for each group
averaged_results = []
for key, results in grouped_results.items():
    policy, model, cache_size = key
    
    avg_stats = {}
    for stat in ['hits', 'misses', 'accesses', 'current_size', 'hit_object_size_sum', 'hit_response_time_sum']:
        values = [r['stats'][stat] for r in results]
        avg_value = sum(values) / len(values)
        if not all(val == values[0] for val in values):
            # Indicate that there was variance with an asterisk
            avg_stats[stat] = f"{avg_value:.1f}*"
        else:
            avg_stats[stat] = avg_value

    avg_timing = {
        'user_time': sum(r['timing']['user_time'] for r in results) / len(results),
        'system_time': sum(r['timing']['system_time'] for r in results) / len(results),
        'elapsed_time': sum(r['timing']['elapsed_time'] for r in results) / len(results),
        'max_rss': sum(r['timing']['max_rss'] for r in results) / len(results),
        'exit_code': results[0]['timing']['exit_code']
    }
    
    averaged_results.append({
        'run': {'policy': policy, 'model': model, 'cache_size': cache_size},
        'stats': avg_stats,
        'timing': avg_timing
    })

# Sort by policy, cache size, and model
averaged_results.sort(key=lambda x: (x['run']['policy'], x['run']['cache_size'], x['run']['model']))

md = "| Policy | Model | Cache Size | Hits | Misses | Accesses | Hit Object Size Sum | Hit Response Time Sum | User Time | Elapsed Time | Max RSS | Exit Code |"
md += "\n|--------|-------|------------|------|--------|----------|---------------------|----------------------|-----------|--------------|---------|-----------|"
for result in averaged_results:
    md += f"\n| {result['run']['policy']} | {result['run']['model']} | {int(result['run']['cache_size'])} | {result['stats']['hits']:.1f} | {result['stats']['misses']:.1f} | {result['stats']['accesses']:.1f} | {result['stats']['hit_object_size_sum']:.1f} | {result['stats']['hit_response_time_sum']:.2f} | {result['timing']['user_time']:.3f} | {result['timing']['elapsed_time']:.3f} | {result['timing']['max_rss']:.1f} | {result['timing']['exit_code']} |"

with open(os.path.join(BASE_DIR, 'report.md'), 'w') as report_file:
    report_file.write("# Caching Policies Report\n\n")
    report_file.write("Last updated at: " + subprocess.getoutput("date") + "\n\n")
    report_file.write(md)
    report_file.write("\n")
    report_file.write(f"\n*Values marked with an asterisk (\\*) indicate variance across {RUN_REPEATS} runs.*\n")