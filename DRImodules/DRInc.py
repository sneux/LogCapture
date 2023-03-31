import re
import os
import time
import threading
import nclib as nc
from DRImodules import DRIinterfaces
from os import SEEK_END



class NC:

    def __init__(self,
                 clientIP=None,
                 port=42069,
                 interface='eth0'):

        try:

            # self.ne = DRIinterfaces.interfaceStuff()

            if clientIP is None:

                self.clientIP = self.ne.getClientIP(interface)

            else:

                self.clientIP = clientIP

        except Exception as e:

            pass

        self.port = port



    def listen(self):

        try:

            result = nc.Netcat(listen=(self.port))

            return result

        except Exception as e:

            print("There has been an error trying to listen on port {}: {}".format(self.port,e))

            return False



    def listenForFile(self,
                      path='./',
                      fileName = 'results',
                      prefixDate = True):

        try:
            
            if prefixDate:

                print("\nPrefixing date\n")

                fullPath = "{}/{}M-{}D-{}".format(path,
                                                    time.localtime().tm_mon,
                                                    time.localtime().tm_mday,
                                                    fileName)
                                            
            else:

                fullPath = "{}/{}".format(path,
                                          fileName)

            # if os.path.exists(fullPath):

            #     print("\nPrevious syslog Exists\n")

            #     self.handlePreExisting(path,
            #                            fullPath)

            # else:

            # print(os.path.exists(fullPath))

            # print("\nNo previous syslog\n")

            with open(fullPath,'wb+') as sysFile:

                # print("\nConnecting...\n")

                results = nc.Netcat(listen = self.port).recv_all(30)

                # print("Data recieved writing to file...\n")

                sysFile.write(results)

                # print("Completed!\n")

                # print("Data recieved {} \n".format(results.decode("utf-8")))

                return results

        except Exception as e:

            print("There has been an error {}".format(e))

            return False



    def handlePreExisting(self,
                          path,
                          fullPath):

        try:

            with open (fullPath, 'rb+') as oldFile:

                with open("{}/tempSys.txt".format(path),'wb+') as tempFile:

                    print("\nWaiting for data\n")

                    results = nc.Netcat(listen = self.port).recv_all(30)

                    print("\nWriting bytes to temp file\n")

                    tempFile.write(results)

                    print("\nGoing to start of file\n")

                    tempFile.seek(0)

                    print("\n Finding last line of old file\n")

                    lastLine = self.lastLineParser(oldFile).decode("utf-8").rstrip("\r\n")

                    print(lastLine)

                    difference = False

                    search = True

# Scan through the temporary file and compare each line to the last stored line of the previous 
# syslog when you find a match begin writing the new lines to the old syslog

                    for line in tempFile:

                        formattedLine = line.decode("utf-8").rstrip("\r\n")

                        if(difference is True):

                            # print("\n{}\n".format(formattedLined))

                            oldFile.write(line) 



                        # if((re.search(regex, line.decode("utf-8"))) and (search  == True)): # Over Engineering at its finest

                        # if((re.search(lastLine, formattedLine)) and (search  is True)):
                        
                        if((lastLine in formattedLine) and (search  is True)):

                            print("\Match Found begin writing\n")

                            print(line)
                            
                            difference = True

                            search = False

                    if(difference is False):
                        
                        print("\nNo match found\n")
            
            return True

        except Exception as e:

            print("there has been an error in the handle pre existing method: {}".format(e))



    def lastLineParser(self,
                 file = None):
    
        for line in file:

            pass

        return line

                    

if __name__ == "__main__":

   DRInc = NC()

   DRInc.listenForFile(fileName = "syslog.txt")

