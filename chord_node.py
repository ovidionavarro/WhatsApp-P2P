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
    def __init__(self, id: int, ip: str, port: int = 8001, m: int = 160):
        self.id = getShaRepr(ip)
        self.ip = ip
        self.port = port
        self.ref = ChordNodeReference(self.id, self.ip, self.port)
        self.succ = self.ref  # Initial successor is itself
        self.pred = self.ref  # Initially predecessor is itself
        self.m = m  # Number of bits in the hash/key space
        self.finger = [self.ref] * self.m  # Finger table
        self.next = 0  # Finger table index to fix next

        logging.info(f"Node initialized with ID {self.id} and IP {self.ip}")

    #     threading.Thread(target=self.stabilize, daemon=True).start()  # Start stabilize thread
    #     threading.Thread(target=self.fix_fingers, daemon=True).start()  # Start fix fingers thread
    #     threading.Thread(target=self.check_predecessor, daemon=True).start()  # Start check predecessor thread
    #     threading.Thread(target=self.start_server, daemon=True).start()  # Start server thread
    #
    # def _inbetween(self, k: int, start: int, end: int) -> bool:
    #     """Check if k is in the interval (start, end]."""
    #     if start < end:
    #         return start < k <= end
    #     else:  # The interval wraps around 0
    #         return start < k or k <= end
    #
    # def find_succ(self, id: int) -> 'ChordNodeReference':
    #     node = self.find_pred(id)  # Find predecessor of id
    #     return node.succ  # Return successor of that node
    #
    # def find_pred(self, id: int) -> 'ChordNodeReference':
    #     node = self
    #     while not self._inbetween(id, node.id, node.succ.id):
    #         node = node.closest_preceding_finger(id)
    #     return node
    #
    # def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
    #     for i in range(self.m - 1, -1, -1):
    #         if self.finger[i] and self._inbetween(self.finger[i].id, self.id, id):
    #             return self.finger[i]
    #     return self.ref
    #
    # def join(self, node: 'ChordNodeReference'):
    #     """Join a Chord network using 'node' as an entry point."""
    #     if node:
    #         self.pred = None
    #         self.succ = node.find_successor(self.id)
    #         self.succ.notify(self.ref)
    #     else:
    #         self.succ = self.ref
    #         self.pred = None
    #
    # def stabilize(self):
    #     """Regular check for correct Chord structure."""
    #     while True:
    #         try:
    #             if self.succ.id != self.id:
    #                 logging.info('Stabilizing...')
    #                 x = self.succ.pred
    #                 if x.id != self.id:
    #                     if x and self._inbetween(x.id, self.id, self.succ.id):
    #                         self.succ = x
    #                     self.succ.notify(self.ref)
    #         except Exception as e:
    #             logging.error(f"Error in stabilize: {e}")
    #
    #         logging.info(f"Successor: {self.succ} Predecessor: {self.pred}")
    #         time.sleep(10)
    #
    # def notify(self, node: 'ChordNodeReference'):
    #     if node.id == self.id:
    #         pass
    #     if not self.pred or self._inbetween(node.id, self.pred.id, self.id):
    #         self.pred = node
    #
    # def fix_fingers(self):
    #     while True:
    #         try:
    #             self.next = (self.next + 1) % self.m
    #             self.finger[self.next] = self.find_succ((self.id + 2 ** self.next) % (2 ** self.m))
    #         except Exception as e:
    #             logging.error(f"Error in fix_fingers: {e}")
    #         time.sleep(1)
    #
    # def check_predecessor(self):
    #     while True:
    #         try:
    #             if self.pred:
    #                 self.pred.check_predecessor()
    #         except Exception as e:
    #             self.pred = None
    #         time.sleep(10)
    #
    # def start_server(self):
    #     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #         s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    #         s.bind((self.ip, self.port))
    #         s.listen(10)
    #         logging.info(f"Server started at {self.ip}:{self.port}")
    #
    #         while True:
    #             conn, addr = s.accept()
    #             logging.info(f'New connection from {addr}')
    #
    #             data = conn.recv(1024).decode().split(',')
    #
    #             data_resp = None
    #             option = int(data[0])
    #
    #             if option == FIND_SUCCESSOR:
    #                 id = int(data[1])
    #                 data_resp = self.find_succ(id)
    #             elif option == FIND_PREDECESSOR:
    #                 id = int(data[1])
    #                 data_resp = self.find_pred(id)
    #             elif option == GET_SUCCESSOR:
    #                 data_resp = self.succ if self.succ else self.ref
    #             elif option == GET_PREDECESSOR:
    #                 data_resp = self.pred if self.pred else self.ref
    #             elif option == NOTIFY:
    #                 id = int(data[1])
    #                 ip = data[2]
    #                 self.notify(ChordNodeReference(id, ip, self.port))
    #             elif option == CHECK_PREDECESSOR:
    #                 pass
    #             elif option == CLOSEST_PRECEDING_FINGER:
    #                 id = int(data[1])
    #                 data_resp = self.closest_preceding_finger(id)
    #
    #             if data_resp:
    #                 response = f'{data_resp.id},{data_resp.ip}'.encode()
    #                 conn.sendall(response)
    #             conn.close()
    #


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    id = getShaRepr(ip)
    node = ChordNode(id, ip)

    # if len(sys.argv) >= 2:
    #     other_ip = sys.argv[1]
    #     id = getShaRepr(other_ip)
    #     node.join(ChordNodeReference(id, other_ip, node.port))
    #
    # while True:
    #     pass
