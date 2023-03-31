import pprint
import netifaces as ni


class interfaceFinder:
    def __init__(self):
        self.pp = pprint.PrettyPrinter(indent=4)
    def gatewayParser(self,
                      gatewayArr,
                      interface):
        for gateway in gatewayArr:
            # print(gateway)
            if interface in gateway:
                return gateway
        return False


    def getClientIP(self,
                    interface = "eth0" ):
        try:
            # print("Trying to get Ip")
            # self.pp.pprint(ni.ifaddresses(interface))
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            # print("The IP of interface: {}, is {}".format(interface,ip))
            return ip
        except Exception:
            print("There was an error getting the IP of interface {}".format(interface))
            return False


    def getDeviceIP(self,
                    interface = 'eth0'):
        try:
            # print("Trying to get Gateway")
            gatewayTuple = self.gatewayParser(ni.gateways()[2],interface)
            if gatewayTuple is not False:
                # print(gatewayTuple[0])
                return gatewayTuple[0] 
        except Exception:
            print("There was an error getting the gateway of interface {}".format(interface))
            return False
        
        
if __name__ == "__main__":
    ne = interfaceFinder()
    print(ni.gateways()[2])
    ne.getClientIP('en8')
    ne.getDeviceIP('en8')