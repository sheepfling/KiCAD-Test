"""training fixture — blink an external status LED on BCM GPIO17.

J1.1 connects to physical header pin 11 / BCM GPIO17. J1.2 is physical pin 6 / GND.
This fixture is NOT FOR MANUFACTURE and must never connect 5 V to a GPIO pin.
"""

from signal import pause

from gpiozero import LED


status_led = LED(17)  # GPIO Zero uses Broadcom (BCM) numbering.
status_led.blink(on_time=0.5, off_time=0.5)
pause()
