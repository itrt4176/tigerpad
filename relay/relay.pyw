#!/usr/bin/env python3

import atexit
import os
import platform
import struct
import sys
import webbrowser
from functools import cache
from pathlib import Path
from signal import SIGINT, SIGTERM, signal
from typing import Callable

import click
import cloup
import serial
from ntcore import (
    IntegerSubscriber,
    NetworkTableInstance,
    PubSubOptions,
)
from PIL import Image
from PIL.ImageDraw import Draw
from pystray import Icon as icon
from pystray import Menu as menu
from pystray import MenuItem as item
from pystray._base import Icon
from serial import SerialException
from serial.tools import list_ports
from serial.tools.list_ports_common import ListPortInfo

try:
    from _version import _VERSION  # type: ignore

    VERSION: str = _VERSION
except ImportError:
    VERSION = "dev build"

echo = click.echo

pid_file = Path("relay.pid")

with pid_file.open("w") as f:
    f.write(f"{os.getpid()}")

match platform.system():
    case "Windows":
        DEFAULT_PORT = "COM41"
    case "Darwin":
        DEFAULT_PORT = "/dev/cu.usbmodem144403"
    case "Linux":
        DEFAULT_PORT = "/dev/ttyTigerPad"
    case _:
        DEFAULT_PORT = None


tray_img = Image.open("relay/res/itrt_paw_64x64.png")
supports_radio = icon.HAS_MENU_RADIO

ser = serial.Serial()


def ser_connected_str(_):
    return f"TigerPad: {'connected' if ser.is_open else 'disconnected'}"


nt_host: str | None
nt_team: int

do_stop: Callable


@cloup.command()
@cloup.argument("serial_port", default=DEFAULT_PORT)
@cloup.option_group(
    "NetworkTables Connection",
    cloup.option("--host", "-H", help="NetworkTables server address"),
    cloup.option("--team", "-t", default=4176, help="Team number", show_default=True),
    help="The host option will take priority over the team option",
)
def main(serial_port: str, host: str | None, team: int):
    global ser
    ser.port = serial_port
    ser.baudrate = 115200

    global nt_host
    global nt_team
    nt_host = host
    nt_team = team

    tray_icon: Icon = icon(
        "itrt_relay_tray",
        get_state_icon(nt_inst.isConnected(), ser.is_open),
        "TigerPad Relay",
    )

    tray_icon.run(relay)


nt_inst = NetworkTableInstance.getDefault()


def nt_connected_str(_):
    return f"NetworkTables: {'connected' if nt_inst.isConnected() else 'disconnected'}"


leds_table = nt_inst.getTable("tigerpad").getSubTable("leds")

listener_map: dict[int, int] = {}
subscribers: list[IntegerSubscriber] = []

led_state: int = 0b1010101010101010


def relay(tray_icon: Icon):
    """Relay LED commands from NetworkTables to the TigerPad over serial."""
    for led_id in range(0, 8):
        topic = leds_table.getSubTable(f"{led_id}").getIntegerTopic("value")
        sub = topic.subscribe(
            1, PubSubOptions(periodic=0.01, sendAll=True, excludeSelf=True)
        )
        subscribers.append(sub)

    nt_inst.startClient4("tigerpad-relay")

    if nt_host:
        nt_inst.setServer(nt_host)
    else:
        nt_inst.setServerTeam(nt_team, NetworkTableInstance.kDefaultPort4)

    nt_inst.startDSClient()

    send_serial = False

    global led_state

    def get_port_menu_name(port: ListPortInfo) -> str:
        dev = port.device
        sep = " - " if port.manufacturer or port.product else ""
        manufacturer = f"{port.manufacturer} " if port.manufacturer else ""
        product = port.product if port.product else ""

        return dev + sep + manufacturer + product

    def set_selected_port(_, menu_item: item) -> None:
        global ser

        if ser.is_open:
            ser.close()

        ser.port = menu_item.text.split()[0]  # type: ignore

    def is_selected_port(menu_item: item) -> bool:
        global ser
        state: bool = ser.port == menu_item.text.split()[0]  # type: ignore
        return state

    def ser_is_open(_) -> bool:
        global ser
        return ser.is_open

    run = True

    def stop():
        nonlocal run
        run = False

    global do_stop
    do_stop = stop

    tray_icon.menu = menu(
        item(nt_connected_str, action=lambda: None, enabled=False),
        item(ser_connected_str, action=lambda: None, enabled=False),
        menu.SEPARATOR,
        item(
            "Serial Port",
            menu(
                lambda: (
                    item(
                        get_port_menu_name(port),
                        action=set_selected_port,
                        checked=is_selected_port,
                        radio=supports_radio,
                    )
                    for port in list_ports.comports(True)
                )
            ),
        ),
        menu.SEPARATOR,
        item("Quit", lambda _: do_stop()),
        menu.SEPARATOR,
        item(
            VERSION,
            action=lambda: webbrowser.open(
                "https://github.com/itrt4176/tigerpad/releases/latest"
            ),
            enabled=True,
        ),
    )

    tray_icon.visible = True

    last_nt = nt_inst.isConnected()
    last_ser = ser.is_open

    while run:
        if ser.port not in [port.device for port in list_ports.comports(True)]:
            ser.close()

        if not ser.is_open:
            try:
                ser.open()
                send_serial = True
            except SerialException:
                pass

        if last_nt != nt_inst.isConnected() or last_ser != ser.is_open:
            last_nt = nt_inst.isConnected()
            last_ser = ser.is_open
            tray_icon.icon = get_state_icon(nt_connected=last_nt, tp_connected=last_ser)
            tray_icon.update_menu()

        for led_id, sub in enumerate(subscribers):
            state_updates = sub.readQueue()

            if len(state_updates) > 0:
                for state in state_updates:
                    new_state = state.value

                    bit_idx = 2 * led_id
                    mask = ~((1 << (bit_idx + 1)) | (1 << bit_idx))
                    led_state &= mask
                    led_state |= new_state << bit_idx

                send_serial = True

        try:
            if send_serial and ser.is_open:
                state_output = bytearray(2)
                struct.pack_into("<H", state_output, 0, led_state)
                ser.write(state_output)
                ser.flush()
                send_serial = False
        except SerialException:
            ser.close()

    tray_icon.stop()


@cache
def get_state_icon(nt_connected: bool, tp_connected: bool) -> Image.Image:
    if not tp_connected:
        state_img = tray_img.convert("LA").convert("RGBA")
    else:
        state_img = tray_img.copy()

    img_draw = Draw(state_img, "RGBA")
    start = tuple(coord * 2 // 3 for coord in state_img.size)

    tp_color = "#00ff00" if nt_connected else "#ff0000"

    img_draw.ellipse([start, state_img.size], tp_color, "#ffffff00", 0)

    return state_img


@atexit.register
def cleanup():
    do_stop()
    if ser.is_open:
        ser.close()
    if pid_file.exists():
        os.remove(pid_file)


def sigint_handler(*args, **kwargs):
    sys.exit()


if __name__ == "__main__":
    signal(SIGINT, sigint_handler)
    signal(SIGTERM, sigint_handler)
    main()
