from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from microcontroller import Pin
from rotaryio import IncrementalEncoder

from utils import clamp, map_val


class HIDInputBase:
    def __init__(self, hid_id: int) -> None:
        self._id = hid_id

    @property
    def id(self) -> int:
        return self._id

    @property
    def state(self):
        raise NotImplementedError(
            "This is a base class which should not be used directly."
        )

    def __lt__(self, other: "HIDInputBase") -> bool:
        return self.id < other.id


class HIDDigitalInput(HIDInputBase):
    def __init__(self, pin: Pin, hid_id: int) -> None:
        super().__init__(hid_id)
        self._dio = DigitalInOut(pin)
        self._dio.direction = Direction.INPUT
        self._dio.pull = Pull.DOWN

    @property
    def state(self) -> bool:
        return self._dio.value


class HIDAnalogInput(HIDInputBase):
    def __init__(self, pin: Pin, hid_id: int) -> None:
        super().__init__(hid_id)
        self._ain = AnalogIn(pin)

    @property
    def state(self) -> int:
        return map_val(self._ain.value, 0, 65535, -2048, 2047)


class HIDRotaryEncoder(HIDInputBase):
    def __init__(self, pin_a: Pin, pin_b: Pin, hid_id: int) -> None:
        super().__init__(hid_id)
        self._enc = IncrementalEncoder(pin_a, pin_b)
        self._last_pos = 0

    @property
    def state(self) -> int:
        pos = self._enc.position
        delta = pos - self._last_pos
        self._last_pos = pos

        return clamp(delta * 10, -1000, 1000)
