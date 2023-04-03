"""

DataRemote Inc. Remote Command Library

Perform commands on a remote DRI device using either Telnet or SSH through a

unified interface.

"""

import enum

from .drissh import DriSSH

from .dritelnet import DriTelnet



class DeviceEnum(enum.IntEnum):

    """

    Enum of all of the different devices.

    """

    DE_9090 = enum.auto()

    DE_9080 = enum.auto()

    DE_9070 = enum.auto()

    DE_9010 = enum.auto()

    DE_90XX = enum.auto()



class DRIRC:

    def __init__(self,

                 host = "192.168.1.1",

                 username = "superadmin",

                 password = "abc123",

                 device = DeviceEnum.DE_9090,

                 use_ssh = False,

                 port = None):

        """Unified interface through which all actions are performed. Use this

        class to execute commands on the remote device, regardless of whether 

        you are use Telnet or SSH.

        Args:

            `host`

                `str` containing the IP of the remote device to connect to.

            `username`

                `str` containing username to use to login into the device.

            `password`

                `str` containing the password to use to login into the device.

            `device`

                `DeviceEnum` to tell the class what kind of device we're logging 

                into.

            `use_ssh`

                `bool` dictating whether to use SSH or Telnet.

        """

        if device is DeviceEnum.DE_9090:

            self.shell_prompt = '\r\nsuperadmin@DataRemote:~# '

        elif device is DeviceEnum.DE_90XX:

            self.shell_prompt =  "dri # "

        else:

            self.shell_prompt = '\r\n# '

        if use_ssh:

            self.shell = DriSSH(host, username, password, self.shell_prompt, port)

        else:

            self.shell = DriTelnet(host, username, password, self.shell_prompt, port)



    def connect(self, timeout = 5) -> bool:

        """Connect to the remote device.

        Returns:

            `bool` containing `True` if connection was successful.

        """

        return self.shell.connect(timeout=timeout)



    def close(self):

        return self.shell.close()



    def exec(self, cmd: str, timeout: float = 5) -> str:

        """Execute a command on the remote device.
        
        Args:

        `cmd`

            `str` containing the command to execute on the remote device.

        `timeout`

            `float` containing the timeout to be passed along to the underlying

            libraries.


        Returns:

            `str` containing the output of the command executed on the device.

        """

        return self.shell.exec(cmd, timeout)



    def interactiveExec(self, cmd : str, timeout : float = 10) -> str:

        return self.shell.interactiveExec(cmd, timeout)



    def get(self, local_path: str, remote_path: str) -> str:

        self.shell.get(local_path, remote_path)



    def put(self, local_path: str, remote_path: str) -> str:

        self.shell.put(local_path, remote_path)
