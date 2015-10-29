import socket
import threading
Import random
class readThread (threading.Thread):
 def __init__(self, socket, message):
        threading.Thread.__init__(self)
        self.socket = socket
        self.message = message
    def run(self):
       
class writeThread (threading.Thread):

s = socket.socket()
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
