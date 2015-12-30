import datetime
import time
import threading
import socket
import Queue
from PyQt4 import *
import sys
import ip
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import hashlib



class PeerClient (threading.Thread):
	def __init__(self, host, port, app, connection_list,my_host,my_port,threadQueue,lock):
		threading.Thread.__init__(self)
		self.app = app
		self.csoc= socket.socket()
		##socket
		self.connection_list = connection_list
		self.host=host
		self.port=port
		self.my_host=my_host
		self.my_port=my_port
		self.threadQueue=threadQueue
		self.lock=lock
	def run (self):
		self.csoc.connect((self.host, self.port))
		self.csoc.settimeout(30.0)				
		self.csoc.send("HELLO")	
	
		try:		
			incoming_data = self.csoc.recv(1024)		
		except :			
			self.app.cprint("Connection Failed to " + self.host +" "+ str(self.port))			
			return 

		incoming_data = incoming_data.strip()
		
		if incoming_data[0:5] =="SALUT":	
			##Peer-Nego SALUT 
			if incoming_data[6]=="N":
				
				self.csoc.send("REGME "+str(self.my_host)+":"+ str(self.my_port))
				try:		
					incoming_data = self.csoc.recv(1024)		
				except :			
					self.app.cprint("Connection Failed to " + str(self.host) +" "+ str(self.port))			
					self.threadQueue.put("1")
					return
				incoming_data = incoming_data.strip()
				if incoming_data[0:5] =="REGWA":					
					
					try:		
						incoming_data = self.csoc.recv(1024)		
					except :			
						self.app.cprint("Connection Failed to " + str(self.host) +" "+ str(self.port))					
						self.threadQueue.put("1")
						return
					incoming_data = incoming_data.strip()
					if incoming_data[0:5] =="REGOK":
						self.csoc.send("GETNL")

						try:		
							incoming_data = self.csoc.recv(1024)		
						except :			
							self.app.cprint("Connection Failed to " + str(self.host) +" "+ str(self.port))						
							self.threadQueue.put("1")
							return
						incoming_data = incoming_data.strip()
						if incoming_data[0:11] =="NLIST BEGIN":
							if incoming_data[-9:] == "NLIST END":
								lenght=len(incoming_data)
								if lenght >23:
									data=incoming_data[13:lenght-10].split("\n")
									print data
									lenght= len(data)
									new_connection_list = []
									for l in data:
										peer= l.split(":")
										new_connection_list.append([peer[0],peer[1],peer[2],"S"])
									
									self.connection_list = new_connection_list
									
								self.csoc.send("CLOSE")
								try:
									incoming_data=self.csoc.recv(1024)
								except:
									self.app.cprint("Connection Failed to " + str(self.host) +" "+ str(self.port))						
									self.threadQueue.put("1")
									return
								if incoming_data[0:5] == "BUBYE":
									self.csoc.close()
									self.threadQueue.put(self.connection_list)
									return 
				elif incoming_data [0:5] == "REGER":
					self.app.cprint("Connection Failed to " + str(self.host) +" "+ str(self.port))
					self.threadQueue.put("1")			
					return 
			##Peer-Peer 
		
			elif incoming_data[6]=="P":

				self.csoc.send("REGME "+str(self.my_host)+":"+ str(self.my_port))
				try:		
					incoming_data = self.csoc.recv(1024)		
				except :			
					self.app.cprint("Connection Failed to " + str(self.host) +" "+ str(self.port))			
					self.threadQueue.put("1")
					return
				if incoming_data=="REGER":
					self.app.cprint("Connection Failed to " + str(self.host) +" "+ str(self.port))			
					
					self.threadQueue.put("1")
					return	 

		
		







class PeerServer (threading.Thread):
	def __init__(self,csoc ,addr,connection_list , app,lock):
		threading.Thread.__init__(self)
		self.app = app
		self.csoc = csoc
		self.connection_list = connection_list
		self.addr=addr
		self.lock=lock
	def run (self):
		print "server connection list"+str(self.connection_list)
		self.csoc.settimeout(30.0)
		while True:
			try:		
				incoming_data = self.csoc.recv(1024)
				incoming_data=incoming_data.strip()		
			except :			
				self.app.cprint("Connection Failed ")
				self.csoc.close()			
				return 

			incoming_data=incoming_data.strip()
			print "incoming data to peer_server : "+incoming_data
			if incoming_data[0:5] == "HELLO":
				self.csoc.send("SALUT P")
			elif incoming_data[0:5] == "CLOSE":
				self.csoc.send("BUBYE")
				self.csoc.close()
				break
			elif incoming_data[0:5] == "REGME":
				splitted = incoming_data[6:].split(":")
				is_online=False
				print "splitted   "+str(splitted)
				
				for c in self.connection_list:
					
					if c[0]==splitted[0] and c[1]==splitted[1]:
						is_online=True
						break
				
				if not is_online:
					self.csoc.send("REGER")
					self.csoc.close()			
					return	
				else :
					self.csoc.send("REGOK")

				try:		
					incoming_data = self.csoc.recv(1024)
					print incoming_data
					incoming_data=incoming_data.strip()			
				except :			
					self.app.cprint("Connection Failed ")
					self.csoc.close()			
					return 		
				if incoming_data[0:5]=="FUNRQ":	
					functionname=incoming_data[6:]
					
					
					if functionname in functionList:

						self.csoc.send("FUNYS"+functionname+":"+parameter_intervals)
					else :
						self.csoc.send("FUNNO"+functionname)


								
		
				

				elif incoming_data[0:5]=="EXERQ":			
					return 0


				elif incoming_data[0:5]=="PATCH":
					return 0
			
					


			else:
				self.csoc.send("REGER")
				self.csoc.close()
				break



		
				

class Listener (threading.Thread):
	def __init__(self,s,listQueue,lock):
		threading.Thread.__init__(self)
		self.s=s
		self.connection_list = []
		self.listQueue=listQueue
		self.size=1
		self.lock = lock
	def run (self):
		
		while True:
			try:

				c, addr = s.accept()

				if self.listQueue.qsize() > self.size:

					self.connection_list=self.listQueue.get()
					self.size=self.listQueue.qsize()
					print "listener list "+str(self.connection_list)

				thread = PeerServer(c, addr,self.connection_list,app,lock)
				thread.start()
			except:
				break

functionList = ['Gray Scale Filter', 'Sobel Filter', 'Binarize Filter', 'Prewitt Filter', 'Gaussian Filter']
lock=threading.Lock()
connection_list = []

s = socket.socket()
host = socket.gethostname()

port = 12340
neg_port=12349


s.bind((host, port))
s.listen(5)

listQueue=Queue.LifoQueue()

listener=Listener(s,listQueue,lock)
listener.start()









