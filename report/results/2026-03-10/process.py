# Unclean code for processing the results.
import os
import csv
import json
import math
from pprint import pp
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESULTS_PATH = os.path.join(BASE_DIR, "results.csv")

POLICIES = ['lru', 'lfu', 'lfu-aging', 'lfu-sliding', 'lfu-byte', 'lfu-latency-byte', 'lfu-doorkeeper', 'tiny-lfu-byte-latency', 'two-segment']
POLICIES_DISPLAY_NAMES = {
    'lru': 'LRU',
    'lfu': 'LFU',
    'lfu-aging': 'LFU-Aging',
    'lfu-sliding': 'LFU-Sliding',
    'lfu-byte': 'LFU-Byte',
    'lfu-latency-byte': 'LFU-Latency-Byte',
    'lfu-doorkeeper': 'LFU-Doorkeeper',
    'tiny-lfu-byte-latency': 'TinyLFU-Byte-Latency',
    'two-segment': 'TwoSegment',
}
MODELS = ['docker-lon02', 'wiki-t-10', 'letapartika']
MODELS_DISPLAY_NAMES = {
    'docker-lon02': 'Docker Registry',
    'wiki-t-10': 'Wikipedia',
    'letapartika': 'Letapartika',
}
RUN_CONFIG_KEYS = ["admission_threshold","cache_size","cms_delta","cms_epsilon","default_latency","latency_utility","model","policy","protected_fraction","request_count","size_utility","tau","tiny_window_size","window_size","expected_count","victim_sample_proportion"]

# Selected through grid search in the first round (here hit_ratio is highest)
TOP_CONFIGURATIONS = ['1054', '1057', '1060', '1061', '1072', '1081', '1084', '1086', '1156', '1159', '1162', '1163', '1174', '1183', '1186', '1188', '1258', '1261', '1264', '1265', '1276', '1285', '1288', '1290', '1360', '1363', '1366', '1367', '1378', '1387', '1390', '1392', '1394', '1400', '1406', '1412', '1417', '1418', '1419', '1420', '1547', '1549', '1552', '1554', '1557', '1573', '1576', '1578', '1649', '1651', '1654', '1656', '1659', '1675', '1678', '1680', '1751', '1753', '1756', '1758', '1761', '1777', '1780', '1782', '1853', '1855', '1858', '1860', '1863', '1879', '1882', '1884', '1890', '1896', '1902', '1908', '1909', '1910', '1911', '1912', '564', '565', '568', '570', '587', '590', '592', '594', '666', '667', '670', '672', '689', '692', '694', '696', '768', '769', '772', '774', '791', '794', '796', '798', '870', '871', '874', '876', '893', '896', '898', '900', '904', '910', '916', '922', '925', '926', '927', '928']
TOP_BYTE_RATIO_CONFIGURATIONS = ['1055', '1057', '1058', '1062', '1065', '1082', '1083', '1086', '1157', '1159', '1160', '1164', '1167', '1184', '1185', '1188', '1259', '1261', '1262', '1266', '1269', '1286', '1287', '1290', '1361', '1363', '1364', '1368', '1371', '1388', '1389', '1392', '1397', '1403', '1409', '1415', '1417', '1418', '1419', '1420', '1545', '1549', '1550', '1553', '1566', '1574', '1577', '1578', '1647', '1651', '1652', '1655', '1668', '1676', '1679', '1680', '1749', '1753', '1754', '1757', '1770', '1778', '1781', '1782', '1851', '1855', '1856', '1859', '1872', '1880', '1883', '1884', '1889', '1895', '1901', '1907', '1909', '1910', '1911', '1912', '561', '565', '567', '569', '582', '589', '593', '594', '663', '667', '669', '671', '684', '691', '695', '696', '765', '769', '771', '773', '786', '793', '797', '798', '867', '871', '873', '875', '888', '895', '899', '900', '905', '911', '917', '923', '925', '926', '927', '928']

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
                    row['byte_hit_ratio'] = float(row.get('hit_object_size_sum', 0)) / float(row.get('object_size_sum', 0)) if row.get('object_size_sum', 0) > 0 else 0
                    row['hit_response_time_sum'] = float(row.get('hit_response_time_sum', 0))
                    row['size_ratio'] = float(row.get('cache_size', 0)) / float(row.get('object_size_sum', 1)) if float(row.get('object_size_sum', 0)) > 0 else 0
                    row['latency_saved'] = row['hit_response_time_sum'] / float(row.get('response_time_sum', 0)) if float(row.get('response_time_sum', 0)) > 0 else 0
                    row['cpu_per_access'] = (float(row.get('user_time', 0)) + float(row.get('system_time', 0))) / float(row.get('accesses', 1))
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
    policies = POLICIES
    colors = plt.get_cmap('tab10', len(policies))
    return {policy: colors(i) for i, policy in enumerate(policies)}

def get_top_configurations(data, property='hit_ratio'):
    top_configs = {}
    data = filter_by(data, 'victim_sample_proportion', '0.01') # argued in the paper
    for model in get_models(data):
        model_data = filter_by(data, 'model', model)
        top_configs[model] = {}
        for policy in POLICIES:
            policy_data = filter_by(model_data, 'policy', policy)
            config_keys = RUN_CONFIG_KEYS.copy()
            config_keys.remove('cache_size')
            runs_by_config_key = {}
            for run in policy_data:
                def safe_float_or_str(value):
                    try:
                        return float(value)
                    except (ValueError, TypeError):
                        return value if value is not None else ''

                unique_key = tuple(safe_float_or_str(run.get(key)) for key in config_keys)
                runs_by_config_key.setdefault(unique_key, {'sum': 0, 'runs': []})
                runs_by_config_key[unique_key]['sum'] += float(run.get(property, 0))
                runs_by_config_key[unique_key]['runs'].append(run)

            cheapest_key = max(runs_by_config_key, key=lambda k: runs_by_config_key[k]['sum'], default=None)
            if cheapest_key is None:
                print(f"No runs found for model {model} and policy {policy}")
                continue
            top_configs[model][policy] = [run.get('id') for run in runs_by_config_key[cheapest_key]['runs']]

    return top_configs

def get_top_configurations_ids(data, property='hit_ratio'):
    top_configs = get_top_configurations(data, property)
    ids = []
    for model, policies in top_configs.items():
        for policy, runs in policies.items():
            ids.extend(runs)
    return sorted(set(ids))

def extract_ratio_table(data, property):
    ratios_by_policy_and_model = {}
    for model in get_models(data):
        model_data = filter_by(data, 'model', model)
        ratios_by_policy_and_model[model] = {}
        for policy in get_unique_values(model_data, "policy"):
            policy_data = filter_by(model_data, 'policy', policy)
            # here put for statistical significance
            ranges = dict(
                min=min(get_unique_values(policy_data, property) or [None]),
                max=max(get_unique_values(policy_data, property) or [None]),
            )
            ratios_by_policy_and_model[model][policy] = ranges

    return ratios_by_policy_and_model

def format_ratio_table(ratios_by_policy_and_model, ratio_name):
    print(f"Ratio Table for {ratio_name}")
    print('\t'.join(['policy', *MODELS]))
    for policy in POLICIES:
        row = [policy]
        for model in MODELS:
            min_ratio = ratios_by_policy_and_model.get(model, {}).get(policy, {}).get('min', None)
            max_ratio = ratios_by_policy_and_model.get(model, {}).get(policy, {}).get('max', None)
            row.append((f"{min_ratio:.3f}".lstrip('0') if min_ratio is not None else "..") +  ' - ' +  (f"{max_ratio:.3f}".lstrip('0') if max_ratio is not None else ".."))
        print('\t'.join(row))

def policy_compare(data, property='hit_ratio'):
    result_by_models = {}

    for model in get_models(data):
        all_stdevs = []
        model_data = filter_by(data, 'model', model)
        result_by_models[model] = {}
        for cache_size in get_unique_values(model_data, "cache_size"):
            result_by_models[model][cache_size] = {}
            cache_size_data = filter_by(model_data, 'cache_size', cache_size)
            for policy in POLICIES:
                result_by_models[model][cache_size][policy] = {}
                policy_data = filter_by(cache_size_data, 'policy', policy)

                if not policy_data:
                    continue
                avg_value = sum(float(row.get(property, 0)) for row in policy_data) / len(policy_data)

                try:
                    stddev_value = (
                        sum((float(row.get(property, 0)) - avg_value) ** 2 for row in policy_data)
                        / (len(policy_data) - 1)
                    ) ** 0.5
                    all_stdevs.append(stddev_value)
                except ZeroDivisionError:
                    print(f"Warning: Only one run for model {model}, cache size {cache_size}, policy {policy}. Standard deviation set to 0.")
                    stddev_value = 0.0

                result_by_models[model][cache_size][policy] = dict(
                    avg=avg_value,
                    min=min(float(row.get(property, 0)) for row in policy_data),
                    max=max(float(row.get(property, 0)) for row in policy_data),
                    stddev=stddev_value,
                    count=len(policy_data),
                    confidence_interval=2.262 * stddev_value / math.sqrt(len(policy_data)) # 95% confidence interval
                )

            for policy_1 in POLICIES:
                for policy_2 in POLICIES:
                    if policy_1 == policy_2:
                        continue

                    policy_1_data = filter_by(cache_size_data, 'policy', policy_1)
                    policy_2_data = filter_by(cache_size_data, 'policy', policy_2)

                    if len(policy_1_data) > 1 and len(policy_2_data) > 1:
                        values_1 = [float(row.get(property, 0)) for row in policy_1_data]
                        values_2 = [float(row.get(property, 0)) for row in policy_2_data]
                        
                        # Perform Wilcoxon rank-sum test (Mann-Whitney U test)
                        u_stat, p_value = stats.mannwhitneyu(values_1, values_2, alternative='two-sided')
                        significance = {
                            'u_statistic': u_stat,
                            'p_value': p_value,
                            'significant': p_value < 0.05
                        }

                        result_by_models[model][cache_size][policy_1].setdefault('significance', {})[policy_2] = significance
                        result_by_models[model][cache_size][policy_2].setdefault('significance', {})[policy_1] = significance
        print(max(all_stdevs) if all_stdevs else "No standard deviations calculated for model", model)
    return result_by_models

def significance_matrix(data, property='hit_ratio'):
    data = policy_compare(data, property=property)
    upperscripts = '⁰¹²³⁴⁵⁶⁷⁸⁹'
    matrix_by_model = {}
    for model, cache_sizes in data.items():
        matrix = {}
        for cache_size, policies in cache_sizes.items():
            matrix[cache_size] = {}
            for policy, results in policies.items():
                significant_upperscripts = []
                for i, other_policy in enumerate(POLICIES):
                    if other_policy != policy:
                        significance = results.get('significance', {}).get(other_policy, {})
                        if significance.get('significant'):
                            significant_upperscripts.append(upperscripts[i + 1])

                matrix[cache_size][policy] = f"{results.get('avg', 0):.3f}".lstrip('0') + (''.join(significant_upperscripts) if len(significant_upperscripts) < len(POLICIES) - 1 else '*')

        matrix_by_model[model] = matrix
    return matrix_by_model

def draw_comparison(data, property='hit_ratio'):
    result_by_models = policy_compare(data, property=property)
    Y_LABEL_DISPLAY_NAMES = {
        'hit_ratio': 'Hit Ratio',
        'byte_hit_ratio': 'Byte Hit Ratio',
        'latency_saved': 'Latency Saved',
        'log_efficiency': 'Log Efficiency',
        'log_cpu_per_access': 'Log CPU per Access',
        'cpu_per_access': 'CPU Time per Access',
        'efficiency': 'Efficiency',
    }

    fig, axes = plt.subplots(1, 3, figsize=(12, 4), dpi=160)
    legend_handles = {}
    
    for i, model in enumerate(MODELS):
        cache_size_results = result_by_models.get(model, {})

        for policy in POLICIES:
            x = []
            y = []
            confidence_intervals = []
            for cache_size, policy_data in cache_size_results.items():
                if policy in policy_data:
                    x.append(float(cache_size))
                    y.append(policy_data[policy]['avg'])
                    confidence_intervals.append(policy_data[policy].get('confidence_interval', 0))

            if x and y:
                sorted_pairs = sorted(zip(x, y, confidence_intervals))
                x, y, confidence_intervals = zip(*sorted_pairs)
                policy_name = POLICIES_DISPLAY_NAMES.get(policy, policy)

                linewidth = 2 if policy in ('lfu', 'lru') else 1
                line, = axes[i].plot(
                    x, y,
                    label=policy_name,
                    color=get_policy_colors(data)[policy],
                    linewidth=linewidth,
                    alpha=0.9
                )
                axes[i].errorbar(
                    x,
                    y,
                    yerr=confidence_intervals,
                    fmt='-',
                    color=get_policy_colors(data)[policy],
                    alpha=0.7,
                    capsize=1.5
                )

                if policy_name not in legend_handles:
                    legend_handles[policy_name] = line

        axes[i].set_xscale('log')
        axes[i].set_yscale('log')
        if i == 0:
            axes[i].set_ylabel(Y_LABEL_DISPLAY_NAMES.get(property, property))
        if i == 1:
            axes[i].set_xlabel("Cache Size")

        axes[i].set_title(f"{MODELS_DISPLAY_NAMES.get(model, model)}")
        # axes[i].set_ylim(0, 1)
        axes[i].spines['top'].set_visible(False)
        axes[i].spines['right'].set_visible(False)
        axes[i].grid(axis='y', linestyle='--', alpha=0.5)

    fig.text(0.91, 0.78, 'Policy', ha='center', va='top')
    fig.legend(
        legend_handles.values(),
        legend_handles.keys(),
        loc='center right',
    )

    plt.tight_layout(rect=[0, 0, 0.82, 1])

if __name__ == "__main__":
    data = read_and_normalize_csv()
    # data = filter_by(data, 'expected_count', '10')
    filtered_data = []
    config_count = {}
    for row in data:
        config_id = row.get('config_id')
        if config_id in TOP_CONFIGURATIONS:
            if config_count.get(config_id, 0) < 10:
                filtered_data.append(row)
                config_count[config_id] = config_count.get(config_id, 0) + 1
    data = filtered_data

    print("Significance Matrix for Log CPU per Access:")
    significance_matrix = significance_matrix(data, property='latency_saved')
    for model in significance_matrix:
        print("Model:", model)
        for i, policy in enumerate(POLICIES):
            print(f"{i+1}. {POLICIES_DISPLAY_NAMES.get(policy, policy)}".ljust(30), end='\t')
            for cache_size in ['100000', '1000000', '10000000', '100000000']:
                print(significance_matrix[model][cache_size].get(policy, '').ljust(30), end='\t')
            print()
        print()

    for model in MODELS:
        print(f"Top configurations for model {model}:")
        seen_config_ids = set()
        for config_id in TOP_CONFIGURATIONS:
            runs = filter_by(filter_by(data, 'config_id', config_id), 'model', model)
            if runs:
                relevant_params = [param for param in RUN_CONFIG_KEYS if param not in ['cache_size', 'model', 'policy', 'expected_count', 'request_count', 'victim_sample_proportion']]
                key = tuple(runs[0].get(param) for param in relevant_params)
                if key in seen_config_ids:
                    continue
                seen_config_ids.add(key)
                print(f"\t{runs[0].get('policy')}:", end=' ')
                for param in relevant_params:
                    if param in runs[0] and runs[0].get(param, '') != '':
                        print(f"{param}: {runs[0].get(param)}", end=', ')
                print()

    # draw_comparison(data, property='hit_ratio')
    # draw_comparison(data, property='byte_hit_ratio')
    # draw_comparison(data, property='latency_saved')
    draw_comparison(data, property='cpu_per_access')
    # draw_comparison(data, property='efficiency')
    plt.show()
    # print(format_ratio_table(extract_ratio_table(data, property='hit_ratio'), ratio_name='hit_ratio'))
    # print(format_ratio_table(extract_ratio_table(data, property='byte_hit_ratio'), ratio_name='byte_hit_ratio'))
    # print(format_ratio_table(extract_ratio_table(data, property='latency_saved'), ratio_name='latency_saved'))

    property = 'hit_ratio'
    print(f"Top configurations IDs based on {property}:")
    ids = get_top_configurations_ids(data, property=property)
    print(len(ids), "runs found")
    print(ids)