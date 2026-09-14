import socket
import threading
import json
import account_handling
import sqlite3

active_clients = {}

def run_server():
    host_ip = '127.0.0.1'
    host_port = 7567
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((host_ip, host_port))
        server.listen()

        while True:
            client_socket, client_address = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            thread.start()
    except Exception as e:
        print(f'Error: {e}')
    finally:
        server.close()

def handle_client(client_socket, client_address):
    current_uid = None
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

            response = "Invalid request type"

            if msg_type == 0:
                if uid == 0:
                    new_uid = account_handling.create_account(msg_content)
                    response = str(new_uid)
                else:
                    sessionkey = account_handling.login(uid, msg_content)
                    response = str(sessionkey)
                    if sessionkey != 0:
                        current_uid = uid
                        active_clients[uid] = client_socket
                        
                        connection = sqlite3.connect('data.db')
                        cursor = connection.cursor()
                        cursor.execute('SELECT sender_id, msg_content, timestamp FROM messages WHERE receipient_id = ?', (uid,))
                        unread = cursor.fetchall()
                        if unread:
                            response += f" | Unread messages: {unread}"
                            cursor.execute('DELETE FROM messages WHERE receipient_id = ?', (uid,))
                            connection.commit()
                        connection.close()

            elif msg_type == 100:
                if msg_content.lower() == 'close':
                    response = 'closed'
                    client_socket.send(response.encode('utf-8'))
                    break

            elif msg_type == 200:
                if account_handling.sessionkey_verification(uid, sessionkey):
                    current_uid = uid
                    active_clients[uid] = client_socket
                    
                    connection = sqlite3.connect('data.db')
                    cursor = connection.cursor()
                    cursor.execute('INSERT INTO messages VALUES (?, ?, ?, ?, ?)',
                                    (msg_type, receipient_id, uid, msg_content, timestamp)
                                   )
                    connection.commit()
                    connection.close()
                    
                    if receipient_id in active_clients:
                        live_payload = f"\n[Message from {uid}]: {msg_content}\n"
                        try:
                            active_clients[receipient_id].send(live_payload.encode('utf-8'))
                        except Exception:
                            active_clients.pop(receipient_id, None)

                    response = f'Message to {receipient_id} sent successfully'
                else:
                    response = 'Not authorized, login required'

            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f'Error when handling {e}')
    finally:
        if current_uid and current_uid in active_clients:
            del active_clients[current_uid]
        client_socket.close()

run_server()