import traceback, weakref, logging, stackless, socket
from dep import stacklesssocket
from EVEMarshal import *

class EVEClient:
	disconnected = False
	marshal = EVEMarshal()
	version = 170472, 399, 312337, 8.45, 805617, "EVE-TRANQUILITY@ccp", None

	def __init__(self, clientSocket, clientAddress):
		logging.info("Connection established from %s", clientAddress)

		self.clientSocket = clientSocket
		self.clientAddress = clientAddress

		# Send version information to client
		self.write(self.version)
		self.verfiyVersion()

		stackless.tasklet(self.handleCommand)()

	def disconnect(self):
		if self.disconnected:
			logging.error("Tried to disconnect already disconnected client ", self.clientAddress)

		self.disconnected = True
		self.clientSocket.close()

	def handleCommand(self):
		while self.disconnected == False:
			packetData = self.read()

			if (type(packetData) != tuple):
				logging.error('%s: Received %s when expecting tuple', self.clientAddress[0], type(packetData).__name__)
			elif packetData[0] == None:
				if packetData[1] == 'QC':
					self.write(1)
					self.write(self.version)
					self.verfiyVersion()
				elif packetData[1] == 'VK':
					# We don't really care about this packet, so get the next one
					packetData = self.read()
					if packetData[0] == 'placebo':
						self.write("OK CC")
						packetData = self.read()
						
					else:
						logging.error("%s: You must change your client to use Placebo crypto in common.ini to talk to this server!", self.clientAddress[0])

				else:
					logging.warning('%s: Unknown packet receieved: %s', self.clientAddress[0], packetData[:1])
			else:
				logging.warning('%s: Unknown service: %s', self.clientAddress[0], packetData[0])

	def write(self, data):
		writeData = pack('<b', 0x7E)
		writeData += pack('<l', 0)
		writeData += self.marshal.marshal(data)
		size = pack('<l', len(writeData))
		writeData = size + writeData

		self.clientSocket.send(writeData)

	def read(self):
		packetSize = unpack('<l', self.clientSocket.recv(4))[0]
		packetHeader = self.clientSocket.recv(5)

		packetData = self.marshal.unmarshal(self.clientSocket.recv(packetSize - 5))
		logging.debug('%s: Received packet: %s', self.clientAddress[0], packetData)

		return packetData

	def verfiyVersion(self):
		packetData = self.read()

		if packetData[0] != self.version[0] or packetData[1] != self.version[1] or packetData[3] != self.version[3] or packetData[4] != self.version[4] or packetData[5] != self.version[5]:
			logging.error("%s: Client attempting to connect with wrong client", self.clientAddress[0])
			logging.debug("%s: Client has this version %s", self.clientAddress[0], packetData)
