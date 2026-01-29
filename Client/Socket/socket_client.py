import socket
import time
#build function for ongoing conversation using while true loop
host = '127.0.0.1'
port = 7567

class client:
    host = '127.0.0.1'
    port = 7567
    def connect(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        while True:
            header = input('input header')
            msg = input('input msg')
            message = header + ' ' + msg
            print(message)
            message = message.encode('utf-8')
            print(len(message))
            s.send(message)
            response = (s.recv(1024)).decode('utf-8')
            print(response)

if __name__ == '__main__':
    client.connect(host, port)