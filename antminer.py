#! /usr/bin/python

import sys
import base_miner
import getpass
import pexpect
from pexpect import pxssh
from local_config import *

localhost_test = {"ip":"localhost", "user":"dmclane", "pass":"", "prompt":"\$ "}
try:
    test_miner = Antminer_S7_1
except:
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
            child = pexpect.spawn('ssh ' + self.user + '@' + self.ip_address, timeout=self.TIME_OUT, echo=False) 

            if debug_flag: child.logfile = sys.stdout
            child.expect('password: ')
            child.sendline(self.password)
            child.expect(self.prompt)
            child.sendline('ls /sbin/monitorcg')
            index = child.expect(['ls: ', '/sbin/monitorcg'])
            if index == 1:
                child.expect(self.prompt)
                child.sendline('rm /sbin/monitorcg')
                child.expect(self.prompt)
                child.sendline('killall monitorcg')

            child.expect(self.prompt)

            if operation == "status":
                child.sendline('cgminer-api stats')
                index = child.expect(['Reply', 'Socket connect failed'])
                if index == 0:
                    result = 'on'
                else:
                    result = 'off'
                child.expect(self.prompt)

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
        finally:
            child.close()

        return result


    def miner_pxssh_op(self, operation, debug_flag=False):

        result = 0

        try:
            session = pxssh.pxssh(echo=False)

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
        finally:
            session.logout()

        return result

if __name__ == "__main__":

    if test_miner["pass"] == "":
        test_miner["pass"] = getpass.getpass()
    miner = Antminer(test_miner)
    if len(sys.argv) == 1:
        miner.miner_ssh_op("", debug_flag=True)

    elif sys.argv[1] == "pxssh":
        miner.miner_pxssh_op("", debug_flag=True)

    elif sys.argv[1] == "status":
        result = miner.miner_ssh_op("status", debug_flag=True)
        print result

    elif sys.argv[1] == "start":
        miner.miner_ssh_op("start", debug_flag=True)

    elif sys.argv[1] == "stop":
        miner.miner_ssh_op("stop", debug_flag=True)


