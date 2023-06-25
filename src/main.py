# main.py
from display.leds import neostick
from comm.ble import ble_demo
from machine import Pin

import bluetooth


neo = neostick.NeoStick(Pin(13))


def report_callback(value):
    print('Callback!:', value)


def set_neo_callback(values):
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


# initialize ble-module and hook write-event-callbacks
tp_ble = ble_demo.BleSmartLeaf(bluetooth.BLE(), report_callback, set_neo_callback)
