import socket
import threading
import json
import account_handling

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
            raw_bytes = client_socket.recv(2048)
            if not raw_bytes:
                break
            json_string = raw_bytes.decode('utf-8')
            data = json.loads(json_string)
            msg_type = data.get('msg_type')
            recipient_id = data.get('recipient_id')
            uid = data.get('uid')
            msg_content = data.get('msg_content')
            timestamp = data.get('timestamp')
            sessionkey = data.get('sessionkey')
            print(data)
            if msg_type == '0':
                if uid == 0:
                    new_uid = account_handling.create_account(msg_content)
                    response = f'Your user id is: {new_uid}'
                    client_socket.send(response.encode('utf-8'))
                else:
                    message, sessionkey = account_handling.login(uid, msg_content)
                    response = message + ' ' + str(sessionkey)
                    client_socket.send(response.encode('utf-8'))
            if msg_type == '100':
                if msg_content.lower() == 'close':
                    response = 'Connection closed'
                    client_socket.send(response.encode('utf-8'))
                    break
            # print(msg_type, recipient_id, uid, msg_content, timestamp, sessionkey)
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f'Error when handling {e}')
    finally:
        client_socket.close()
        



run_server() 