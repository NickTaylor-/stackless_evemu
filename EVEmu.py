import traceback, weakref, logging, stackless, stacklesssocket
stacklesssocket.install()
import socket

class Connection:
    disconnected = False

    def __init__(self, clientSocket, clientAddress):
        logging.info("Connection established from %s", clientAddress)

        self.clientSocket = clientSocket
        self.clientAddress = clientAddress

        stackless.tasklet(self.Read)()

    def Disconnect(self):
        if self.disconnected:
            raise RuntimeError("Unexcpected call")
        self.disconnected = True
        self.clientSocket.close()

    def Write(self, s):
        self.clientSocket.send(bytearray(s))

    def Read(self):
        global server

        readBuffer = ""

        # send join data
        version = 170472, 320, 0, 7.31, 360299, "EVE-EVE-TRANQUILITY@ccp"
        self.Write(version)

        while True:
            if readBuffer != "":
                logging.info("Received packet: %s", readBuffer)
                readBuffer = ""

            chunkBuffer = self.clientSocket.recv(1024).decode("utf-8")
            
            if chunkBuffer == "":
                logging.info("Client remotely disconnected (unclean)")
                self.Disconnect()
                break
            
            readBuffer += chunkBuffer


class Server:
    def __init__(self, host, port):
        self.host = host
        self.port = port

        self.userIndex = weakref.WeakValueDictionary()

        stackless.tasklet(self.Run)()

    def Run(self):
        listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listenSocket.bind((self.host, self.port))
        listenSocket.listen(5)

        logging.info("Accepting connections on %s:%s", self.host, self.port)
        try:
            while 1:
                clientSocket, clientAddress = listenSocket.accept()
                Connection(clientSocket, clientAddress)
                stackless.schedule()
        except socket.error:
            traceback.print_exc()

def Run(host, port):
    global server
    server = Server(host, port)
    while 1:
        stackless.run()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s')
    
    try:
        Run("127.0.0.1", 26000)
    except KeyboardInterrupt:
        logging.info("Server stopped manually")
