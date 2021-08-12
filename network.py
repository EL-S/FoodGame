import socket
import pickle
from config_loader import client_settings


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = socket.gethostbyname(client_settings['server_ip'])
        self.port = int(client_settings['server_port'])
        self.addr = (self.server, self.port)
        self.p = self.connect()

    def getP(self):
        return self.p

    def connect(self):
        try:
            self.client.connect(self.addr)
            return self.client.recv(2048).decode()
        except:
            pass

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            response = pickle.loads(self.client.recv(2048*2))
            return response # The response data, including the board and other players
        except socket.error as e:
            print(e)
