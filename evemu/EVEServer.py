import traceback, weakref, logging, stackless, socket
from dep import stacklesssocket
import EVEClient

class EVEServer:
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
				EVEClient(clientSocket, clientAddress)
				stackless.schedule()
		except socket.error:
			traceback.print_exc()
