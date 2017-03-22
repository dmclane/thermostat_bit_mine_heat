##############################################################################
#                                                                            #
#                                                                            #
#                     One Wire Temperature Sensor class                      #
#                                                                            #
#                                                                            #
##############################################################################

import local_config
from w1thermsensor import W1ThermSensor

W1_TEMP_CAL = +1.0

class W1_Temp_Sensor:

    def __init__(self):
        self.sensor = W1ThermSensor()

    def get_temp(self):
        s = self.sensor.get_temperature(W1ThermSensor.DEGREES_F)
        n = float(s) + local_config.W1_GPIO_CAL
        return n

if __name__ == "__main__":
    sensor = W1_Temp_Sensor()
    print sensor.get_temp()
