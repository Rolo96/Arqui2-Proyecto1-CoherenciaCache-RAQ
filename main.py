##########################################
#       Tecnologico de Costa Rica        #
#     Arquitectura de computadores 2     #
#               Proyecto 1               #
#               Main file                #
#               Raul Arias               #             
##########################################

"""
This file contains the main thread and gui
"""

#---------------------------------Imports --------------------------------------
import clock
import busGlobals
import settings
import mainMemory
import processor
import tkinter as tk
from tkinter import ttk
import threading

#---------------------------Main GUI variables ---------------------------------
guiRunning = True
GuiBusRequestCount = 0
GuiCacheBusRequestCount = 0
isPause = False
processorsTable = []

#--------------------------------GUI methods -----------------------------------
def draw_gui():
    global GuiBusRequestCount, GuiCacheBusRequestCount
    while(guiRunning): #Read instructions to gui
        data = settings.GuiQueue.get()
        dataSplitted = data.split(settings.GUI_INSTRUCTION_SEPARATOR)

        if dataSplitted[0] == settings.PROCESSOR_GUI_INSTRUCTION_TYPE: #Change processor instruction
            instructionSplitted = dataSplitted[1].split(settings.INSTRUCTION_SEPARATOR)
            processorsTable[int(instructionSplitted[0])].set('Instruction','Value', dataSplitted[1])
            processorsTable[int(instructionSplitted[0])].set('CacheStatus','Value', "")
            processorsTable[int(instructionSplitted[0])].set('Status','Value', "")

        elif dataSplitted[0] == settings.PROCESSOR_STATUS_GUI_INSTRUCTION_TYPE: #Change cache hit/miss
            processorsTable[int(dataSplitted[1])].set('CacheStatus','Value', dataSplitted[2])

        elif dataSplitted[0] == settings.PROCESSOR_STATE_GUI_INSTRUCTION_TYPE: #Change processor state
            processorsTable[int(dataSplitted[1])].set('Status','Value', dataSplitted[2])

        elif dataSplitted[0] == settings.GREEN_CLOCK_GUI_INSTRUCTION_TYPE:#Change green clock
            canvas8.configure(bg = "green")
            
        elif dataSplitted[0] == settings.RED_CLOCK_GUI_INSTRUCTION_TYPE:#Change red clock
            canvas8.configure(bg = "red")

        #-----------------------------------------Cache bus--------------------------------------
        elif dataSplitted[0] == settings.CACHE_BUS_REQUEST_GUI_INSTRUCTION_TYPE: #Add request to cache bus requests
            line = "Request" + str(GuiCacheBusRequestCount)
            cacheBusTable.set(line,'Value', dataSplitted[1])
            GuiCacheBusRequestCount = GuiCacheBusRequestCount + 1

        elif dataSplitted[0] == settings.CACHE_BUS_REQUEST_NOW_GUI_INSTRUCTION_TYPE: #Add request to cache bus requests in first position
            for x in range(9):
                line = "Request" + str(9-x)
                prevLine = "Request" + str(9-x-1)
                cacheBusTable.set(line,'Value', cacheBusTable.set(prevLine,'Value'))
            cacheBusTable.set("Request0",'Value', dataSplitted[1])
            GuiCacheBusRequestCount = GuiCacheBusRequestCount + 1 

        elif dataSplitted[0] == settings.CACHE_BUS_GUI_INSTRUCTION_TYPE: #Move request to cache bus
            cacheBusTable.set('ActualInstruction','Value', dataSplitted[1])
            for x in range(9):
                line = "Request" + str(x)
                nextLine = "Request" + str(x+1)
                cacheBusTable.set(line,'Value', cacheBusTable.set(nextLine,'Value'))
            cacheBusTable.set('Request9','Value', 'Nothing')
            if GuiCacheBusRequestCount > 0: 
                GuiCacheBusRequestCount = GuiCacheBusRequestCount - 1

        elif dataSplitted[0] == settings.CACHE_BUS_SIMPLE_GUI_INSTRUCTION_TYPE: #Update cache bus value from memory
            cacheBusTable.set('ActualInstruction','Value', dataSplitted[1])

        #-----------------------------------------Main bus--------------------------------------
        elif dataSplitted[0] == settings.BUS_REQUEST_GUI_INSTRUCTION_TYPE: #Add request to main bus requests
            line = "Request" + str(GuiBusRequestCount)
            busTable.set(line,'Value', dataSplitted[1])
            GuiBusRequestCount = GuiBusRequestCount + 1

        elif dataSplitted[0] == settings.BUS_REQUEST_NOW_GUI_INSTRUCTION_TYPE: #Add request to main bus requests in first position
            for x in range(9):
                line = "Request" + str(9-x)
                prevLine = "Request" + str(9-x-1)
                busTable.set(line,'Value', busTable.set(prevLine,'Value'))
            busTable.set("Request0",'Value', dataSplitted[1])
            GuiBusRequestCount = GuiBusRequestCount + 1  

        elif dataSplitted[0] == settings.BUS_GUI_INSTRUCTION_TYPE: #Move request to main bus
            busTable.set('ActualInstruction','Value', dataSplitted[1])
            for x in range(9):
                line = "Request" + str(x)
                nextLine = "Request" + str(x+1)
                busTable.set(line,'Value', busTable.set(nextLine,'Value'))
            busTable.set('Request9','Value', 'Nothing')
            if GuiBusRequestCount > 0: 
                GuiBusRequestCount = GuiBusRequestCount - 1

        elif dataSplitted[0] == settings.BUS_SIMPLE_GUI_INSTRUCTION_TYPE: #Update main bus value from memory
            busTable.set('ActualInstruction','Value', dataSplitted[1])

        elif dataSplitted[0] == settings.CACHE_GUI_INSTRUCTION_TYPE: #Update processor cache
            line = "Line" + str(int(dataSplitted[2])%settings.CACHE_MEMORY_SIZE)
            processorsTable[int(dataSplitted[1])].set(line,'Value', dataSplitted[3])

        elif dataSplitted[0] == settings.MEMORY_GUI_INSTRUCTION_TYPE: #Update memory
            line = "Memory" + str(dataSplitted[1])
            memoryTable.set(line,'Value', dataSplitted[2])
            

def play_pause_action():
    global isPause, clk
    if isPause:
        clk.isRunning = True
        clk.run()
        isPause = False
        button.configure(text = "Pause")
    else:
        clk.isRunning = False
        isPause = True
        button.configure(text = "Play")

#-------------------------------Main thread ------------------------------------

#-----------------------Generate components --------------------------

busGlobals.MainBus.run()
busGlobals.CacheBus.run()

memory = mainMemory.MainMemory()
memory.run()

mem1 = ['1-s-7-1', '1-l-8', '1-l-12', '1-l-3', '1-l-5', '1-l-15', '1-l-2', '1-l-1' ]
mem = ['0-l-4', '0-l-9', '0-l-14', '0-s-8-0', '0-l-7', '0-l-13', '0-s-0-0', '0-l-13', '0-l-9', '0-l-1', '0-l-3', '0-l-2']

proc1 = processor.Processor(0)

proc1.instructionsMemory.memory = mem
proc1.run()
proc2 = processor.Processor(1)
proc2.run()
proc2.instructionsMemory.memory = mem1
proc3 = processor.Processor(2)
proc3.run()
proc4 = processor.Processor(3)
proc4.run()

clk = clock.Clock()
clk.run()

#---------------------------Generate GUI -----------------------------

#----------------Main Window-------------------------
root = tk.Tk()
root.title("Arqui2 - Project #1")
root.geometry('1650x900')

#--------------Create processor 1 gui----------------

#--------Create containers--------------
canvas1 = tk.Frame(root, bg = "black", height = 350, width = 350)
canvas1.place(x=50, y=25)
canvas1.pack_propagate(False)

#------Create processor label-----------
proc1 = tk.Label(canvas1, text = "Processor #0", fg='white', bg='black', font='Helvetica 18 bold')
proc1.place(x=100, y=20)

#------Create processor table-----------
processor1Table = ttk.Treeview(canvas1,selectmode="extended",columns=("Value"), height = 12)
processor1Table.place(x=0, y=50)
processor1Table.heading("#0", text="Property", anchor=tk.CENTER)
processor1Table.column("#0",minwidth=0,width=175, stretch=tk.NO)
processor1Table.heading("Value", text="Value", anchor=tk.CENTER)
processor1Table.column("Value",minwidth=0,width=175, stretch=tk.NO)

processor1Table.insert("", tk.END, "Instruction", text = "Instruction:", values = ("Nothing"))
processor1Table.insert("", tk.END, "CacheStatus", text = "Cache hit/miss:", values = ("Nothing"))
processor1Table.insert("", tk.END, "Status", text = "Status:", values = ("Starting"))
processor1Table.insert("", tk.END, "cacheLines", text = "Cache lines:")
processor1Table.insert("cacheLines", tk.END, "Line0", text = "Cache line 0:", values = ("I-0-0"))
processor1Table.insert("cacheLines", tk.END, "Line1", text = "Cache line 1:", values = ("I-0-0"))
processor1Table.insert("cacheLines", tk.END, "Line2", text = "Cache line 2:", values = ("I-0-0"))
processor1Table.insert("cacheLines", tk.END, "Line3", text = "Cache line 3:", values = ("I-0-0"))
processor1Table.insert("cacheLines", tk.END, "Line4", text = "Cache line 4:", values = ("I-0-0"))
processor1Table.insert("cacheLines", tk.END, "Line5", text = "Cache line 5:", values = ("I-0-0"))
processor1Table.insert("cacheLines", tk.END, "Line6", text = "Cache line 6:", values = ("I-0-0"))
processor1Table.insert("cacheLines", tk.END, "Line7", text = "Cache line 7:", values = ("I-0-0"))

processor1Table.item('cacheLines', open = True)
processorsTable.append(processor1Table)

#--------------Create processor 2 gui----------------

#--------Create containers--------------
canvas2 = tk.Frame(root, bg = "black", height = 350, width = 350)
canvas2.place(x=450, y=25)
canvas2.pack_propagate(False)

#------Create processor label-----------
proc2 = tk.Label(canvas2, text = "Processor #1", fg='white', bg='black', font='Helvetica 18 bold')
proc2.place(x=100, y=20)

#------Create processor table-----------
processor2Table = ttk.Treeview(canvas2,selectmode="extended",columns=("Value"), height = 12)
processor2Table.place(x=0, y=50)
processor2Table.heading("#0", text="Property", anchor=tk.CENTER)
processor2Table.column("#0",minwidth=0,width=175, stretch=tk.NO)
processor2Table.heading("Value", text="Value", anchor=tk.CENTER)
processor2Table.column("Value",minwidth=0,width=175, stretch=tk.NO)

processor2Table.insert("", tk.END, "Instruction", text = "Instruction:", values = ("Nothing"))
processor2Table.insert("", tk.END, "CacheStatus", text = "Cache hit/miss:", values = ("Nothing"))
processor2Table.insert("", tk.END, "Status", text = "Status:", values = ("Starting"))
processor2Table.insert("", tk.END, "cacheLines", text = "Cache lines:")
processor2Table.insert("cacheLines", tk.END, "Line0", text = "Cache line 0:", values = ("I-0-0"))
processor2Table.insert("cacheLines", tk.END, "Line1", text = "Cache line 1:", values = ("I-0-0"))
processor2Table.insert("cacheLines", tk.END, "Line2", text = "Cache line 2:", values = ("I-0-0"))
processor2Table.insert("cacheLines", tk.END, "Line3", text = "Cache line 3:", values = ("I-0-0"))
processor2Table.insert("cacheLines", tk.END, "Line4", text = "Cache line 4:", values = ("I-0-0"))
processor2Table.insert("cacheLines", tk.END, "Line5", text = "Cache line 5:", values = ("I-0-0"))
processor2Table.insert("cacheLines", tk.END, "Line6", text = "Cache line 6:", values = ("I-0-0"))
processor2Table.insert("cacheLines", tk.END, "Line7", text = "Cache line 7:", values = ("I-0-0"))

processor2Table.item('cacheLines', open = True)
processorsTable.append(processor2Table)

#--------------Create processor 3 gui----------------


#--------Create containers--------------
canvas3 = tk.Frame(root, bg = "black", height = 350, width = 350)
canvas3.place(x=50, y=525)
canvas3.pack_propagate(False)

#------Create processor label-----------
proc3 = tk.Label(canvas3, text = "Processor #2", fg='white', bg='black', font='Helvetica 18 bold')
proc3.place(x=100, y=20)

#------Create processor table-----------
processor3Table = ttk.Treeview(canvas3,selectmode="extended",columns=("Value"), height = 12)
processor3Table.place(x=0, y=50)
processor3Table.heading("#0", text="Property", anchor=tk.CENTER)
processor3Table.column("#0",minwidth=0,width=175, stretch=tk.NO)
processor3Table.heading("Value", text="Value", anchor=tk.CENTER)
processor3Table.column("Value",minwidth=0,width=175, stretch=tk.NO)

processor3Table.insert("", tk.END, "Instruction", text = "Instruction:", values = ("Nothing"))
processor3Table.insert("", tk.END, "CacheStatus", text = "Cache hit/miss:", values = ("Nothing"))
processor3Table.insert("", tk.END, "Status", text = "Status:", values = ("Starting"))
processor3Table.insert("", tk.END, "cacheLines", text = "Cache lines:")
processor3Table.insert("cacheLines", tk.END, "Line0", text = "Cache line 0:", values = ("I-0-0"))
processor3Table.insert("cacheLines", tk.END, "Line1", text = "Cache line 1:", values = ("I-0-0"))
processor3Table.insert("cacheLines", tk.END, "Line2", text = "Cache line 2:", values = ("I-0-0"))
processor3Table.insert("cacheLines", tk.END, "Line3", text = "Cache line 3:", values = ("I-0-0"))
processor3Table.insert("cacheLines", tk.END, "Line4", text = "Cache line 4:", values = ("I-0-0"))
processor3Table.insert("cacheLines", tk.END, "Line5", text = "Cache line 5:", values = ("I-0-0"))
processor3Table.insert("cacheLines", tk.END, "Line6", text = "Cache line 6:", values = ("I-0-0"))
processor3Table.insert("cacheLines", tk.END, "Line7", text = "Cache line 7:", values = ("I-0-0"))

processor3Table.item('cacheLines', open = True)
processorsTable.append(processor3Table)

#--------------Create processor 4 gui----------------

#--------Create containers--------------
canvas4 = tk.Frame(root, bg = "black", height = 350, width = 350)
canvas4.place(x=450, y=525)
canvas4.pack_propagate(False)

#------Create processor label-----------
proc4 = tk.Label(canvas4, text = "Processor #3", fg='white', bg='black', font='Helvetica 18 bold')
proc4.place(x=100, y=20)

#------Create processor table-----------
processor4Table = ttk.Treeview(canvas4,selectmode="extended",columns=("Value"), height = 12)
processor4Table.place(x=0, y=50)
processor4Table.heading("#0", text="Property", anchor=tk.CENTER)
processor4Table.column("#0",minwidth=0,width=175, stretch=tk.NO)
processor4Table.heading("Value", text="Value", anchor=tk.CENTER)
processor4Table.column("Value",minwidth=0,width=175, stretch=tk.NO)

processor4Table.insert("", tk.END, "Instruction", text = "Instruction:", values = ("Nothing"))
processor4Table.insert("", tk.END, "CacheStatus", text = "Cache hit/miss:", values = ("Nothing"))
processor4Table.insert("", tk.END, "Status", text = "Status:", values = ("Starting"))
processor4Table.insert("", tk.END, "cacheLines", text = "Cache lines:")
processor4Table.insert("cacheLines", tk.END, "Line0", text = "Cache line 0:", values = ("I-0-0"))
processor4Table.insert("cacheLines", tk.END, "Line1", text = "Cache line 1:", values = ("I-0-0"))
processor4Table.insert("cacheLines", tk.END, "Line2", text = "Cache line 2:", values = ("I-0-0"))
processor4Table.insert("cacheLines", tk.END, "Line3", text = "Cache line 3:", values = ("I-0-0"))
processor4Table.insert("cacheLines", tk.END, "Line4", text = "Cache line 4:", values = ("I-0-0"))
processor4Table.insert("cacheLines", tk.END, "Line5", text = "Cache line 5:", values = ("I-0-0"))
processor4Table.insert("cacheLines", tk.END, "Line6", text = "Cache line 6:", values = ("I-0-0"))
processor4Table.insert("cacheLines", tk.END, "Line7", text = "Cache line 7:", values = ("I-0-0"))

processor4Table.item('cacheLines', open = True)
processorsTable.append(processor4Table)

#--------------Create cache bus gui------------------

#--------Create containers--------------
canvas5 = tk.Frame(root, bg = "black", height = 350, width = 350)
canvas5.place(x=850, y=25)
canvas5.pack_propagate(False)

#---------Create bus label--------------
cacheBus = tk.Label(canvas5, text = "Cache bus", fg='white', bg='black', font='Helvetica 18 bold')
cacheBus.place(x=110, y=20)

#----------Create bus table-------------
cacheBusTable = ttk.Treeview(canvas5,selectmode="extended",columns=("Value"), height = 12)
cacheBusTable.place(x=0, y=50)
cacheBusTable.heading("#0", text="Property", anchor=tk.CENTER)
cacheBusTable.column("#0",minwidth=0,width=175, stretch=tk.NO)
cacheBusTable.heading("Value", text="Value", anchor=tk.CENTER)
cacheBusTable.column("Value",minwidth=0,width=175, stretch=tk.NO)

cacheBusTable.insert("", tk.END, "ActualInstruction", text = "Bus instruction:", values = ("Nothing"))
cacheBusTable.insert("", tk.END, "Requests", text = "Requests:")
cacheBusTable.insert("Requests", tk.END, "Request0", text = "Request #0", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request1", text = "Request #1", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request2", text = "Request #2", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request3", text = "Request #3", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request4", text = "Request #4", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request5", text = "Request #5", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request6", text = "Request #6", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request7", text = "Request #7", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request8", text = "Request #8", values = ("Nothing"))
cacheBusTable.insert("Requests", tk.END, "Request9", text = "Request #9", values = ("Nothing"))

cacheBusTable.item('Requests', open = True)

#--------------Create main bus gui-------------------

#--------Create containers--------------
canvas6 = tk.Frame(root, bg = "black", height = 350, width = 350)
canvas6.place(x=850, y=525)
canvas6.pack_propagate(False)

#-----------Create bus label------------
bus = tk.Label(canvas6, text = "Main bus", fg='white', bg='black', font='Helvetica 18 bold')
bus.place(x=110, y=20)

#----------Create bus table-------------
busTable = ttk.Treeview(canvas6,selectmode="extended",columns=("Value"), height = 12)
busTable.place(x=0, y=50)
busTable.heading("#0", text="Property", anchor=tk.CENTER)
busTable.column("#0",minwidth=0,width=175, stretch=tk.NO)
busTable.heading("Value", text="Value", anchor=tk.CENTER)
busTable.column("Value",minwidth=0,width=175, stretch=tk.NO)

busTable.insert("", tk.END, "ActualInstruction", text = "Bus instruction:", values = ("Nothing"))
busTable.insert("", tk.END, "Requests", text = "Requests:")
busTable.insert("Requests", tk.END, "Request0", text = "Request #0", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request1", text = "Request #1", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request2", text = "Request #2", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request3", text = "Request #3", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request4", text = "Request #4", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request5", text = "Request #5", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request6", text = "Request #6", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request7", text = "Request #7", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request8", text = "Request #8", values = ("Nothing"))
busTable.insert("Requests", tk.END, "Request9", text = "Request #9", values = ("Nothing"))

busTable.item('Requests', open = True)

#--------------Create main memory gui----------------

#--------Create containers--------------
canvas7 = tk.Frame(root, bg = "black", height = 430, width = 350)
canvas7.place(x=1250, y=240)
canvas7.pack_propagate(False)

#-----Create main memory label----------
memoryLabel = tk.Label(canvas7, text = "Main memory", fg='white', bg='black', font='Helvetica 18 bold')
memoryLabel.place(x=100, y=20)

#-------Create memory table-------------
memoryTable = ttk.Treeview(canvas7,selectmode="extended",columns=("Value"), height = 16)
memoryTable.place(x=0, y=50)
memoryTable.heading("#0", text="Property", anchor=tk.CENTER)
memoryTable.column("#0",minwidth=0,width=175, stretch=tk.NO)
memoryTable.heading("Value", text="Value", anchor=tk.CENTER)
memoryTable.column("Value",minwidth=0,width=185, stretch=tk.NO)

memoryTable.insert("", tk.END, "Memory0", text = "Memory address 0:", values = ("0"))
memoryTable.insert("", tk.END, "Memory1", text = "Memory address 1:", values = ("0"))
memoryTable.insert("", tk.END, "Memory2", text = "Memory address 2:", values = ("0"))
memoryTable.insert("", tk.END, "Memory3", text = "Memory address 3:", values = ("0"))
memoryTable.insert("", tk.END, "Memory4", text = "Memory address 4:", values = ("0"))
memoryTable.insert("", tk.END, "Memory5", text = "Memory address 5:", values = ("0"))
memoryTable.insert("", tk.END, "Memory6", text = "Memory address 6:", values = ("0"))
memoryTable.insert("", tk.END, "Memory7", text = "Memory address 7:", values = ("0"))
memoryTable.insert("", tk.END, "Memory8", text = "Memory address 8:", values = ("0"))
memoryTable.insert("", tk.END, "Memory9", text = "Memory address 9:", values = ("0"))
memoryTable.insert("", tk.END, "Memory10", text = "Memory address 10:", values = ("0"))
memoryTable.insert("", tk.END, "Memory11", text = "Memory address 11:", values = ("0"))
memoryTable.insert("", tk.END, "Memory12", text = "Memory address 12:", values = ("0"))
memoryTable.insert("", tk.END, "Memory13", text = "Memory address 13:", values = ("0"))
memoryTable.insert("", tk.END, "Memory14", text = "Memory address 14:", values = ("0"))
memoryTable.insert("", tk.END, "Memory15", text = "Memory address 15:", values = ("0"))

#-----------------Create clock gui-------------------

#--------Create containers--------------
canvas8 = tk.Canvas(bg = "red", height = 100, width = 1150)
canvas8.place(x=50, y=400)

#---------Create clock label------------
clockLabel = tk.Label(canvas8, text = "----Clock----", fg='white', bg='black')
clockLabel.place(x=490, y=35)
clockLabel.config(font=("Courier", 16))

#------Create play pause button ---------
button = tk.Button(root, text="Pause", command=play_pause_action, fg="black", bg="white", font='Helvetica 18 bold')
button.place(x=1450, y=830)

#-------------------Run GUI thread-------------------
t = threading.Thread(target=draw_gui)
t.start()

#print(processor1Table.set('cacheLines','Value', 'AAA'))

#---------------------Main loop----------------------
root.mainloop()
