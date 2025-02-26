import struct
import time

import board
import digitalio
import microcontroller
import usb_cdc
import usb_hid
from adafruit_hid import find_device  # type: ignore

from constants import FW_UPDATE_PIN, REPORT_SIZE
from hid_io.input import HIDAnalogInput, HIDDigitalInput, HIDRotaryEncoder
from hid_io.output import HIDLEDOutput
from utils import DEBUG_MODE

fw_update_btn = digitalio.DigitalInOut(FW_UPDATE_PIN)
fw_update_btn.pull = digitalio.Pull.DOWN

serial: usb_cdc.Serial = usb_cdc.data  # type: ignore

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
    board.GP17,
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

rotary_encoder = HIDRotaryEncoder(board.GP18, board.GP19, 4)

led_out_pins = (
    board.GP1,
    board.GP3,
    board.GP5,
    board.GP7,
    board.GP9,
    board.GP11,
    board.GP13,
    board.GP15,
)
led_out_ids = range(1, 9)
led_hids = [HIDLEDOutput(pin, hid_id) for pin, hid_id in zip(led_out_pins, led_out_ids)]

device: usb_hid.Device = find_device(usb_hid.devices, usage_page=0x01, usage=0x05)  # type: ignore

send_errors = 0
last_run = 0
last_digital = 0
last_analog = [0] * len(analog_hids)
last_rotary = 0

while True:
    if fw_update_btn.value:
        microcontroller.reset()

    if time.monotonic_ns() >= last_run + 10_000_000:
        report = bytearray(REPORT_SIZE)

        digital_bits: int = 0
        for digital_in in digital_hids:
            digital_bits |= digital_in.state << (digital_in.id - 1)

        rotary_state = rotary_encoder.state
        analog_state = [analog_in.state for analog_in in analog_hids]

        changed = (
            last_digital != digital_bits
            or last_rotary != rotary_state
            or any(abs(new - old) > 41 for (old, new) in zip(last_analog, analog_state))
        )

        if changed:
            if DEBUG_MODE:
                print(f"[{time.monotonic_ns()}] Report updated")

            last_digital = digital_bits
            last_analog = analog_state
            last_rotary = rotary_state

            struct.pack_into(
                "<Hhhhh",
                report,
                0,
                digital_bits,
                *analog_state,
                rotary_state,
            )

            try:
                device.send_report(report)
                last_run = time.monotonic_ns()
                if send_errors > 0:
                    if DEBUG_MODE:
                        print("Sent")
                send_errors = 0
            except OSError as e:
                send_errors = send_errors + 1
                if DEBUG_MODE:
                    print(f"send_report: {e} (error count {send_errors})")

    if serial.connected and serial.in_waiting >= 2:
        if DEBUG_MODE:
            print(f"[{time.monotonic_ns()}] Rcvd relay data")
            print(f"serial waiting: {serial.in_waiting}")
        output_states = bytearray(2)

        while serial.in_waiting > 0:
            serial.readinto(output_states)

        led_bits: int = struct.unpack_from("<H", output_states)[0]
        for led in led_hids:
            led.state = (led_bits >> (2 * (led.id - 1))) & 0b11  # type: ignore

    for led in led_hids:
        led.run()
