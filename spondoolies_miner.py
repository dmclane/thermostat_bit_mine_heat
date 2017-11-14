
import pexpect
from local_config import *

##############################################################################
#                                                                            #
#                                                                            #
#             Spondoolies_Miner class                                        #
#                                                                            #
#                                                                            #
##############################################################################
class Spondoolies_Miner:

    # not sure why it sometimes takes so long to respond, but I've seen it take
    # more that 3 minutes.
    TIME_OUT = 300

    def status(self, debug=False):
        return self.miner_ssh_op("status", debug_flag=debug)

    def start(self, debug=False):
        return self.miner_ssh_op("start", debug_flag=debug)

    def stop(self, debug=False):
        return self.miner_ssh_op("stop", debug_flag=debug)

    def miner_ssh_op(self, operation, debug_flag=False):

        result = 0

        try:
            child = pexpect.spawn('ssh ' + Spondoolies_miner["user"] + '@' + Spondoolies_miner["ip"])

        except (KeyboardInterrupt, SystemExit, StopIteration):
            raise
        except:
             logger.error('pexpect.spawn, ' + operation + ' threw exception', exc_info=True)

        else:
            try:
                if debug_flag: child.logfile = sys.stdout
                child.expect('password: ', timeout=self.TIME_OUT)
                child.sendline(Spondoolies_miner["pass"])
                child.expect(Spondoolies_miner["prompt"], timeout=self.TIME_OUT)

                if operation == "status":
                    child.sendline('spond-manager status')
                    child.expect(Spondoolies_miner["prompt"], timeout=self.TIME_OUT)
                    status = child.before
                    if '1' in status:
                        result = "on"
                    else:
                        result = "off"

                elif operation == "start":
                    child.sendline('spond-manager start')
                    child.expect(Spondoolies_miner["prompt"], timeout=self.TIME_OUT)

                elif operation == "stop":
                    child.sendline('spond-manager stop')
                    child.expect(Spondoolies_miner["prompt"], timeout=self.TIME_OUT)

                child.sendline('exit')
            except (KeyboardInterrupt, SystemExit, StopIteration):
                raise
            except:
                logger.error(operation + ' threw exception', exc_info=True)
            finally:
                child.close()

        return result


