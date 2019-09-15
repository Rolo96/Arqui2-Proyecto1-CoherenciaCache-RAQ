##########################################
#       Tecnologico de Costa Rica        #
#     Arquitectura de computadores 2     #
#               Proyecto 1               #
#             Clock component            #
#               Raul Arias               #             
##########################################

"""
This file contains the clock component implementation
"""

#---------------------------------Imports --------------------------------------
from time import sleep
import threading
from threading import Event
import settings

#------------------------------Clock ---------------------------------
class Clock:
    """
    Class to abstract the clock component
    """

    #----------------Constructor---------------------
    def __init__(self):
        """
        Class constructor    
        """
        self.isRunning = True

    def runClock (self):
        """
        Method to update the clock based on system delay
        """
        while (self.isRunning):
            
            # ---------------High clock--------------
            settings.HighEvent.set()
            settings.HighEvent.clear()
            settings.GuiMutex.acquire()
            settings.GuiQueue.put(settings.GREEN_CLOCK_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR)
            settings.GuiMutex.release()
            sleep(0.5*settings.SYSTEM_DELAY)

            # ---------------Low clock---------------
            settings.LowEvent.set()
            settings.LowEvent.clear()
            settings.GuiMutex.acquire()
            settings.GuiQueue.put(settings.RED_CLOCK_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR)
            settings.GuiMutex.release()
            sleep(0.5*settings.SYSTEM_DELAY)

    def run (self):
        """
        Method to create the clock thread
        """
        t = threading.Thread(target=self.runClock)
        t.start()
