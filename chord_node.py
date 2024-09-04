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
    def __init__(self, ip: str, port: int = 8001, m: int = 160):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.ip, self.port)
        self.succ = self.ref  # Initial successor is itself
        self.pred = None  # Initially no predecessor
        self.pred_2=None
        self.m = m  # Number of bits in the hash/key space
        self.finger = [self.ref] * self.m  # Finger table
        self.next = 0  # Finger table index to fix next
        self.data = {}  # Dictionary to store key-value pairs

        # Start background threads for stabilization, fixing fingers, and checking predecessor
        threading.Thread(target=self.stabilize, daemon=True).start()  # Start stabilize thread
        threading.Thread(target=self.fix_fingers, daemon=True).start()  # Start fix fingers thread
        threading.Thread(target=self.check_predecessor, daemon=True).start()  # Start check predecessor thread
        threading.Thread(target=self.start_server, daemon=True).start()  # Start server thread

    # Helper method to check if a value is in the range (start, end]
    def _inbetween(self, k: int, start: int, end: int) -> bool:
        if start < end:
            return start < k <= end
        else:  # The interval wraps around 0
            return start < k or k <= end

    # Method to find the successor of a given id
    def find_succ(self, id: int) -> 'ChordNodeReference':
        node = self.find_pred(id)  # Find predecessor of id
        return node.succ  # Return successor of that node

    # Method to find the predecessor of a given id
    def find_pred(self, id: int) -> 'ChordNodeReference':
        node = self
        while not self._inbetween(id, node.id, node.succ.id):
            node = node.closest_preceding_finger(id)
        return node

    # Method to find the closest preceding finger of a given id
    def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
        for i in range(self.m - 1, -1, -1):
            if self.finger[i] and self._inbetween(self.finger[i].id, self.id, id):
                return self.finger[i]
        return self.ref

    # Method to join a Chord network using 'node' as an entry point
    def join(self, node: 'ChordNodeReference'):
        if node:
            logging.info(f"nodoooooooooooooooooooo :{node.id}  succcccccc :{node.succ.id}")
            if (
                    node.id == node.succ.id):  # aki solo entra cuando id = id del succersor osea cuando unido yo soy mi succesor
                self.succ = node
                self.pred = node
                self.succ.notify(self.ref)
                self.succ.case_basic(self.ref)
            else:
                self.pred = None
                self.succ = node.find_successor(self.id)
                self.succ.notify(self.ref)
        else:
            self.succ = self.ref
            self.pred = None

    # Stabilize method to periodically verify and update the successor and predecessor
    def stabilize(self):
        while True:
            try:
                if self.succ.id != self.id:
                    logging.info('stabilize')
                    x = self.succ.pred
                    logging.info(f"esto es el stabilize {x.id}")
                    if x.id != self.id:
                        logging.info(x)
                        if x and self._inbetween(x.id, self.id, self.succ.id):
                            self.succ = x
                        self.succ.notify(self.ref)
            except Exception as e:
                logging.info(f"Error in stabilize: {e}")
            if self.pred!=None:
                self.pred_2=self.pred.pred
                logging.info(f"pred_pred :{self.pred_2.id}")

            logging.info(f"successor : {self.succ} predecessor : {self.pred} ")
            
            fing = ''
            for i in range(0, m):
                fing += f"[{self.finger[i].id}]"
            logging.info(f"finger:{fing}")
            time.sleep(10)

    # Notify method to inform the node about another node
    def notify(self, node: 'ChordNodeReference'):
        if node.id == self.id:
            pass
        if not self.pred or self._inbetween(node.id, self.pred.id, self.id):
            self.pred = node

    def case_basic(self, node: 'ChordNodeReference'):
        logging.info(f"casobase recibiendo nodo: {node.id}")
        self.succ = node

    # Fix fingers method to periodically update the finger table
    def fix_fingers(self):
        while True:
            try:
                self.next += 1
                if self.next >= self.m:
                    self.next = 0
                self.finger[self.next] = self.find_succ((self.id + 2 ** self.next) % 2 ** self.m)
            except Exception as e:
                logging.info(f"Error in fix_fingers: {e}")
            time.sleep(10)

    # Check predecessor method to periodically verify if the predecessor is alive
    def check_predecessor(self):
        while True:
            try:
                if self.pred:
                    self.pred.check_predecessor()
            except Exception as e:
                self.pred = None
            time.sleep(10)

    # Store key method to store a key-value pair and replicate to the successor
    def store_key(self, key: str, value: str):
        key_hash = getShaRepr(key)
        node = self.find_succ(key_hash)
        node.store_key(key, value)
        self.data[key] = value  # Store in the current node
        self.succ.store_key(key, value)  # Replicate to the successor

    # Retrieve key method to get a value for a given key
    def retrieve_key(self, key: str) -> str:
        key_hash = getShaRepr(key)
        node = self.find_succ(key_hash)
        return node.retrieve_key(key)

    # Start server method to handle incoming requests
    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            s.listen(10)

            while True:
                conn, addr = s.accept()

                data = conn.recv(1024).decode().split(',')

                data_resp = None
                option = int(data[0])
                logging.info(f'new connection from {addr},option:{option}')

                if option == FIND_SUCCESSOR:
                    id = int(data[1])
                    data_resp = self.find_succ(id)
                elif option == FIND_PREDECESSOR:
                    id = int(data[1])
                    data_resp = self.find_pred(id)
                elif option == GET_SUCCESSOR:
                    data_resp = self.succ if self.succ else self.ref
                elif option == GET_PREDECESSOR:
                    data_resp = self.pred if self.pred else self.ref
                elif option == NOTIFY:
                    id = int(data[1])
                    ip = data[2]
                    self.notify(ChordNodeReference(ip, self.port))
                elif option == BASE:
                    id = int(data[1])
                    ip = data[2]
                    self.case_basic(ChordNodeReference(ip, self.port))
                elif option == CHECK_PREDECESSOR:
                    pass
                elif option == CLOSEST_PRECEDING_FINGER:
                    id = int(data[1])
                    data_resp = self.closest_preceding_finger(id)
                elif option == STORE_KEY:
                    key, value = data[1], data[2]
                    self.data[key] = value
                elif option == RETRIEVE_KEY:
                    key = data[1]
                    data_resp = self.data.get(key, '')

                if data_resp:
                    response = f'{data_resp.id},{data_resp.ip}'.encode()
                    conn.sendall(response)
                conn.close()


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    node = ChordNode(ip, 8001, m)

    if len(sys.argv) >= 2:
        other_ip = sys.argv[1]
        node.join(ChordNodeReference(other_ip, node.port))

    while True:
        pass