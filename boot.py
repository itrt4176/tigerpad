import os

import board
import digitalio
import storage
import supervisor
import usb_cdc

supervisor.set_usb_identification("Iron Tigers", "TigerPad Controller")

debug_button = digitalio.DigitalInOut(board.GP16)
debug_button.pull = digitalio.Pull.DOWN

if not bool(os.getenv("DEBUG_MODE", 1)) or not debug_button.value:
    storage.disable_usb_drive()
    usb_cdc.disable()
else:
    usb_cdc.enable(data=True)
