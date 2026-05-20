# Stepper Motor Sediment Feeder

> **Note:** This README was generated with AI assistance. While it reflects the actual code and hardware used in this project, some details (library versions, port names, wiring notes) may be inaccurate or become outdated. Verify against the source files and your hardware before following any instructions.

A CircuitPython firmware package for the Raspberry Pi Pico that drives a laboratory sediment feeder. A stepper motor controls a hopper/auger mechanism to dispense sediment at a programmable, adjustable rate. Speed and direction can be set manually via a rotary encoder and hardware buttons, or remotely from a PC over USB serial.

---

## Hardware Components

| Component | Description | Notes |
|---|---|---|
| Raspberry Pi Pico | RP2040 microcontroller | Standard Pico (not Pico W) |
| Stepper motor | NEMA stepper with step/dir/enable driver | Tested at 400 steps/rev |
| Stepper motor driver | A4988, DRV8825, or similar | Must expose STEP, DIR, and ENA pins |
| [Adafruit I2C Rotary Encoder Breakout](https://www.adafruit.com/product/4991) | Seesaw-based encoder with button | Product ID 4991, I2C addr `0x36` |
| SSD1306 OLED display | 128×64 monochrome, I2C | I2C addr `0x3D` |
| 3× momentary push buttons | Through-hole or panel-mount | Pulled down internally via Pico GPIO |

---

## Pin Wiring

| Pico Pin | Function |
|---|---|
| GP4 (SDA) | I2C data — shared bus for OLED and encoder |
| GP5 (SCL) | I2C clock — shared bus for OLED and encoder |
| GP8 | Button C — stop/exit program |
| GP9 | OLED reset |
| GP10 | Button B — reverse motor direction |
| GP15 | Button A — toggle motor enable |
| GP18 | Stepper STEP (PWM output) |
| GP19 | Stepper DIR |
| GP22 | Stepper ENA |

The three GPIO buttons connect between the pin and GND; the firmware configures them with internal pull-downs, so they read HIGH when pressed.

---

## Software Requirements

### CircuitPython

Install **CircuitPython 9.2.x** on the Pico:

1. Download the UF2 from [circuitpython.org](https://circuitpython.org/board/raspberry_pi_pico/).
2. Hold BOOTSEL on the Pico and plug in USB; drag the UF2 to the `RPI-RP2` drive.

### Libraries

Copy the following from the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries) into the `lib/` folder on the Pico:

| Library | Source |
|---|---|
| `adafruit_seesaw/` | Adafruit CircuitPython Seesaw |
| `adafruit_displayio_ssd1306.py` | Adafruit CircuitPython DisplayIO SSD1306 |
| `adafruit_display_text/` | Adafruit CircuitPython Display Text |
| `adafruit_bus_device/` | Adafruit CircuitPython BusDevice |
| `adafruit_motor/` | Adafruit CircuitPython Motor |
| `adafruit_pixelbuf.mpy` | Adafruit CircuitPython Pixelbuf |
| `adafruit_ht16k33/` | Adafruit CircuitPython HT16K33 |

The following are built into CircuitPython and require no separate install: `pwmio`, `digitalio`, `displayio`, `busio`, `supervisor`, `usb_cdc`.

---

## Project Files

| File | Purpose |
|---|---|
| `boot.py` | Runs at power-on; enables dual USB CDC endpoints (console + data) |
| `stepper.py` | `Stepper` class — low-level motor control via PWM and GPIO |
| `code.py` | Main application — display, encoder, buttons, serial command loop |

---

## Getting Started

1. Wire up the hardware per the pin table above.
2. Flash CircuitPython and copy the `lib/` folder to the Pico.
3. Copy `boot.py`, `stepper.py`, and `code.py` to the root of the Pico (`CIRCUITPY` drive).
4. The Pico will reboot and start the feeder firmware automatically.

The OLED will show **"Feeder initialized."** briefly, then display live status:

```
speed: 0.080 Hz
motor is: OFF
direction is: CW
enable pin is: ON
```

---

## Manual Controls

| Control | Action |
|---|---|
| Rotate encoder knob | Increase / decrease motor speed |
| Press encoder knob | Toggle motor start / stop |
| Button A (GP15) | Toggle motor enable (releases coil torque when OFF) |
| Button B (GP10) | Reverse motor direction (CW ↔ CCW) |
| Button C (GP8) | Exit the program (stops motor cleanly) |

---

## PC-Side Python Setup

To send commands from a PC you need the `pyserial` package. Using a virtual environment keeps this isolated from your system Python.

### Create and activate a venv

**Linux / macOS:**
```bash
python3 -m venv feeder-env
source feeder-env/bin/activate
```

**Windows:**
```bat
python -m venv feeder-env
feeder-env\Scripts\activate
```

### Install dependencies

```bash
pip install pyserial
```

To save the environment for later:
```bash
pip freeze > requirements.txt
```

To restore it on another machine:
```bash
pip install -r requirements.txt
```

### Find the correct serial ports

When the Pico is plugged in, it will appear as two serial ports — one for the console and one for data. To find them:

**Linux:**
```bash
ls /dev/ttyACM*
# typically /dev/ttyACM0 (console) and /dev/ttyACM1 (data)
```

**macOS:**
```bash
ls /dev/tty.usbmodem*
```

**Windows:** Open Device Manager and look under **Ports (COM & LPT)** for two new COM ports.

---

## Remote Control via USB Serial

The Pico exposes two USB serial ports when connected to a PC:

- **Console port** — receives commands and prints debug output.
- **Data port** — returns telemetry responses to `get:` queries.

Send commands as plain text lines (terminated with `\n`) to the **console port**.

### Commands

| Command | Description |
|---|---|
| `speed=<float>` | Set motor speed in rotations per second (e.g. `speed=0.5`) |
| `toggle` | Start or stop the motor |
| `switch_direction` | Reverse motor direction |
| `enable` | Enable motor driver |
| `disable` | Disable motor driver (releases torque) |
| `get:speed` | Query current speed (RPS) — response on data port |
| `get:direction` | Query direction (`-1`=CW, `1`=CCW) — response on data port |
| `get:enabled` | Query enable state (`True`/`False`) — response on data port |
| `get:running` | Query running state (`True`/`False`) — response on data port |
| `stop` | Exit the program |

### Example (Python on PC)

```python
import serial, time

# Adjust port names for your OS (e.g. 'COM3' on Windows, '/dev/ttyACM0' on Linux)
console = serial.Serial('/dev/ttyACM0', timeout=1)
dataport = serial.Serial('/dev/ttyACM1', timeout=1)

console.write(b'speed=0.25\n')   # set 0.25 RPS
time.sleep(0.1)
console.write(b'toggle\n')       # start motor

console.write(b'get:speed\n')
print(dataport.readline())       # b'0.25\n'
```

---

## Stepper Class Reference

`stepper.py` provides the `Stepper` class used by `code.py`, but can be imported into any CircuitPython project:

```python
from stepper import Stepper
import board

s = Stepper(
    step_pin=board.GP18,
    dir_pin=board.GP19,
    ena_pin=board.GP22,
    steps_per_rev=400,   # match your motor/driver microstepping setting
    speed_sps=800        # initial speed in steps per second
)

s.start()              # begin stepping
s.speed_rps(0.5)       # change to 0.5 RPS
s.change_direction()   # reverse
s.stop()               # halt and disable
```

`steps_per_rev` should match your driver's microstepping setting (e.g. 400 for half-step, 1600 for 1/8, 3200 for 1/16).

---

## License

MIT License — Eric Barefoot, 2025. Encoder example adapted from Adafruit (John Furcean, 2021, MIT).
