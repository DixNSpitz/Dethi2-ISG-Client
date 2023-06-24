from sensors.light import light
from sensors.humidity import humidity
from sensors.touch import touch
from display.leds import neostick, neo_onboard
from comm.ble import ble_demo

from machine import Pin
import time
import bluetooth

bble = bluetooth.BLE()
tp_ble_indicator = neo_onboard.NeoBlue()
tp_ble = ble_demo.BleTechProbe(bble)

ble_mac = ''
for byte in bble.config('mac')[1]:
    ble_mac += hex(byte).replace('0x','').upper() + ':'

print('BLE-Address is: ', ble_mac)
while not tp_ble.connected:
    tp_ble_indicator.refresh_emit()
    time.sleep_ms(100)

time.sleep(3)
tp_ble.set_light_value(10, True, True)

def test():
    test_generic('Light Sense', test_sense_light)
    test_generic('Humidity Sense', test_sense_humidity)
    test_generic('Touch Sense', test_sense_touch)
    test_generic('LED Display', test_display_neo)
    game_guess_waterlevel()

# Returns led level 1-8 based on thresholds
def categorize_sensor_value(value, thresholds):
    for i, threshold in enumerate(thresholds):
        if value < threshold:
            return i + 1
    return len(thresholds) + 1

def get_light_level():
    sense_light = light.SenseLight(Pin(14), Pin(32), i2c_bus_idx=0)
    value = sense_light.read()
    thresholds = [100, 200, 300, 400, 500, 600, 700] # adjust these thresholds
    return categorize_sensor_value(value, thresholds)

def get_humidity_level():
    sense_humidity = humidity.SenseHumidity(Pin(15), Pin(33), i2c_bus_idx=1)
    value_humidity = sense_humidity.read_moisture()
    thresholds = [10, 20, 30, 40, 50, 60, 70] # adjust these thresholds
    return categorize_sensor_value(value_humidity, thresholds)

def idle_state():
    sense_touch = touch.SenseTouch(Pin(12), touch_threshold=150)
    neo = neostick.NeoStick(Pin(13))
    neo.clear()

    red = (255,0,0,0)
    blue = (0,0,255,0)
    yellow = (255,255,0,0)
    green = (0,255,0,0)
    colors = [blue, yellow, green]

    led_counts = [get_humidity_level(), get_light_level(), 4]

    touch_counter = 0
    for i in range(150):
        value = sense_touch.read()
        if value == touch.SenseTouch.SenseTouchValueEnum.SHORT:
            neo.clear()
            if led_counts[touch_counter] > 2 and led_counts[touch_counter] < 7:
                color = colors[touch_counter]
            else: # if led count is 1, 2, 7, or 8
                color = red
            for j in range(led_counts[touch_counter]): # light up LEDs based on the current count
                neo.set_rgbw(j, color)
            touch_counter = (touch_counter + 1) % 3
        elif value == touch.SenseTouch.SenseTouchValueEnum.LONG:  # Check for long touch
            # Call a random game from the server.
            # choose_random_game() 
            pass
        time.sleep(0.1)

def game_guess_waterlevel():
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

def test_generic(name, test_func):
    print('Testing', name, '..')
    success = test_func()
    if success:
        print(name, 'Test Done')
    else:
        print(name, 'Test Failed!')


def test_sense_light():
    try:
        sense_light = light.SenseLight(Pin(14), Pin(32), i2c_bus_idx=0)
        for i in range(5):
            value = sense_light.read()
            print('Light level: [{0:>7.1f}] lx'.format(value))
            time.sleep(0.5)
        return True

    except:
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

    except:
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

    except:
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

    except:
        return False


if __name__ == "__main__":
    test()
