import requests 
import urllib3
import datetime
import sys
import os
import logging
import tarfile
import json
from PCAPmodules.dri_logger import getLogger
import shutil
from zipfile import ZipFile
# from modules._check_session import checkSessionExpired

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


import requests
import urllib3 

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)




class Device: 

    session: requests.session

    def __init__(self, ip : str, password: str) -> None:


        self.__testIterarion = 0

        self.ip = ip

        self.__password = password

        self.username = 'superadmin'


        ## Create logs parents folder and log folder
        try:

            if os.path.exists('pcap-logs/logs') is False:

                os.makedirs('pcap-logs/logs')

            self.logger = getLogger(name='pcap-monitor', loggerFile='./pcap-logs/logs/pcap-mon.log')
            
        except:

            self.logger.critical('Could not create log folder "pcap-logs/logs" in init')


        ## Create pcaps parents folder and log folder
        try:

            if os.path.exists('pcap-logs/pcaps') is False:

                os.makedirs('pcap-logs/pcaps')
            
        except:

            self.logger.critical('Could not create pcaps folder "pcap-logs/pcaps" in init')

            
        ## Check session creation
        try:
            
            self.session = requests.Session()

        except:

            self.logger.critical('Could not create session object in device initialization')

    ## Check session
    def pingTest(self) -> bool:

        '''Checks if the session is active by pinging the web server returns False if not 200 and True otherwise'''

        pingReq = self.session.get(url=f"https://{self.ip}:8443/api/ping", verify=False)

        if pingReq.status_code != 200:

            #print('Unauthorized ping')
            return False
        
        #print('Ping success')
        return True


    ## Renew session
    def getNewSession(self) -> requests.session:

        tmp_session = requests.Session()

        loginUrl = f"https://{self.ip}:8443/api/login"

        loginPayload = "{username: " + f"\"{self.username}\", " + f"password: \"{self.__password}\"" + "}"

        loginHeaders = {'Content-Type' : 'text/plain'}

        ## Login Request
        loginReq = tmp_session.post(loginUrl, headers = loginHeaders, data = loginPayload, verify = False, timeout = 20)

        if loginReq.status_code != 200:

            self.logger.critical('Could not login in error: ', loginReq.status_code)

            # print('Could not login in error: ', loginReq.status_code)

            return 
        
        self.logger.info('Login sucess returning new session')

        # print('Login success returning new session')

        return tmp_session


    ## Decorator to check if expired session if expired log back in and set the new session for the program to use
    def checkSessionExpired(paramFunction) -> None:

        def checkTokenWrapper(self, *args, **kargs):

            isSessionAuth = self.pingTest()

            if isSessionAuth is False:

                print("hi from checksessionexpored issesssionauth is false")

                ## Get new session and replace exisiting session

                newSession = self.getNewSession()
                
                if newSession is None:

                    self.logger.critical('Session was not created')

                    return

                self.logger.info('Session expired renewing and retrying')

                self.__setSession(newSession)
            
            return paramFunction(self, *args, **kargs)

        return checkTokenWrapper


    def login(self) -> None:

        '''
        Expects key word arguments: dri_username & dri_password. Logs into the devices web server using the class session.
        '''

        loginUrl = f"https://{self.ip}:8443/api/login"

        loginPayload = "{username: " + f"\"{self.username}\", " + f"password: \"{self.__password}\"" + "}"

        loginHeaders = {'Content-Type' : 'text/plain'}


        try:

            loginRequest = self.session.post(loginUrl, headers = loginHeaders, data = loginPayload, verify = False, timeout = 20)

            if loginRequest.status_code != 200:

                loginError = f"Unable to login to device {self.ip}. Response: {loginRequest.status_code}" 

                self.logger.debug(loginError)

                self.session.close()

                return None

        except Exception as e:

            self.logger.debug(f"Error occurred trying to login to device {self.ip}.")

            self.logger.error('Could not log into device. Status code: ', loginRequest.status_code)

            self.session.close()

            return

    @checkSessionExpired
    def logout(self) -> None:

        '''Logs out of the web server using the class session'''

        if self.session is None:

            raise TypeError("Session is of type None. Login credentials may be source of error")
            

        logoutUrl = f"https://{self.ip}:8443/api/logout"

        try:

            logoutRequest = self.session.post(url = logoutUrl, verify = False, timeout = 10)

            if logoutRequest.status_code != 200:

                self.logger.debug(f"Unable to logout from {self.ip}. Response: {logoutRequest.status_code}", file=sys.stderr)

                self.session.close()

                return
            
            self.logger.info('Logout successful')
            # print('Logout successful')

        except Exception:

            self.logger.debug(f"An error occurred while trying to logout of device {self.ip}.")

            self.logger.error('Could not logout from device')

            self.session.close()

            return
        
        
        self.session.close()

        # print('Session closed')
        self.logger.info('Session closed')


    @checkSessionExpired
    def startPcap(self, interface = None, filter = None):

        dt = datetime.datetime.now()

        date = dt.strftime('%Y-%m-%d')

        timestamp = dt.strftime('%Hh-%Mm-%Ss')

        try:

            if filter is not None:
                
                payload = json.dumps({'iface': interface,
                                      'filter': filter})
                
            else:

                payload = json.dumps({'iface': interface})

            startPcapReq = self.session.post(url=f"https://{self.ip}:8443/api/diag/pcap/start", headers = {'Content-Type' : 'application/json'}, data = payload, verify = False, timeout = 20)

            if startPcapReq.status_code != 200:

                self.logger.debug('Could not start pcap, code:', startPcapReq.status_code)

                self.logout()

                return 

            self.logger.info('Started pcap')

        except Exception as e:

            self.logger.debug("Error occured trying to start pcap")

        return timestamp
        

    @checkSessionExpired
    def stopPcap(self):

        try:
            stopPcapReq = self.session.post(url=f"https://{self.ip}:8443/api/diag/pcap/stop", verify = False, data = {}, timeout = 20)

            if stopPcapReq.status_code != 200:

                self.logger.debug('Could not stop pcap, code:', stopPcapReq.status_code)

                self.logout()

                return 

            self.logger.info('Stopped pcap')

        except:

            self.logger.debug("Error occured trying to stop pcap")
        

    @checkSessionExpired
    def savePcap(self) -> str:

        try:
            savePcapReq = self.session.get(url=f"https://{self.ip}:8443/api/diag/pcap/file", headers = {}, data = {}, verify = False, timeout = 20)

            if savePcapReq.status_code != 200:

                self.logger.debug('Could not save pcap, code:', savePcapReq.status_code)

                self.logout()

                return 

            self.logger.info('Successfully downloaded pcap')

            return savePcapReq.content

        except Exception:

            self.logger.debug("Error occured trying to save pcap response: ", savePcapReq.status_code)

            self.logout()
    

    @checkSessionExpired
    def checkPcapSize(self):

        try:
            checkPcapReq = self.session.post(url=f"https://{self.ip}:8443/api/diag/pcap/status", verify = False, data = {}, headers = {})

            if checkPcapReq.status_code != 200:

                self.logger.debug('Could not check pcap, code:', checkPcapReq.status_code)

                self.logout()

                return 

            # self.logger.info('Got pcap status')

            pcap_status = json.loads(checkPcapReq.text)

            return pcap_status['data']['saved_bytes']

        except:

            self.logger.debug("Error occured trying to check pcap")
    

    def storePcap(self, timestamp) -> None:

        '''Creates the parent key and array to store all the future device data entries'''

        dt = datetime.datetime.now()

        date = dt.strftime('%Y-%m-%d')

        deviceSerial = self.getDeviceName()
        
        if os.path.exists(f'pcap-logs/pcaps/{date}') is False:

            os.mkdir(f'pcap-logs/pcaps/{date}')

        try:

            tmp_pcap = self.savePcap()

            with open(f'pcap-logs/pcaps/{date}/{timestamp}-{deviceSerial}.pcap', "wb") as file:

                file.write(tmp_pcap)

            self.logger.info(f'Successfully stored pcap: {timestamp}-{deviceSerial}.pcap in folder {date}')

        except Exception as e:

            self.logger.critical('Could not store pcap')      

            self.logout()


    def __setSession(self, session):

            try:

                self.session = session

                self.logger.info('Successfully set new session')

            except:

                self.logger.critical('Could not set new session')


    @checkSessionExpired
    def debug_snapshot(self):

        dt = datetime.datetime.now()

        deviceSerial = self.getDeviceName()

        timestamp = dt.strftime('%Hh-%Mm-%Ss')

        try:

            print("Grabbing debug snapshot")

            response = self.session.get(url=f"https://{self.ip}:8443/api/diag/download/debugsnapshot", headers = {}, data = {}, verify = False, stream=True)
            
            print(response.status_code)

            if response.status_code != 200:

                self.logger.critical('Could not grab system snapshot')    

            if response.status_code == 200:

                try:

                    print("Saving debug snapshot")

                    if os.path.exists('pcap-logs/logs/snapshot') is False:

                        os.makedirs('pcap-logs/logs/snapshot')

                    with open('pcap-logs/logs/snapshot/system_snapshot', 'wb') as f:

                        for chunk in response.raw.stream(1024):

                            if chunk:  # filter out keep-alive new chunks

                                f.write(chunk)

                    with tarfile.open('pcap-logs/logs/snapshot/system_snapshot', 'r|gz') as z:

                        z.extractall('pcap-logs/logs/snapshot')

                    self.logger.info(f'Successfully stored system snapshot: {timestamp}-{deviceSerial} in folder "logs"')

                except Exception as e:

                    print(e)

                    self.logger.critical('Could not store system snapshot')

                    self.logout()

        except Exception as e:

            print(e)

            self.logout()
        


    @checkSessionExpired
    def getDeviceName(self) -> dict:

        try:

            getParameterRequest = self.session.get(f"https://{self.ip}:8443/api/parameter?data=%7B%22data%22%3A%7B%22path%22%3A%22%2BStatus.DeviceInfo%40%22%7D%7D&ext_session=no", verify=False)

            if getParameterRequest.status_code != 200:

                self.logger.debug(f"Get info parameter failed. Response: {getParameterRequest.status_code}.")

                self.logout()

                return

        except Exception as e:

            self.logger.critical(f"Error occured trying to get parameter to {self.ip}. Error:{e}")

            self.checkSessionExpired = 1

            return

        self.logger.info(f"Get device info param - {self.ip} - success.")

        deviceSerial = json.loads(getParameterRequest.text)['data']['response']['attributes']['SerialNumber']

        return deviceSerial


    def shouldDeleteFolder(self, folder_creation_date) -> bool:

        '''Returns True or False if the folder is three days or older'''

        temp_date = datetime.datetime.strptime(folder_creation_date, '%Y-%m-%d')

        today = datetime.datetime.today()

        if (today - temp_date).days >= 3:

            return True
        
        return False


    def getFolderDates(self) -> list:

        folderDates = os.listdir('./pcap-logs/pcaps')

        if len(folderDates) != 0:
        
            return folderDates
        
        else:

            return [] 
    
        
    def deleteFolders(self, folderDates) -> None:

        for folder in folderDates:

            if self.shouldDeleteFolder(folder):

                try:

                    shutil.rmtree(f'./pcap-logs/pcaps/{folder}')

                    self.logger.info(f'Deleted folder: ./pcap-logs/pcaps/{folder}')

                except OSError as e:

                    self.logger.error(f'Could not delete: ./pcap-logs/pcaps/{folder}. Error: {e}')

                    return 


    def rollPcaps(self) -> None:
        
        ''' Deletes pcap folder that are older than 3 days '''

        folderDates = self.getFolderDates()

        if len(folderDates) > 0:

            return self.deleteFolders(folderDates)
        
        else:

            return


        







        

