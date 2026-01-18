import argparse
import logging
from components.core.cache import Cache
from components.core.storage import Storage
from traffic.reader import TrafficReader
import tqdm
from components.state.state import State

from policies.lfu import LFU
from policies.lru import LRU
from policies.lfu_sliding import LFU_Sliding
from policies.lfu_aging import LFU_Aging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("caching-policies-runner")

POLICIES = {
    "lru": LRU,
    "lfu-sliding": LFU_Sliding,
    "lfu": LFU,
    "lfu-aging": LFU_Aging
}

def main():
    parser = argparse.ArgumentParser(description="Run caching policies")
    parser.add_argument("--policy", type=str, required=True, help="Policy to run")
    parser.add_argument("--model", type=str, required=True, help="Model to use")
    parser.add_argument("--request-count", type=int, required=False, help="Number of requests to process")
    parser.add_argument("--cache-size", type=int, required=False, help="Cache size", default=100)
    parser.add_argument("--window-size", type=int, required=False, help="Sliding window size (timestamp units)", default=100)
    parser.add_argument("--tau", type=float, required=False, help="Decay constant for LFU aging", default=3600.0)

    args = parser.parse_args()
    
    logger.info(f"Running policy {args.policy} with model {args.model}")
    
    policy_class = POLICIES.get(args.policy)
    if not policy_class:
        logger.error(f"Unknown policy: {args.policy}")
        return
    
    policy_class_args = {}
    if args.policy == "lfu-sliding":
        policy_class_args['window_size'] = args.window_size
    elif args.policy == "lfu-aging":
        policy_class_args['tau'] = args.tau

    cache = Cache(policy_class(**policy_class_args), Storage(args.cache_size))
    state = State().attach_to(cache)

    traffic_reader = TrafficReader(args.model)
    request_count = traffic_reader.request_count()
    if args.request_count and args.request_count < request_count:
        request_count = args.request_count

    request_index = 0
    with tqdm.tqdm(total=request_count, desc="Simulating caching policy") as pbar:
        for req in traffic_reader.read_traffic():
            hit = "hit" in cache.access(req.object_id, req.timestamp, req.object_size)
            state.on_access(req.object_id, req.timestamp, hit, req.object_size, req.response_time)
            pbar.update(1)

            request_index += 1
            if request_index >= request_count:
                pbar.close()
                logger.info(f"Hit limit of {request_count} requests")
                break

    logger.info(f"Policy {args.policy} with model {args.model} finished")
    stats = state.to_dict()
    logger.info(f"Stats: hits={stats['hit_count']}, misses={stats['miss_count']}, accesses={stats['access_count']}, size={stats['current_size']}/{stats['capacity']}, hit_object_size_sum={stats['hit_object_size_sum']}, hit_response_time_sum={stats['hit_response_time_sum']}")

if __name__ == "__main__":
    main()
