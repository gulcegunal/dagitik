import datetime
import time
import threading
import socket
import Queue



class NegotiatorServer (threading.Thread):
	def __init__(self, cSocket, address,connection_list):
		threading.Thread.__init__(self)
		self.csoc = cSocket
		self.address = address
		self.connection_list = connection_list

		self.status = "W"
		self.csoc.settimeout(30.0)

	def parser(self,data):
		print data 
		if data[0:5] == "HELLO":
			self.csoc.send("SALUT N")
			return 0
		if data[0:5] == "CLOSE":
			self.csoc.send("BUBYE")
			return 1
		if data[0:5] == "REGME":
			splitted = data[6:].split(":")
			if len(splitted) == 2: 
				self.csoc.send("REGWA")
				for l in connection_list:
					if l[0]== splitted[0] and l[1] == splitted[1]:
						self.csoc.send("REGOK ")
						self.status = "S"
						return 0

				t = datetime.datetime.now()
				posixtime=time.mktime(t.timetuple())
				connection_list.append([splitted[0],splitted[1],str(posixtime),"W"])
				index = connection_list.index([splitted[0],splitted[1],str(posixtime),"W"])
				threadQueue = Queue.Queue()
				thread = NegotiatorClient(splitted[0],splitted[1],threadQueue)
				thread.start()
				while True:
					if threadQueue.qsize() > 0:
						status = threadQueue.get()	
						if status == "1":
							self.csoc.send("REGER")
							connection_list.remove([splitted[0],splitted[1],str(posixtime),"W"])
							return 1
						else :	
							for l in connection_list:
								if l[0]== splitted[0] and l[1] == splitted[1]:
									loc = connection_list.index(l)
									connection_list[loc]=[splitted[0],splitted[1],str(posixtime),"S"]
									self.status = "S"
									break
							self.csoc.send("REGOK "+str(posixtime))
							return 0

					
			else :
				self.csoc.send("REGER")
				return 1
		
		if data[0:5] == "GETNL":
			if self.status == "W":
				self.csoc.send("REGER")
				return 1
				
			elif len(data) == 5:
				index = len(self.connection_list)
			else :
				index = len(data[6:])
			
			response = "NLIST BEGIN \n"				
			for i in range(0,index):
				response= response +self.connection_list[i][0]+":"+self.connection_list[i][1]+":"+self.connection_list[i][2]+":"+"P"+ "\n"	
			response = response +"NLIST END"			
			self.csoc.send(response)
			return 0
		

		else :
			self.csoc.send("CMDER")
			return 1


	
	def run(self):
		
		while True:
			try: 
				incoming_data = self.csoc.recv(1024)
			except :
				break			
			incoming_data = incoming_data.strip()
			status = self.parser(incoming_data)
			if status == 0:
				pass
			else :
				break
		self.csoc.close()	
		
class NegotiatorClient (threading.Thread):
	def __init__(self, host, port, threadQueue):
		threading.Thread.__init__(self)
		self.host = host
		self.port = int(port)
		self.threadQueue = threadQueue
		self.csoc = socket.socket()
		
	def run(self):
		try:
			self.csoc.connect((self.host,self.port))
			
		except:
			self.threadQueue.put("1")
			return

		self.csoc.settimeout(30.0)
		self.csoc.send("HELLO")
				
		try:		
			incoming_data = self.csoc.recv(1024)		
		except :
			self.threadQueue.put("1")
			return 

		incoming_data = incoming_data.strip()
		if incoming_data[0:5] =="SALUT":
			if incoming_data[6]=="N":
				self.csoc.send("CMDER")
				self.threadQueue.put("1")
				return
			elif incoming_data[6]=="P":
				pass
			else :
				self.csoc.send("CMDER")
				self.threadQueue.put("1")
				return
		else :
			self.csoc.send("CMDER")
			self.threadQueue.put("1")
			return	

		self.csoc.send("CLOSE")
		try:		
			incoming_data = self.csoc.recv(1024)		
		except :
			self.threadQueue.put("1")
			return 
		incoming_data = incoming_data.strip()
		if incoming_data[0:5] =="BUBYE":
			self.threadQueue.put("0")
			return

		else :
			self.csoc.send("CMDER")	
			self.threadQueue.put("1")	
			return

class Updater (threading.Thread):

	def __init__(self,connection_list):
		threading.Thread.__init__(self)
		self.connection_list = connection_list

	def run(self):
		threadQueue = Queue.Queue()
		while True:
			time.sleep(5.0)			
			for l in self.connection_list:
				thread = NegotiatorClient(l[0],l[1],threadQueue)
				thread.start()
				while True:
					if threadQueue.qsize() > 0:
						status = threadQueue.get()
						if status == "1":
							self.connection_list.remove(l)
							
						break	
			print self.connection_list
connection_list = []

s = socket.socket()
host = socket.gethostname()
port = 12349

s.bind((host, port))
s.listen(5)
thread = Updater(connection_list)
thread.start()

while True:
	c, addr = s.accept()
	thread = NegotiatorServer(c, addr,connection_list)
	thread.start()




