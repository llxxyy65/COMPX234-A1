import threading
import time
import random

from printDoc import printDoc
from printList import printList


class Assignment1:
    # parameter
    NUM_MACHINES = 50
    NUM_PRINTERS = 5
    SIMULATION_TIME = 30
    MAX_PRINTER_SLEEP = 3
    MAX_MACHINE_SLEEP = 5

    def __init__(self):
        self.sim_active = True
        self.print_list = printList()
        self.mThreads = []
        self.pThreads = []


        self.emptySlots = threading.Semaphore(self.NUM_PRINTERS)  # control spaces
        self.mutex = threading.Semaphore(1)  # protection of queue accessibility

    def startSimulation(self):
        # set threads
        for i in range(self.NUM_MACHINES):
            self.mThreads.append(self.machineThread(i, self))
        for i in range(self.NUM_PRINTERS):
            self.pThreads.append(self.printerThread(i, self))

        # start
        for t in self.mThreads: t.start()
        for t in self.pThreads: t.start()

        #
        time.sleep(self.SIMULATION_TIME)

        # termination
        self.sim_active = False
        for t in self.pThreads: t.join()
        print("Simulation finished.")

    # printer thread
    class printerThread(threading.Thread):
        def __init__(self, printerID, outer):
            threading.Thread.__init__(self)
            self.printerID = printerID
            self.outer = outer

        def run(self):
            while self.outer.sim_active:
                time.sleep(random.randint(1, self.outer.MAX_PRINTER_SLEEP))
                self.printDox(self.printerID)

        def printDox(self, printerID):
            self.outer.mutex.acquire()  # lock queue
            if self.outer.print_list.head:  #  ！empty
                print(f"Printer {printerID} printing")
                self.outer.print_list.queuePrint(printerID)

                self.outer.emptySlots.release()  # release a space
            self.outer.mutex.release()  # unlock  the queue

    # machine thread
    class machineThread(threading.Thread):
        def __init__(self, machineID, outer):
            threading.Thread.__init__(self)
            self.machineID = machineID
            self.outer = outer

        def run(self):

            while self.outer.sim_active:
                time.sleep(random.randint(1, self.outer.MAX_MACHINE_SLEEP))
                self.sendRequest(self.machineID)

        def sendRequest(self, id):
            print(f"Machine {id} waiting")
            self.outer.emptySlots.acquire()  # wait a space
            self.outer.mutex.acquire()  # lock  the queue

            # send requests
            print(f"Machine {id} sent request")
            doc = printDoc(f"From machine {id}", id)
            self.outer.print_list.queueInsert(doc)

            self.outer.mutex.release()

