import os

import board
from constants import FW_UPDATE_PIN
import digitalio
import storage
import supervisor
import usb_cdc
import usb_hid
import usb_midi

supervisor.runtime.autoreload = False
supervisor.set_usb_identification("Iron Tigers", "TigerPad Controller", 0x4176, 2025)
usb_hid.set_interface_name("TigerPad Controller") # type: ignore

fw_update_button = digitalio.DigitalInOut(FW_UPDATE_PIN)
fw_update_button.pull = digitalio.Pull.DOWN

usb_midi.disable()

if not (bool(os.getenv("DEBUG_MODE", 1)) or fw_update_button.value):
    storage.disable_usb_drive()
    usb_cdc.enable(console=False, data=True)
else:
    usb_cdc.enable(console=True, data=True)


# fmt: off
GAMEPAD_REPORT_DESCRIPTOR = bytes((
    0x05, 0x01,                    # USAGE_PAGE (Generic Desktop)
    0x09, 0x05,                    # USAGE (Game Pad)
    0xa1, 0x01,                    # COLLECTION (Application)
    0xa1, 0x00,                    #   COLLECTION (Physical)
    0x05, 0x09,                    #     USAGE_PAGE (Button)
    0x19, 0x01,                    #     USAGE_MINIMUM (Button 1)
    0x29, 0x0a,                    #     USAGE_MAXIMUM (Button 10)
    0x15, 0x00,                    #     LOGICAL_MINIMUM (0)
    0x25, 0x01,                    #     LOGICAL_MAXIMUM (1)
    0x95, 0x0a,                    #     REPORT_COUNT (10)
    0x75, 0x01,                    #     REPORT_SIZE (1)
    0x81, 0x02,                    #     INPUT (Data,Var,Abs)
    0x95, 0x01,                    #     REPORT_COUNT (1)
    0x75, 0x06,                    #     REPORT_SIZE (6)
    0x81, 0x03,                    #     INPUT (Cnst,Var,Abs)
    0xc0,                          #   END_COLLECTION
    0x05, 0x01,                    #   USAGE_PAGE (Generic Desktop)
    0xa1, 0x00,                    #   COLLECTION (Physical)
    0x09, 0x31,                    #     USAGE (Y)
    0x16, 0x00, 0xf8,              #     LOGICAL_MINIMUM (-2048)
    0x26, 0xff, 0x07,              #     LOGICAL_MAXIMUM (2047)
    0x75, 0x10,                    #     REPORT_SIZE (16)
    0x95, 0x01,                    #     REPORT_COUNT (1)
    0x81, 0x02,                    #     INPUT (Data,Var,Abs)
    0xc0,                          #   END_COLLECTION
    0xa1, 0x00,                    #   COLLECTION (Physical)
    0x09, 0x34,                    #     USAGE (Ry)
    0x16, 0x00, 0xf8,              #     LOGICAL_MINIMUM (-2048)
    0x26, 0xff, 0x07,              #     LOGICAL_MAXIMUM (2047)
    0x75, 0x10,                    #     REPORT_SIZE (16)
    0x95, 0x01,                    #     REPORT_COUNT (1)
    0x81, 0x02,                    #     INPUT (Data,Var,Abs)
    0xc0,                          #   END_COLLECTION
    0xa1, 0x00,                    #   COLLECTION (Physical)
    0x09, 0x32,                    #     USAGE (Z)
    0x16, 0x00, 0xf8,              #     LOGICAL_MINIMUM (-2048)
    0x26, 0xff, 0x07,              #     LOGICAL_MAXIMUM (2047)
    0x75, 0x10,                    #     REPORT_SIZE (16)
    0x95, 0x01,                    #     REPORT_COUNT (1)
    0x81, 0x02,                    #     INPUT (Data,Var,Abs)
    0xc0,                          #   END_COLLECTION
    0xa1, 0x00,                    #   COLLECTION (Physical)
    0x09, 0x37,                    #     USAGE (Dial)
    0x15, 0x9c,                    #     LOGICAL_MINIMUM (-100)
    0x25, 0x64,                    #     LOGICAL_MAXIMUM (100)
    0x75, 0x08,                    #     REPORT_SIZE (8)
    0x95, 0x01,                    #     REPORT_COUNT (1)
    0x81, 0x02,                    #     INPUT (Data,Var,Abs)
    0xc0,                          #   END_COLLECTION
    0xc0                           # END_COLLECTION
))
# fmt: on

hid_gamepad = usb_hid.Device(
    report_descriptor=GAMEPAD_REPORT_DESCRIPTOR,
    usage_page=0x01,
    usage=0x05,
    report_ids=(0,),
    in_report_lengths=(9,),
    out_report_lengths=(0,),
)

usb_hid.enable((hid_gamepad,))
