import socket
import threading
import sys
import time
import logging
from chord_node_reference import ChordNodeReference
from codes import *
from utils import getShaRepr

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')


class ChordNode:
    def __init__(self, id: int, ip: str, port: int = 8001, m: int = 2):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.id, self.ip, self.port, m)
        self.succ = self.ref  # Initial successor is itself
        self.pred = self.ref  # Initially predecessor is itself
        self.m = m  # Number of bits in the hash/key space
        self.finger = [self.ref] * self.m  # Finger table
        self.next = 0  # Finger table index to fix next

        threading.Thread(target=self.start_server, daemon=True).start()

        logging.info(f"Node initialized with ID {self.id} and IP {self.ip}")

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            logging.info("Esperando Nodos")
            s.listen(10)

            while True:
                conn, addr = s.accept()
                print(f'new connection from {addr}')

                data = conn.recv(1024).decode()
                print(f'Recibido del cliente: {data.decode("utf-8")}')
                conn.sendto(b'Hola cliente!', addr)
                time.sleep(1)

    def join(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 8001))
        sock.sendall(b'Hola servidor!')
        data = sock.recv(1024)
        print(data.decode('utf-8'))
        self.start_server()


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    id = getShaRepr(ip)
    node = ChordNode(id, ip, 8001, M)

    print(node.id)

    if len(sys.argv) >= 2:
        other_ip = sys.argv[1]
        id = getShaRepr(other_ip)
        node.join(other_ip, node.port)

    while True:
        pass
