import socket
import time
import json

server_ip = '127.0.0.1'
server_port = 7567

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

def run_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((server_ip, server_port))
    receipient_id = 0
    uid = 828190126
    sessionkey = 358801184
    while True:
        msg = message(input('input type code: 0 - Login, 100 - server, 200 - message'), receipient_id, uid, input('input message'), sessionkey)
        client.send(msg.encode('utf-8'))
        response = client.recv(2048)
        response = response.decode('utf-8')
        if response.lower() == 'closed':
            print('Connection closed!')
            break
        print(response)
    client.close()

run_client()

