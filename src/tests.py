from sensors.light import light
from sensors.humidity import humidity
from sensors.touch import touch
from display.leds import neostick, neo_onboard
from comm.ble import ble_demo

from machine import Pin
import time
import bluetooth


def test():
    print('Starting Tests...')
    #test_generic('Light Sense', test_sense_light)
    #test_generic('Humidity Sense', test_sense_humidity)
    #test_generic('Touch Sense', test_sense_touch)
    #test_generic('LED Display', test_display_neo)
    test_generic('BLE-Comm', lambda: test_ble_comm(False, False, False, False))
    #test_generic('Game Guess Waterlevel', test_game_guess_waterlevel)
    print('Ending Tests')


def test_generic(name, test_func):
    print('Testing', name, '..')
    success = test_func()
    if success:
        print(name, 'Test Done')
    else:
        print(name, 'Test Failed!')


def test_ble_comm(notify_lum=False, notify_hum=False, notify_bat=False, notify_touch=False):
    try:
        tp_ble_indicator = neo_onboard.NeoBlue()
        tp_ble = ble_demo.BleSmartLeaf(bluetooth.BLE())

        print('BLE-Address is: ', tp_ble.get_mac_address())
        while not tp_ble.connected:
            tp_ble_indicator.refresh_emit()
            time.sleep_ms(10)

        if not notify_lum and not notify_hum and not notify_bat and not notify_touch:
            return True

        time.sleep(5)
        if notify_lum:
            sense_light = light.SenseLight(Pin(14), Pin(32), i2c_bus_idx=0)
            value = sense_light.read()
            print('trying to send luminosity data:', value)
            tp_ble.set_light_value(value, True)

        time.sleep(5)
        if notify_hum:
            sense_humidity = humidity.SenseHumidity(Pin(15), Pin(33), i2c_bus_idx=1)
            value = sense_humidity.read_moisture()
            print('trying to send humidity data:', value)
            tp_ble.set_humidity_value(value, True)

        if notify_touch:
            sense_touch = touch.SenseTouch(Pin(12), touch_threshold=150)
            for i in range(350):
                value = sense_touch.read()
                if value == touch.SenseTouch.SenseTouchValueEnum.SHORT:
                    print('Short Touch')
                    tp_ble.set_touch_value(0, True)
                elif value == touch.SenseTouch.SenseTouchValueEnum.LONG:
                    print('Long Touch')
                    tp_ble.set_touch_value(1, True)

                time.sleep(0.1)

        return True

    except Exception as e:
        print(e)
        return False


def test_game_guess_waterlevel():
    sense_touch = touch.SenseTouch(Pin(12), touch_threshold=150)
    neo = neostick.NeoStick(Pin(13))
    neo.clear()
    counter = 0
    for i in range(150):
        value = sense_touch.read()
        if counter == 9:
                  counter = 0
                  neo.clear()
        if value == touch.SenseTouch.SenseTouchValueEnum.SHORT and counter == 8:
                  counter = counter +1
        if value == touch.SenseTouch.SenseTouchValueEnum.SHORT and counter <8:
                  neo.set_rgbw(counter,(0,255,255,0))
                  counter = counter +1
        time.sleep(0.1)


def test_sense_light():
    try:
        sense_light = light.SenseLight(Pin(14), Pin(32), i2c_bus_idx=0)
        for i in range(5):
            value = sense_light.read()
            print('Light level: [{0:>7.1f}] lx'.format(value))
            time.sleep(0.5)
        return True

    except Exception as e:
        print(e)
        return False


def test_sense_humidity():
    try:
        sense_humidity = humidity.SenseHumidity(Pin(15), Pin(33), i2c_bus_idx=1)
        for i in range(5):
            value_temp = sense_humidity.read_temp()
            value_humidity = sense_humidity.read_moisture()
            print('Coarse Soil Temperature: [{0:>7.1f}] °C'.format(value_temp))
            print('Soil Humidity: [{0:>7.1f}]'.format(value_humidity))
            time.sleep(0.5)
        return True

    except Exception as e:
        print(e)
        return False


def test_sense_touch():
    try:
        sense_touch = touch.SenseTouch(Pin(12), touch_threshold=150)
        for i in range(100):
            value = sense_touch.read()
            if value == touch.SenseTouch.SenseTouchValueEnum.SHORT:
                print('Short Touch')
            elif value == touch.SenseTouch.SenseTouchValueEnum.LONG:
                print('Long Touch')

            time.sleep(0.1)
        return True

    except Exception as e:
        print(e)
        return False


def test_display_neo():
    try:
        neo = neostick.NeoStick(Pin(13))
        i = 0
        while i < 5:
            neo.rainbow_cycle(5)
            i += 1

        neo.clear()
        return True

    except Exception as e:
        print(e)
        return False


if __name__ == "__main__":
    test()
