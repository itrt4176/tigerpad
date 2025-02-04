#!/usr/bin/env python3

import platform
from signal import signal, SIGINT
import struct
import sys

import click
import cloup
from cloup.constraints import mutually_exclusive
from ntcore import EventFlags, IntegerSubscriber, MultiSubscriber, NetworkTableInstance, NetworkTableListener, Event as NTEvent, NetworkTableListenerPoller, PubSubOptions, Subscriber, Topic, ValueEventData
from serial import Serial, SerialException
import serial


echo = click.echo

match platform.system():
    case 'Windows':
        DEFAULT_PORT = 'COM41'
    case 'Darwin':
        DEFAULT_PORT = '/dev/cu.usbmodem144403'
    case 'Linux':
        DEFAULT_PORT = '/dev/ttyTigerPad'
    case _:
        DEFAULT_PORT = None

ser = serial.Serial()

nt_inst = NetworkTableInstance.getDefault()
leds_table = nt_inst.getTable('tigerpad').getSubTable('leds')
listener = NetworkTableListenerPoller()
# event_mask = EventFlags.kImmediate | EventFlags.kValueAll
event_mask = EventFlags.kTopic | EventFlags.kConnection | EventFlags.kLogMessage | EventFlags.kTimeSync

listener_map: dict[int, int] = {}
subscribers: list[IntegerSubscriber] = []

led_state: int = 0b1010101010101010

@cloup.command()
@cloup.argument('serial_port', default=DEFAULT_PORT)
@cloup.option_group(
    'NetworkTables Connection',
    cloup.option('--host', '-H', help='NetworkTables server address'),
    cloup.option('--team', '-t', default=4176, help='Team number', show_default=True),
    help='The host option will take priority over the team option'
)
def relay(serial_port: str, host: str | None, team: int):
    '''Relay LED commands from NetworkTables to the TigerPad over serial.'''
    for led_id in range(0,8):
        topic = leds_table.getSubTable(f'{led_id}').getIntegerTopic('value')
        sub = topic.subscribe(1, PubSubOptions(periodic=0.01, sendAll=True, excludeSelf=True))
        subscribers.append(sub)
        # handle = listener.addListener([f'/tigerpad/leds/{led_id}/0'], event_mask)
        # listener_map[handle] = led_id

    # print(listener_map)

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
                    echo(f'New state for {led_id}: {state.value}')
                    new_state = state.value

                    bit_idx = 2 * led_id
                    mask = ~((1 << (bit_idx + 1)) | (1 << bit_idx))
                    echo(f'mask: {bin(mask)}')
                    led_state &= mask
                    led_state |= new_state << bit_idx
                    echo(f'led_state: {bin(led_state)}')
                
                send_serial = True

        if send_serial and ser.is_open:
            state_output = bytearray(2)
            struct.pack_into('<H', state_output, 0, led_state)
            ser.write(state_output)
            ser.flush()
            send_serial = False
            echo("Serial sent")


def sigint_handler(*args, **kwargs):
    if ser.is_open:
        ser.close()
    listener.close()
    sys.exit()

if __name__ == '__main__':
    signal(SIGINT, sigint_handler)
    relay()
