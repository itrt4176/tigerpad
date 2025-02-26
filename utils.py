import os
import digitalio

from constants import FW_UPDATE_PIN

fw_update_button = digitalio.DigitalInOut(FW_UPDATE_PIN)
fw_update_button.pull = digitalio.Pull.DOWN

DEBUG_MODE = bool(os.getenv("DEBUG_MODE", 1)) or fw_update_button.value
fw_update_button.deinit()

def map_val(val: int, in_min: int, in_max: int, out_min: int, out_max: int) -> int:
    return (val - in_min) * (out_max - out_min) // (in_max - in_min) + out_min


def clamp(val: int, low: int, high: int) -> int:
    return min(max(low, val), high)

def input_modulus(val: int | float, min_val: int | float, max_val: int | float) -> int | float:
    modulus = max_val - min_val

    num_max = int((val - min_val) / modulus)
    val -= num_max * modulus

    num_min = int((val - max_val) / modulus)
    val -= num_min * modulus

    return val
