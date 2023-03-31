import argparse


title = """Pcap Monitor"""

parser = argparse.ArgumentParser(description=f'{title}\nPcap monitor to catch VOIP_SERVER_FAIL', formatter_class=argparse.RawDescriptionHelpFormatter)

parser.add_argument("-i", "--ip", help="IP address of the devices gateway (optional)", default=None)

parser.add_argument("-p", "--password", help="Pass a custom password if the device is configured to use one", default = '') 

args = parser.parse_args()