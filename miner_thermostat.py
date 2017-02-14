
import subprocess
import time
import sys
import pexpect
import logging
import logging.handlers
import datetime
from local_config import *

TURN_OFF_TEMP = 70.0
TURN_ON_TEMP = 68.0
TEMPER_TEMP_CAL = -10.0

# these need to be defined before the next import

##############################################################################
#                                                                            #
#                                                                            #
#                 Temper_Temp_Sensor class                                   #
#                                                                            #
#                                                                            #
##############################################################################

class Temper_Temp_Sensor:
    def get_temp(self):
        s = subprocess.check_output(["temper-poll", "-f"])
        n = float(s) + TEMPER_TEMP_CAL
        return n

##############################################################################
#                                                                            #
#                                                                            #
#                     One Wire Temperature Sensor class                      #
#                                                                            #
#                                                                            #
##############################################################################

class W1_Temp_Sensor:

    def __init__(self):
        self.sensor = W1ThermSensor()

    def get_temp(self):
        s = self.sensor.get_temperature(W1ThermSensor.DEGREES_F)
        n = float(s)
        return n

# W1_Temp_Sensor and Temper_Temp_sensor are now defined.
# Presense of One Wire module determines what sensor we're using.

try:
    from w1thermsensor import W1ThermSensor
    default_temp_sensor = W1_Temp_Sensor()
except ImportError:
    default_temp_sensor = Temper_Temp_Sensor()


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
#             Spondoolies_Miner class                                        #
#                                                                            #
#                                                                            #
##############################################################################
class Spondoolies_Miner:

    def status(self, debug=False):
        return self.miner_ssh_op("status", debug_flag=debug)

    def start(self, debug=False):
        return self.miner_ssh_op("start", debug_flag=debug)

    def stop(self, debug=False):
        return self.miner_ssh_op("stop", debug_flag=debug)

    def miner_ssh_op(self, operation, debug_flag=False):

        result = 0

        child = pexpect.spawn('ssh ' + Spondoolies_miner["user"] + '@' + Spondoolies_miner["ip"])
        if debug_flag: child.logfile = sys.stdout
        child.expect('password: ')
        child.sendline(Spondoolies_miner["pass"])
        child.expect('SP31-5# ')

        if operation == "status":
            child.sendline('spond-manager status')
            child.expect('SP31-5# ')
            status = child.before
            if '1' in status:
                result = "on"
            else:
                result = "off"

        elif operation == "start":
            child.sendline('spond-manager start')
            child.expect('SP31-5# ')

        elif operation == "stop":
            child.sendline('spond-manager stop')
            child.expect('SP31-5# ')

        child.sendline('exit')

        return result

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
        status = self.miner.status()

        if (status == "on") and (temp > TURN_OFF_TEMP):
            self.miner.stop()
            logger.info(str(temp) + ", off, " + self.calc_interval())

        if (status == "off") and (temp < TURN_ON_TEMP):
            self.miner.start()
            logger.info(str(temp) + ",  on, " + self.calc_interval())

##############################################################################
#                                                                            #
#                                                                            #
#               main(...)                                                    #
#                                                                            #
#                                                                            #
##############################################################################
def main(miner, temp_sensor, period=60):

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


    file_handler = logging.handlers.RotatingFileHandler('thermostat.log', maxBytes=10000, backupCount=3)
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


