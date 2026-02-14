import numpy as np

def coin_flip(num_flips: int) -> np.ndarray:
    """
    Generates a random boolean vector of length `num_flips`.

    Args:
        num_flips: Number of flips

    Returns:
        A numpy array of shape (num_flips,) representing the boolean vector

    Example:
    """
    # Use a generator
    generator = np.random.default_rng()
    return generator.integers(0, 2, num_flips) == 1
