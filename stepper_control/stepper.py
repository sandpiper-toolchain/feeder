# import board
from pwmio import PWMOut
# from time import sleep, monotonic
import digitalio

class Stepper:
    """Controls a NEMA stepper motor for the sediment feeder hopper/auger.

    Manages motor speed, direction, and enable state via PWM and GPIO pins.
    Used on Raspberry Pi Pico to drive the sediment dispenser mechanism."""
    def __init__(self, step_pin, dir_pin, ena_pin, steps_per_rev=3200, speed_sps=800, invert_dir=False, invert_enable=False, timer_id=-1):
        """Initialize the stepper motor with GPIO pins and parameters.

        Args:
            step_pin: PWM pin for step pulses (frequency controls speed)
            dir_pin: Digital pin for rotation direction
            ena_pin: Digital pin to enable/disable motor
            steps_per_rev: Microsteps per full revolution (typically 1600-3200)
            speed_sps: Initial speed in steps per second
            invert_dir: Flip direction logic if motor rotates backwards
            invert_enable: Flip enable logic if wired inverted
        """

        if not isinstance(step_pin, PWMOut):
            step_pin = PWMOut(step_pin, frequency=speed_sps, duty_cycle=0, variable_frequency=True)
        if not isinstance(dir_pin, digitalio.DigitalInOut):
            dir_pin = digitalio.DigitalInOut(dir_pin)
            dir_pin.direction = digitalio.Direction.OUTPUT
        if (ena_pin != None) and (not isinstance(ena_pin, digitalio.DigitalInOut)):
            # print("setting up enable pin")
            ena_pin = digitalio.DigitalInOut(ena_pin)
            ena_pin.direction = digitalio.Direction.OUTPUT
 
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.ena_pin = ena_pin
        self.invert_dir = invert_dir
        self.invert_enable = invert_enable

        self.min_hz = 10

        self.direction = -1 # counting direction, 1 for counter-clockwise, -1 for clockwise

        self.enable(True)
        
        self.steps_per_sec = speed_sps
        self.steps_per_rev = steps_per_rev
        self.rps = self.steps_per_sec / self.steps_per_rev

        self.running = False
        self.enabled = self.is_enabled()
        
        
    def speed(self, sps):
        """Set motor speed in steps per second, with a minimum frequency floor.

        Adjusts PWM frequency to control rotation speed; clamped to min_hz to
        avoid stalling. Updates cached speed values for RPM calculations.
        """

        if sps >= self.min_hz:
            self.step_pin.frequency = int(sps)
            self.sec_per_step = 1/sps
            self.steps_per_sec = self.step_pin.frequency
            self.rps = self.step_pin.frequency / self.steps_per_rev
        else:
            self.step_pin.frequency = self.min_hz
            self.sec_per_step = 1/self.min_hz
            self.rps = self.step_pin.frequency / self.steps_per_rev
    
    def speed_rps(self, rps):
        """Set motor speed in rotations per second.

        Convenience method for users who think in RPM; converts to steps/sec
        and delegates to speed().
        """
        self.speed(rps*self.steps_per_rev)

    def start(self):
        """Enable the motor and begin stepping at the current speed."""
        self.enable(True)
        self.step_pin.duty_cycle = 2**14  # 25% duty cycle for step pulses
        self.running = True

        # if self.direction>0:
        #     self.dir_pin.value = 1
        #     self.step_pin.duty_cycle = 2**15  # 50% duty cycle
        # elif self.direction<0:
        #     self.dir_pin.value = 0
        #     self.step_pin.duty_cycle = 2**15
        # else:
        #     self.step_pin.duty_cycle = 0
        #     print("Stepper: start called with d=0, no steps will be taken")

    def stop(self):
        """Halt stepping and disable the motor to release torque."""
        self.step_pin.duty_cycle = 0
        # self.dir_pin.value = 0  # Reset direction pin to low when stopping
        self.enable(False)
        self.running = False

    def change_direction(self):
        """Reverse the motor rotation direction and update tracking state."""
        d = self.dir_pin.value
        self.dir_pin.value = bool(d^1)  # Toggle direction pin
        self.direction = self.direction * -1

    def enable(self, e=True):
        """Enable or disable the motor driver. When disabled, motor coils are de-energized."""
        self.ena_pin.value = bool(0^e)

    def is_enabled(self):
        """Return whether the motor is currently enabled."""
        return bool(self.ena_pin.value)


