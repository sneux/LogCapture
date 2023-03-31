import gpiozero

class led():

    def __init__(self):
        
        self.builtLEDs = []


    def isList(self,
               toCheck=None):

        if type(toCheck) == list:

            return True

        return False
        
    

    def buildLedObj(self,
                    ledArr=None,
                    color=None,
                    pin=None):
        
        builtLEDs = []

        print(ledArr)

        print(color)
        
        print(pin)


        if ledArr is None:

                try:

                    print("\nBuilding LED\n")

                    builtLED = {
                        "color": color,
                        "pin": pin,
                        "action": gpiozero.PWMLED(pin)
                    }

                    print("LED Object Created sucessfully")

                    builtLEDs.append(builtLED)

                    self.builtLEDs.append(builtLED)

                    return builtLEDs

                except Exception as e:

                    print("\nYour LED object could not be built \nError: {}\n".format(e))

                    return False
        
        else:

            try:

                for led in ledArr:

                    print(led)

                    builtLED = {
                        "color": led["color"],
                        "pin": led["pin"],
                        "action": gpiozero.PWMLED(led["pin"])
                    }

                    print("\nLED Object Created sucessfully\n")

                    builtLEDs.append(builtLED)

                    self.builtLEDs.append(builtLED)

                
                
                return builtLEDs

            except Exception as e:

                print("\nYour LED objects could not be built \nError: {}\n".format(e))

                return False



    def findLed(self,
                color = None,
                pin = None):

        for led in self.builtLEDs:
            if color == led["color"] and pin == led["pin"]:
                return led



    def ledOn(self,
              ledObj = None,
              power = 0.5,
              color = None,
              pin = None):
        
        try:

            if (self.isList(ledObj)):

                for led in ledObj:

                    led["action"].value = power

                    print("{} LED turned on".format(led))

                return True
            
            else:

                if ((ledObj is None) and (pin is not None)):

                    ledObj = self.findLed(color,pin)

                ledObj["action"].value = power

                print("\nLED Turned On\n")

                return True

            print("\n*****Theres no way it should have gotten here but it did so turning off the LED may have failed.\n*****")

            return False

        except Exception as e:

            print("\nThere was an error turning On the LED: {}\n".format(e))

            return False
            


    def ledOff(self,
               ledObj = None,
               color = None,
               pin = None):

        try:

            if self.isList(ledObj):

                print("I was passed a list to shut off")

                for led in ledObj:

                    led["action"].value = 0.0

                return True
            
            else:

                if ((ledObj is None) and (pin is not None)):

                    print("I'm about to look for the LEDs")

                    ledObj = self.findLed(color,pin)

                print("I'm shutting off the LED now")

                ledObj["action"].value = 0.0

                print("\nLED Turned Off\n")

                return True

            print("\n*****Theres no way it should have gotten here but it did so turning off the LED may have failed.\n*****")

            return False

        except Exception as e:

            print("\nThere was an error turning off the LED: {}\n".format(e))

            return False



    def ledAllOff(self,
                  ledList=None):

        try:

            if ledList is not None:

                for led in ledList:

                    print("Shutting off {} LED on pin {}".format(led["color"],led["pin"]))

                    led["action"].value = 0.0

                return True
            
            else:
                

                for led in self.builtLEDs:

                    print("Turning off: {}".format(led))

                    print("Shutting off {} LED on pin {}".format(led["color"],led["pin"]))

                    led["action"].value = 0.0

        except gpiozero.GPIOZeroError as e:

            print("\nThere has been an Error shutting off the LEDs\n")

        

    def ledBlink(self,
                 ledObj = None,
                 speed = 1,
                 color = None,
                 pin = None):

        try:

            if self.isList(ledObj):

                for led in ledObj:

                    print("\n Beginning LED Blink at speed: {}".format(speed))

                    led["action"].blink(speed,speed)

                    return True

                print("LED not found")

                return False

            else:

                if ((ledObj is None) and (pin is not None)):

                    ledObj = self.findLed(color,pin)

                print("\n Beginning LED Blink at speed: {}".format(speed))

                ledObj["action"].blink(speed,speed)

                return True
                
        
        except Exception as e:

            print("\nThere has been an error trying to make the LED Blink\n")



    def ledPulse(self,
                 ledObj=None,
                 speed=1,
                 color = None,
                 pin = None):
        try:

            if self.isList(ledObj):

                for led in ledObj:

                    print("{} LED pulsing at speed: {}\n".format(led.color,speed))

                    led["action"].pulse(speed,speed)

                return True

            else:

                if ((ledObj is None) and (pin is not None)):

                    ledObj = self.findLed(color,pin)

                print("{} LED pulsing at speed: {}\n".format(ledObj.color,speed))

                ledObj["action"].pulse(speed,speed)

        except Exception as e:

            print("\n There has been an error making the LED pulse: {}\n".format(e))