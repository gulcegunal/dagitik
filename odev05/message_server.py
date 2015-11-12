
__author__ = 'gulce'
import threading
import time
import Queue
import socket

class ReadThread (threading.Thread):
    def __init__(self, name, cSocket, address, logQueue):
        threading.Thread.__init__(self)
        self.name = name
        self.cSocket = cSocket
        self.address = address
        self.lQueue = logQueue
        self.fihrist = fihrist
        self.tQueue = threadQueue
        self.nickname = ""
        self.lock = queueLock
        self.alreadySigned = 0

    def parser(self, data): 
        data = data.strip()
        if not self.nickname and not data[0:3] == "USR":
            response = "ERL"
            self.cSocket.send(response.encode())
            return 0

        if data[0:3] == "USR" and data[4:].count(" ") >0:
            response = "ERR"
            self.cSocket.send(response.encode())
            return 0

        if data[0:3] == "USR" and self.alreadySigned == 0:
            self.nickname = data[4:]
            if not self.nickname in self.fihrist.keys():
                self.alreadySigned = 1

                response = "HEL " + self.nickname
                self.cSocket.send(response.encode())

                user = {self.nickname: self.tQueue}
                self.fihrist.update(user)

                sMessage = self.nickname + " has joined."
                queue_message = ("", "", sMessage)
				
                for nickname in self.fihrist.keys():
                    self.lock.acquire()
                    self.fihrist[nickname].put(queue_message)
                    self.lock.release()
                self.lQueue.put(sMessage)
                return 0

            else:
                response = "REJ " + self.nickname
                self.cSocket.send(response.encode())
                return 1

        elif data[0:3] == "QUI":
            response = "BYE " + self.nickname
            self.cSocket.send(response.encode())
            del fihrist[self.nickname]
            sMessage = self.nickname + " has left."
            queue_message = ("", "", sMessage)
            for nickname in self.fihrist.keys():
                self.lock.acquire()
                self.fihrist[nickname].put(queue_message)
                self.lock.release()
            self.lQueue.put(sMessage)
            return 1

        elif data[0:3] == "LSQ":
            response = "LSA "
            for nickname in self.fihrist.keys():
                response += nickname + ":" 
            response = response[:-1]
            self.cSocket.send(response.encode()) 
            return 0    
           
        elif data[0:3] == "TIC": 
            response = "TOC"
            self.cSocket.send(response.encode())
            return 0

        elif data[0:3] == "SAY":
            message = data[4:]
            queue_message = ("", self.nickname, message)

            for nickname in self.fihrist.keys():
                self.lock.acquire()
                self.fihrist[nickname].put(queue_message)
                self.lock.release()
            response = "SOK"
            self.cSocket.send(response.encode()) 
            return 0  

        elif data[0:3] == "MSG":
            index = data.index(":")
            to_nickname = data[4:index]
            message = data[index+1:]

            if not to_nickname in self.fihrist.keys():
                response = "MNO"

            else: 
                queue_message = (to_nickname, self.nickname, message)
                self.lock.acquire()
                self.fihrist[to_nickname].put(queue_message)
                self.lock.release()
                response = "MOK"
            self.cSocket.send(response.encode())
            return 0

        else:  
            response = "ERR"
            self.cSocket.send(response.encode())
            return 0

    def run(self):
        print("Starting " + self.name)
        self.lQueue.put("Starting " + self.name + "\n")

        while True:
            try:         
                incoming_data = self.cSocket.recv(1024).decode()
                queue_message = self.parser(incoming_data)
                if queue_message == 1:
                    self.cSocket.close()
                    break

            except: 
                del fihrist[self.nickname]
                self.lQueue.put("Socket problem in " + self.name + "\n")
                self.lQueue.put("Closing socket" + str(self.address) + "\n")
                self.lQueue.put(self.nickname + " had a connection problem.\n")
                break

        print("Exiting " + self.name)
        self.lQueue.put("Exiting " + self.name + "\n")

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
                time.sleep(5)
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

class LoggerThread (threading.Thread):
    def __init__(self, name, logQueue, logFileName):
        threading.Thread.__init__(self)
        self.name = name
        self.lQueue = logQueue
        self.fid = open(logFileName, "a")

    def log(self, message):
        t = time.ctime()
        self.fid.write(t + " " +message)
        self.fid.flush()

    def run(self):  
        self.log("Starting " + self.name + "\n") 
        
        while(True):
            if self.lQueue.qsize() > 0:
                to_be_logged = self.lQueue.get()
                self.log(to_be_logged)

        self.log("Exiting" + self.name + "\n")
        self.fid.close()

s = socket.socket()
host = socket.gethostname()
port = 60000
s.bind((host, port))
s.listen(5)

threadCounter = 0
fihrist = dict()
lQueue = Queue.Queue()

logger = LoggerThread("LoggerThread", lQueue, "logger.txt")
logger.start()

while True: 
    sMessage = "Waiting for connection"
    print(sMessage)
    lQueue.put(sMessage + "\n")

    c, addr = s.accept()

    sMessage = "Got a connection from " + str(addr)
    print(sMessage)
    lQueue.put(sMessage  + "\n")

    threadCounter +=1
    rThreadName = "ReadThread-" + str(threadCounter)
    wThreadName = "WriteThread-" + str(threadCounter)

    threadQueue = queue.Queue()
    queueLock = threading.Lock()

    rThread = ReadThread(rThreadName, c, addr, lQueue)
    rThread.start()

    wThread = WriteThread(wThreadName, c, addr, threadQueue, lQueue)  
    wThread.start()  

