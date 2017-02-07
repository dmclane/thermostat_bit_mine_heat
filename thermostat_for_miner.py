
import subprocess
import time
import sys
import pexpect
import logging
import logging.handlers
import datetime

TURN_OFF_TEMP = 70.0
TURN_ON_TEMP = 68.0
TEMP_CAL = -10.0

miner_1 = {"ip":"192.168.17.17", "user":"root", "pass":"aestas"}

class Dummy_Temp_Sensor:

    def __init__(self):
        self.generator = self.temp_gen()

    def temp_gen(self):
        self.temps = [69, 70, 71, 70, 69, 68, 67, 68, 71, 69, 60]
        for i in self.temps:
            yield i

    def get_temp(self):
        return self.generator.next()

class Temper_Temp_Sensor:
    def get_temp(self):
        try:
            s = subprocess.check_output(["temper-poll", "-f"])
            n = float(s) + TEMP_CAL
        except:
            logger.error('get_temp exception', exc_info=True)
            n = "error"

        return n


def spond_miner(operation, debug_flag=False):

    result = 0

    try:
        child = pexpect.spawn('ssh root@192.168.17.17')
        if debug_flag: child.logfile = sys.stdout
        child.expect('password: ')
        child.sendline('aestas')
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

    except:
        logger.error("spond_miner exception", exc_info=True)
    return result

class Dummy_Miner:

    def __init__(self):
        self.generator = self.stat_gen()

    def stat_gen(self):
        stat = ["off", "on", "on", "off", "off", "on", "on", "on", "on", "off", "off"]
        for i in stat:
            yield i

    def status(self):
        logger.info("dummy_miner.status()")
        return self.generator.next()

    def start(self):
        logger.info("dummy_miner.start()")

    def stop(self):
        logger.info("dummy_miner.stop()")

class Spondoolies_Miner:

    def status(self):
        return spond_miner("status")

    def start(self):
        return spond_miner("start")

    def stop(self):
        return spond_miner("stop")

class Thermostat:

    def __init__(self, miner):
        self.miner = miner
        self.last_event_time = datetime.datetime.now()

    def calc_interval(self):
        now = datetime.datetime.now()
        interval = now - self.last_event_time
        self.last_event_time = now
        logger.info("interval = " + str(interval))


    def check(self, temp):

        status = self.miner.status()

        if status == "on" and temp > TURN_OFF_TEMP:
            self.miner.stop()
            self.calc_interval()
            logger.info("temp = " + str(temp) + ", turning off " )

        if status == "off" and temp < TURN_ON_TEMP:
            self.miner.start()
            self.calc_interval()
            logger.info("temp = " + str(temp) + ", turning on" )

def main(miner, temp_sensor):

    thermostat = Thermostat(miner)

    while True:
        temp = temp_sensor.get_temp()
        if temp != "error":
            thermostat.check(temp)
        time.sleep(60)   # seconds, miner takes at least 30 seconds to respond,
                         # so wait at least that long.


if __name__ == "__main__":


    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(levelname)s, %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.RotatingFileHandler('thermostat.log', maxBytes=10000, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if len(sys.argv) == 1:  # no arguments passed

        try:
            logger.info('Starting ...')
            main(Spondoolies_Miner(), Temper_Temp_Sensor())

        except KeyboardInterrupt:
            pass
        except Exception, e:
            logger.error("main exception", exc_info=True)

        logger.info('quitting ...')

    elif sys.argv[1] == "test":

        try:
            main(Dummy_Miner(), Dummy_Temp_Sensor())
        except:
            pass
        
    else:

        miner = Spondoolies_Miner()

        if sys.argv[1] == "status":
            print(miner.status())

        elif sys.argv[1] == "Status":
            print(spond_miner("status", debug_flag=True))

        elif sys.argv[1] == "start":
            miner.start()

        elif sys.argv[1] == "Start":
            spond_miner("start", debug_flag=True)

        elif sys.argv[1] == "stop":
            miner.stop()

        elif sys.argv[1] == "Stop":
            spond_miner("stop", debug_flag=True)

        elif sys.argv[1] == "temp":
            print(Temper_Temp_Sensor().get_temp())

        elif sys.argv[1] == "Temp":
            print(subprocess.check_output("temper-poll"))


