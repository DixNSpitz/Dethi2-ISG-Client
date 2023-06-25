import bluetooth
import struct

from micropython import const
from . import ble_advertising

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

# Characteristics
# org.bluetooth.characteristic.report
_REP_CHAR = (bluetooth.UUID(0x2A4D), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.luminous_intensity
_LUM_CHAR = (bluetooth.UUID(0x2B01), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.humidity
_HUM_CHAR = (bluetooth.UUID(0x2A6F), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.pressure
_TOU_CHAR = (bluetooth.UUID(0x2A6D), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.battery_energy_status
_BAT_CHAR = (bluetooth.UUID(0x2BF0), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)

# Services
# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.service.battery
_BAT_UUID = bluetooth.UUID(0x180F)

_ENV_SENSE_SERVICE = (_ENV_SENSE_UUID, (_LUM_CHAR, _HUM_CHAR, _TOU_CHAR, _REP_CHAR,),)
_BAT_SERVICE = (_BAT_UUID, (_BAT_CHAR,),)
_SERVICES = (_ENV_SENSE_SERVICE, _BAT_SERVICE,)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_LIGHT_SOURCE = const(1984)


class BleSmartLeaf:
    def __init__(self, ble, name="smart-leaf-ble"):
        self.connected = False
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._lum_handle, self._hum_handle, self._tou_handle, self._rep_handle,), (self._bat_handle,), ) = self._ble.gatts_register_services(_SERVICES)
        self._connections = set()
        self._payload = ble_advertising.advertising_payload(
            name=name, services=[_ENV_SENSE_UUID, _BAT_UUID], appearance=_ADV_APPEARANCE_GENERIC_LIGHT_SOURCE
        )
        self._advertise()

    def _irq(self, event, data):
        # Track connections so we can send notifications.
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            self._connections.add(conn_handle)
            print('BLE Device connected to ESP32')
            self.connected = True
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
            print('BLE Device disconnected to ESP32')
            self.connected = False
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data

    def set_light_value(self, light_value, notify=False, indicate=False):
        self.set_value(self._lum_handle, 'd', light_value, notify, indicate)

    def set_humidity_value(self, humidity_value, notify=False, indicate=False):
        self.set_value(self._hum_handle, 'd', humidity_value, notify, indicate)

    def set_battery_value(self, battery_value, notify=False, indicate=False):
        self.set_value(self._bat_handle, '<i', battery_value, notify, indicate)

    def set_touch_value(self, touch_value, notify=False, indicate=False):
        self.set_value(self._tou_handle, '<i', touch_value, notify, indicate)

    def set_value(self, handle, struct_fmt, value, notify=False, indicate=False):
        self._ble.gatts_write(handle, struct.pack(struct_fmt, value))
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._ble.gatts_notify(conn_handle, handle)
                if indicate:
                    # Indicate connected centrals.
                    self._ble.gatts_indicate(conn_handle, handle)

    def get_mac_address(self):
        ble_mac = ''
        for byte in self._ble.config('mac')[1]:
            ble_mac += hex(byte).replace('0x', '').upper() + ':'

        if ble_mac:
            ble_mac = ble_mac[0: len(ble_mac)-1]

        return ble_mac

    def _advertise(self, interval_us=500000):
        self._ble.gap_advertise(interval_us, adv_data=self._payload)
