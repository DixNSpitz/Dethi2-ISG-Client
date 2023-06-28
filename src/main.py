# main.py
from comm.ble import ble_demo
from main_ble_callbacks import report_callback, set_neo_callback
from sensors.touch import touch
from display.leds import neostick
from machine import Pin

import time
import bluetooth


# initialize ble-module and hook default write-event-callbacks
tp_ble = ble_demo.BleSmartLeaf(bluetooth.BLE(), report_callback, set_neo_callback)
print('mac', tp_ble.get_mac_address())

conn_ct = 0
conn_neo_toggle = False


def refresh_switch_ble_led(connected):
    global conn_ct, conn_neo_toggle
    neo = neostick.NeoStick(Pin(13))
    if connected:
        if conn_ct > 0:
            for i in range(8):
                neo.set_rgbw(i, (0, 0 ,255, 1))
                time.sleep_ms(50)
            neo.clear()
        conn_ct = 0
    else:
        conn_ct += 1
        if conn_ct > 20:
            conn_ct = 0
            conn_neo_toggle = not conn_neo_toggle
            neo.set_rgbw(0, (0, 0, 128 if conn_neo_toggle else 0, 1 if conn_neo_toggle else 0))


sense_touch = touch.SenseTouch(Pin(12), touch_threshold=350)
while True:
    refresh_switch_ble_led(tp_ble.connected)
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
