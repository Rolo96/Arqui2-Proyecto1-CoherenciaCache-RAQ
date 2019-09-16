##########################################
#       Tecnologico de Costa Rica        #
#     Arquitectura de computadores 2     #
#               Proyecto 1               #
#             Cache component            #
#               Raul Arias               #             
##########################################

"""
This file contains the cache and cache controller component implementation
"""

#---------------------------------Imports --------------------------------------
import settings
import threading
import busGlobals

#-------------------------CacheMemory --------------------------------
class CacheMemory:
    """
    Class to abstract the cache memory component
    """

    #----------------Constants-----------------------
    VALID_BIT = "Valid"
    ADDRESS = "Address"
    VALUE = "Value" 
    
    #----------------Constructor---------------------
    def __init__(self, processorId):
        """
        Class constructor
        Parameters:
        processorId (int): Processor identifier
        """
        self.processorId = processorId
        self.memorySize = settings.CACHE_MEMORY_SIZE
        self.delay = settings.CACHE_DELAY
        self.memory = []
        
        EmptyValue =	{
          self.VALID_BIT: 'I',
          self.ADDRESS: 0,
          self.VALUE: 0
        }

        for position in range(settings.CACHE_MEMORY_SIZE): #Fill memory
            self.memory.append(EmptyValue.copy())
            
    #------------------Methods-----------------------
    def isInCache(self, address, modifyIfExists, modifyIfNotExists ):
        """
        Find data in cache
        
        Parameters:
        address (int): Main memory position to find data
        modifyIfExists (bool): If value exists in M state send to memory
        modifyIfNotExists (bool): If value not exists and the actual value is in M state send to memory 
        
        Returns:
        int: Value in memory or None if value isnot in memory
        """

        #---------------Memory delay-----------------
        count = 0
        while(count<settings.CACHE_DELAY):
            settings.LowEvent.wait()
            count = count + 1

        #------------------Read----------------------
        position = address%self.memorySize #Direct correspondence

        if self.memory[position][self.ADDRESS] == address: #Maybe hit
            
            if self.memory[position][self.VALID_BIT] == 'S': #Hit -> Is in cache shared -> return the value
                return self.memory[position][self.VALUE]
            
            elif self.memory[position][self.VALID_BIT] == 'M': #Hit -> Is in cache but modified -> return the value and if is necesary write back
                
                if modifyIfExists == True: #If value exists in M state -> Write back

                    instruction = str(self.processorId) + settings.INSTRUCTION_SEPARATOR + settings.STORE_INSTRUCTION_TYPE + settings.INSTRUCTION_SEPARATOR + str(address) + settings.INSTRUCTION_SEPARATOR + str(self.processorId)

                    settings.MainBusMutex.acquire() #Send to main bus
                    busGlobals.MainBus.requests.insert(0,instruction)
                    settings.MainBusMutex.release()

                    self.memory[position][self.VALID_BIT] == 'S'
                    instructionToGui = "S-" + str(address) + "-" + str(self.memory[position][self.VALUE])

                    settings.GuiMutex.acquire() #GUI draw
                    settings.GuiQueue.put(settings.BUS_REQUEST_NOW_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + instruction)
                    settings.GuiQueue.put(settings.CACHE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) +
                                          settings.GUI_INSTRUCTION_SEPARATOR + str(address) + settings.GUI_INSTRUCTION_SEPARATOR +
                                          instructionToGui)
                    settings.GuiMutex.release()
                return self.memory[position][self.VALUE]
            
            else: #Miss -> Is in cache but invalid -> return none
                return None
            
        else:# Miss -> Return none and write back if necesary
            
            if modifyIfNotExists == True and self.memory[position][self.VALID_BIT] == 'M': #Write back position will be used

                settings.GuiMutex.acquire() # -> Waiting to gui
                settings.GuiQueue.put(settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) + settings.GUI_INSTRUCTION_SEPARATOR + "Waiting write back")
                settings.GuiMutex.release()
                
                instruction = str(self.processorId) + settings.INSTRUCTION_SEPARATOR + settings.STORE_INSTRUCTION_TYPE + settings.INSTRUCTION_SEPARATOR + str(self.memory[position][self.ADDRESS]) + settings.INSTRUCTION_SEPARATOR + str(self.processorId)
                settings.MainBusMutex.acquire() #Instruction to bus
                busGlobals.MainBus.requests.insert(0,instruction)
                settings.MainBusMutex.release()

                settings.GuiMutex.acquire() #GUI draw
                settings.GuiQueue.put(settings.BUS_REQUEST_NOW_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + instruction)
                settings.GuiMutex.release()

                count = 0
                inBus = False
                #--------Wait write the value----
                while(count<settings.PROCESSOR_BUS_MAX_DELAY):
                    settings.LowEvent.wait()
                    actualBusData = busGlobals.MainBus.bus.data

                    if actualBusData == instruction: #Instruction in bus -> Memory is writing
                        inBus = True
                    elif inBus == True: #Was in bus but not now -> Continue
                        break;
                    count = count + 1
                
            return None
         
    def insert_data(self, address, data, status):
        """
        Insert data in memory position

        Parameters:
        address (int): Memory position to store data
        data (int): Data to store
        """

        #---------------Memory delay-----------------
        count = 0
        while(count<settings.CACHE_DELAY):
            settings.HighEvent.wait()
            count = count + 1
        
        #--------------------Write-------------------
        position = address%self.memorySize #Direct correspondence
        self.memory[position][self.VALID_BIT] = status 
        self.memory[position][self.ADDRESS] = address
        self.memory[position][self.VALUE] = data

    def invalid_data(self, address):
        """
        Invalid data in memory position
        
        Parameters:
        address (int): Memory position to invalid
        """        
        #--------------------Write-------------------
        if self.isInCache(address, False, False) != None:# Is in cache -> Invalid
            settings.HighEvent.wait()
            position = address%self.memorySize #Direct correspondence
            self.memory[position][self.VALID_BIT] = 'I'
            
            instructionToGui = "I-" + str(self.memory[position][self.ADDRESS]) + "-" + str(self.memory[position][self.VALUE])
            settings.GuiMutex.acquire() #GUI Draw
            settings.GuiQueue.put(settings.CACHE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + str(self.processorId) +
                                  settings.GUI_INSTRUCTION_SEPARATOR + str(address) + settings.GUI_INSTRUCTION_SEPARATOR +
                                  instructionToGui)
            settings.GuiMutex.release()
            
    def print_memory(self):
        """
        Prints memory content
        """
        print(self.memory)


#-----------------------------CacheController ------------------------
class CacheController:
    """
    Class to abstract the cache controller component
    """
    def __init__(self, processorId):
        """
        Class constructor

        Parameters:
        processorId (int): Processor identifier
        """
        self.processorId = processorId
        self.cacheMemory = CacheMemory(processorId)
        self.isRunning = True

    def runCache (self):
        """
        Method to run the cache memory
        """
        value = None
        while (self.isRunning):

            #-----------Write time-------------------
            settings.HighEvent.wait()
            actualBusData = busGlobals.CacheBus.bus.data
            
            if  actualBusData!= "": #Instruction in bus -> Maybe write too bus
                
                instructionSplitted = actualBusData.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction
                if instructionSplitted[1] == settings.LOAD_INSTRUCTION_TYPE: #Read instruction -> If have the value answer
                    if (value != None): #I have the value -> If I am first -> Write to bus and gui
                        settings.CacheBusMutex.acquire()
                        if (len(busGlobals.CacheBus.bus.data.split(settings.INSTRUCTION_SEPARATOR)) < 4):#Not answered -> answer
                            newData = actualBusData + settings.INSTRUCTION_SEPARATOR + str(value)
                            busGlobals.CacheBus.bus.data = newData
                            settings.GuiMutex.acquire()
                            settings.GuiQueue.put(settings.CACHE_BUS_SIMPLE_GUI_INSTRUCTION_TYPE + settings.GUI_INSTRUCTION_SEPARATOR + newData)
                            settings.GuiMutex.release()
                        settings.CacheBusMutex.release()           
                        value = None
                
            #------------Read time-------------------
            settings.LowEvent.wait()
            actualBusData = busGlobals.CacheBus.bus.data
            
            if actualBusData != "": #Instruction in bus
                instructionSplitted = actualBusData.split(settings.INSTRUCTION_SEPARATOR) #Split the instruction

                if instructionSplitted[0] != str(self.processorId):# Not me -> read
                    
                    if instructionSplitted[1] == settings.LOAD_INSTRUCTION_TYPE and len(instructionSplitted)<4: #Read and not aswered -> Find the value -> If exists send to memory
                        value = self.cacheMemory.isInCache(int(instructionSplitted[2]), True, False)
                        
                    elif instructionSplitted[1] == settings.STORE_INSTRUCTION_TYPE: #Write -> Invalid
                        self.cacheMemory.invalid_data(int(instructionSplitted[2])) 
                    
    def run (self):
        """
        Method to create the cache memory thread
        """
        t = threading.Thread(target=self.runCache)
        t.start()
