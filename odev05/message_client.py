
__author__ = 'gulce'
import sys
import socket
import threading
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Queue
import time

socketClosed = 0
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

class ClientDialog(QDialog):
	''' An example application for PyQt. Instantiate
	and call the run method to run. '''
	def __init__(self, threadQueue):
		self.threadQueue = threadQueue
        
		# create a Qt application --- every PyQt app needs one
		self.qt_app = QApplication(sys.argv)
        
		# Call the parent constructor on the current object
		QDialog.__init__(self, None)

		# Set up the window
		self.setWindowTitle('IRC Client')
		self.setMinimumSize(500, 200)
        
		# Add a vertical layout
		self.vbox = QVBoxLayout()
		
		# The sender textbox
		self.sender = QLineEdit("", self)
		
		# The channel region
		self.channel = QTextBrowser()
		
		# The send button
		self.send_button = QPushButton('&Send')

		# Connect the Go button to its callback
		self.send_button.clicked.connect(self.outgoing_parser)
		
		# Add the controls to the vertical layout
		self.vbox.addWidget(self.channel)
		self.vbox.addWidget(self.sender)
		self.vbox.addWidget(self.send_button)
		
		# A very stretchy spacer to force the button to the bottom
		# self.vbox.addStretch(100)

		# Use the vertical layout for the current window
		self.setLayout(self.vbox)
		self.flag = 0

	def cprint(self, data):
		data = time.ctime() + " " + data 
		self.channel.append(data)

	def outgoing_parser(self):
		data = self.sender.text()
		if len(data) == 0:
			return
		msg = "-Local-: " + data
		self.cprint(msg)
		if data[0:5] == "/nick" and self.flag == 0:			
			nickname = data[6:]
			self.threadQueue.put("USR " + nickname)
			self.flag = 1
			self.sender.clear()
			return

		if data[0] == "/" and self.flag == 1:
			command = data[1:5]
			if command == "list":
				self.threadQueue.put("LSQ ")

			elif command == "quit":
				self.threadQueue.put("QUI ")

			elif command == "msg ":
				index = data[5:].index(" ")
				to_nickname = data[5:5+index]
				message = data[index+6:]
				msg = to_nickname
				self.threadQueue.put("MSG " + str(to_nickname) + ":" + str(message))

			else:
				self.cprint("-Local-: Command Error.") 

		else:
			self.threadQueue.put("SAY " + data)
		self.sender.clear()
	def run(self):
		''' Run the app and show the main form. '''
		self.show()
		self.qt_app.exec_()

s = socket.socket()
host = sys.argv[1]
port = int(sys.argv[2])
s.connect((host,port))

sendQueue = Queue.Queue()

app = ClientDialog(sendQueue)

rt = ReadThread("ReadThread", s, sendQueue, app)
rt.start()

wt = WriteThread("WriteThread", s, sendQueue)
wt.start()

app.run()

rt.join() 
wt.join()
s.close()
