import neopixel
import time


class NeoStick:
    def __init__(self, pin, brightness=0.2):
        self.np = neopixel.NeoPixel(pin, 8, bpp=4)
        self.brightness = brightness

    def wheel(self, pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            return 0, 0, 0, 0
        if pos < 85:
            return self._perform_brightness((255 - pos * 3, pos * 3, 0, 1))
        if pos < 170:
            pos -= 85
            return self._perform_brightness((0, 255 - pos * 3, pos * 3, 1))
        pos -= 170
        return self._perform_brightness((pos * 3, 0, 255 - pos * 3, 1))

    def rainbow_cycle(self, wait):
        for j in range(255):
            for i in range(self.np.n):
                rc_index = (i * 256 // self.np.n) + j
                self.np[i] = self.wheel(rc_index & 255)
            self.np.write()
            time.sleep_ms(wait)

    def set_brightness(self, brightness):
        self.brightness = brightness

    def set_rgbw(self, index, value, write=True):
        if index < 0 or index > 7:
            raise IndexError('NeoPixel index must be within the range of 0 to 7')

        self.np[index] = self._perform_brightness(value)
        if write:
            self.np.write()

    def fill_rgbw(self, value, write=True):
        self.np.fill(self._perform_brightness(value))
        if write:
            self.np.write()

    def clear(self):
        self.fill_rgbw((0, 0, 0, 0))

    def _perform_brightness(self, value):
        nb = int(value[0] * self.brightness), int(value[1] * self.brightness), int(value[2] * self.brightness), value[3]
        return nb
