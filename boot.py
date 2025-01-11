import os

import board
import digitalio
import storage
import supervisor
import usb_cdc
import usb_hid

supervisor.set_usb_identification("Iron Tigers", "TigerPad Controller")

debug_button = digitalio.DigitalInOut(board.GP16)
debug_button.pull = digitalio.Pull.DOWN

if not (bool(os.getenv("DEBUG_MODE", 1)) or debug_button.value):
    storage.disable_usb_drive()
    usb_cdc.disable()
else:
    usb_cdc.enable(data=True)


# fmt: off
GAMEPAD_REPORT_DESCRIPTOR = bytes((
    0x05, 0x01,                    # USAGE_PAGE (Generic Desktop)
    0x09, 0x05,                    # USAGE (Game Pad)
    0xA1, 0x01,                    # COLLECTION (Application)
    0xA1, 0x00,                    #   COLLECTION (Physical)
    0x85, 0x01,                    #     REPORT_ID (1)
    0x05, 0x09,                    #     USAGE_PAGE (Button)
    0x1B, 0x01, 0x00, 0x09, 0x00,  #     USAGE_MINIMUM (Button:Button 1)
    0x2B, 0x0A, 0x00, 0x09, 0x00,  #     USAGE_MAXIMUM (Button:Button 10)
    0x15, 0x00,                    #     LOGICAL_MINIMUM (0)
    0x25, 0x01,                    #     LOGICAL_MAXIMUM (1)
    0x95, 0x0A,                    #     REPORT_COUNT (10)
    0x75, 0x01,                    #     REPORT_SIZE (1)
    0x81, 0x02,                    #     INPUT (Data,Var,Abs)
    0x75, 0x06,                    #     REPORT_SIZE (6)
    0x95, 0x01,                    #     REPORT_COUNT (1)
    0x81, 0x01,                    #     INPUT (Cnst,Ary,Abs)
    0xC0,                          #   END_COLLECTION
    0xC0,                          # END_COLLECTION
))
# fmt: on

hid_gamepad = usb_hid.Device(
    report_descriptor=GAMEPAD_REPORT_DESCRIPTOR,
    usage_page=0x01,
    usage=0x05,
    report_ids=(1,),
    in_report_lengths=(2,),
    out_report_lengths=(0,),
)
