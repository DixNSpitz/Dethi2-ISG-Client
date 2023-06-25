# main.py
from comm.ble import ble_demo
from main_ble_callbacks import report_callback, set_neo_callback

import bluetooth


# initialize ble-module and hook default write-event-callbacks
tp_ble = ble_demo.BleSmartLeaf(bluetooth.BLE(), report_callback, set_neo_callback)
