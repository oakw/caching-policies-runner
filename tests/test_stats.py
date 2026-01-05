import math
import pytest
from components.core.cache import Cache
from components.core.storage import Storage
from components.state.state import State
from traffic.reader import TrafficReader
from policies.lru import LRU
from policies.lfu import LFU

# Expected hit/miss ratios per capacity for each policy
EXPECTED = {
    "lru": {
        20: {"hit": 0.10, "miss": 0.90},
        40: {"hit": 0.28, "miss": 0.72},
        60: {"hit": 0.44, "miss": 0.56},
        80: {"hit": 0.58, "miss": 0.42},
        100: {"hit": 0.70, "miss": 0.30},
    },
    "lfu": {
        20: {"hit": 0.12, "miss": 0.88},
        40: {"hit": 0.32, "miss": 0.68},
        60: {"hit": 0.48, "miss": 0.52},
        80: {"hit": 0.62, "miss": 0.38},
        100: {"hit": 0.74, "miss": 0.26},
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
        hit = cache.access(req.object_id, req.timestamp, req.object_size)
        state.on_access(req.object_id, req.timestamp, hit)

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
