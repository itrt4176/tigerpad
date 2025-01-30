import struct

import board
from hid_io.output import HIDLEDOutput
import usb_hid
from adafruit_hid import find_device
from supervisor import ticks_ms

from constants import INPUT_REPORT_ID, OUTPUT_REPORT_ID
from hid_io.input import HIDAnalogInput, HIDDigitalInput

digital_in_pins = (
    board.GP0,
    board.GP2,
    board.GP4,
    board.GP6,
    board.GP8,
    board.GP10,
    board.GP12,
    board.GP14,
    board.GP16,
    board.GP19,
)
digital_in_ids = range(1, 11)
digital_hids = [
    HIDDigitalInput(pin, hid_id) for pin, hid_id in zip(digital_in_pins, digital_in_ids)
]

analog_in_pins = (board.GP26_A0, board.GP27_A1, board.GP28_A2)
analog_in_ids = range(1, 4)
analog_hids = [
    HIDAnalogInput(pin, hid_id) for pin, hid_id in zip(analog_in_pins, analog_in_ids)
]

led_out_pins = (board.GP1, board.GP3, board.GP5, board.GP7, board.GP9, board.GP11, board.GP13, board.GP15)
led_out_ids = range(1, 9)
led_hids = [HIDLEDOutput(pin, hid_id) for pin, hid_id in zip(led_out_pins, led_out_ids)]

device: usb_hid.Device = find_device(usb_hid.devices, usage_page=0x01, usage=0x05)  # type: ignore

last_run = ticks_ms()
while True:
    if ticks_ms() >= last_run + 5:
        report = bytearray(10)

        digital_bits: int = 0
        for digital_in in digital_hids:
            digital_bits |= digital_in.state << (digital_in.id - 1)

        struct.pack_into(
            "<Hhhhh",
            report,
            0,
            digital_bits,
            *[analog_in.state for analog_in in analog_hids],
            0,
        )

        device.send_report(report, INPUT_REPORT_ID)
        last_run = ticks_ms()
    
    output_report = device.get_last_received_report(OUTPUT_REPORT_ID)
    if output_report:
        led_bits: int = struct.unpack_from('<H', output_report)[0]
        for led in led_hids:
            led.state = (led_bits >> (2 * (led.id - 1))) & 0b11 # type: ignore
    
    for led in led_hids:
        led.run()

