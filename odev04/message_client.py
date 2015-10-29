import socket
import threading
import random
class readThread (threading.Thread):
 def __init__(self, socket, message):
        threading.Thread.__init__(self)
        self.socket = socket
        self.message = message
    def run(self):
    	
        while self.message != "End":
            message = raw_input("")
            self.setMessage(message)
            self.socket.send(message)
    def setMessage(self, data):
        self.message = data
    def getMessage(self):
        return self.message
       
class writeThread (threading.Thread):

s = socket.socket()
message = ""
threads = []
host ="127.0.0.1"
port = 12345
s.connect((host, port))
	...
	...
	...
rThread = readThread(...)
rThread.start()
wThread = writeThread(...)
wThread.start()
