
import sys
import base_miner
from pexpect import pxssh
from local_config import *

test_user = "root"
test_password = "admin"
test_ip_address = "192.168.17.20"
#test_ip_address = "192.168.17.209"
test_prompt = "~# "

##############################################################################
#                                                                            #
#                                                                            #
#                      Antminer class                                        #
#                                                                            #
#                                                                            #
##############################################################################
class Antminer(base_miner.Base_Miner):

    def __init__(self, user, password, ip_address, prompt):
        self.user = user
        self.password = password
        self.ip_address = ip_address
        self.prompt = prompt
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
#            child = pexpect.spawn('ssh ' + self.user + '@' + self.ip_address, timeout=self.TIME_OUT) 
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
#                if debug_flag: child.logfile = sys.stdout
                if debug_flag: session.logfile = sys.stdout
#                child.expect('password: ')
#                child.sendline(self.password)
#                child.expect(self.prompt)
#                child.sendline('ls /sbin/monitorcg')
                session.sendline('ls /sbin/monitorcg')
#                index = child.expect(['/sbin/monitorcg', 'ls: /sbin/monitorcg: No such file or directory'])
                index = session.expect(['/sbin/monitorcg', 'ls: /sbin/monitorcg: No such file or directory'])
                if index == 0:
#                    child.expect(self.prompt)
#                    child.sendline('rm /sbin/monitorcg')
#                    child.expect(self.prompt)
#                    child.sendline('killall monitorcg')
#                    child.expect(self.prompt)
                    session.prompt()
                    session.sendline('rm /sbin/monitorcg')
                    session.expect(self.prompt)
                    session.sendline('killall monitorcg')

                session.prompt()
                    

                if operation == "status":
                    pass

                elif operation == "start":
#                    child.sendline('/etc/init.d/cgminer.sh start')
#                    child.expect(self.prompt)
                    session.sendline('/etc/init.d/cgminer.sh start')
                    session.prompt()

                elif operation == "stop":
#                    child.sendline('/etc/init.d/cgminer.sh stop')
#                    child.expect(self.prompt)
                    session.sendline('/etc/init.d/cgminer.sh stop')
                    session.prompt()

#                child.sendline('exit')
#                child.expect(pexpect.EOF)
            except (KeyboardInterrupt, SystemExit, StopIteration):
                raise
#            except:
#                logger.error(operation + ' threw exception', exc_info=True)
            finally:
#                child.close()
                session.logout()

        return result

if __name__ == "__main__":

    miner = Antminer(test_user, test_password, test_ip_address, test_prompt)
    miner.miner_ssh_op("", debug_flag=True)

