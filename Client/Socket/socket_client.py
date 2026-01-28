import socket
import time
#build function for ongoing conversation using while true loop
HOST = '127.0.0.1'
PORT = 7567

socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((HOST, PORT))
header = input('input header')
msg = input('input msg')
message = header + ' ' + msg
print(message)
socket.send(message.encode('utf-8'))
response = (socket.recv(1024)).decode('utf-8')
print(response) 