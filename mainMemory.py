##########################################
#       Tecnologico de Costa Rica        #
#     Arquitectura de computadores 2     #
#               Proyecto 1               #
#               Main memory              #
#               Raul Arias               #             
##########################################

"""
This file contains the main memory component implementation
"""

#---------------------------------Imports --------------------------------------
import threading
import settings
import busGlobals

#-----------------------------MainMemory -----------------------------
class MainMemory:
    """
    Class to abstract the main memory component
    """
    #----------------Constructor---------------------
    def __init__(self):
        """
        Class constructor 
        """
        self.memorySize = settings.MAIN_MEMORY_SIZE
        self.delay = settings.MAIN_MEMORY_DELAY
        self.isRunning = True
        self.memory = []
        self.memory = [0] * self.memorySize # Fill memory with zeros

    #------------------Methods-----------------------
    def get_data(self, position):
        """
        Get data from position with delay

        Parameters:
        position (int): Memory position to get

        Returns:
        int:Data in memory
        """

        #---------------Memory delay-----------------
        count = 0
        while(count<settings.MAIN_MEMORY_DELAY):
            settings.LowEvent.wait()
            count = count + 1

        #------------------Read----------------------
        return self.memory[position]
         
    def insert_data(self, position, data):
        """
        Insert data in memory position

        Parameters:
        position (int): Memory position to store data
        data (int): Data to store
        """

        #---------------Memory delay-----------------
        count = 0
        while(count<settings.MAIN_MEMORY_DELAY):
            settings.HighEvent.wait()
            count = count + 1
        
        #--------------------Write-------------------
        self.memory[position] = data

    def print_memory(self):
        """
        Prints memory content
        """
        print(self.memory)

    def runMemory (self):
        """
        Method to run the main memory
        """
        value = None
        lastInstruction = ""
        while (self.isRunning):

            #-----------Write time-----------
            settings.HighEvent.wait()
            actualBusData = busGlobals.MainBus.bus.data
            if actualBusData != "": #INstruction in bus
                instructionSplitted = actualBusData.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction
                if instructionSplitted[1] == settings.LOAD_INSTRUCTION_TYPE: #Read -> I have the value -> answer
                    if value != None: #I have the value -> write
                        newData = actualBusData + settings.INSTRUCTION_SEPARATOR + str(value)
                        busGlobals.MainBus.bus.data = newData #Write to bus
                        settings.GuiMutex.acquire()
                        settings.GuiQueue.put(settings.BUS_SIMPLE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + newData)#Write to gui
                        settings.GuiMutex.release()
                        value = None
                else: #Write -> Write to mem and gui
                    if value != None:
                        self.insert_data(int(instructionSplitted[2]), int(instructionSplitted[3]))
                        settings.GuiMutex.acquire()
                        settings.GuiQueue.put(settings.MEMORY_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + instructionSplitted[2] + settings.GUI_INSTRUCTION_SEPARATOR + instructionSplitted[3] )
                        settings.GuiMutex.release()
                        value = None

            #------------Read time--------------
            settings.LowEvent.wait()
            actualBusData = busGlobals.MainBus.bus.data
            if  actualBusData != "": #Instruction in bus -> Read
                instructionSplitted = actualBusData.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction
                if instructionSplitted[1] == settings.LOAD_INSTRUCTION_TYPE and len(instructionSplitted)<4: #Read -> and not answered-> read
                    value = self.get_data(int(instructionSplitted[2])) #Read
                elif instructionSplitted[1] == settings.STORE_INSTRUCTION_TYPE and lastInstruction != actualBusData: #Write
                    value = 0
                lastInstruction = actualBusData

    def run (self):
        """
        Method to create the main memory thread
        """
        t = threading.Thread(target=self.runMemory)
        t.start()
