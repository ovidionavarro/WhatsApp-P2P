import socket
import threading


class Client():
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect_to(self, ip, port):
        # Conectar al servidor
        try:
            client_socket.connect((ip, port))
            print("[+] Conectado al servidor.")
        except e:
            print('[-] No se pudo conectar :-(')
            print(e)


# Función para manejar la recepción de mensajes del servidor
def receive_messages(client_socket):
    while True:
        try:
            # Recibir mensaje del servidor
            message = client_socket.recv(1024).decode()
            if message:
                print(message)
        except:
            # Si hay algún error, desconectar al cliente
            print("[-] Error al recibir mensaje del servidor.")
            client_socket.close()
            break


# Dirección y puerto del servidor
SERVER_HOST = '127.0.0.1'
SERVER_PORT = 5555

# Nombre de usuario del cliente
username = input("Ingrese su nombre de usuario: ")

# Crear socket del cliente
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    # Conectar al servidor
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    print("[+] Conectado al servidor.")

    # Enviar nombre de usuario al servidor
    client_socket.send(username.encode())

    # Iniciar hilo para recibir mensajes del servidor
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()

    # Loop para enviar mensajes al servidor
    while True:
        message = input()
        if message.lower() == 'exit':
            # Si el usuario escribe 'exit', salir del bucle y cerrar la conexión
            break
        else:
            # Enviar mensaje al servidor
            client_socket.send(message.encode())
except Exception as e:
    print(f"[-] Error al conectar al servidor: {e}")
finally:
    # Cerrar conexión al salir del bucle
    client_socket.close()
