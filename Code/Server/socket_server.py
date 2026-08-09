import socket
import threading
import json
import account_handling
import sqlite3

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
            msg_type = int(data.get('msg_type'))
            receipient_id = int(data.get('receipient_id'))
            uid = int(data.get('uid'))
            msg_content = data.get('msg_content')
            timestamp = int(data.get('timestamp'))
            sessionkey = int(data.get('sessionkey'))
            print(data)
            if msg_type == 0: # login related
                if uid == 0:
                    new_uid = account_handling.create_account(msg_content)
                    response = new_uid
                    client_socket.send(response.encode('utf-8'))
                else:
                    sessionkey = account_handling.login(uid, msg_content)
                    response = str(sessionkey)
                    client_socket.send(response.encode('utf-8'))
            if msg_type == 100: # status to server
                if msg_content.lower() == 'close':
                    response = 'Connection closed'
                    client_socket.send(response.encode('utf-8'))
                    break
            if msg_type == 200: # Message to another user
                receipient_id = int(receipient_id)
                if account_handling.sessionkey_verification(uid, sessionkey) == True:
                    connection = sqlite3.connect('data.db')
                    cursor = connection.cursor()
                    cursor.execute('INSERT INTO messages VALUES (?, ?, ?, ?, ?)',
                                    (msg_type, receipient_id, uid, msg_content, timestamp)
                                   )
                    connection.commit()
                    connection.close()
                    response = f'Message to {receipient_id} sent successfully'
                else:
                    response = 'Not authorized, login required'
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f'Error when handling {e}')
    finally:
        client_socket.close()
        



run_server() 