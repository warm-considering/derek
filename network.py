import socket
from multiprocessing import Process

class Network():
    def __init__(self):
        self.host = ''
        self.chatport = 34
        self.audioport = 35
        self.connections = []
        self.cssocket = socket.socket()
        self.cssocket.bind((self.host, self.chatport))

    def createChatConnection(self, q):        
        while True:
            self.cssocket.listen(5)
            conn, addr = self.cssocket.accept()
            self.connections.append((conn, addr))
            self.messageThread = Process(target=self.listenMessage, args=(q,conn))
            self.messageThread.daemon = True
            self.messageThread.start()

    def listenMessage(self, q, conn):
        while True:
            response = conn.recv(1024)
            if response is not None:
                q.append(response)

    def makeConn(self, remhost):
        self.cssocket.connect((remhost,self.chatport))
        new = self.cssocket.dup()
        self.connections.append(new)
        
