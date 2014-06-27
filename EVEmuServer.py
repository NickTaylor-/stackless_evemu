import EVEmu
import traceback, weakref, logging, stackless, stacklesssocket, socket
from struct import *
from EVEMarshal import EVEMarshal

class EVEmuServer:
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.userIndex = weakref.WeakValueDictionary()

		stackless.tasklet(self.run)()

	def run(self):
		listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listenSocket.bind((self.host, self.port))
		listenSocket.listen(5)

		try:
			while True:
				clientSocket, clientAddress = listenSocket.accept()
				Connection(clientSocket, clientAddress)
				stackless.schedule()
		except socket.error:
			traceback.print_exc()

class Connection:
	disconnected = False
	marshal = EVEMarshal()

	def __init__(self, clientSocket, clientAddress):
		logging.info("Connection established from %s", clientAddress)

		self.clientSocket = clientSocket
		self.clientAddress = clientAddress

		# Send version information to client
		version = 170472, 399, 312337, 8.45, 801047, "EVE-TRANQUILITY@ccp", None
		print(self.marshal.unmarshal(self.marshal.marshal(version)))
		self.write(version)

		stackless.tasklet(self.read)()

	def disconnect(self):
		if self.disconnected:
			raise RuntimeError("Unexpected call: already disconnected")

		self.disconnected = True
		self.clientSocket.close()

	def write(self, data):
		writeData = pack('<b', 0x7E)
		writeData += pack('<l', 0)
		writeData += self.marshal.marshal(data)
		size = pack('<l', len(writeData))
		writeData = size + writeData

		self.clientSocket.send(writeData)

	def read(self):
		readBuffer = None