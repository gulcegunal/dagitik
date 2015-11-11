
__author__ = 'gulce'
import threading
import time
import queue
import socket

class WriteThread (threading.Thread):
    def __init__(self, name, cSocket, address, threadQueue, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.cSocket = cSocket
        self.address = address
        self.lQueue = logQueue
        self.tQueue = threadQueue

    def run(self):
        print("Starting " + self.name)
        self.lQueue.put("Starting " + self.name + "\n")
        while True:
            try:
                
                self.cSocket.send("TIC".encode())
                if self.tQueue.qsize() > 0:
                    queue_message = self.tQueue.get()

                    if queue_message[0]:
                        message_to_send = "MSG " + queue_message[1]+ ":" + queue_message[2]

                    elif queue_message[1]:
                        message_to_send = "SAY " + queue_message[1] + ":" + queue_message[2]

                    else: 
                        message_to_send = "SYS " + queue_message[2]
                    self.cSocket.send((message_to_send ).encode()) 

            except: 
                self.lQueue.put("Socket problem in " + self.name + "\n")
                self.lQueue.put("Closing socket " + str(self.address) + "\n")
                break

        print("Exiting " + self.name)
        self.lQueue.put("Exiting " + self.name + "\n")

