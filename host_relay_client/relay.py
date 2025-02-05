#!/usr/bin/env python3

import atexit
import os
import platform
import struct
import sys
from pathlib import Path
from signal import SIGINT, SIGTERM, signal

import click
import cloup
import serial
from ntcore import (
    IntegerSubscriber,
    NetworkTableInstance,
    PubSubOptions,
)
from serial import SerialException

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

ser = serial.Serial()

nt_inst = NetworkTableInstance.getDefault()
leds_table = nt_inst.getTable("tigerpad").getSubTable("leds")

listener_map: dict[int, int] = {}
subscribers: list[IntegerSubscriber] = []

led_state: int = 0b1010101010101010


@cloup.command()
@cloup.argument("serial_port", default=DEFAULT_PORT)
@cloup.option_group(
    "NetworkTables Connection",
    cloup.option("--host", "-H", help="NetworkTables server address"),
    cloup.option("--team", "-t", default=4176, help="Team number", show_default=True),
    help="The host option will take priority over the team option",
)
def relay(serial_port: str, host: str | None, team: int):
    """Relay LED commands from NetworkTables to the TigerPad over serial."""
    for led_id in range(0, 8):
        topic = leds_table.getSubTable(f"{led_id}").getIntegerTopic("value")
        sub = topic.subscribe(
            1, PubSubOptions(periodic=0.01, sendAll=True, excludeSelf=True)
        )
        subscribers.append(sub)

    nt_inst.startClient4("tigerpad-relay")

    if host:
        nt_inst.setServer(host)
    else:
        nt_inst.setServerTeam(team, NetworkTableInstance.kDefaultPort4)

    nt_inst.startDSClient()

    global ser
    ser.port = serial_port
    ser.baudrate = 115200
    send_serial = False

    global led_state

    while True:
        if not ser.is_open:
            try:
                ser.open()
                send_serial = True
            except SerialException:
                pass

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


def sigint_handler(*args, **kwargs):
    sys.exit()


@atexit.register
def cleanup():
    if ser.is_open:
        ser.close()
    if pid_file.exists():
        os.remove(pid_file)


if __name__ == "__main__":
    signal(SIGINT, sigint_handler)
    signal(SIGTERM, sigint_handler)
    relay()
