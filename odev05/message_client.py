
__author__ = 'gulce'
import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import time

class ReadThread (threading.Thread):
	def __init__(self, name, csoc, threadQueue, app):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.nickname = ""
		self.threadQueue = threadQueue
		self.app = app

	def incoming_parser(self, data):	
		global socketClosed	
		if len(data) == 0:
			return

		rest = data[4:]

		if data[0:3] == "BYE":
			msg = "-Server- Bye " + rest
			self.app.cprint(msg)
			socketClosed = 1
			return 1
		if data[0:3] == "ERL":
			msg = "-Server- Nick not registered."
			self.app.cprint(msg)
			return 0
		if data[0:3] == "HEL":
			self.nickname = rest
			msg = "Registered as <" + self.nickname + ">"
			self.app.cprint(msg)
			return 0
		if data[0:3] == "REJ":
			msg = "-Server- Nick already in used."
			self.app.cprint(msg)
			socketClosed = 1
			return 1

		if data[0:3] == "MNO":
			msg = "-Server- User cannot be found."
			self.app.cprint(msg)
			return 0

		if data[0:3] == "MSG":
			index = data.index(":")
			from_nickname = data[4:index]
			message = data[index+1:]
			msg = "<" + from_nickname + ">: " + message
			self.app.cprint(msg)
			return 0

		if data[0:3] == "SAY":
			index = data.index(":")
			from_nickname = data[4:index]
			message = data[index+1:]
			msg = "<" + from_nickname + ">" + data[4+len(self.nickname):] 
			self.app.cprint(msg)
			return 0

		if data[0:3] == "SYS":
			msg = "-Server- " + data[4:]
			self.app.cprint(msg)
			return 0

		if data[0:3] == "LSA":
			splitted = rest.split(":")
			msg = "-Server- Registered nicks: "
			for i in splitted:
				msg += i +","
			msg = msg[:-1]
			self.app.cprint(msg)
			return 0

	def run(self):
		print("Starting " + self.name)
		while True:
			data = self.csoc.recv(1024).decode()
			queue_message = self.incoming_parser(data)	
			if (queue_message == 1):
				self.csoc.close()
				break
		print("Exiting " + self.name)
class WriteThread (threading.Thread):

	def __init__(self, name, csoc, threadQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.csoc = csoc
		self.threadQueue = threadQueue

	def run(self):
		print("Starting " + self.name)
		while True: 
			if self.threadQueue.qsize() > 0:
				queue_message = str(self.threadQueue.get())
				try:
					self.csoc.send(queue_message.encode())
				except socket.error:
					self.csoc.close()
					break
			if socketClosed == 1:
				break
		print("Exiting " + self.name)
