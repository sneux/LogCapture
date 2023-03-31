#v0.0.1
#Telnet wrapper specifically for our DRI devices

import os
import re
import time
import telnetlib



class DRItelnet:

    def __init__(self,
                 host=None,
                 User="superadmin",
                 Pass="abc123"):

        try:

            from DRImodules import DRIinterfaces

            if host is None:

                host = DRIinterfaces.interfaceStuff().getDeviceIP('eth0')

        except ImportError as e:

            print("Interface module not able to import")

            pass

        try:

            tn = telnetlib.Telnet(host)

            print(f"Connection Established: {tn}")

            tn.read_until(b"login:")

            tn.write(User.encode("ascii") + b"\n")

            tn.read_until(b"Password:")

            tn.write(Pass.encode("ascii") + b"\n")

            self.tn = tn

        except Exception as e:

            print("There an been an error initializing your telnet connection: {}".format(e))          



    def sendCommand(self,
                    command=None,
                    extraArgs=None,
                    waitFor=None):

        try:

            if(extraArgs is not None) and (command is not None):

                cmd = "{} {}".format(command, extraArgs)

            elif(command is not None):

                cmd = "{}".format(command)

            else:

                print("Command was not given\n")

            print("Sending Command")

            self.tn.write(cmd.encode("ascii") + b"\n")

            if(waitFor is not None):

                print("Waiting for {}".format(waitFor))

                return self.tn.read_until(waitFor.encode("ascii"))

            return True

        except OSError as e:

            print("There has been an error sending your byte string (command): {}".format(e))

            return False



    def readUntil(self,
                  waitFor=None):

        print("Waiting for {}".format(waitFor))

        return self.tn.read_until(waitFor.encode("ascii"))



if __name__ == "__main__":

    tel = DRItelnet()

    print("\nLogin Pass\n")

    tel.sendCommand('ls')

    print('\nCommand Pass\n')

    tel.tn.interact()

    print('\nInteract Pass\n')