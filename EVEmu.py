import EVEmuServer
import traceback, weakref, logging, stackless, stacklesssocket, socket

def runServer(host, port):
	global server
	server = EVEmuServer.EVEmuServer(host, port)

	while 1:
		stackless.run()

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s')
	stacklesssocket.install()

	try:
		runServer("127.0.0.1", 26000)
	except KeyboardInterrupt:
		logging.info("Server stopped manually")