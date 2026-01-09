import math
import pytest
import os
import datetime
from components.core.cache import Cache
from components.core.storage import Storage
from components.state.state import State
from traffic.reader import TrafficReader
from policies.lru import LRU
from policies.lfu import LFU

start_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
def log_info_to_file(policy: str, message: str):
    os.makedirs(f"tests/runs/{start_time}", exist_ok=True)
    with open(f"tests/runs/{start_time}/{policy}.log", "a") as f:
        f.write(message + "\n")

# Expected hit/miss ratios per capacity for each policy
EXPECTED = {
    "lru": {
        20: {"hit": 0.12, "miss": 0.88},
        40: {"hit": 0.34, "miss": 0.66},
        60: {"hit": 0.54, "miss": 0.46},
        80: {"hit": 0.66, "miss": 0.34},
        100: {"hit": 0.82, "miss": 0.18},
    },
    "lfu": {
        20: {"hit": 0.08, "miss": 0.92},
        40: {"hit": 0.22, "miss": 0.78},
        60: {"hit": 0.42, "miss": 0.58},
        80: {"hit": 0.68, "miss": 0.32},
        100: {"hit": 0.82, "miss": 0.18},
    },
}

MODEL_ID = "test-1"

@pytest.mark.parametrize("policy_name,policy_factory", [("lru", LRU), ("lfu", LFU)])
@pytest.mark.parametrize("capacity", [20, 40, 60, 80, 100])
def test_policy_hit_miss_ratios(policy_name, policy_factory, capacity):
    reader = TrafficReader(MODEL_ID)
    cache = Cache(policy_factory(), Storage(capacity))
    state = State().attach_to(cache)

    for req in reader.read_traffic():
        actions = cache.access(req.object_id, req.timestamp, req.object_size)
        state.on_access(req.object_id, req.timestamp, "hit" in actions)
        log_info_to_file(f"{policy_name}-capacity-{capacity}", f"Request: {req}, Actions: {actions}, State: {state}")

    stats = state.to_dict()
    assert stats["access_count"] > 0, "Traffic should not be empty"

    hit_ratio = stats["hit_count"] / stats["access_count"]
    miss_ratio = stats["miss_count"] / stats["access_count"]

    expected = EXPECTED[policy_name][capacity]

    tolerance = 0.02
    assert math.isclose(hit_ratio, expected["hit"], rel_tol=tolerance, abs_tol=tolerance), \
        f"{policy_name.upper()} hit ratio {hit_ratio:.2f} != expected {expected['hit']:.2f} for capacity {capacity}"
    assert math.isclose(miss_ratio, expected["miss"], rel_tol=tolerance, abs_tol=tolerance), \
        f"{policy_name.upper()} miss ratio {miss_ratio:.2f} != expected {expected['miss']:.2f} for capacity {capacity}"
