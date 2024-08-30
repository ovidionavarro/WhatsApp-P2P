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
        self.leader=True
        self.first=True

        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.print_status, daemon=True).start()

        logging.info(f"Node initialized with ID {self.id} and IP {self.ip}")

    def print_status(self):
        while True:
            string=f'pred: {self.pred} ={self.ip}= succ: {self.succ}'
            print(string)
            time.sleep(10)


    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            logging.info("Esperando Nodos")
            s.listen(10)

            while True:
                conn, addr = s.accept()
                print(f'new connection from {addr}')

                data = conn.recv(1024).decode("utf-8").split(',')
                if int(data[0])==JOIN:
                    if(self.pred.id==self.id):
                        self.succ=ChordNodeReference(getShaRepr(str(addr[0])),addr[0],8001)
                        self.pred=ChordNodeReference(getShaRepr(str(addr[0])),addr[0],8001)
                        data=f'{self.ip},{self.port}'.encode()
                        print(f'Recibido del cliente: {data}')
                        conn.sendto(data, addr)
                time.sleep(1)

    def join(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 8001))
        sock.sendall(f'{JOIN},{ip}'.encode('utf-8'))
        data= sock.recv(1024).decode().split(',')
        print(data)
        if len(data)==2:
            ref_ip,ref_port=data
            self.pred=ChordNodeReference(getShaRepr(ref_ip),ref_ip,int(ref_port))
            self.succ=self.pred
            

    def update_succ(self,node:ChordNodeReference):
        self.succ=node



if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    print(f'My IP: {ip}')
    id = getShaRepr(ip)
    node = ChordNode(id, ip, 8001, M)

    print(f'My ID: {node.id}')

    if len(sys.argv) >= 2:
        other_ip = sys.argv[1]
        id = getShaRepr(other_ip)
        node.join(other_ip, node.port)

    while True:
        pass
