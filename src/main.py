from sensors.light import light
from sensors.humidity import humidity
from sensors.touch import touch
from display.leds import neostick, neo_onboard
from comm.ble import ble_demo
from machine import Pin

import time
import bluetooth

sense_light = light.SenseLight(Pin(14), Pin(32), i2c_bus_idx=0)
sense_humidity = humidity.SenseHumidity(Pin(15), Pin(33), i2c_bus_idx=1)

def test():
    #print('Starting Tests...')
    idle_state()
    #test_generic('Light Sense', test_sense_light)
    #test_generic('Humidity Sense', test_sense_humidity)
    #test_generic('Touch Sense', test_sense_touch)
    #test_generic('LED Display', test_display_neo)
    #test_generic('BLE-Comm', lambda: test_ble_comm(False, False, False, False))
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
            tp_ble.set_light_value(sense_light.read(), True)

        time.sleep(5)
        if notify_hum:
            sense_humidity = humidity.SenseHumidity(Pin(15), Pin(33), i2c_bus_idx=1)
            tp_ble.set_humidity_value(sense_humidity.read_moisture(), True)

        if notify_touch:
            sense_touch = touch.SenseTouch(Pin(12), touch_threshold=150)
            for i in range(350):
                value = sense_touch.read()
                if value == touch.SenseTouch.SenseTouchValueEnum.SHORT:
                    tp_ble.set_touch_value(0, True)
                elif value == touch.SenseTouch.SenseTouchValueEnum.LONG:
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
        sense_touch = touch.SenseTouch(Pin(12), touch_threshold=350)
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

def categorize_sensor_value(value, thresholds):
    for i, threshold in enumerate(thresholds):
        if value < threshold:
            return i + 1
    return len(thresholds) + 1


'''

# THIS IS THE SERVER SIDE JUST TO ILLLUSTRATE
from sensors.temperatur.temperatur import SenseTemperature
# Initialize the sensor at the beginning of script
sense_temp = SenseTemperature(1, 0x44, 0x2C, [0x06])

def notification_handler(sender, data):
    global last_value
    last_value = struct.unpack('<i', data)[0]
    print('Received value:', last_value)

    if last_value == 1:  # Start a game on receiving -1
        start_random_game()
    elif last_value == 2:  # Read temperature on receiving 0
        cTemp, _, _ = sense_temp.read()
        print(f"Current temperature: {cTemp}")

'''

def get_light_level(): #300-7000
    
    value = sense_light.read()
    thresholds = [330, 1000, 2000, 3000, 4000, 5000, 6500] # adjust these thresholds
    return categorize_sensor_value(value, thresholds)

def get_humidity_level(): #400-1600
    
    value_humidity = sense_humidity.read_moisture()
    thresholds = [450, 600, 800, 1200, 1300, 1400, 1500] # adjust these thresholds
    return categorize_sensor_value(value_humidity, thresholds)

def get_temperature_level():
    value_temp = sense_humidity.read_temp()
    print('Temperatursensor: ')
    print(value_temp)
    thresholds = [15, 17, 22, 25, 27, 30, 35] # adjust these thresholds
    return categorize_sensor_value(value_temp, thresholds)

def idle_state():
    sense_touch = touch.SenseTouch(Pin(12), touch_threshold=350)
    neo = neostick.NeoStick(Pin(13))
    neo.clear()
    print(str(get_light_level()))
    print(str(get_humidity_level()))
    
    print('clear leds')

    red = (255,0,0,0)
    blue = (0,0,255,0)
    yellow = (255,255,0,0)
    green = (0,255,0,0)
    colors = [blue, yellow, green]  #water #light # temperatur

    led_counts = [get_humidity_level(), get_light_level(), get_temperature_level()]
    print(led_counts)

    touch_counter = 0
    start_time = time.time()
    counterblink= 0
    while True:
        counterblink = counterblink +1
        led_counts = [get_humidity_level(), get_light_level(), get_temperature_level()]
        print(led_counts)
        neo.clear()
       
        color = colors[touch_counter]
        
        for j in range(led_counts[touch_counter]): # light up LEDs based on the current count
            neo.set_rgbw(j, color)
        if((led_counts[touch_counter]<2 or led_counts[touch_counter]>7) and counterblink>10):
            neo.clear()
            counterblink = 0
                
                
        value = sense_touch.read()
        if value == touch.SenseTouch.SenseTouchValueEnum.SHORT:
            led_counts = [get_humidity_level(), get_light_level(), get_temperature_level()]
            print(led_counts)
            neo.clear()
            
            color = colors[touch_counter]
            
            for j in range(led_counts[touch_counter]): # light up LEDs based on the current count
                neo.set_rgbw(j, color)
            touch_counter = (touch_counter + 1) % 3
        
            # Call a random game from the server.
            # choose_random_game() 
            pass

        # Check if 2 minutes have passed
        #if time.time() - start_time >= 120:  # 120 seconds = 2 minutes
        #led_counts = [get_humidity_level(), get_light_level(), 3]
            #start_time = time.time()  # Reset the start time

        time.sleep(0.05)



test()


