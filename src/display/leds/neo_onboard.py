import neopixel
from machine import Pin

_RGB_MAX_VAL = 255


class NeoBlue:
    def __init__(self) -> None:
        self.np_power = Pin(2, Pin.PULL_UP, value=1)
        self.np = neopixel.NeoPixel(Pin(0), 1)
        self.np_blue_val = 0
        self.np_pulse_dir = 1

    def power_on(self):
        self.np_power.value(1)

    def power_off(self):
        self.np_power.value(0)

    # better in high refresh rates
    def refresh_emit(self, pulse=True):
        if not pulse:
            self.np_blue_val = _RGB_MAX_VAL
        else:
            np_blue_newval = self.np_blue_val + 5 * self.np_pulse_dir
            if np_blue_newval > _RGB_MAX_VAL:
                np_blue_newval = _RGB_MAX_VAL
                self.np_pulse_dir = -1
            elif np_blue_newval < 0:
                np_blue_newval = 0
                self.np_pulse_dir = 1

            self.np_blue_val = np_blue_newval

        self.np[0] = (0, 0, self.np_blue_val)
        self.np.write()