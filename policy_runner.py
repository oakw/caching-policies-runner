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
from policies.lfu_doorkeeper import LFU_Doorkeeper
from policies.lfu_byte import LFU_Byte
from policies.two_segment import TwoSegmentPolicy
from policies.lfu_latency_byte import LFU_LatencyByte
from components.admission.tiny_lfu_byte import TinyLFUByteAdmission
from components.policy import Policy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("caching-policies-runner")

def tiny_lfu_byte_factory(storage: Storage, tiny_window_size: int = 100000):
    eviction_policy = LFU_Byte(storage=storage, mode="freq_over_size")
    admission_policy = TinyLFUByteAdmission(window_size=tiny_window_size)
    return eviction_policy, admission_policy


POLICIES = {
    "lru": LRU,
    "lfu-sliding": LFU_Sliding,
    "lfu": LFU,
    "lfu-aging": LFU_Aging,
    "lfu-doorkeeper": LFU_Doorkeeper,
    "lfu-byte": LFU_Byte,
    "two-segment": TwoSegmentPolicy,
    "tiny-lfu-byte": tiny_lfu_byte_factory,
    "lfu-latency-byte": LFU_LatencyByte,
}

def main():
    parser = argparse.ArgumentParser(description="Run caching policies")
    parser.add_argument("--policy", type=str, required=True, help="Policy to run")
    parser.add_argument("--model", type=str, required=True, help="Model to use")
    parser.add_argument("--request-count", type=int, required=False, help="Number of requests to process")
    parser.add_argument("--cache-size", type=int, required=False, help="Cache size", default=100)
    parser.add_argument("--window-size", type=int, required=False, help="Sliding window size (timestamp units)", default=100)
    parser.add_argument("--tau", type=float, required=False, help="Decay constant for LFU aging", default=3600.0)
    parser.add_argument("--admission-threshold", type=int, required=False, default=2, help="Admit object on miss only if estimated freq >= this")
    parser.add_argument("--cms-epsilon", type=float, required=False, default=0.001, help="CMS epsilon (error bound) for doorkeeper")
    parser.add_argument("--cms-delta", type=float, required=False, default=1e-6, help="CMS delta (failure probability) for doorkeeper")
    parser.add_argument("--cms-width", type=int, required=False, default=None, help="CMS width override for doorkeeper")
    parser.add_argument("--cms-depth", type=int, required=False, default=None, help="CMS depth override for doorkeeper")
    parser.add_argument(
        "--size-utility",
        type=str,
        required=False,
        default="freq_over_size",
        choices=["freq_over_size", "freq_times_size"],
        help="Size-aware utility mode (only for lfu-byte)",
    )
    parser.add_argument(
        "--latency-utility",
        type=str,
        required=False,
        default="freq_times_size_times_latency",
        choices=["freq_times_size_times_latency", "freq_times_latency_over_size"],
        help="Latency+size-aware utility mode (only for lfu-latency-byte)",
    )
    parser.add_argument(
        "--default-latency",
        type=float,
        required=False,
        default=1.0,
        help="Default latency used if trace lacks response_time (lfu-latency-byte)",
    )
    parser.add_argument(
        "--protected-fraction",
        type=float,
        required=False,
        default=0.5,
        help="Protected segment fraction in (0,1) for two-segment policy (object-count based)",
    )
    parser.add_argument(
        "--tiny-window-size",
        type=int,
        required=False,
        default=100000,
        help="Sliding window size (timestamp units) for tiny-lfu-byte admission sketch",
    )
    parser.add_argument(
        "--victim-sample-proportion",
        type=float,
        required=False,
        default=1.0,
        help="Proportion of cache keys to evaluate during victim selection (0,1]",
    )

    args = parser.parse_args()
    
    logger.info(f"Running policy {args.policy} with model {args.model}")
    
    policy_factory = POLICIES.get(args.policy)
    if not policy_factory:
        logger.error(f"Unknown policy: {args.policy}")
        return

    storage = Storage(args.cache_size)

    policy_factory_args = {}
    if args.policy == "lfu-sliding":
        policy_factory_args['window_size'] = args.window_size
    elif args.policy == "lfu-aging":
        policy_factory_args['tau'] = args.tau
    elif args.policy == "lfu-doorkeeper":
        policy_factory_args.update(
            dict(
                threshold=args.admission_threshold,
                epsilon=args.cms_epsilon,
                delta=args.cms_delta,
                width=args.cms_width,
                depth=args.cms_depth,
            )
        )
    elif args.policy == "lfu-byte":
        policy_factory_args.update(dict(storage=storage, mode=args.size_utility))
    elif args.policy == "two-segment":
        policy_factory_args.update(dict(protected_fraction=args.protected_fraction))
    elif args.policy == "lfu-latency-byte":
        policy_factory_args.update(
            dict(storage=storage, mode=args.latency_utility, default_latency=args.default_latency)
        )
    elif args.policy == "tiny-lfu-byte":
        policy_factory_args.update(dict(storage=storage, tiny_window_size=args.tiny_window_size))

    policy_obj = policy_factory(**policy_factory_args)

    admission_policy = None
    if isinstance(policy_obj, tuple) and len(policy_obj) == 2:
        eviction_policy, admission_policy = policy_obj
    else:
        eviction_policy = policy_obj

    eviction_policy.set_victim_sample_proportion(args.victim_sample_proportion)
    cache = Cache(eviction_policy, storage, admission_policy=admission_policy)
    state = State().attach_to(cache)

    traffic_reader = TrafficReader(args.model)
    request_count = traffic_reader.request_count()
    if args.request_count and args.request_count < request_count:
        request_count = args.request_count

    request_index = 0
    with tqdm.tqdm(total=request_count, desc="Simulating caching policy") as pbar:
        for req in traffic_reader.read_traffic():
            hit = "hit" in cache.access(req.object_id, req.timestamp, req.object_size, latency=req.response_time or 0.0)
            state.on_access(req.object_id, req.timestamp, hit, req.object_size, req.response_time)
            pbar.update(1)

            request_index += 1
            if request_index >= request_count:
                pbar.close()
                logger.info(f"Hit limit of {request_count} requests")
                break

    logger.info(f"Policy {args.policy} with model {args.model} finished")
    stats = state.to_dict()
    logger.info(f"Stats: hits={stats['hit_count']}, misses={stats['miss_count']}, accesses={stats['access_count']}, size={stats['current_size']}/{stats['capacity']}, hit_object_size_sum={stats['hit_object_size_sum']}, hit_response_time_sum={stats['hit_response_time_sum']}, total_object_size_sum={stats['total_object_size_sum']}, total_response_time_sum={stats['total_response_time_sum']}")

if __name__ == "__main__":
    main()
