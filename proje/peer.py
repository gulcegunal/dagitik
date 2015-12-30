class RegistrationThread(threading.Thread):
	def __init__(self, name, cIp, cPort, ip, port, ts):
		threading.Thread.__init__(self)
		self.name = name
		self.cIp = cIp
		self.cPort = cPort
		self.ip = ip
		self.port = port
		self.cPointList = connectPointList
		self.pQueue = peerQueue
		self.ts = ts
	def client(self,data):
		global ts
		data = data.strip()
		rest = data[6:]

		if data[0:5] == "REGWA":
			self.ts.close()
			self.ts = socket.socket()
			self.ts.connect((self.cIp, self.cPort))
			print(data)

			return 0

		elif data[0:5] == "REGOK": 
			print(data)

			return 1

		elif data[0:5] == "REGER":
			print(data)

			return 0	

		elif data[0:5] == "NLIST":
			print(data)
			rest = rest.split("\n")

			for peer in rest[1:-1]:
				peer = peer.split(":")
				peerKey = peer[0] + ":" + peer[1]

				if peer[0] ==self.ip and peer[1] == self.port:
					continue

				newPeer = { peerKey: "W"}
				self.cPointList.update(newPeer)

				self.pQueue.put(peerKey)

				test = TestThread("TestThread", self.pQueue, self.cPointList)			
				test.start()	
		
			return 2

	def run(self):  
		print("Starting " +self.name)
		while True:
			try:
				self.ts.send(("REGME " + self.ip + ":"+str(self.port)).encode())
				data = self.ts.recv(1024).decode()
				time.sleep(3)
				response = self.client(data)

				if response == 1:
					self.ts.send("GETNL ".encode())
					data = self.ts.recv(1024).decode()
					response = self.client(data)
					if response == 2:
						break
				print(response)
			except:
				self.ts.close()
				break
			
		print("Ending " +self.name)


class TestThread (threading.Thread):
	def __init__(self, name, peerQueue, connectPointList):
		threading.Thread.__init__(self)
		self.name = name
		self.pQueue = peerQueue	
		self.cPoints = connectPointList
		self.tSocket = socket.socket()
		self.tSocket.settimeout(60)

	def test(self, peer):
		connectPoint = peer.split(":")

		try:
			self.tSocket.connect((connectPoint[0], int(connectPoint[1])))

			self.tSocket.send("HELLO".encode())

			data = self.tSocket.recv(1024).decode()
			data = data.strip()

			print(data)
			rest = data[6:]

			if data[0:5] == "SALUT":
				self.cPoints[peer] = "S " + str(int(time.time())) + rest
				print(self.cPoints)

			else:
				self.tSocket.send("CMDER".encode())			
	
		except:
			del self.cPoints[peer]
			self.tSocket.close()	

	def run(self):  
		print("Starting " + self.name)

		while True:
			if self.pQueue.qsize() > 0:                                                                 
				toBeTested = self.pQueue.get()
				self.test(toBeTested)

			else:
				self.tSocket.close()
				break		
	
		print("Ending " + self.name)


class UpdateThread(threading.Thread):
	def __init__(self, name, connectPointList, updateInterval, peerQueue):
		threading.Thread.__init__(self)
		self.name = name
		self.cPoints = connectPointList
		self.updateInterval = updateInterval
		self.pQueue = peerQueue
		self.counter = 0

	def update(self):
		for peer in self.cPoints.keys():
			self.pQueue.put(peer)

		for i in range(0,5):
			self.counter +=1

			test = TestThread("TestThread" +str(self.counter), peerQueue, connectPointList)			
			test.start()

	def run(self):
		while True:
			time.sleep(self.updateInterval)
			self.update()

