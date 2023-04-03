from DRImodules import DRInc, DRIinterfaces, drirc
from PCAPmodules._device import Device
from drirc import drirc
import threading
import argparse
import socket
import time
import sys
import re
import os

# Dictionary to easily determine the channel to capture on
def channel_9090(line):
    cds_9090_channel_dict = {
        1: '0',
        2: '1',
        3: '2',
        4: '3',
        5: '4',
        6: '5',
        7: '6',
        8: '7'
    }
    return cds_9090_channel_dict[line]


# 9010 Channel Dictionary
def channel_9010(line):

    try:

        cds_9010_channel_dict = {
            1: '1',
            2: '0'
        }

        return cds_9010_channel_dict[line]
    
    except KeyError:

        pass

    # return cds_9010_channel_dict[line]


# 9070/9080/VAB Channel Dictionary
def other_channel(line):

    cds9070_dri9080_channel_dict = {

        1: '0',
        2: '1',
        3: '2',
        4: '3',
        5: '4',
        6: '5',
        7: '6',
        8: '7'

    }

    return cds9070_dri9080_channel_dict[line]


# This dictionary is a path to clear the syslog
def syslog_path(device_model):

    sys_path = {

        'CDS9090': '/tmp/log/messages',
        'CDS9010': '/tmp/syslog.txt',
        'CDS9070': '/tmp/syslog.txt',
        'DRI9080': '/tmp/syslog.txt'

    }

    return sys_path[device_model]


# Finds the proper channels for the D.U.T.
def channel(device_model, line):

    dictionary_picker = {

        'CDS9090': channel_9090(line),
        'CDS9010': channel_9010(line),
        'CDS9070': other_channel(line),
        'DRI9080': other_channel(line)

    }

    return dictionary_picker[device_model]


# Will add the proper search item for files
def pcm(call):

    pcm_dict = {

        'fax': 'Fax',
        'data': ''

    }

    return pcm_dict[call]


def get_wan_ip(interface_name):
    """
    Get WAN IP of user's machine for later use.
    """

    host = None
    client = None

    for attempts in range(3):

        try:

            # IP(interface_name)
            host = interface_name

            client = input('\nInput the local WAN IP of your machine: ')
            # IP(client)

            break

        except ValueError:

            interface = DRIinterfaces.interfaceFinder()

            host = interface.getDeviceIP(interface_name)

            client = interface.getClientIP(interface_name)

            break

    return (host, client)


def verify_fxs_against_model(fxs_port, model):
    
    """
    Verifies that the user supplied FXS port is within the range of ports
    available on the device.
    
    `fxs_port`: Integer representing the FXS port to capture on. User supplied.
    `model`: String containing the model of the device to capture on.

    Returns GFGFe if `fxs_port` is valid.
    """

    # Validates that the integer entered as a CL arg is within the range for the devices
    if (model == 'CDS9090') or (model == 'DRI9080') or (model == 'VAB1'):

        if (fxs_port > 8) or (fxs_port < 1):

            print(f'The FXS port entered for the {model} is not a valid option')

            return False
        
    elif (model == 'CDS9070') or (model == 'CDS9010'):

        if (fxs_port > 2) or (fxs_port < 1):

            print(f'The FXS port entered for the {model} is not a valid option')

            return False
        
    return True


def verify_capture_name(rc, capture):

    for x in range(3):
            
            if os.path.isdir(f'{os.getcwd()}/Logs/{capture}'):

                print(f'\nError: There is already a capture with the name "{capture}"')

                overwrite = input('\nPlease enter a new name:  ')

                capture = overwrite

                if os.path.isdir(f'{os.getcwd()}/Logs/{overwrite}'):

                    new_overwrite = input(f'\nThe capture "{overwrite}" also exists, please choose a new name: ')

                    if new_overwrite == "":

                        rc.close()

                        raise Exception('File name cannot be blank')

                    if x == 2:

                        rc.close()

                        raise Exception('Too many invalid attempts')

                    capture = new_overwrite

            else:

                os.mkdir(f'{os.getcwd()}/Logs/{capture}')

                break

    return capture


def nc_listener_callback(*args, **kwargs):

    """Listener thread for netcatting file over."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.settimeout(10)
    # s.bind(("", kwargs['port']))

    s.bind((kwargs['client'], kwargs['port']))

    s.listen()

    (data_socket, addr) = s.accept()

    pcm_buffer = b''

    while True:

        buffer = data_socket.recv(4096)

        if len(buffer) == 0:

            break

        pcm_buffer += buffer

    capture = kwargs['capture']

    with open(f"Logs/{capture}/{capture}.raw", "wb") as f:

        f.write(pcm_buffer)


def perform_capture(rc, capture, model, fxs_ports, 
                    stream_raw=False, client=None, file_port=None):
        
        # Wait to start
        input('\nPress [Enter] to start the capture')

        # Clear the syslog
        rc.exec(cmd=f'echo ""> {syslog_path(model)}')

        # Send the echo capture start command
        if len(fxs_ports) == 1:

            rc.exec(cmd=f'echo "capture_start {channel(model, fxs_ports[0])}" >> /proc/ks_cpld')

        else:

            #pcm
            rc.exec(cmd=f'echo "capture_start {channel(model, fxs_ports[0])} {channel(model, fxs_ports[1])}" >> /proc/ks_cpld')

        # Start writing to a file
        if stream_raw:

            th = threading.Thread(target=nc_listener_callback, kwargs={

                'port': file_port,
                'client': client,
                'capture': capture

            })

            th.start()

            time.sleep(1)

            rc.exec(cmd=f'cat /proc/ks_capture | nc {client} {file_port}')

        else:

            rc.exec(cmd=f'cat /proc/ks_capture > /tmp/{capture}.raw')

        # Wait to stop
        input('\nPress [Enter] to stop the capture')

        # Send CTRL-C to stop the capture
        rc.exec(cmd='\x03')

        if stream_raw:

            th.join()

        # Send the echo capture stop command
        if len(fxs_ports) == 1:

            rc.exec(cmd=f'echo "capture_stop {channel(model, fxs_ports[0])}" >> /proc/ks_cpld')

        else:

            rc.exec(cmd=f'echo "capture_stop {channel(model, fxs_ports[0])} {channel(model, fxs_ports[1])}" >> /proc/ks_cpld')


def get_file_names(rc, capture, model, fxs_port):

    # Subtract 1 from the FXS port int b/c indexing starts at 0
    if len(fxs_port) == 1:

        fxs = [fxs_port[0] - 1]

    else:

        fxs = [fxs_port[0] - 1, fxs_port[1] -1]
    
    # fxs = fxs_port - 1

    syslog_name = {
        'CDS9090': 'messages',
        'CDS9010': 'syslog',
        'CDS9070': 'syslog',
        'DRI9080': 'syslog'
    }

    if model == 'CDS9090':

        rc.exec(cmd='cp /tmp/log/messages /tmp/')

    rc_output = rc.exec(cmd='ls /tmp').strip('[];\\')

    #telnet_output = telnet.read('#')

    # if (telnet.deviceClass() == 'CDS9010'):
    #     telnet_output = telnet.read('#')

    fileMatches = re.compile(r'PCMInData_[0-7] | '
                            r'PCMOutData_[0-7] | '
                            r'FaxPCMInData_[0-7] | '
                            r'FaxPCMOutData_[0-7] | '
                            r'syslog.txt | '
                            r'messages | '
                            r'{0}.raw'.format(capture), flags=re.X)

    foundMatches = list(set(fileMatches.findall(rc_output)))

    # All found files will be appended to this list 
    log_files = []

    for hit in foundMatches:

        # Are there typically PCM files in the tmp directory??.
        # We can simplify this code by simply omitting the port and just looking
        # for files with 'PCM' as a substring.
        if ('PCM' and f'{fxs[0]}') in hit:

            log_files.append(hit)

        # If there are two FXS ports then lets also search for a PCM file with
        # the second port provided.
        if len(fxs) > 1:

            if ('PCM' and f'{fxs[1]}') in hit:

                log_files.append(hit)

        if 'syslog' in hit:

            log_files.append(hit)

        if 'messages' in hit:

            log_files.append(hit)

        if f'{capture}' in hit:

            log_files.append(hit)

    return set(log_files)


def get_files(nc, rc, client, capture, log_files):

    for file in log_files:

        fileName = file

        netcat = threading.Thread(target=nc.listenForFile,
                                args=(f'{os.getcwd()}/Logs/{capture}', fileName, False))

        netcat.start()

        time.sleep(1)

        rc.exec(cmd=f'nc {client} {nc.port} < /tmp/{fileName}')

        netcat.join()

        print(f'Successfully downloaded: {fileName}')


def clean_files(rc, log_files):

    print("Cleaning files from device.")

    for file in log_files:

        if "syslog" in file or "messages" in file:

            continue

        rc.exec(cmd=f'rm /tmp/{file}')


def vab_pcap(ip, password, interface, filter):
    '''
    Perform packet capture on a VAB
    REQUIRED PARAMETERS: 
        ip (int) : IP of the device
        password (str) : superadmin password
    OPTIONAL PARAMETERS:
        interface (str) : interface to capture on
        filter (str) : filter the capture
    '''

    sys.path.append('Logs')

    myDevice = Device(ip, password)

    myDevice.login()

    time.sleep(3)

    input('\nPress [Enter] to start the capture')

    timestamp = myDevice.startPcap(interface, filter)

    input('\nPress [Enter] to stop the capture') 

    '''
    save = False

    while save == False:

        time.sleep(5)
        
        pcap_size = myDevice.checkPcapSize()

        if int(pcap_size) >= 9_000:
        
            save = True '''

    time.sleep(2)

    myDevice.stopPcap()

    time.sleep(5)

    myDevice.storePcap(timestamp)

    myDevice.debug_snapshot()

    myDevice.logout()

    print("Done!")


def main():
    parser = argparse.ArgumentParser(description="DRI LogCapture Script")
    parser.add_argument('-s', '--stream', help='Stream raw file.', action="store_true", required=False)
    parser.add_argument('-p', '--port', help='Port used to transfer files.', required=False)
    parser.add_argument('-pw', '--password', help='VAB password', required=False, default="abcde12345")
    parser.add_argument('-i', '--interface', help="Interface to capture on. VAB ONLY.", required=False, default="WAN")
    parser.add_argument('-f', '--filter', help="Filter for PCAP", required=False, default=None)
    parser.add_argument('-fxs', type=int, help='FXS port, or ports, to perform capture on. Maximum of two ports.', nargs='+', required=False)
    parser.add_argument('-c', '--client', help='IP of local machine.')
    parser.add_argument('device', help='Device model')
    parser.add_argument('name', help='What to call this current capture.')
    parser.add_argument('host', help='IP of the device to perform capture on.')

     
    args = parser.parse_args()

    # CL args makes the program easier to use
    model = args.device
    capture = args.name
    host = args.host
    client = args.client
    fxs_ports = args.fxs
    vab_pass = args.password
    interface = args.interface
    vab_filter = args.filter
    stream_raw = args.stream
    file_port = 9999

    if args.port is not None:
        file_port = int(args.port)

    # DRI NetCat module
    if file_port is None:

        nc = DRInc.NC(client)

    else:

        nc = DRInc.NC(client, file_port)
    
    # Checks file name for error
    if '.raw' in capture:

        capture = capture.replace('.raw', '')

    print(f'\nConnecting to: {host} ')
    
    print(f'Files will be sent to: {client}')

    if model == "VAB1":

        vab_pcap(host, vab_pass, interface, vab_filter)

    else:
        rc = drirc.DRIRC()

        rc.connect()
    
        for port in fxs_ports:

            if verify_fxs_against_model(model, port) is False:

                print(f'FXS port {port} is out of range for {model}.')

                exit()

        # Begins Log capture process
        try:
            # Check if path exists otherwise create it to store logs
            if os.path.isdir(f'{os.getcwd()}/Logs'):

                pass

            else:

                os.mkdir(f'{os.getcwd()}/Logs')

            capture = verify_capture_name(rc, capture)

            perform_capture(rc, capture, model, fxs_ports, 
                            stream_raw, client, file_port)

            log_files = get_file_names(rc, capture, model, fxs_ports)

            print(f'\nThese were the files that were found on the device')

            for file_in_device in log_files:

                print(file_in_device)

            get_files(nc, rc, client, capture, log_files)

            clean_files(rc, log_files=log_files)


        except KeyboardInterrupt as e:

            print(f'\nThe operation failed: {e}')

        finally:

            rc.close()

            print('Done!')

if __name__ == "__main__":

    main()