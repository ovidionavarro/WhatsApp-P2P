import socket
import threading
import sys
import time
import logging
from chord_node_reference import ChordNodeReference
from codes import *
from utils import getShaRepr
import pickle

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
        self.leader = True
        self.first = True
        self.chord = [self.ref]

        threading.Thread(target=self.escuchar_broadcast, daemon=True).start()
        threading.Thread(target=self.start_server, daemon=True).start()
        threading.Thread(target=self.enviar_broadcast, args=("JOIN", "255.255.255.255"), daemon=True).start()
        threading.Thread(target=self.update_chord, daemon=True).start()
        threading.Thread(target=self.print_status, daemon=True).start()

        # logging.info(f"Node initialized with ID {self.id} and IP {self.ip}")

    def finger_status(self):
        string = ''
        for i in range(self.m):
            string += f'[{(self.id + 2 ** i) % 2 ** self.m}:{self.finger[i].id}] '
        return string

    def print_status(self):
        while True:
            string = f'pred: {self.pred} *=*=* succ: {self.succ}'
            if self.leader and self.succ.id > self.id:
                self.leader = False
            if self.first and self.pred.id < self.id:
                self.first = False
            if not self.leader and self.succ.id < self.id:
                self.leader = True
            if not self.first and self.pred.id > self.id:
                self.first = True
            logging.info(string)
            if self.leader:
                logging.info(f"Lider")
            if self.first:
                logging.info("Primero")
            # print finger
            # print(self.finger_status())
            time.sleep(5)

    def enviar_broadcast(self, mensaje, direccion_broadcast):
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

    def escuchar_broadcast(self):
        # Crear un socket UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Permitir la reutilización de la dirección
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Enlazar el socket a todas las interfaces de red y al puerto especificado
        sock.bind(("", 8001))

        while True:
            logging.info(f"Esperando mensajes broadcast en el puerto {8001}...")
            # Recibir el mensaje y la dirección de donde proviene
            data, addr = sock.recvfrom(1024)
            if data.decode() == "JOIN" and addr[0] != self.ip and self.leader:
                logging.info("Otro nodo quiere unirse")
                # Enviar mensage al nodo que quiere entrar notificandole que ha sido aceptado, y los datos de el chord
                new_node = ChordNodeReference(getShaRepr(addr[0]), addr[0])
                self.chord.append(new_node)
                for i in self.chord:
                    if i == self.ref:
                        continue
                    else:
                        self.accept_node(i.ip)

            else:
                logging.info(f"Mensaje recibido de {addr}: {data.decode()}")

    def accept_node(self, ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 8001))

        data = pickle.dumps(['ACCEPTED', self.chord])
        sock.sendall(data)

    def update_chord(self):
        while True:

            chord = sorted(self.chord)
            logging.info(f"List Chord >>>: {chord}")

            for i in chord:
                logging.info(f" Chord elements: {i}")

            index = chord.index(self.ref)
            if index == 0:
                self.first = True
                self.pred = chord[- 1]

            if index == len(chord) - 1:
                self.leader = True
            try:
                self.succ = chord[index + 1]
            except:
                self.succ = chord[0]
            self.chord = chord
            logging.info(f"chord status: {self.chord}")
            time.sleep(5)

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.ip, self.port))
            logging.info(f"Bind en {self.ip}, {self.port}")
            s.listen(10)

            while True:
                conn, addr = s.accept()
                logging.info(f'New connection from {addr}')
                data = conn.recv(1024)
                data = pickle.loads(data)
                logging.info(f"Paquete Recibido de {addr}: {data}")
                if data[0] == "ACCEPTED":
                    logging.info(f"{type(data[1])}")

                    self.chord = data[1]
                    logging.info(f"My Chord: {self.chord}")

                # if int(data[0]) == JOIN:
                #     if self.pred.id == self.id:
                #         #update predecesor and succesor
                #         self.succ = ChordNodeReference(getShaRepr(str(addr[0])), addr[0], 8001)
                #         self.pred = ChordNodeReference(getShaRepr(str(addr[0])), addr[0], 8001)
                #         data = f'{self.ip},{self.port}'.encode()
                #         print(f'Recibido del cliente: {data}')
                #         conn.sendto(data, addr)
                #         #update finger table
                #         for i in range(self.m):
                #             if(self._inbetween(self.id+(2**i)%2**self.m,self.id,self.succ.id)):
                #                 self.finger[i] = self.succ

                time.sleep(1)

    def join(self, ip, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((ip, 8001))
        sock.sendall(f'{JOIN},{ip}'.encode('utf-8'))
        data = sock.recv(1024).decode().split(',')
        print(data)
        if len(data) == 2:
            ref_ip, ref_port = data
            self.pred = ChordNodeReference(getShaRepr(ref_ip), ref_ip, int(ref_port))
            self.succ = self.pred
            # update finger table
            for i in range(self.m):
                if (self._inbetween(self.id + (2 ** i) % 2 ** self.m, self.id, self.succ.id)):
                    self.finger[i] = self.succ

    def update_succ(self, node: ChordNodeReference):
        self.succ = node

    def _inbetween(self, k: int, start: int, end: int) -> bool:
        if start < end:
            return start < k <= end
        else:  # The interval wraps around 0
            return start < k or k <= end


if __name__ == "__main__":
    ip = socket.gethostbyname(socket.gethostname())
    logging.info(f'My IP: {ip}')
    logging.info(f'My ID: {getShaRepr(ip)}')
    id = getShaRepr(ip)
    node = ChordNode(id, ip, 8001, M)

    if len(sys.argv) >= 2:
        other_ip = sys.argv[1]
        id = getShaRepr(other_ip)
        node.join(other_ip, node.port)

    while True:
        pass
