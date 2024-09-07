import socket
import threading
import sys
import time
import logging
from chord_node_reference import ChordNodeReference
from codes import *
from utils import getShaRepr
from db import DB

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
        self.pred_2 = None
        self.m = m  # Number of bits in the hash/key space
        self.finger = [self.ref] * self.m  # Finger table
        self.next = 0  # Finger table index to fix next
        self.data = {}  # Dictionary to store key-value pairs
        self.leader = True

       # threading.Thread(target=self.broadcast_listening, daemon=True).start()
        threading.Thread(target=self.listening_tcp, daemon=True).start()
        # Start background threads for stabilization, fixing fingers, and checking predecessor
        threading.Thread(target=self.stabilize, daemon=True).start()  # Start stabilize thread
        threading.Thread(target=self.fix_fingers, daemon=True).start()  # Start fix fingers thread
        threading.Thread(target=self.check_predecessor, daemon=True).start()  # Start check predecessor thread
        threading.Thread(target=self.start_server, daemon=True).start()  # Start server thread
        self.send_broadcast("JOIN")

    def send_tcp(self, ip, port=8001):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((ip, port))
            s.sendall(f'{UPDATE_PRED}'.encode('utf-8'))
            s.close()

    def listening_tcp(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port + 1))
            s.listen(10)
            while True:
                conn, addr = s.accept()
                data = conn.recv(1024).decode().split(',')
                option = int(data[0])
                logging.info(f"option: {option}")
                if option == ACCEPTED:
                    cnr = ChordNodeReference(addr[0])
                    self.join(cnr)
                    logging.info("loginnnnnnnn")
                    conn.close()

    def broadcast_listening(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', 8001))

        while True:
            logging.info("Esperando broadcast....")
            data, addr = sock.recvfrom(1024)
            data = data.decode().split(',')
            logging.info(f"Mensaje: {data[0]} de: {addr[0]}")
            if data[0] == "JOIN" and addr[0] != self.ip and self.leader:
                self.accept_node(addr[0])
            if data[0] == "ASK_SUCC" and self.succ.id == int(data[1]) and self.ip != addr[0]:
                logging.info("Actualizando Succ por no existe pred2 del remitente")
                self.succ = ChordNodeReference(addr[0])
                self.succ.update_pred(self.ref)
                logging.info("Mensaje envidao 111111111111111111111")

    def send_broadcast(self, mensaje, direccion_broadcast="255.255.255.255"):

        # Crear un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Permitir la reutilización de la dirección
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Habilitar la opción para enviar mensajes broadcast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Enviar el mensaje broadcast
        sock.sendto(mensaje.encode(), (direccion_broadcast, 8001))
        logging.info(f"Mensaje broadcast enviado: {mensaje}")

        # Cerrar el socket
        sock.close()

    def accept_node(self, ip, port=8001):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(5.0)
            s.connect((ip, port + 1))
            s.sendall(f'{ACCEPTED}'.encode('utf-8'))
            s.close()

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

            logging.info(f"successor : {self.succ} predecessor : {self.pred} ")

            if (self.id >= self.succ.id):
                self.leader = True
                logging.info(f"leader change {self.id} >= {self.succ.id}")
            else:
                self.leader = False

            fing = ''
            for i in range(0, m):
                fing += f"[{self.finger[i].id}]"
            logging.info(f"finger:{fing}")
            time.sleep(5)

    # Notify method to inform the node about another node
    def notify(self, node: 'ChordNodeReference'):
        if node.id == self.id:
            pass
        if not self.pred or self._inbetween(node.id, self.pred.id, self.id):
            self.pred = node
            self.pred_2 = self.pred.pred

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
            time.sleep(5)

    # Check predecessor method to periodically verify if the predecessor is alive
    def check_predecessor(self):
        while True:
            try:
                if self.pred:
                    resp = self.pred.check_predecessor()
                    logging.info(f" respuesta de pred: {resp}")
                    if resp == b'':
                        if self.id == self.pred_2.id:
                            self.pred = None
                            self.succ = self.ref
                        else:
                            resp1 = self.pred_2.check_predecessor()
                            logging.info(f" respuesta de pred: {resp}")
                            if resp1 == b'':
                                ##tirar boadcast
                                logging.info("No se encontro pred2 Preguntando broadcast!!!!!!!!!")
                                self.send_broadcast(f"ASK_SUCC,{self.pred_2.id}")

                            else:
                                # actualizar mi predecesor y su sucesor
                                logging.info(f"1111111111 cambiando predecesor {self.pred.id} -> {self.pred_2.id}")
                                self.pred = self.pred_2
                                self.pred_2.update_succ(self.ref)
                                self.pred_2 = self.pred.pred
                    self.pred_2 = self.pred.pred
                    logging.info(f"pred_pred :{self.pred_2.id}")
            except Exception as e:
                self.pred = None

            time.sleep(5)

    def update_succ(self, node: 'ChordNodeReference'):
        logging.info(f"22222222222222 actualizando mi succ {self.succ.id} a {node.id}")
        self.succ = node

    ########DATABASE

    def _get_contacts(self,name,number,endpoint):
        resp=DB.get_contacts(name,number,endpoint)
        print('22222222222222222',resp)
        return resp
    def get_contacts(self, id, name, numb,endpoint):
        logging.info(f"Buscando {endpoint} de {name}")
        node = self.find_succ(id)
        return node.get_contacts(f"{id},{name},{numb},{endpoint}").decode()

    def sing_up(self, id: int, name: str, number: str):
        logging.info(f'{id} del nuevo user9999999999999999999999999')
        node = self.find_succ(id)
        return node.sing_up(f'{id},{name},{number}')  # poner .decode()

    # Store key method to store a key-value pair and replicate to the successor
    def _sing_up(self, name, number):
        resp = DB.register(name, number)
        print("eeeeeeeeeeeeeeeeeeeeeeeeee", resp)
        return resp

    def sing_in(self, id: int, name: str, number: str):
        logging.info(f' buscando a {id} name ')
        node = self.find_succ(id)
        return node.sing_in(f'{id},{name},{number}').decode()

    def _sing_in(self, name, number):
        resp = DB.sing_in(name, number)
        print("eeeeeeeeeeeeeeeeeeeeeeeeee", resp)
        return resp

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
                elif option == UPDATE_SUCC:
                    id = int(data[1])
                    ip = data[2]
                    self.update_succ(ChordNodeReference(ip, self.port))

                elif option == BASE:
                    id = int(data[1])
                    ip = data[2]
                    self.case_basic(ChordNodeReference(ip, self.port))
                elif option == CHECK_PREDECESSOR:
                    conn.sendall("True".encode())
                    conn.close()
                    continue

                elif option == UPDATE_PRED:
                    logging.info("Updating Pred!!!!!!!!!!!!!!!")
                    id = int(data[1])
                    ip = data[2]
                    self.pred = ChordNodeReference(ip, self.port)

                elif option == CLOSEST_PRECEDING_FINGER:
                    id = int(data[1])
                    data_resp = self.closest_preceding_finger(id)

                ###########DATABASE
                elif option == SING_UP:
                    name = data[2]
                    number = data[3]
                    data_resp = self._sing_up(name, number)
                    if (data_resp == 'True'):
                        conn.sendall("True".encode())
                    else:
                        conn.sendall("False".encode())
                    conn.close()
                    continue
                elif option == SING_IN:
                    name = data[2]
                    number = data[3]
                    data_resp = self._sing_in(name, number)
                    logging.info(f'entrando a sing in con data {data_resp}')
                    if (data_resp == 'True'):
                        conn.sendall("True".encode())
                    else:
                        conn.sendall("False".encode())
                    conn.close()
                    continue

                elif option == GET_CONTACTS:
                    name = data[2]
                    number = data[3]
                    endpoint=data[4]
                    data_resp = self._get_contacts(name, number,endpoint)


                    conn.sendall(data_resp.encode())

                    conn.close()
                    continue

                # elif option == STORE_KEY:
                #     key, value = data[1], data[2]
                #     self.data[key] = value
                # elif option == RETRIEVE_KEY:
                #     key = data[1]
                #     data_resp = self.data.get(key, '')

                if data_resp:
                    response = f'{data_resp.id},{data_resp.ip}'.encode()
                    conn.sendall(response)
                conn.close()

    # def store_key(self, key: str, value: str):
    # key_hash = getShaRepr(key)
    # node = self.find_succ(key_hash)
    # node.store_key(key, value)
    # self.data[key] = value  # Store in the current node
    # self.succ.store_key(key, value)  # Replicate to the successor
    # Retrieve key method to get a value for a given key
    # def retrieve_key(self, key: str) -> str:
    # key_hash = getShaRepr(key)
    # node = self.find_succ(key_hash)
    # return node.retrieve_key(key)
