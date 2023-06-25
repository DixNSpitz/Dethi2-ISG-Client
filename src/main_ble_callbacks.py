import time

from sensors.light import light
from sensors.humidity import humidity
from display.leds import neostick
from comm.ble.ble_demo import BleSmartLeaf

from machine import Pin


neo = neostick.NeoStick(Pin(13))


def report_callback_with_retries(ble_smart_leaf: BleSmartLeaf, value):
    sense_retry_ct = 5
    retry_ct = 0
    value = None
    while retry_ct < sense_retry_ct and value is None:
        try:
            sense_light = light.SenseLight(Pin(14), Pin(32), i2c_bus_idx=0)
            value = sense_light.read()
        except Exception as e:
            value = None
            retry_ct += 1
            time.sleep_ms(50)

    if value is not None:
        ble_smart_leaf.set_light_value(value, True)

    time.sleep(1)

    retry_ct = 0
    value = None
    while retry_ct < sense_retry_ct and value is None:
        try:
            sense_humidity = humidity.SenseHumidity(Pin(15), Pin(33), i2c_bus_idx=1)
            value = sense_humidity.read_moisture()
        except Exception as e:
            value = None
            retry_ct += 1
            time.sleep_ms(50)

    if value is not None:
        ble_smart_leaf.set_humidity_value(value, True)


def report_callback(ble_smart_leaf: BleSmartLeaf, value):
    sense_light = light.SenseLight(Pin(14), Pin(32), i2c_bus_idx=0)
    ble_smart_leaf.set_light_value(sense_light.read(), True)
    time.sleep(1)
    sense_humidity = humidity.SenseHumidity(Pin(15), Pin(33), i2c_bus_idx=1)
    ble_smart_leaf.set_humidity_value(sense_humidity.read_moisture(), True)


def set_neo_callback(ble_smart_leaf: BleSmartLeaf, values):
    if not values:
        return

    # unpack everything
    ctrl, r, g, b = values

    ctrl = str(ctrl)
    ctrl_clear = None
    ctrl_idxs = []
    for i in range(len(ctrl)):
        if i == 0:
            if ctrl[i] == '1':
                ctrl_clear = True
            elif ctrl[i] == '2':
                ctrl_clear = False
            continue

        if ctrl[i] == '1':
            # first one (i == 0) is not an LED-index, therefore i-1
            ctrl_idxs.append(i-1)

    if ctrl_clear:
        neo.clear()
    for idx in ctrl_idxs:
        neo.set_rgbw(idx, (r, g, b, 1))