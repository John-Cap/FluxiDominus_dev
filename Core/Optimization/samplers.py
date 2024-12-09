import random


class Sampler:
    def __init__(self) -> None:
        pass
    
    def trendBasedSampler(min_val, max_val, recent_yields, recent_params = [], bias_factor=0.85):
        """
        Custom sampling function that biases towards recent trends.

        Parameters:
        - min_val, max_val: The range for the parameter.
        - recent_yields: A list of recent yield values.
        - recent_params: A list of corresponding parameter values.
        - bias_factor: Controls the weighting of the trend (0 = uniform sampling, 1 = fully biased).

        Returns:
        - A new sampled value within the given range.
        """
        if len(recent_yields) < 2 or len(recent_params) == 0:
            # Not enough data to establish a trend, sample uniformly
            return random.uniform(min_val, max_val)

        # Compute the trend in the last two results
        delta_yield = recent_yields[-1] - recent_yields[-2]
        target_param = recent_params[-1]

        if delta_yield > 0:
            # Improving yield: bias towards current region
            center = target_param
        else:
            # Declining yield: explore other regions
            center = (min_val + max_val) / 2

        # Generate a biased sample
        sampled = random.gauss(center, (max_val - min_val) * bias_factor)
        if sampled < 0:
            sampled = min_val
        return max(min_val, min(max_val, sampled))  # Clip to range
