import socket
import time

HOST = '100.74.19.74'
PORT = 3747

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
socket.send("Love you man!".encode('utf-8'))
time.sleep(1)
response = (socket.recv(1024)).decode('utf-8')
print(response)