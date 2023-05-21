from machine import TouchPad
import time


class SenseTouch:
    """ capacitance gets smaller on touch
        e.g. touch by average human skin in normal condition
        it's around 200 on the tech-probe, plan touch_threshold accordingly """
    class SenseTouchValueEnum:
        NONE = 0
        SHORT = 1
        LONG = 2

    def __init__(self, pin, touch_threshold=100, debug=False) -> None:
        self.touch_pin = TouchPad(pin)
        self.start_time = None
        self.touch_threshold = touch_threshold
        self.debug = debug

    def read(self):
        """ call this in the main loop
            needs high refresh-rate,
            otherwise this will not be accurate """
        val = self.touch_pin.read()
        if self.debug:
            print('current touch value:', val)

        if val < self.touch_threshold:
            if self.start_time is None:
                # Touch started
                self.start_time = time.ticks_ms()

        elif self.start_time is not None:
            # Touch ended
            diff = time.ticks_ms() - self.start_time
            self.start_time = None

            if diff > 1000:
                # Long press
                return self.SenseTouchValueEnum.LONG
            elif diff > 75:
                # Shorter than 1 second
                return self.SenseTouchValueEnum.SHORT

        return self.SenseTouchValueEnum.NONE
