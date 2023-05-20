from sensors import lux
from machine import Pin
import time


def do_test():
    print('Testing Light Sensor...')
    light_sense_success = test_light_sense()
    if light_sense_success:
        print('Light Sensing Test Done')
    else:
        print('Light Sensing Failed!')

    # TODO extend tests with other sensors


def test_light_sense():
    try:
        sense_light = lux.LightSensor(Pin(14), Pin(32))
        for i in range(5):
            value = sense_light.read()
            print( 'Light level: [{0:>7.1f}] lx'.format(value) )
            time.sleep(0.5)
        return True

    except:
        return False


if __name__ == "__main__":
    do_test()
