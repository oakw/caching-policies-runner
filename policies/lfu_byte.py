from typing import Literal

from components.features.frequency import FrequencyFeature
from components.policy import Policy
from components.core.storage import Storage
from components.ranking.min_utility import MinUtilityRanker
from components.utility.size_aware import SizeAwareLFUUtility

SizeUtilityMode = Literal["freq_over_size", "freq_times_size"]

def LFU_Byte(storage: Storage, mode: SizeUtilityMode = "freq_over_size"):
    """LFU eviction with size-aware GreedyDual-style utility.

    This accepts two mode parameters:
      - freq_over_size: U = freq / size
      - freq_times_size: U = freq * size
    """

    frequency = FrequencyFeature()
    utility = SizeAwareLFUUtility(frequency, storage, mode=mode)
    ranker = MinUtilityRanker()
    return Policy([frequency], utility, ranker)
