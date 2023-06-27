# main.py
from comm.ble import ble_demo
from main_ble_callbacks import report_callback, set_neo_callback
from sensors.touch import touch
from machine import Pin

import time
import bluetooth


# initialize ble-module and hook default write-event-callbacks
tp_ble = ble_demo.BleSmartLeaf(bluetooth.BLE(), report_callback, set_neo_callback)


sense_touch = touch.SenseTouch(Pin(12), touch_threshold=350)
while True:
    value = sense_touch.read()
    if value == touch.SenseTouch.SenseTouchValueEnum.SHORT:
        print('Short Touch')
        if tp_ble.connected:
            tp_ble.set_touch_value(1, True)
    elif value == touch.SenseTouch.SenseTouchValueEnum.LONG:
        print('Long Touch')
        if tp_ble.connected:
            tp_ble.set_touch_value(2, True)

    time.sleep(0.1)
