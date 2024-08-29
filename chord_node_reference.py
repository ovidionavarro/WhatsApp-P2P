import socket
import threading
import sys
import time
import hashlib
import logging
from utils import getShaRepr
from codes import *


class ChordNodeReference:
    def __init__(self, id: int, ip: str, port: int = 8001, m: int = 4):
        self.id = getShaRepr(ip) % 2**m
        self.ip = ip
        self.port = port

    #
    # def _send_data(self, op: int, data: str = None) -> bytes:
    #     try:
    #         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    #             s.connect((self.ip, self.port))
    #             s.sendall(f'{op},{data}'.encode('utf-8'))
    #             return s.recv(1024)
    #     except Exception as e:
    #         logging.error(f"Error sending data: {e}")
    #         return b''
    #
    # def find_successor(self, id: int) -> 'ChordNodeReference':
    #     response = self._send_data(FIND_SUCCESSOR, str(id)).decode().split(',')
    #     return ChordNodeReference(int(response[0]), response[1], self.port)
    #
    # def find_predecessor(self, id: int) -> 'ChordNodeReference':
    #     response = self._send_data(FIND_PREDECESSOR, str(id)).decode().split(',')
    #     return ChordNodeReference(int(response[0]), response[1], self.port)
    #
    # @property
    # def succ(self) -> 'ChordNodeReference':
    #     response = self._send_data(GET_SUCCESSOR).decode().split(',')
    #     return ChordNodeReference(int(response[0]), response[1], self.port)
    #
    # @property
    # def pred(self) -> 'ChordNodeReference':
    #     response = self._send_data(GET_PREDECESSOR).decode().split(',')
    #     return ChordNodeReference(int(response[0]), response[1], self.port)
    #
    # def notify(self, node: 'ChordNodeReference'):
    #     self._send_data(NOTIFY, f'{node.id},{node.ip}')
    #
    # def check_predecessor(self):
    #     self._send_data(CHECK_PREDECESSOR)
    #
    # def closest_preceding_finger(self, id: int) -> 'ChordNodeReference':
    #     response = self._send_data(CLOSEST_PRECEDING_FINGER, str(id)).decode().split(',')
    #     return ChordNodeReference(int(response[0]), response[1], self.port)

    def __str__(self) -> str:
        return f'{self.id},{self.ip},{self.port}'

    def __repr__(self) -> str:
        return str(self)
