"""Board-specific firmware requirements; no Raspberry Pi or GPIO library needed."""
import runpy
import types
import unittest
from pathlib import Path
from unittest.mock import Mock, patch


class StatusFirmwareTests(unittest.TestCase):
    def test_status_led_uses_bcm17_and_half_second_pulses(self) -> None:
        gpiozero = types.ModuleType("gpiozero")
        led = Mock()
        gpiozero.LED = Mock(return_value=led)
        firmware = Path(__file__).resolve().parents[1] / "firmware/status_led.py"
        # Raspberry Pi exposes pause(); the portable test host may be Windows.
        with patch.dict("sys.modules", {"gpiozero": gpiozero}), patch("signal.pause", create=True) as pause:
            runpy.run_path(str(firmware))
        gpiozero.LED.assert_called_once_with(17)
        led.blink.assert_called_once_with(on_time=0.5, off_time=0.5)
        pause.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
