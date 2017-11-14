#!/usr/bin/python

import subprocess
import time
import sys
import pexpect
import logging
import logging.handlers
import datetime
from w1_gpio_therm import W1_Gpio_Therm
try:
    from timos_lib import W1_Temp_Sensor
except: pass
from local_config import *

TURN_OFF_TEMP = 70.0
TURN_ON_TEMP = 68.0

try:
    #default_temp_sensor = W1_Temp_Sensor()
    #default_temp_sensor = Temper_Temp_Sensor()
    default_temp_sensor = W1_Gpio_Therm()
except: pass

##############################################################################
#                                                                            #
#                                                                            #
#    Dummy classes used for testing                                          #
#                                                                            #
#                                                                            #
##############################################################################

# if they haven't been changed, TURN_OFF_TEMP = 70.0, and TURN_ON_TEMP = 68.0
# so result should be:
#             off     on    off   off    off    on    on     on    off   off    on
test_temps = [ 69,    70,   71,   70,    69,    68,   67,    68,   71,   69,    60]
test_stats = ["off", "on", "on", "off", "off", "on", "off", "on", "on", "off", "off"]

class Dummy_Temp_Sensor:

    def __init__(self):
        self.generator = self.temp_generator(test_temps)

    def temp_generator(self, temp_list):
        for i in temp_list:
            yield i

    def get_temp(self):
        return next(self.generator)

class Dummy_Miner:

    def __init__(self):
        self.generator = self.stat_generator(test_stats)

    def stat_generator(self, stat_list):
        for i in stat_list:
            yield i

    def status(self):
        stat = next(self.generator)
        logger.info("dummy_miner.status() %s" % stat)
        return stat

    def start(self):
        logger.info("dummy_miner.start()")

    def stop(self):
        logger.info("dummy_miner.stop()")

##############################################################################
#                                                                            #
#                                                                            #
#               Thermostat class                                             #
#                                                                            #
#                                                                            #
##############################################################################
class Thermostat:

    def __init__(self, miner, temp_sensor):
        self.miner = miner
        self.temp_sensor = temp_sensor
        self.last_event_time = datetime.datetime.now()

    def calc_interval(self):
        now = datetime.datetime.now()
        interval = now - self.last_event_time
        self.last_event_time = now
        return str(interval).split('.')[0]

    def run(self):

        temp = self.temp_sensor.get_temp()
        if (temp < TURN_ON_TEMP) or (temp > TURN_OFF_TEMP):
            # don't need to query miner if temp is within range

            status = self.miner.status()

            if (status == "on") and (temp > TURN_OFF_TEMP):
                self.miner.stop()
                logger.info( "%2.1f" % (temp,) + ", off, " + self.calc_interval())

            if (status == "off") and (temp < TURN_ON_TEMP):
                self.miner.start()
                logger.info( "%2.1f" % (temp,) + ",  on, " + self.calc_interval())

##############################################################################
#                                                                            #
#                                                                            #
#               main(...)                                                    #
#                                                                            #
#                                                                            #
##############################################################################
def main(miner, temp_sensor, period=120):

    thermostat = Thermostat(miner, temp_sensor)

    while True:
        try:
            thermostat.run()
        except (KeyboardInterrupt, SystemExit, StopIteration):
            raise
        except:
             logger.error('thermostat threw exception', exc_info=True)
        time.sleep(period)   # seconds, miner takes at least 30 seconds to respond,
                             # so wait at least that long.


##############################################################################
#                                                                            #
#                                                                            #
#          Entry point                                                       #
#                                                                            #
#                                                                            #
##############################################################################
if __name__ == "__main__":


    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(levelname)s, %(asctime)s, %(message)s', datefmt="%Y-%m-%d, %H:%M")


    file_handler = logging.handlers.RotatingFileHandler(log_dir + 'thermostat.log', maxBytes=100000, backupCount=1)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if len(sys.argv) == 1:  # no arguments passed
        #
        # default action if no arguments passed
        #

        try:
            logger.info('Starting ...')
            main(Spondoolies_Miner(), default_temp_sensor)

        except KeyboardInterrupt:
            pass

        logger.info('quitting ...')

    elif sys.argv[1] == "test":
        #
        #  "test" was passed as an argument.  Run with test classes.
        #
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        main(Dummy_Miner(), Dummy_Temp_Sensor(), period=1)

    else:
        #
        #  other test routines.
        #    

        miner = Spondoolies_Miner()

        if sys.argv[1] == "status":
            print(miner.status())

        elif sys.argv[1] == "Status":
            print(miner.status(debug=True))

        elif sys.argv[1] == "start":
            miner.start()

        elif sys.argv[1] == "Start":
            miner.start(debug=True)

        elif sys.argv[1] == "stop":
            miner.stop()

        elif sys.argv[1] == "Stop":
            miner.stop(debug=True)

        elif sys.argv[1] == "temp":
            print(default_temp_sensor.get_temp())

        elif sys.argv[1] == "Temper":
            print(subprocess.check_output("temper-poll"))


