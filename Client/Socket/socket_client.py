import socket
import time

HOST = '127.0.0.1'
PORT = 3747

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
message = f'timfr$$$$$ {input()}'
socket.send(message.encode('utf-8'))
time.sleep(1)
response = (socket.recv(1024)).decode('utf-8')
print(response)