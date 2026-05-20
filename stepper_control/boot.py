"""Boot configuration for Pico.

Enables dual USB CDC endpoints: console for serial output/logging,
and data for remote command/telemetry communication with the PC.
"""

from usb_cdc import enable

enable(console=True, data=True)