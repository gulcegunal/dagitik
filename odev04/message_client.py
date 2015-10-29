import socket
import threading
import random
class readThread (threading.Thread):
 def __init__(self, socket, message):
        threading.Thread.__init__(self)
        self.socket = socket
        self.message = message
    def run(self):
    	print "starting read-thread"
        while self.message != "End":
            message = raw_input("")
            self.setMessage(message)
            self.socket.send(message)
    def setMessage(self, data):
        self.message = data
    def getMessage(self):
        return self.message
       
class writeThread (threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket

    def run(self):

            while True:
                data = self.socket.recv(1024)
                if  (data != "End"):
                    print(data)

s = socket.socket()
host = socket.gethostname()
port = 12345


s.connect((host,port))

message = ""
threads = []

rThread = readThread(s, message)
rThread.start()
wThread = writeThread(s)
wThread.start()

threads.append(rThread)
threads.append(wThread)

for t in threads:
    t.join()

print "Exiting Main Thread"
s.close()

