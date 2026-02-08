from components.features.frequency import FrequencyFeature
from components.utility.simple import SimpleUtility
from components.ranking.min_utility import MinUtilityRanker
from components.policy import Policy

from components.admission.doorkeeper import DoorkeeperCMSAdmission

def LFU_Doorkeeper(
    threshold: int = 2,
    epsilon: float = 0.001,
    delta: float = 1e-6,
    width: int | None = None,
    depth: int | None = None,
    conservative: bool = True,
):
    """Factory returning (eviction_policy, admission_policy)."""
    frequency = FrequencyFeature()
    utility = SimpleUtility(frequency)
    ranker = MinUtilityRanker()
    eviction_policy = Policy([frequency], utility, ranker)

    admission_policy = DoorkeeperCMSAdmission(
        threshold=threshold,
        epsilon=epsilon,
        delta=delta,
        width=width,
        depth=depth,
        conservative=conservative,
    )

    return eviction_policy, admission_policy
