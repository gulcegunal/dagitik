
import threading
import socket
import time
import random


class myThread (threading.Thread):
    def __init__(self, threadID, clientSocket, clientAddr, message):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.clientAddr = clientAddr
        self.message = message
    def run(self):
        print "Starting receive-thread-" + str(self.threadID)
        while True:
            data = self.clientSocket.recv(1024)
            self.setMessage(data)
            if data == "End":
                break
            else:
                self.clientSocket.send("Got it!")
        self.clientSocket.close()
        print "Ending receive-thread-" + str(self.threadID)
    def setMessage(self, data):
        self.message = data
    def getMessage(self):
        return self.message
       

class timeThread(threading.Thread):
    global message
    def __init__(self, threadID, clientSocket, myThread):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.clientSocket = clientSocket
        self.myThread = myThread
    def run(self):
        print "Starting time-thread-" + str(self.threadID)
        while self.myThread.getMessage() != "End":
            time.sleep(random.randrange(10))
            currentTime = "Hello, the time is %s" %(time.ctime(time.time()))
            self.clientSocket.send(currentTime)
        print "Ending time-thread-" + str(self.threadID)
        self.clientSocket.close()


threadCounter = 0
message = ""
s = socket.socket()
host = socket.gethostname()
port = 12345
s.bind((host, port))
s.listen(5)
while True:
	print "Waiting for connection"
	c, addr = s.accept()
	print 'Got a connection from ', addr
	threadCounter += 1
	thread = myThread(threadCounter, c, addr)
	thread.start()
	tThread = timeThread(threadCounter, c, Thread)
        tThread.start()
