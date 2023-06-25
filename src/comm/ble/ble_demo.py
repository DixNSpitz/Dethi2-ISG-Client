import bluetooth
import struct

from micropython import const
from . import ble_advertising

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)
_IRQ_GATTS_INDICATE_DONE = const(20)

_FLAG_READ = const(0x0002)
_FLAG_NOTIFY = const(0x0010)
_FLAG_INDICATE = const(0x0020)

_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)

# Characteristics
# org.bluetooth.characteristic.report
_REP_CHAR = (bluetooth.UUID(0x2A4D), _FLAG_WRITE_NO_RESPONSE | _FLAG_WRITE,)
# org.bluetooth.characteristic.luminous_intensity
_LUM_CHAR = (bluetooth.UUID(0x2B01), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.humidity
_HUM_CHAR = (bluetooth.UUID(0x2A6F), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.pressure
_TOU_CHAR = (bluetooth.UUID(0x2A6D), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.battery_energy_status
_BAT_CHAR = (bluetooth.UUID(0x2BF0), _FLAG_READ | _FLAG_NOTIFY | _FLAG_INDICATE,)
# org.bluetooth.characteristic.light_output
_NEO_CHAR = (bluetooth.UUID(0x2BE2), _FLAG_WRITE_NO_RESPONSE | _FLAG_WRITE,)

# Services
# org.bluetooth.service.environmental_sensing
_ENV_SENSE_UUID = bluetooth.UUID(0x181A)
# org.bluetooth.service.battery
_BAT_UUID = bluetooth.UUID(0x180F)
# org.bluetooth.service.generic_media_control
_GME_UUID = bluetooth.UUID(0x1849)

_ENV_SENSE_SERVICE = (_ENV_SENSE_UUID, (_LUM_CHAR, _HUM_CHAR, _TOU_CHAR, _REP_CHAR,),)
_BAT_SERVICE = (_BAT_UUID, (_BAT_CHAR,),)
_GME_SERVICE = (_GME_UUID, (_NEO_CHAR,),)
_SERVICES = (_ENV_SENSE_SERVICE, _BAT_SERVICE, _GME_SERVICE,)
# org.bluetooth.characteristic.gap.appearance.xml
_ADV_APPEARANCE_GENERIC_LIGHT_SOURCE = const(1984)


class BleSmartLeaf:
    def __init__(self, ble, callback_rep=None, callback_neo=None, name="smart-leaf-ble"):
        self.connected = False
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        self._callback_rep = callback_rep
        self._callback_neo = callback_neo
        ((self._lum_handle, self._hum_handle, self._tou_handle, self._rep_handle,), (self._bat_handle,), (self._neo_handle,), ) = self._ble.gatts_register_services(_SERVICES)
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
            self._log('Central connected to ESP32', '(handle: ' + str(conn_handle) + ')')
            self.connected = True
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            self._connections.remove(conn_handle)
            # Start advertising again to allow a new connection.
            self._advertise()
            self._log('Central disconnected from ESP32', '(handle: ' + str(conn_handle) + ')')
            self.connected = False
        elif event == _IRQ_GATTS_INDICATE_DONE:
            conn_handle, value_handle, status = data
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            self._log('Central write received', '(handle: ' + str(conn_handle) + ')', '(value-handle: ' + str(value_handle) + ')')
            if value_handle == self._rep_handle:
                upckd = struct.unpack('<i', self._ble.gatts_read(value_handle))[0]
                self._log('Report value received:', upckd)
                if self._callback_rep is not None:
                    self._callback_rep(upckd)
            if value_handle == self._neo_handle:
                upckd = struct.unpack('IHHH', self._ble.gatts_read(value_handle))
                # First value are NEO-LED indexes e.g. 100000000 which means no LED is written to
                # e.g. 111100000 which means first three LEDs are written to
                # e.g. 211100000 which means first three LEDs are written to and other LED-values are not cleared
                # Second, Third, Fourth values are unsigned RGB-shorts e.g. (255, 0, 0) => RED
                # e.g. (255, 255, 255) => White
                # e.g. (128, 128, 128) => 50% Grey, and so on
                self._log('Neo value received:', upckd)
                if self._callback_neo is not None:
                    self._callback_neo(upckd)

    def set_light_value(self, light_value, notify=False, indicate=False):
        self._log('Writing Luminosity value:', light_value)
        self.set_value(self._lum_handle, 'd', light_value, notify, indicate)

    def set_humidity_value(self, humidity_value, notify=False, indicate=False):
        self._log('Writing Humidity value:', humidity_value)
        self.set_value(self._hum_handle, 'd', humidity_value, notify, indicate)

    def set_battery_value(self, battery_value, notify=False, indicate=False):
        self._log('Writing Battery value:', battery_value)
        self.set_value(self._bat_handle, '<i', battery_value, notify, indicate)

    def set_touch_value(self, touch_value, notify=False, indicate=False):
        self._log('Writing Touch value:', touch_value)
        self.set_value(self._tou_handle, '<i', touch_value, notify, indicate)

    def set_value(self, handle, struct_fmt, value, notify=False, indicate=False):
        self._ble.gatts_write(handle, struct.pack(struct_fmt, value))
        if notify or indicate:
            for conn_handle in self._connections:
                if notify:
                    # Notify connected centrals.
                    self._log('Trying to notify central', '(handle: ' + str(conn_handle) + ')')
                    self._ble.gatts_notify(conn_handle, handle)
                if indicate:
                    # Indicate connected centrals.
                    self._log('Trying to indicate central', '(handle: ' + str(conn_handle) + ')')
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

    def _log(self, *values: object):
        a = list(values)
        a.insert(0, '[BLE]')
        values = tuple(a)
        print(*values)
