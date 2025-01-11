import struct
import time

import usb_hid
from adafruit_hid import find_device

button_ids = range(1, 11)

device: usb_hid.Device = find_device(usb_hid.devices, usage_page=0x01, usage=0x05)  # type: ignore

while True:
    report = bytearray(2)
    for i in button_ids:
        state_bits: int = 0
        for j in button_ids:
            state = i == j
            state_bits |= state << (j - 1)

        struct.pack_into("<H", report, 0, state_bits)

        device.send_report(report, 1)
        print(report)

        time.sleep(1)
