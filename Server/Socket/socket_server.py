import socket
import threading
from _thread import start_new_thread
from libserver import *
lock = threading.Lock()


def process_request(communication_socket):
    while True:
        data = ''
        data = (communication_socket.recv(2048)).decode('utf-8')
        if not data:
            print('bye')
            lock.release()
            break
        header, msg = data_to_msg(str(data))
        communication_socket.send(f'Recieved {msg}'.encode('utf-8'))
        communication_socket.send(f'Transmitting {msg} to {header}'.encode('utf-8'))
    communication_socket.close()


def server_main():
    HOST = ''
    PORT = 3747
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen(5)
    while True:
        communication_socket, address = s.accept()
        lock.acquire()
        print(f'Connected to {address[0]}:{address[1]}')
        start_new_thread(process_request, (communication_socket,))


server_main()