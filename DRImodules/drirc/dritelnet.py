# DataRemote Telnet Wrapper Library
import re

import time

import socket

import platform

import netifaces

import threading

import telnetlib

import subprocess


def connectionManager(function):

    def checkConnection(self, *args, **kwargs):

        try:

            functionResponse = function(self, *args, **kwargs)

            if functionResponse == False:

                print(f"Connection to {self.host} has terminated, trying again...")

                connectionStatus = self.connect()

                if connectionStatus == True:

                    print(f"Connection to {self.host} successful!")

                    return function(self, *args, **kwargs)

                else:

                    print(f"Unable to reconnect to {self.host}")

                    return
                
        except Exception as e:

            print(f"An error occurred attempting to connect to {self.host}: {e}")

            return
        
        return functionResponse
    
    return checkConnection


class DriTelnet:

    def __init__(self, host : str, username : str, password : str, shell_prompt : str, port : int = 23):

        self.tn = None

        self.host = host

        self.username = username

        self.password = password

        self.shell_prompt = shell_prompt

        self.port = port



    def __parseDarwinInterface(self, interface : str) -> str | None:

        try:

            matchInterface = re.search(': (.+?)\\\\', interface)

            if matchInterface:

                parsedInterface = matchInterface.group(1)

                return parsedInterface
            
            else:

                print(f"Unable to parse interface on Darwin system.")

                return None

        except Exception as e:

            print(f"An error occurred attempting to parse the default interface for Darwin system: {e}")

            return None



    def __getDarwinDefaultInterface(self) -> str | None:

        getDefaultCmd = 'route get default | grep interface'

        try:

            defaultInterface = subprocess.run(getDefaultCmd, shell = True, capture_output = True)

            defaultInterface = str(defaultInterface.stdout)

            defaultInterface = self.__parseDarwinInterface(defaultInterface)

        except Exception as e:

            print(f"An error occurred attempting to get the default interface for Darwin system: {e}")

            return None

        return defaultInterface



    def __getLocalIP(self) -> str | None:

        try:

            if platform.system() == 'Darwin':

                defaultInterface = self.__getDarwinDefaultInterface()

            else:

                defaultInterface = netifaces.gateways()['default'][netifaces.AF_INET][1]

            ifAddresses = netifaces.ifaddresses(defaultInterface)

            ipAddress = ifAddresses[netifaces.AF_INET][0]['addr']

            return ipAddress
    
        except Exception as e:

            print(f"An error occurred trying to get the local IP address: {e}")

            return None



    def __getFileFromSocket(self, port : int, timeout : int) -> bytes | None:

        try:

            listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            listenSocket.settimeout(timeout)

            listenSocket.bind(('', port))

            listenSocket.listen()

            clientSocket, returnAddress = listenSocket.accept()

            fileData = b''

        except Exception as ose:

            print(f"An OS error has occurred: {ose}.")

            return None
        
        while True:

            try:

                buffer = clientSocket.recv(2048)

                if len(buffer) == 0:

                    break

                fileData += buffer

            except Exception as e:

                print(f"An error occurred while reading file buffer: {e}.\nReturning what buffer managed to get saved...")

                return fileData

        return fileData



    def __saveFile(self, fileData : bytes, local_path : str) -> None:

        try:

            with open(local_path, "wb") as f:

                f.write(fileData)

        except Exception as e:

            print(f"Failed to save file data to {local_path}: {e}")



    def __getFileBootstrap(self, *args) -> None:
        
        fileData = self.__getFileFromSocket(args[0], args[1])

        self.__saveFile(fileData, args[2])



    def connect(self, timeout : float = 5) -> bool:

        try:

            self.tn = telnetlib.Telnet(host = self.host, port = self.port, timeout = timeout)

        except TimeoutError as tme:

            print(f"An error occurred attempting to connect to {self.host}: {tme}")

            return False
        
        except Exception as e:

            print(f"An unknown error occurred attempting to connect to {self.host}: {e}")

            return False

        try:

            self.tn.read_until(b"login: ", timeout=timeout)

            self.tn.write(self.username.encode('ascii') + b"\n")

            self.tn.read_until(b"Password: ", timeout=timeout)

            self.tn.write(self.password.encode('ascii') + b"\n")

            self.tn.read_until(self.shell_prompt.encode())

        except TimeoutError as toe:

            print(f"Login failed to {self.host}: {toe}")

            return False
        
        except Exception as f:

            print(f"An unknown error occurred attempting to connect to {self.host}: {f}")

            return False

        return True



    def close(self) -> None:

        self.tn.close()


    @connectionManager
    def _send(self, cmd) -> bool:

        try:

            self.tn.write(cmd.encode() + b'\n')

            return True

        except OSError as ose:

            print(f"An socket error occurred attempting to write {cmd} to {self.host}: {ose}")

            return False
        
        except Exception as e:

            print(f"An unknown error occured attempting to write {cmd} to {self.host}: {e}")

            return False


    @connectionManager
    def _read_all(self, timeout : float) -> bytes | bool:

        try:

            return self.tn.read_until(self.shell_prompt.encode(), timeout = timeout)
        
        except EOFError as eof:

            print(f"An error with the connection to {self.host} occurred while reading data: {eof}")

            return False
        
        except Exception as e:

            print(f"An unknown error occurred attempting to read data from {self.host}: {e}")

            return False


    @connectionManager
    def exec(self, cmd : str, timeout : float) -> str | bool:

        """Returns a string containing output from command."""

        try:

            if self.tn is None:

                return False

            self._send(cmd)

            result = self._read_all(timeout).decode()

            result = result.strip(cmd + '\n').strip(self.shell_prompt)

            return result
        
        except Exception as e:

            print(f"An error occurred sending command to {self.host}: {e}")

            return False


    @connectionManager
    def get(self, local_path : str, remote_path : str, port : int = 12345, timeout : int = 20) -> bool:

        localIP = self.__getLocalIP()

        if not localIP:

            print(f"File transfer failed, no local IP to transfer file to.")

            return False
        
        try:

            th = threading.Thread(target = self.__getFileBootstrap, args = [port, timeout, local_path])

            th.start()

            time.sleep(2)

            cmd = f"nc {localIP} {port} < {remote_path}"

            self.exec(cmd, timeout = timeout)

            th.join()

            return True

        except Exception as e:

            print(f"An error occurred getting {remote_path} from the device: {e}")

            return False


    @connectionManager
    def put(self, local_path : str, remote_path : str, port : int) -> None:

        print("Not implemented")

        return None