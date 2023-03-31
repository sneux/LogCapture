from modules._device import Device
import time
from modules._arg import args
import sys

sys.path.append('/home/pi/scriptsToMonitor/pcapMonitor/modules')

myDevice = Device(ip='10.20.48.149', password='abcde12345')

myDevice.login()

def main():

    myDevice.rollPcaps()
        
    timestamp = myDevice.startPcap()

    ## Modified as request by Turan and Antonio
    # myDevice.startPcap()

    save = False 

    while save == False:

        time.sleep(5)
        
        pcap_size = myDevice.checkPcapSize()

        if int(pcap_size) >= 9_000_000:
            
            save = True 

    time.sleep(2)

    myDevice.stopPcap()

    time.sleep(5)

    myDevice.storePcap(timestamp)

# myDevice.logout()


while True:

    main()


