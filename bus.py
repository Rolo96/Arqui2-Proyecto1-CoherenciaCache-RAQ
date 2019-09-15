##########################################
#       Tecnologico de Costa Rica        #
#     Arquitectura de computadores 2     #
#               Proyecto 1               #
#              Bus component             #
#               Raul Arias               #             
##########################################

"""
This file contains the bus and bus controller component implementation
"""

#---------------------------------Imports --------------------------------------
import threading
import settings

#--------------------------------Bus ---------------------------------
class Bus:
    """
    Class to abstract the bus component
    """
    #----------------Constructor---------------------
    def __init__(self):
        """
        Class constructor
        """
        self.data = ""

#------------------------------BusController -------------------------
class BusController:
    """
    Class to abstract the bus controller component
    """
    #----------------Constructor---------------------
    def __init__(self):
        """
        Class constructor
        """
        self.requests = []
        self.bus = Bus()
        self.bus.data = ""
        self.isRunning = True
        

    def runController (self):
        """
        Method to run the bus controller
        """
        count = 0
        value = None
        while (self.isRunning):

            #-----------------Read time--------------
            settings.LowEvent.wait()
            actualBusData = self.bus.data #Get bus data

            if actualBusData == "":#Bus empty -> Can write
                if len(self.requests) > 0: #There is a request -> Save to write
                    value = self.requests.pop(0)
                else: #Keep value
                    value = None
                count = 0
                
            elif count >= settings.BUS_DELAY:#No empty and is delay -> Can write
                if len(self.requests) > 0:#There is more to load -> Save to write
                    value = self.requests.pop(0)
                else: #Nothing more -> Save empty to write
                    value = ""
                count = 0
            else: # Keep value
                value = None
                
            count = count + 1

            
            #-----------------Write time-------------
            settings.HighEvent.wait()
            if value != None: #There is a value to load to bus -> Load it to bus and gui
                self.bus.data = value
                settings.GuiMutex.acquire()
                settings.GuiQueue.put(settings.BUS_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + value)
                settings.GuiMutex.release()

    def run (self):
        """
        Method to create the bus controller thread
        """
        t = threading.Thread(target=self.runController)
        t.start()
