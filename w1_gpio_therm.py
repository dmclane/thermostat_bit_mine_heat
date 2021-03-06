
# based on https://cdn-learn.adafruit.com/downloads/pdf/adafruits-raspberry-pi-lesson-11-ds18b20-temperature-sensing.pdf

import os
import glob
import time
import local_config

class W1_Gpio_Therm:

    def __init__(self):
        os.system('modprobe w1-gpio')
        os.system('modprobe w1-therm')

        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28*')[0]
        self.device_file = device_folder + '/w1_slave'

    def read_temp_raw(self):
        f = open(self.device_file, 'r')
        lines = f.readlines()
        f.close()
        return lines

    def read_temp(self):
        lines = self.read_temp_raw()
        # this seems dangerous
#        while lines[0].strip()[-3:] != 'YES':
#            time.sleep(0.2)
#            lines = self.read_temp_raw()
        # try a few times before throwing exception
        for i in xrange(3):
            if lines[0].strip()[-3:] != 'YES':
                time.sleep(0.2)
                lines = self.read_temp_raw()
            else:
                break
        if lines[0].strip()[-3:] != 'YES':
            raise Exception("W1_Gpio_Therm sensor not ready.")

        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            temp_c = float(temp_string) / 1000.0
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            return temp_c, temp_f

    def get_temp(self):
        return self.read_temp()[1] + local_config.W1_GPIO_CAL

if __name__ == "__main__":
    sensor = W1_Gpio_Therm()
    print(sensor.get_temp()) 

