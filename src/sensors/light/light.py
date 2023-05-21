import machine
import utime


class SenseLight:
    def __init__(self, i2c_scl_pin, i2c_sda_pin, i2c_bus_idx=0):
        self.i2c = machine.I2C(i2c_bus_idx, freq=400000, scl=i2c_scl_pin, sda=i2c_sda_pin)
        self.addr = 0x23

        # power on the BH1750
        self.i2c.writeto(self.addr, bytes([0x01]))

        # reset the BH1750
        self.i2c.writeto(self.addr, bytes([0x07]))
        utime.sleep_ms(200)

        # set mode to 1.0x high-resolution, continuous measurement
        self.i2c.writeto(self.addr, bytes([0x10]))
        utime.sleep_ms(150)

    def read(self):
        data = self.i2c.readfrom(self.addr, 2)  # read two bytes
        value = (data[0] << 8 | data[1]) / 1.2
        return value
