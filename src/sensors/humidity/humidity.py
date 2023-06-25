# MIT License

# MicroPython Port Copyright (c) 2019
# Mihai Dinculescu

# CircuitPython Implementation Copyright (c) 2017
# Dean Miller for Adafruit Industries

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
This is a lightweight port from CircuitPython to MicroPython
of Dean Miller's https://github.com/adafruit/Adafruit_CircuitPython_seesaw/blob/master/adafruit_seesaw/seesaw.py

* Author(s): Mihai Dinculescu

Implementation Notes
--------------------

**Hardware:**
* Adafruit Adafruit STEMMA Soil Sensor - I2C Capacitive Moisture Sensor: https://www.adafruit.com/product/4026

**Software and Dependencies:**
* MicroPython firmware: https://micropython.org
* SeeSaw Base Class: seesaw.py

**Tested on:**
* Hardware: Adafruit HUZZAH32 - ESP32 Feather https://learn.adafruit.com/adafruit-huzzah32-esp32-feather/overview
* Firmware: MicroPython v1.12 https://micropython.org/resources/firmware/esp32-idf3-20191220-v1.12.bin
"""

import time
import ustruct
import machine

_STATUS_TEMP = const(0x04)
_TOUCH_CHANNEL_OFFSET = const(0x10)

STATUS_BASE = const(0x00)
TOUCH_BASE = const(0x0F)

_STATUS_HW_ID = const(0x01)
_STATUS_SWRST = const(0x7F)

_HW_ID_CODE = const(0x55)


class SenseHumidity:
    """Driver for Adafruit STEMMA Soil Sensor - I2C Capacitive Moisture Sensor
       :param I2C i2c: I2C bus the SeeSaw is connected to.
       :param int addr: I2C address of the SeeSaw device. Default is 0x36."""
    def __init__(self, i2c_scl_pin, i2c_sda_pin, i2c_bus_idx=0):
        self.i2c = machine.I2C(i2c_bus_idx, freq=400000, scl=i2c_scl_pin, sda=i2c_sda_pin)
        self.addr = 0x36
        # self._sw_reset()
        """Trigger a software reset of the SeeSaw chip"""
        self._write(STATUS_BASE, _STATUS_SWRST, bytearray([0xFF]))
        time.sleep(.500)

        ret = bytearray(1)
        self._write(STATUS_BASE, _STATUS_HW_ID)
        time.sleep(.005)
        self.i2c.readfrom_into(self.addr, ret)
        chip_id = ret[0]

        if chip_id != _HW_ID_CODE:
            raise RuntimeError("SeeSaw hardware ID returned (0x{:x}) is not "
                               "correct! Expected 0x{:x}. Please check your wiring."
                               .format(chip_id, _HW_ID_CODE))

    # def _sw_reset(self):
    #     """Trigger a software reset of the SeeSaw chip"""
    #     self._write(STATUS_BASE, _STATUS_SWRST, bytearray([0xFF]))
    #     time.sleep(.500)
    #
    #     ret = bytearray(1)
    #     self._write(STATUS_BASE, _STATUS_HW_ID)
    #     time.sleep(.005)
    #     self.i2c.readfrom_into(self.addr, ret)
    #     chip_id = ret[0]
    #
    #     if chip_id != _HW_ID_CODE:
    #         raise RuntimeError("SeeSaw hardware ID returned (0x{:x}) is not "
    #                            "correct! Expected 0x{:x}. Please check your wiring."
    #                            .format(chip_id, _HW_ID_CODE))

    # def _write8(self, reg_base, reg, value):
    #     self._write(reg_base, reg, bytearray([value]))

    # def _read8(self, reg_base, reg):
    #     ret = bytearray(1)
    #     self._read(reg_base, reg, ret)
    #     return ret[0]

    # def _read(self, reg_base, reg, buf, delay=.005):
    #     self._write(reg_base, reg)
    #
    #     time.sleep(delay)
    #
    #     self.i2c.readfrom_into(self.addr, buf)

    def _write(self, reg_base, reg, buf=None):
        full_buffer = bytearray([reg_base, reg])
        if buf is not None:
            full_buffer += buf

        self.i2c.writeto(self.addr, full_buffer)

    def read_temp(self):
        buf = bytearray(4)
        # self._read(STATUS_BASE, _STATUS_TEMP, buf, .005)

        self._write(STATUS_BASE, _STATUS_TEMP)
        time.sleep(.005)
        self.i2c.readfrom_into(self.addr, buf)

        buf[0] = buf[0] & 0x3F
        ret = ustruct.unpack(">I", buf)[0]
        return 0.00001525878 * ret

    def read_moisture(self):
        buf = bytearray(2)

        #self._read(seesaw.TOUCH_BASE, _TOUCH_CHANNEL_OFFSET, buf, .005)
        self._write(TOUCH_BASE, _TOUCH_CHANNEL_OFFSET)
        time.sleep(.005)
        self.i2c.readfrom_into(self.addr, buf)

        ret = ustruct.unpack(">H", buf)[0]
        time.sleep(.001)

        # retry if reading was bad
        count = 0
        while ret > 4095:
            #self._read(seesaw.TOUCH_BASE, _TOUCH_CHANNEL_OFFSET, buf, .005)
            self._write(TOUCH_BASE, _TOUCH_CHANNEL_OFFSET)
            time.sleep(.005)
            self.i2c.readfrom_into(self.addr, buf)

            ret = ustruct.unpack(">H", buf)[0]
            time.sleep(.001)
            count += 1
            if count > 3:
                raise RuntimeError("Could not get a valid moisture reading.")

        return ret
