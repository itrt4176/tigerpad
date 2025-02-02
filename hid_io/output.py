try:
    from typing import Literal
except ImportError:
    pass

from microcontroller import Pin
from digitalio import DigitalInOut, Direction
from micropython import const # type: ignore
from supervisor import ticks_ms


class HIDOutputBase:
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
    
    @state.setter
    def state(self, state):
        raise NotImplementedError(
            "This is a base class which should not be used directly."
        )
    
    def run(self, *args, **kwargs):
        raise NotImplementedError(
            "This is a base class which should not be used directly."
        )

class HIDLEDOutput(HIDOutputBase):
    class Mode:
        OFF: 'Literal[0]' = const(0)
        BLINK: 'Literal[1]' = const(1)
        ON: 'Literal[2]' = const(2)

    def __init__(self, pin: Pin, hid_id: int) -> None:
        super().__init__(hid_id)
        self._led = DigitalInOut(pin)
        self._led.direction = Direction.OUTPUT
        self._state : 'Literal[0, 1, 2]' = HIDLEDOutput.Mode.BLINK
        # self._state: 'Literal[0, 1, 2]' = HIDLEDOutput.Mode.BLINK if self.id % 2 == 1 else HIDLEDOutput.Mode.ON
        self._last_run = 0
    
    @property
    def state(self) -> 'Literal[0, 1, 2]':
        return self._state
    
    @state.setter
    def state(self, state: 'Literal[0, 1, 2]') -> None:
        if state not in (0, 1, 2):
            raise ValueError('LED state must be one of OFF (0), BLINK (1), or ON (2)')
        self._state = state
    
    def run(self) -> None:
        if self._state == HIDLEDOutput.Mode.OFF:
            self._led.value = False
        elif self._state == HIDLEDOutput.Mode.BLINK:
            if ticks_ms() >= self._last_run + 1000:
                self._led.value = not self._led.value
                self._last_run = ticks_ms()
        elif self._state == HIDLEDOutput.Mode.ON:
            self._led.value = True