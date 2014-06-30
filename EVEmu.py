import EVEServer, logging, stacklesssocket, socket, stackless

def runServer(host, port):
	global server
	server = EVEServer.EVEServer(host, port)

	while 1:
		stackless.run()

if __name__ == "__main__":
	logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s')
	stacklesssocket.install()

	try:
		runServer("0.0.0.0", 26000)
	except KeyboardInterrupt:
		logging.info("Server stopped manually")