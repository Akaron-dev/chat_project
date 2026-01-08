import socket
import time
import threading

HOST = '127.0.0.1'
PORT = 3747

def process_request(communication_socket, address, communication_socket_backup):
    threading.Thread(target=preprocess_request, args=[communication_socket_backup]).run()
    print(f"Connected to {address}")
    message = communication_socket.recv(1024).decode('utf-8')
    print(f"Messgae from client is: {message}")
    communication_socket.send(f"Got your message! PS: You gay".encode('utf-8'))
    communication_socket.close()
    print(f"Connection with {address} ended!")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()
communication_socket = ()
communication_socket_backup = communication_socket
def preprocess_request(communication_socket_backup):
    while True:
        communication_socket_backup = communication_socket
        communication_socket, address = server.accept()
        if communication_socket != communication_socket_backup:
            name = threading.active_count()
            threading.Thread(target=process_request, args=[communication_socket, address, communication_socket_backup]).run()


