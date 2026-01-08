import socket
import time

HOST = '100.95.128.87'
PORT = 3747

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
message = input()
socket.send(message.encode('utf-8'))
time.sleep(1)
response = (socket.recv(1024)).decode('utf-8')
print(response)