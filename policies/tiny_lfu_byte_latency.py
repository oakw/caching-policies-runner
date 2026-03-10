from components.core.storage import Storage
from policies.lfu_latency_byte import LFU_LatencyByte
from components.admission.tiny_lfu_byte_latency import TinyLFUByteLatencyAdmission

def tiny_lfu_byte_latency_factory(
    storage: Storage,
    tiny_window_size: int = 100000,
    mode: str = "freq_times_size_times_latency",
    default_latency: float = 1.0,
):
    eviction_policy = LFU_LatencyByte(storage=storage, mode=mode, default_latency=default_latency)
    admission_policy = TinyLFUByteLatencyAdmission(
        window_size=tiny_window_size,
        mode=mode,
        default_latency=default_latency,
    )
    return eviction_policy, admission_policy
