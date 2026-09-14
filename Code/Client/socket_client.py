import socket
import time
import json
import threading

server_ip = '127.0.0.1'
server_port = 7567

state = {
    "uid": 0,
    "sessionkey": 0,
    "pending_auth": False
}

def message(msg_type, receipient_id, uid, msg_content, sessionkey):
    data = {
        "msg_type": msg_type,
        "receipient_id": receipient_id,
        "uid": uid,
        "msg_content": msg_content,
        "timestamp": int(time.time()),
        "sessionkey": sessionkey
    }
    return json.dumps(data)

def receive_loop(client):
    while True:
        try:
            response = client.recv(2048).decode('utf-8')
            if not response or response.lower() == 'closed':
                print('\nConnection closed!')
                break

            if state["pending_auth"]:
                raw_val = response.split(' | ')[0].strip()
                if raw_val.isdigit():
                    val = int(raw_val)
                    if state["uid"] == 0:
                        state["uid"] = val
                    else:
                        state["sessionkey"] = val
                state["pending_auth"] = False

            print(f'\n[Server/Message]: {response}')
        except Exception:
            break

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))

    threading.Thread(target=receive_loop, args=(client,), daemon=True).start()

    while True:
        msg_type = input('Input type code (0 - Auth, 100 - Server, 200 - Message): ')

        if msg_type == '0':
            state["pending_auth"] = True
            if state["uid"] == 0:
                state["uid"] = int(input('Input UID (0 to create account): ') or 0)
            password = input('Input password: ')
            msg = message(msg_type, 0, state["uid"], password, 0)

        elif msg_type == '200':
            receipient_id = int(input('Recipient ID: ') or 0)
            msg_content = input('Message: ')
            msg = message(msg_type, receipient_id, state["uid"], msg_content, state["sessionkey"])

        else:
            msg_content = input('Input message/command: ')
            msg = message(msg_type, 0, state["uid"], msg_content, state["sessionkey"])

        client.send(msg.encode('utf-8'))
        time.sleep(0.3)


run_client()