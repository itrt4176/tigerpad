def map_val(val: int, in_min: int, in_max: int, out_min: int, out_max: int) -> int:
    return (val - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def clamp(val: int, low: int, high: int) -> int:
    return min(max(low, val), high)
