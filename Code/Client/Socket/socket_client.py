import socket

server_ip = '127.0.0.1'
server_port = 7567

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    while True:
        msg = input('Enter Message')
        client.send(msg.encode('utf-8'))
        response = client.recv(2048)
        response = response.decode('utf-8')
        if response.lower() == 'closed':
            print('Connection closed!')
            break
        print(response)
    client.close()

run_client()