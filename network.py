import socket

class Network():
    def __init__(self):
        self.host = socket.gethostname()
        self.chatport = 34
        self.audioport = 35
        self.connections = []
        self.cssocket = socket.socket()
        self.cssocket.bind((self.host, self.chatport))

    def createChatConnection(self):        
        while True:
            self.cssocket.listen(5)
            conn, addr = self.cssocket.accept()
            self.connections.append((conn, addr))

    def listenMessage(self, q):
        while True:
            q.put(self.cssocket.recv(1024))

    def makeConn(self, remhost):
        self.cssocket.connect((remhost,self.chatport))
        new = self.cssocket.dup()
        self.connections.append(new)
        
