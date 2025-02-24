from analogio import AnalogIn
from digitalio import DigitalInOut, Direction, Pull
from microcontroller import Pin
from rotaryio import IncrementalEncoder

from firmware.utils import input_modulus, map_val


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

    @property
    def state(self) -> int:
        return input_modulus(self._enc.position, -50, 50)  # type: ignore
