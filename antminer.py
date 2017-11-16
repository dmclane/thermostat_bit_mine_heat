
import sys
import base_miner
import pexpect
from pexpect import pxssh
from local_config import *

test_miner = localhost_test

##############################################################################
#                                                                            #
#                                                                            #
#                      Antminer class                                        #
#                                                                            #
#                                                                            #
##############################################################################
class Antminer(base_miner.Base_Miner):

    def __init__(self, miner):
        self.user = miner["user"]
        self.password = miner["pass"]
        self.ip_address = miner["ip"]
        self.prompt = miner["prompt"]
        self.TIME_OUT = 30

    def status(self, debug=False):
        return self.miner_ssh_op("status", debug_flag=debug)

    def start(self, debug=False):
        return self.miner_ssh_op("start", debug_flag=debug)

    def stop(self, debug=False):
        return self.miner_ssh_op("stop", debug_flag=debug)

    def miner_ssh_op(self, operation, debug_flag=False):

        result = 0

        try:
            child = pexpect.spawn('ssh ' + self.user + '@' + self.ip_address, timeout=self.TIME_OUT) 

            if debug_flag: child.logfile = sys.stdout
            child.expect('password: ')
            child.sendline(self.password)
            child.expect(self.prompt)
            child.sendline('ls /sbin/monitorcg')
            index = child.expect(['/sbin/monitorcg', 'ls: '])
            if index == 1:
                child.expect(self.prompt)
                child.sendline('rm /sbin/monitorcg')
                child.expect(self.prompt)
                child.sendline('killall monitorcg')
                child.expect(self.prompt)

            if operation == "status":
                pass

            elif operation == "start":
                child.sendline('/etc/init.d/cgminer.sh start')
                child.expect(self.prompt)

            elif operation == "stop":
                child.sendline('/etc/init.d/cgminer.sh stop')
                child.expect(self.prompt)

            child.sendline('exit')
            child.expect(pexpect.EOF)
        except (KeyboardInterrupt, SystemExit, StopIteration):
            raise
#            except:
#                logger.error(operation + ' threw exception', exc_info=True)
        finally:
            child.close()

        return result


    def miner_pxssh_op(self, operation, debug_flag=False):

        result = 0

        try:
            session = pxssh.pxssh()

        except (KeyboardInterrupt, SystemExit, StopIteration):
            raise
        except pxssh.ExceptionPxssh as e:
            print("pxssh failed on login.")
            print(e)
#        except:
#             logger.error('pexpect.spawn, ' + operation + ' threw exception', exc_info=True)

        else:
            try:
                if debug_flag: session.logfile = sys.stdout
                session.sendline('ls /sbin/monitorcg')
                index = session.expect(['/sbin/monitorcg', 'ls: /sbin/monitorcg: No such file or directory'])
                if index == 0:
                    session.prompt()
                    session.sendline('rm /sbin/monitorcg')
                    session.expect(self.prompt)
                    session.sendline('killall monitorcg')

                session.prompt()
                    

                if operation == "status":
                    pass

                elif operation == "start":
                    session.sendline('/etc/init.d/cgminer.sh start')
                    session.prompt()

                elif operation == "stop":
                    session.sendline('/etc/init.d/cgminer.sh stop')
                    session.prompt()

            except (KeyboardInterrupt, SystemExit, StopIteration):
                raise
#            except:
#                logger.error(operation + ' threw exception', exc_info=True)
            finally:
                session.logout()

        return result

if __name__ == "__main__":

    miner = Antminer(test_miner)
    if len(sys.argv) == 1:
        miner.miner_ssh_op("", debug_flag=True)

    elif sys.argv[1] == "pxssh":
        print("pxssh arg")

    elif sys.argv[1] == "status":
        print("status arg")

    elif sys.argv[1] == "start":
        print("start arg")

    elif sys.argv[1] == "stop":
        print("stop arg")


