##########################################
#       Tecnologico de Costa Rica        #
#     Arquitectura de computadores 2     #
#               Proyecto 1               #
#              Settings file             #
#               Raul Arias               #             
##########################################

"""
This file contains constants and globals
"""

#---------------------------------Imports --------------------------------------
from threading import Event, Lock
import queue

#---------------------------------Constants ------------------------------------
OPERATION_INSTRUCTION_TYPE = "o"
STORE_INSTRUCTION_TYPE = "s"
LOAD_INSTRUCTION_TYPE = "l"
LOAD_FOR_WRITE_INSTRUCTION_TYPE = "ls"

BUS_GUI_INSTRUCTION_TYPE = "b"
BUS_SIMPLE_GUI_INSTRUCTION_TYPE = "bs"
BUS_REQUEST_GUI_INSTRUCTION_TYPE = "br"
BUS_REQUEST_NOW_GUI_INSTRUCTION_TYPE = "brn"
MEMORY_GUI_INSTRUCTION_TYPE = "m"
GREEN_CLOCK_GUI_INSTRUCTION_TYPE = "gc"
RED_CLOCK_GUI_INSTRUCTION_TYPE = "rc"
CACHE_BUS_GUI_INSTRUCTION_TYPE = "cb"
CACHE_BUS_SIMPLE_GUI_INSTRUCTION_TYPE = "cbs"
CACHE_BUS_REQUEST_GUI_INSTRUCTION_TYPE = "cbr"
CACHE_BUS_REQUEST_NOW_GUI_INSTRUCTION_TYPE = "cbrn"
CACHE_GUI_INSTRUCTION_TYPE = "c"
PROCESSOR_GUI_INSTRUCTION_TYPE = "p"
PROCESSOR_STATUS_GUI_INSTRUCTION_TYPE = "ps"
PROCESSOR_STATE_GUI_INSTRUCTION_TYPE = "pst"

INSTRUCTION_SEPARATOR = "-"
GUI_INSTRUCTION_SEPARATOR = "/"

SYSTEM_DELAY = 5
PROCESSOR_CACHE_BUS_MAX_DELAY = 20
PROCESSOR_BUS_MAX_DELAY = 20
MAIN_MEMORY_DELAY = 1
CACHE_DELAY = 0


BUS_DELAY = MAIN_MEMORY_DELAY + 2
CACHE_BUS_DELAY = CACHE_DELAY + 2

INSTRUCTIONS_MEMORY_SIZE = 100
CACHE_MEMORY_SIZE = 8
MAIN_MEMORY_SIZE = 16

#------------------------------------Globals -----------------------------------
GuiQueue = queue.Queue()
GuiMutex = Lock()
MainBusMutex = Lock()
CacheBusMutex = Lock()
HighEvent = Event()
LowEvent = Event()
