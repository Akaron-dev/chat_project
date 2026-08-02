import socket
import threading

def run_server():
    host_ip = '127.0.0.1'
    host_port = 7567
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host_ip, host_port))
        server.listen()

        while True:
            client_socket, client_address = server.accept()
            thread = threading.Thread(target = handle_client, args = (client_socket, client_address,))
            thread.start()
    except Exception as e:
        print(f'Error: {e}')
    finally:
        server.close()
   

def handle_client(client_socket, client_address):
    try:
        while True:
            request = client_socket.recv(2048).decode('utf-8')
            if request.lower() == 'close':
                client_socket.send('Closed'.encode('utf-8'))
                break
            print(f'Recieved: {request}')
            response = 'Accepted'
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f'Error when handling {e}')
    finally:
        client_socket.close()
        



run_server() 