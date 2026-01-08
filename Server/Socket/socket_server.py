import socket
import time

HOST = '100.74.19.74'
PORT = 3747

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

while True:
    communication_socket, address = server.accept()
    print(f"Connected to {address}")
    message = communication_socket.recv(1024).decode('utf-8')
    print(f"Messgae from client is: {message}")
    communication_socket.send(f"Got your message! PS: You gay".encode('utf-8'))
    communication_socket.close()
    print(f"Connection with {address} ended!")