import socket

class Network:
    def __init__(self, server):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server
        self.port = 12577  # Assuming ngrok always maps to this port
        self.addr = (self.server, self.port)
        self.pos = self.connect()

    def get_pos(self):
        return self.pos

    def connect(self):
        try:
            self.client.connect((self.server, self.port))
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)

    def send(self, data):
        try:
            self.client.send(str.encode(data))
        except socket.error as e:
            print(e)

    def receive(self):
        try:
            return self.client.recv(2048).decode()
        except socket.error as e:
            print(e)
