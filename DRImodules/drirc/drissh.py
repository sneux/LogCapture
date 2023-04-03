# DataRemote SSH Wrapper Library
import re

import time

import paramiko

import scp


def connectionManager(function):

    def checkConnection(self, *args, **kwargs):

        functionResponse = function(self, *args, **kwargs)

        if functionResponse == False:

            try:

                print(f"Retrying connection to {self.host}...")

                connectionStatus = self.connect()

                if connectionStatus == True:

                    print(f"Successfully reconnected to {self.host}! Reruning command...")

                    return function(self, *args, **kwargs)

            except Exception as e:

                print(f"An error occurred attempting to reconnect to host: {e}")

                return

        return functionResponse

    
    def checkTransport(self, *args, **kwargs):

        try:

            self.ssh.get_transport().send_ignore()

        except Exception:

            print(f"No connection to {self.host}, retrying connection...")

            try:

                connectionStatus = self.connect()

                if connectionStatus == True:

                    print(f"Successfully reconnected to {self.host}!")

                    return function(self, *args, **kwargs)
                
                else:

                    print(f"Failed to reconnect to {self.host}")

            except Exception as f:

                print(f"An error occurred attempting to reconnect to host: {f}")

                return
    

    if function.__name__ == "get" or function.__name__ == "put":

        return checkTransport

    else:

        return checkConnection



class DriSSH:

    def __init__(self, host : str, username : str, password : str, shell_prompt : str, port : int = 22):

        self.ssh = paramiko.SSHClient()

        self.host = host

        self.username = username

        self.password = password

        self.shell_prompt = shell_prompt

        self.port = port

        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)

        self.channel = None



    @connectionManager
    def __open_channel(self) -> bool:

        try:

            self.channel = self.ssh.invoke_shell()

            return True

        except Exception as e:

            print(f"Error occurred getting the open channel with SSH: {e}")

            self.channel = None

            return False



    def connect(self, timeout : float = 5) -> bool:

        try:

            self.ssh.connect(self.host, 

            username = self.username, 

            password = self.password,

            port = self.port,

            timeout=timeout)

            self.ssh.get_transport().set_keepalive(15)

        except paramiko.SSHException as e:

            print(f"Error encountered trying to connect to device: {e}")

            return False

        return True



    def close(self) -> None:

        if self.channel:

            self.channel.close()

        self.ssh.close()


    
    def __formatInteractiveOutput(self, cmd : str, data : str) -> str:

        data = data.replace(f"{cmd}", "")

        data = data.replace(f"{self.shell_prompt}", "")

        data = data.replace("[2K", "")

        data = data.replace("\t", " ")

        formattedData = re.sub(f"(\r\n|\r|\n|\x1b)", "", data)

        return formattedData


    @connectionManager
    def interactiveExec(self, cmd: str, timeout : float = 15) -> str | bool:

        """Interactive shell version of exec"""

        self.__open_channel()

        if self.channel == None:

            print(f"Channel could not successfully be established.")

            return False

        self.channel.sendall(f"{cmd}\n".encode())

        time.sleep(1.5)

        data = ""

        self.channel.settimeout(timeout = timeout)

        try:

            retryCount = 1

            timeoutCount = 1

            while True:

                while not self.channel.recv_ready():

                    time.sleep(1.5)

                    retryCount += 1

                    print(timeoutCount)

                    if retryCount > 3 or self.channel.active is None:

                        if data:

                            break

                        self.channel.close()

                        return False

                buffer = self.channel.recv(4096).decode()

                if len(buffer) == 0:

                    break

                data += buffer

                if data.endswith(f"{self.shell_prompt}"):

                    break

                time.sleep(1)

                if timeoutCount > timeout:

                    self.channel.sendall("\x03".encode())

                    break

                timeoutCount += 1

        except Exception as e:

                self.channel.close()

                print(f"Error occured while sending/receiving command: {e}")

                return False

        formattedData = self.__formatInteractiveOutput(cmd, data)

        return formattedData



    @connectionManager
    def exec(self, cmd : str, timeout : float = 5) -> str | bool:

        """Return output from command"""

        try:

            stdout = self.ssh.exec_command(cmd, timeout = timeout)[1]

            result = stdout.read().decode().strip('\n')

        except Exception as e:

            print(f"An error occurred attempting to send a command to {self.host}: {e}")

            return False

        return result



    @connectionManager
    def get(self, local_path : str, remote_path : str) -> bool:

        try:

            scp_client = scp.SCPClient(self.ssh.get_transport())

            scp_client.get(local_path = local_path, remote_path = remote_path)

            scp_client.close()

        except Exception as e:

            print(f"Error occurred getting {remote_path} and saving it to {local_path}: {e}")

            scp_client.close()

            return False

        return True



    @connectionManager
    def put(self, local_path : str, remote_path : str) -> bool:

        try:

            scp_client = scp.SCPClient(self.ssh.get_transport())

            scp_client.put(local_path, remote_path)

            scp_client.close()

        except Exception as e:

            print(f"Error occurred putting {local_path} to {remote_path}.")

            print(e)

            scp_client.close()

            return False

        return True
