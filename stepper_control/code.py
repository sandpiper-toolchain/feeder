"""Sediment feeder controller for Raspberry Pi Pico.

Main application firmware for the laboratory sediment feeder. Manages stepper motor
control, displays real-time status on OLED, handles user input from rotary encoder
and buttons, and accepts remote commands via USB serial for PC integration.

SPDX-FileCopyrightText: 2021 John Furcean
SPDX-License-Identifier: MIT
Modified by Eric Barefoot MIT LICENSE 2025
"""

import board
from time import sleep, monotonic
import digitalio

# USB serial endpoints for remote control and telemetry
from usb_cdc import console as conser
from usb_cdc import data as dataline

from supervisor import runtime

# Disable autoreload to prevent interruption during experiments
runtime.autoreload = False
print(f"AutoReload is {runtime.autoreload=}")

# Stepper motor control (GPIO pins GP18=step, GP19=direction, GP22=enable)
from stepper import Stepper

from adafruit_seesaw import rotaryio, seesaw
from adafruit_seesaw import digitalio as ssdio

s = Stepper(step_pin=board.GP18, dir_pin=board.GP19, ena_pin=board.GP22, steps_per_rev=400)
# TODO: Make steps_per_rev configurable to support different motor types

# Display and input hardware (I2C bus on GP4=SDA, GP5=SCL)
import displayio
import i2cdisplaybus
import adafruit_displayio_ssd1306
import terminalio
from adafruit_display_text import label

displayio.release_displays()

import busio
i2c = busio.I2C(scl=board.GP5, sda=board.GP4)

# Seesaw breakout (addr 0x36) hosts rotary encoder and knob button
seesaw = seesaw.Seesaw(i2c, addr=0x36)

seesaw_product = (seesaw.get_version() >> 16) & 0xFFFF
if seesaw_product != 4991:
    print("Wrong firmware loaded?  Expected 4991")

# Rotary encoder knob button (on seesaw pin 24)
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)
button = ssdio.DigitalIO(seesaw, 24)
button_held = False

# Rotary encoder for speed control
encoder = rotaryio.IncrementalEncoder(seesaw)

# Control buttons on Pico GPIO
# Button A (GP15): Toggle motor enable
# Button B (GP10): Change direction
# Button C (GP8): Stop/exit program
button_a = digitalio.DigitalInOut(board.GP15)
button_a.direction = digitalio.Direction.INPUT
button_a.pull = digitalio.Pull.DOWN

button_b = digitalio.DigitalInOut(board.GP10)
button_b.direction = digitalio.Direction.INPUT
button_b.pull = digitalio.Pull.DOWN

button_c = digitalio.DigitalInOut(board.GP8)
button_c.direction = digitalio.Direction.INPUT
button_c.pull = digitalio.Pull.DOWN

# led = digitalio.DigitalInOut(board.GP25)
# led.direction = digitalio.Direction.OUTPUT

# yellow = digitalio.DigitalInOut(board.GP18)
# yellow.direction = digitalio.Direction.OUTPUT

# redled = digitalio.DigitalInOut(board.GP19)
# redled.direction = digitalio.Direction.OUTPUT

def new_speed(p, spd=1/50):
    """Convert encoder position to motor speed (RPS).

    Maps encoder steps to speed; default spd=1/50 means each encoder step = 0.02 RPS.
    """
    return p * spd

s.dir_pin.value = False  # Set initial direction to clockwise

def wait_pin_change(pin):
    """Wait for a button pin to stabilize (debounce over 20ms)."""
    cur_value = pin.value
    active = 0
    while active < 20:
        if pin.value != cur_value:
            active += 1
        else:
            active = 0
        sleep(0.001)

# Performance timing
t0 = monotonic()
n = 16000
encoder.position = 4
position = encoder.position
s.speed_rps(new_speed(position))
last_position = position

# OLED display setup (SSD1306, 128x64, I2C addr 0x3D)
WIDTH = 128
HEIGHT = 64
BORDER = 5

display_bus = i2cdisplaybus.I2CDisplayBus(i2c, device_address=0x3D)
display = adafruit_displayio_ssd1306.SSD1306(display_bus, width=WIDTH, height=HEIGHT)

# Display group for UI elements
splash = displayio.Group()
display.root_group = splash

color_bitmap = displayio.Bitmap(WIDTH, HEIGHT, 1)
color_palette = displayio.Palette(1)
color_palette[0] = 0xFFFFFF  # White

# bg_sprite = displayio.TileGrid(color_bitmap, pixel_shader=color_palette, x=0, y=0)
# # splash.append(bg_sprite)

# # Draw a smaller inner rectangle
# inner_bitmap = displayio.Bitmap(WIDTH - BORDER * 2, HEIGHT - BORDER * 2, 1)
# inner_palette = displayio.Palette(1)
# inner_palette[0] = 0x000000  # Black
# inner_sprite = displayio.TileGrid(inner_bitmap, pixel_shader=inner_palette, x=BORDER, y=BORDER)
# splash.append(inner_sprite)

# Initialize display with status information
text = f"Feeder initialized."
text_area = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=10)
splash.append(text_area)

sleep(2)
splash.remove(text_area)

# Display labels (updated in real-time in the main loop):
# - Speed (RPS): controlled by rotary encoder or serial command
# - Motor running status: ON/OFF
# - Motor enable status: ON/OFF (soft disable)
# - Direction: CW (clockwise, direction=-1) or CCW (counter-clockwise, direction=1)

text = f"speed: {round(s.rps, 3)} Hz"
speed_splash = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=8)
splash.append(speed_splash)

ison = lambda x: "ON" if x else "OFF" if not x else "Problem..."

text = f"motor is: {ison(s.running)}"
onoff_splash = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=18)
splash.append(onoff_splash)

isenabled = lambda x: "ON" if x else "OFF" if not x else "Problem..."

text = f"enable pin is: {isenabled(s.is_enabled())}"
ena_splash = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=38)
splash.append(ena_splash)

direct = lambda x: "CW" if x < 0 else "CCW" if x > 0 else "Problem..."

text = f"direction is: {direct(s.direction)}"
direction_splash = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=28)
splash.append(direction_splash)

# sleep(2)
# splash.remove(speed_splash)

strcontrolinput = "speed=0.5"  # default speed for testing

print(f"Rice feeder initialized.\nRunning: {s.running}\n")
print(f"Serial connection: {conser.connected}\n")  # type: ignore[reportUnknownVariableType]

# Main control loop
# Handles three input sources:
#   1. Rotary encoder: adjust speed (encoder position -> speed_rps)
#   2. Hardware buttons: toggle motor, change direction, enable/disable, exit
#   3. USB serial commands: remote control from PC (see command handlers below)
# Display updates in real-time whenever state changes.

while True:
    # Read encoder position (controls speed)
    position = encoder.position

    # Check for serial commands from PC
    # Supported commands:
    #   speed=<float>           Set speed in RPS (e.g., speed=0.5)
    #   toggle                  Start/stop motor
    #   switch_direction        Reverse motor direction
    #   enable                  Enable motor driver
    #   disable                 Disable motor driver
    #   get:speed               Query current speed
    #   get:direction           Query current direction (-1=CW, 1=CCW)
    #   get:enabled             Query enable state
    #   get:running             Query running state
    #   stop                    Exit program
    if runtime.serial_bytes_available > 0:
        print("Serial data available")
        controlinput = conser.readline() # type: ignore
        strcontrolinput = controlinput.decode() # type: ignore
        print(f"Received data: {strcontrolinput.split('=')}")

    if position != last_position:
        if position < 0:
            position = 0
            encoder.position = position
        s.speed_rps(new_speed(position))
        # print(f"Position: {position}")
        # print(f"speed: {s.steps_per_sec/s.steps_per_rev} rps")

        # update the speed label
        text = f"speed: {round(s.rps, 3)} Hz"
        speed_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=8)
        splash.remove(speed_splash)
        splash.append(speed_update)
        speed_splash = speed_update

        last_position = position
    elif strcontrolinput.split("=")[0] == 'speed':
        # try:
        speed = float(strcontrolinput.split("=")[1])
        position = speed * 50  # update encoder position index to match speed for display
        s.speed_rps(speed)
        print(f"Speed set to: {speed} rps")
        text = f"speed: {round(s.rps, 3)} Hz"
        strcontrolinput = ""
        speed_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=8)
        splash.remove(speed_splash)
        splash.append(speed_update)
        speed_splash = speed_update
        # except ValueError:
            # print("Invalid speed value received")

    # Rotary encoder knob button: toggle motor start/stop
    if not button.value and not button_held:
        button_held = True
        if not s.running:
            print('start')
            s.start()
        else:
            s.stop()
            print('stop')
        text = f"motor is: {ison(s.running)}"
        onoff_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=18)
        splash.remove(onoff_splash)
        splash.append(onoff_update)
        onoff_splash = onoff_update

    if button.value and button_held:
        button_held = False

    if strcontrolinput.strip() == 'toggle':
        if not s.running:
            print('start')
            s.start()
        else:
            s.stop()
            print('stop')
        text = f"motor is: {ison(s.running)}"
        onoff_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=18)
        splash.remove(onoff_splash)
        splash.append(onoff_update)
        onoff_splash = onoff_update
        strcontrolinput = ""
    
    # Button B (GP10): reverse motor direction
    if button_b.value:
        wait_pin_change(button_b)
        print("Button B Pressed - change direction")
        s.change_direction()
        text = f"direction is: {direct(s.direction)}"
        direction_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=28)
        splash.remove(direction_splash)
        splash.append(direction_update)
        direction_splash = direction_update

    if strcontrolinput.strip() == 'switch_direction':
        s.change_direction()
        text = f"direction is: {direct(s.direction)}"
        direction_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=28)
        splash.remove(direction_splash)
        splash.append(direction_update)
        direction_splash = direction_update
        strcontrolinput = ""

    # Button A (GP15): toggle motor enable (soft disable, releases coil torque)
    if button_a.value:
        wait_pin_change(button_a)
        print("Button A Pressed - toggle enable pin")
        e = s.ena_pin.value
        s.enable(bool(e^1))
        text = f"enable pin is: {isenabled(s.is_enabled())}"
        ena_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=38)
        splash.remove(ena_splash)
        splash.append(ena_update)
        ena_splash = ena_update

    if strcontrolinput.strip() == 'enable':
        s.enable(True)
        text = f"enable pin is: {isenabled(s.is_enabled())}"
        ena_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=38)
        splash.remove(ena_splash)
        splash.append(ena_update)
        ena_splash = ena_update
        strcontrolinput = ""
    elif strcontrolinput.strip() == 'disable':
        s.enable(False)
        text = f"enable pin is: {isenabled(s.is_enabled())}"
        ena_update = label.Label(terminalio.FONT, text=text, color=0xFFFFFF, x=0, y=38)
        splash.remove(ena_splash)
        splash.append(ena_update)
        ena_splash = ena_update
        strcontrolinput = ""

    # Button C (GP8): exit program
    if button_c.value:
        wait_pin_change(button_c)
        print("Button C Pressed - stop program")
        break

    # Serial command: stop program
    if strcontrolinput.strip() == 'stop':
        print("stop program")
        strcontrolinput = ""
        break

    # Serial query commands: return current state via data endpoint
    if strcontrolinput.split(":")[0] == 'get':
        if strcontrolinput.split(":")[1].strip() == 'speed':
            dataline.write(f"{s.rps}\n".encode()) # type: ignore
        elif strcontrolinput.split(":")[1].strip() == 'direction':
            dataline.write(f"{s.direction}\n".encode()) # type: ignore
        elif strcontrolinput.split(":")[1].strip() == 'enabled':
            dataline.write(f"{s.is_enabled()}\n".encode()) # type: ignore
        elif strcontrolinput.split(":")[1].strip() == 'running':
            dataline.write(f"{s.running}\n".encode()) # type: ignore
        else:
            print("Unknown get command")
        strcontrolinput = ""

    n += 1

# Performance diagnostics: total runtime and cycle time
t1 = monotonic()

print(n)
print(f"time elapsed: {t1-t0}\ntime per cycle = {1000 * (t1-t0)/n}ms")
