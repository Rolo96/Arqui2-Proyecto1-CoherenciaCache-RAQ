##########################################
#       Tecnologico de Costa Rica        #
#     Arquitectura de computadores 2     #
#               Proyecto 1               #
#                Processor               #
#               Raul Arias               #             
##########################################

"""
This file contains the processor component implementation and instruction memory
"""

#---------------------------------Imports --------------------------------------
from time import sleep
import numpy as np
import random as rn
import settings
import cache
import threading
import busGlobals


#-------------------------InstructionsMemory -------------------------
class InstructionsMemory:
    """
    Class to abstract the instructions memory component
    """
    #----------------Constants-----------------------
    MEMORY_INSTRUCTIONS_PROBABILITY = .66
    STORE_INSTRUCTIONS_PROBABILITY = .5

    #----------------Constructor---------------------
    def __init__(self, processorId):
        """
        Class constructor

        Parameters:
        memorySize (int): Memory size    
        """
        self.memorySize = settings.INSTRUCTIONS_MEMORY_SIZE
        self.memory = []
        self.memory = [0] * settings.INSTRUCTIONS_MEMORY_SIZE # Fill memory with zeros
        self.processorId = processorId
        self.generate_data()

    #------------------Methods-----------------------
    def get_data(self, position):
        """
        Get data from position with delay

        Parameters:
        position (int): Memory position to get

        Returns:
        string:Data in memory
        """
        return self.memory[position]
         
    def insert_data(self, position, data):
        """
        Insert data in memory position

        Parameters:
        position (int): Memory position to store data
        data (string): Data to store
        """
        self.memory[position] = data

    def generate_data(self):
        """
        Generate instructions based on binomial probability and saves it in memory
        """
        for position in range(self.memorySize): #Fill memory
            
            value = str(rn.randrange(0,15,1))#Position memory for memory instructions or value to operation instruction
            isMemoryInstruction = np.random.binomial(1, self.MEMORY_INSTRUCTIONS_PROBABILITY)#Type of operation based on binomial probability

            if isMemoryInstruction == 1:#Memory instruction
                isStoreInstruction = np.random.binomial(1, self.STORE_INSTRUCTIONS_PROBABILITY)#Type of memory instruction based on binomial probability
                if isStoreInstruction == 1:#Store instruction
                    self.memory[position] = str(self.processorId) + settings.INSTRUCTION_SEPARATOR + settings.STORE_INSTRUCTION_TYPE + settings.INSTRUCTION_SEPARATOR + value + settings.INSTRUCTION_SEPARATOR + str(self.processorId)
                else:#Load instruction
                    self.memory[position] = str(self.processorId) + settings.INSTRUCTION_SEPARATOR + settings.LOAD_INSTRUCTION_TYPE + settings.INSTRUCTION_SEPARATOR + value
            else:#Operation instruction
                self.memory[position] = str(self.processorId) + settings.INSTRUCTION_SEPARATOR + settings.OPERATION_INSTRUCTION_TYPE + settings.INSTRUCTION_SEPARATOR + value
                
    def print_memory(self):
        """
        Prints memory content
        """
        print(self.memory)

#---------------------------------Processor --------------------------
class Processor:
    """
    Class to abstract the processor component
    """
    #----------------Constructor---------------------
    def __init__(self, processorId):
        """
        Class constructor

        Parameters:
        processorId (int): Processor identifier
        """
        self.processorId = processorId
        self.instructionsMemory = InstructionsMemory(processorId)
        self.cacheController = cache.CacheController(processorId)
        self.cacheController.run()

    #------------------Methods-----------------------
    def execute_instructions(self):
        """
        Executes all the instructions in memory   
        """
        for position in range(settings.INSTRUCTIONS_MEMORY_SIZE):#Execute all instructions
            settings.LowEvent.wait()
            instruction = self.instructionsMemory.get_data(position)
            instructionSplitted = instruction.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction
            settings.GuiMutex.acquire()
            settings.GuiQueue.put(settings.PROCESSOR_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + instruction)
            settings.GuiMutex.release()
            if instructionSplitted[1] == settings.OPERATION_INSTRUCTION_TYPE:#Operation instruction
                self.execute_operation_instruction(instruction)
            elif instructionSplitted[1] == settings.STORE_INSTRUCTION_TYPE:#Store instruction
                self.execute_store_instruction(instruction)
            else:#Load instruction
                self.execute_load_instruction(instruction)

    def execute_operation_instruction(self, instruction):
        """
        Executes an operation instruction

        Parameters:
        instruction (string): Instruction to execute
        """
        instructionSplitted = instruction.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction
        result = instructionSplitted[2] + instructionSplitted[2]

    def execute_store_instruction(self, instruction):
        """
        Executes a store instruction

        Parameters:
        instruction (string): Instruction to execute
        """

        instructionSplitted = instruction.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction
        count = 0

        #--------------Read time---------------------
        memoryPosition = int(instructionSplitted[2])#Memory position
        value = int(instructionSplitted[3])
        inCache = self.cacheController.cacheMemory.isInCache(memoryPosition, False, True) #Is in cache? -> if not in cache and the actual value is in M send to memory

        #--------------Write time--------------------
        settings.HighEvent.wait()
        
        if inCache == None: #Not in cache -> Miss to gui
            settings.GuiMutex.acquire()
            settings.GuiQueue.put(settings.PROCESSOR_STATUS_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Cache miss")
            settings.GuiMutex.release()

        else: #In cache -> Hit to gui
            settings.GuiMutex.acquire()
            settings.GuiQueue.put(settings.PROCESSOR_STATUS_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Cache hit")
            settings.GuiMutex.release()
        
        #----------Send invalid to caches------------
        settings.CacheBusMutex.acquire()
        busGlobals.CacheBus.requests.insert(0,instruction)
        settings.CacheBusMutex.release()
        
        #----------Send invalid to gui---------------
        settings.GuiMutex.acquire()
        settings.GuiQueue.put(settings.CACHE_BUS_REQUEST_NOW_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + instruction)
        settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Waiting invalid")
        settings.GuiMutex.release()

        count = 0
        inBus = False
        #--------Wait for cache invalid--------------
        while(count<settings.PROCESSOR_CACHE_BUS_MAX_DELAY):
            settings.LowEvent.wait()
            actualCacheBusData = busGlobals.CacheBus.bus.data

            if actualCacheBusData == instruction: #Instruction in bus -> Caches are invalidating
                inBus = True
            elif inBus == True: #Was in bus but not now -> Caches invalidating correct -> Continue
                break;
            count = count + 1

        #-----------------Write time-----------------
        settings.HighEvent.wait()
        
        #----------Update cache and gui--------------
        self.cacheController.cacheMemory.insert_data(memoryPosition, value, 'M')
        instructionToGui = "M-" + instructionSplitted[2] + "-" + instructionSplitted[3]
        settings.GuiMutex.acquire()
        settings.GuiQueue.put(settings.CACHE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) +
                              settings.GUI_INSTRUCTION_SEPARATOR + instructionSplitted[2] + settings.GUI_INSTRUCTION_SEPARATOR +
                              instructionToGui)
        settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Updating data")
        settings.GuiMutex.release()
        
    def execute_load_instruction(self, instruction):
        """
        Executes a load instruction

        Parameters:
        instruction (string): Instruction to execute
        """

        instructionSplitted = instruction.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction
        count = 0

        #--------------Read time---------------------
        memoryPosition = int(instructionSplitted[2])#Memory position
        value = self.cacheController.cacheMemory.isInCache(memoryPosition, False, True) #Is in cache? -> if not in cache and the actual value is in M send to memory

        #--------------Write time--------------------
        settings.HighEvent.wait()
        
        if value == None: #Not in cache -> Miss to gui
            settings.GuiMutex.acquire()
            settings.GuiQueue.put(settings.PROCESSOR_STATUS_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Cache miss")
            settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Waiting for cache bus")
            settings.GuiQueue.put(settings.CACHE_BUS_REQUEST_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + instruction)
            settings.GuiMutex.release()

            #-Is in another cache? -> Write to bus and gui-
            settings.CacheBusMutex.acquire()
            busGlobals.CacheBus.requests.append(instruction)
            settings.CacheBusMutex.release()

            count = 0
            inBus = False
            
            #--------Wait for cache responses--------
            busCicles = 0
            while(count<settings.PROCESSOR_CACHE_BUS_MAX_DELAY):

                settings.LowEvent.wait()
                actualCacheBusData = busGlobals.CacheBus.bus.data
                if actualCacheBusData == instruction: #Instruction in bus -> Caches are searching
                    inBus = True
                    if busCicles == 0: #-> In bus to gui
                        settings.GuiMutex.acquire() # -> Waiting to gui
                        settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "In cache bus")
                        settings.GuiMutex.release()
                    busCicles = busCicles + 1
                elif instruction in actualCacheBusData: #Instruction in bus but actualiced -> Caches have the data -> get it -> put it in cache and gui
                    settings.GuiMutex.acquire() # -> Read to gui
                    settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Read from another cache")
                    settings.GuiMutex.release()

                    value = actualCacheBusData.split(settings.INSTRUCTION_SEPARATOR)[3]
                    self.cacheController.cacheMemory.insert_data(memoryPosition, int(value), 'S')
                    instructionToGui = "S-" + instructionSplitted[2] + "-" + value
                    settings.GuiMutex.acquire()
                    settings.GuiQueue.put(settings.CACHE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) +
                                          settings.GUI_INSTRUCTION_SEPARATOR + instructionSplitted[2] + settings.GUI_INSTRUCTION_SEPARATOR +
                                          instructionToGui)
                    settings.GuiMutex.release()
                    break;
                elif inBus == True: #Was in bus but not now -> Caches havent the data -> Continue
                    break;

                if busCicles >= settings.CACHE_BUS_DELAY: #Was in bus but anyone respond -> Continue
                    break;
                count = count + 1

            #--------------Write time----------------
            settings.HighEvent.wait()

            #------------Get from memory-------------
            if value == None: # Not in another cache -> Get from memory -> Send to memory bus and gui

                settings.GuiMutex.acquire() # -> Waiting to gui
                settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Waiting for main bus")
                settings.GuiQueue.put(settings.BUS_REQUEST_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + instruction)
                settings.GuiMutex.release()
                
                settings.MainBusMutex.acquire()
                busGlobals.MainBus.requests.append(instruction)
                settings.MainBusMutex.release()

                count = 0
                inBus = False
                #-------Wait for memory response-----
                busCicles = 0
                while(count<settings.PROCESSOR_BUS_MAX_DELAY):

                    settings.LowEvent.wait()
                    actualBusData = busGlobals.MainBus.bus.data

                    if actualBusData == instruction: #Instruction in bus -> Memory are searching
                        inBus = True
                        if busCicles == 0: #-> In bus to gui
                            settings.GuiMutex.acquire() # -> Waiting to gui
                            settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "In main bus")
                            settings.GuiMutex.release()
                        busCicles = busCicles + 1
                    elif instruction in actualBusData: #Instruction in bus but actualiced -> Memory put the data -> get it -> put it in cache and gui
                        settings.GuiMutex.acquire() # -> Waiting to gui
                        settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Read from memory")
                        settings.GuiMutex.release()
                        settings.HighEvent.wait()
                        value = actualBusData.split(settings.INSTRUCTION_SEPARATOR)[3]
                        self.cacheController.cacheMemory.insert_data(memoryPosition, int(value), 'S')
                        instructionToGui = "S-" + instructionSplitted[2] + "-" + str(value)
                        settings.GuiMutex.acquire()
                        settings.GuiQueue.put(settings.CACHE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) +
                                              settings.GUI_INSTRUCTION_SEPARATOR + instructionSplitted[2] + settings.GUI_INSTRUCTION_SEPARATOR +
                                              instructionToGui)
                        settings.GuiMutex.release()
                        break;
                    elif inBus == True: #Was in bus but not now -> Error
                        print("ERROR: " + instruction + " count: " + str(count))
                        break;
                    count = count + 1

        else: #Data in cache -> Hit to gui
            settings.GuiMutex.acquire()
            settings.GuiQueue.put(settings.PROCESSOR_STATUS_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Cache hit")
            settings.GuiMutex.release()
            
    def run (self):
        """
        Method to create the clock thread
        """
        t = threading.Thread(target=self.execute_instructions)
        t.start()
