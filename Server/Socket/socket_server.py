import socket
import threading
import sys
import libserver

class server:
    def connect(communication_socket):
        while True:
            c = communication_socket
            data = ''
            data  = c.recv(4096) #find a way for fixed length header to tell the length of the message
            header, msg = libserver.data_to_msg(data)
            c.send((f'Recieved message {msg}').encode('utf-8'))
            if header == 'BREAK':
                sys.exit()
            
    def main():
        host = ''
        port = 7567
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.listen(5)
        while True:
            communication_socket, address = s.accept()
            print(f'connected to {address}')
            t = threading.Thread(server.connect(communication_socket))
            t.start()


server.main()