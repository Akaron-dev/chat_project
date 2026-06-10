import socket
import threading
import sys
import libserver
import _thread

class server:
    
    def connect(communication_socket):
        lock = threading.Lock()
        while True:
            c = communication_socket
            data = ''
            data  = c.recv(4096)
            header, msg = libserver.data_to_msg(data)
            c.send((f'Recieved message {msg}').encode('utf-8'))
            if header == 'BREAK':
                lock.release()
                break
            
    def main():
        lock = threading.Lock()
        host = ''
        port = 7567
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(5)
        while True:
            communication_socket, address = s.accept()
            lock.acquire()
            print(f'connected to {address}')
            _thread.start_new_thread(server.connect(communication_socket))

if __name__ == '__main__':
    server.main()