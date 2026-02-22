import os
import csv
import json
import math
from pprint import pp
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(BASE_DIR, "results.csv")

def read_and_normalize_csv():
    with open(RESULTS_PATH, "r") as f:
        reader = csv.DictReader(f, delimiter=",")
        data = list(reader)

    fieldnames = set()
    for row in data:
        # expand stats_json and timing_json into separate keys
        for key in list(row.keys()):
            if key in ["stats_json", "timing_json"]:
                try:
                    json_data = json.loads(row[key])
                    for subkey, value in json_data.items():
                        row[f"{subkey}"] = value
                except json.JSONDecodeError:
                    pass
                row.pop(key)
                if row.get('exit_code') == 0:
                    row['hit_ratio'] = float(row.get('hits', 0)) / float(row.get('accesses', 1))
                    row['cpu_per_access'] = float(row.get('user_time', 0)) / float(row.get('accesses', 1))
                    row['log_cpu_per_access'] = math.log10(row['cpu_per_access']) if row['cpu_per_access'] > 0 else float('-inf')
                    row['cpu_per_hit'] = float(row.get('user_time', 0)) / float(row.get('hits', 1))
                    row['avg_hit_latency'] = float(row.get('hit_response_time_sum', 0)) / float(row.get('hits', 1))
                    row['efficiency'] = row['hit_ratio'] / row['cpu_per_access'] if row['cpu_per_access'] > 0 else 0
                    row['log_efficiency'] = math.log10(row['efficiency']) if row['efficiency'] > 0 else float('-inf')

        fieldnames.update(row.keys())

    # with open('./out.csv', "w", newline="") as f:
    #     writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=",")
    #     writer.writeheader()
    #     writer.writerows(data)

    return data

def filter_by(data, column, value):
    return [row for row in data if row.get(column) == value]

def get_unique_values(data, key):
    values = set(row.get(key) for row in data)
    values.discard(None)
    return values

def get_models(data):
    return get_unique_values(data, "model")

def get_policy_colors(data):
    policies = get_unique_values(data, "policy")
    colors = plt.get_cmap('tab10', len(policies))
    return {policy: colors(i) for i, policy in enumerate(policies)}


def compare_based_on_size_ratio(data, property='hit_ratio', draw=False, compare_fn=max):
    result_by_model_size_ratio = {}

    for model in get_models(data):
        result_by_model_size_ratio[model] = {}
        model_data = filter_by(data, 'model', model)
        cache_sizes = get_unique_values(model_data, "cache_size")
        
        object_sizes = get_unique_values(model_data, "object_size_sum")
        assert len(object_sizes) == 1
        object_size = object_sizes.pop()

        for cache_size in cache_sizes:
            size_ratio_log = math.log10(int(cache_size) / object_size)
            result_by_model_size_ratio[model][size_ratio_log] = {}
            for run in filter_by(model_data, 'cache_size', cache_size):
                if run.get(property) is None or run.get(property) == "":
                    continue
                elif run['policy'] not in result_by_model_size_ratio[model][size_ratio_log]:
                    # new one
                    result_by_model_size_ratio[model][size_ratio_log][run['policy']] = run.get(property)
                else:
                    result_by_model_size_ratio[model][size_ratio_log][run['policy']] = compare_fn(result_by_model_size_ratio[model][size_ratio_log][run['policy']], run.get(property))
    
    if draw:
        for model, size_ratio_data in result_by_model_size_ratio.items():
            plt.figure()
            for policy in get_policy_colors(data).keys():
                x = []
                y = []
                for size_ratio_log, policy_data in size_ratio_data.items():
                    if policy in policy_data:
                        x.append(size_ratio_log)
                        y.append(policy_data[policy])
                if x and y:
                    sorted_pairs = sorted(zip(x, y))
                    x, y = zip(*sorted_pairs)

                    linewidth = 2 if policy == 'lfu' or policy == 'lru' else 1
                    plt.plot(x, y, label=policy, color=get_policy_colors(data)[policy], linewidth=linewidth, alpha=0.9)

                plt.xlabel("log10(cache_size / object_size_sum)"); plt.ylabel(property); plt.title(f"{model} - {property} vs Object Size over Cache Size");
                plt.legend(); plt.grid()

if __name__ == "__main__":
    data = read_and_normalize_csv()
    compare_based_on_size_ratio(data, property='hit_ratio', compare_fn=max, draw=True)
    compare_based_on_size_ratio(data, property='log_efficiency', compare_fn=max, draw=True)
    compare_based_on_size_ratio(data, property='log_cpu_per_access', compare_fn=min, draw=True)

    plt.show()
    # print(data)