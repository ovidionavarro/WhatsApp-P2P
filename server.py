import socket
import threading


class ServerWsp():
    def __init__(self, SERVER_HOST, SERVER_PORT):
        self.host = SERVER_HOST
        self.port = SERVER_PORT
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = []
        self.socket.bind((SERVER_HOST, SERVER_PORT))
        self.socket.listen(10)

    # Función para manejar las conexiones entrantes
    def accept_connections(self):
        while True:
            client_socket, client_address = server.accept()
            clients.append(client_socket)
            client_handler = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_handler.start()
            # Agregar el hilo recién creado a una lista de hilos
            threads.append(client_handler)

    # Función para manejar las conexiones de los clientes
    def handle_client(self, client_socket, client_address):
        print(f"[+] Conexión establecida con {client_address}")

        while True:
            try:
                # Recibir mensaje del cliente
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"Mensaje de {client_address}: {message}")

                    # Reenviar el mensaje a todos los clientes conectados
                    for c in clients:
                        if c != client_socket:
                            c.send(message.encode())
                else:
                    # Si el mensaje está vacío, el cliente se desconectó
                    print(f"[-] Cliente {client_address} desconectado.")
                    clients.remove(client_socket)
                    client_socket.close()
                    break
            except:
                # Si hay algún error, desconectar al cliente
                print(f"[-] Cliente {client_address} desconectado.")
                clients.remove(client_socket)
                client_socket.close()
                break


# Dirección y puerto del servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# Crear socket del servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((SERVER_HOST, SERVER_PORT))
server.listen(5)

print("[*] Esperando conexiones entrantes...")

# Lista para almacenar los sockets de los clientes
clients = []

# Lista para almacenar los hilos
threads = []

# Iniciar hilo para aceptar conexiones entrantes
accept_thread = threading.Thread(target=accept_connections)
accept_thread.start()

accept_thread.join()
# Esperar a que todos los hilos se completen antes de terminar el programa
for thread in threads:
    thread.join()
