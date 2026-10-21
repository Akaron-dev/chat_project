import socket
import threading
import json
import time
import os
import sqlite3
import ast
import re

SERVER_IP = '127.0.0.1'
SERVER_PORT = 7567

VALID_INVITE_CODES = None # When set to None, any invite code is valid. Otherwise, only the codes in this list are valid.

state = {
    "uid": None,
    "sessionkey": None,
    "latest_created_uid": None
}

client_socket = None
is_running = False
recv_thread = None

ui_callbacks = {
    "get_active_uid": lambda: None,
    "on_message": lambda msg: None,
    "on_new_chat": lambda: None
}

def register_ui_callbacks(get_active_uid=None, on_message=None, on_new_chat=None): # Registers UI callback functions for the client to call when certain events occur. These callbacks are used to update the user interface in response to incoming messages or new chats.
    if get_active_uid:
        ui_callbacks["get_active_uid"] = get_active_uid
    if on_message:
        ui_callbacks["on_message"] = on_message
    if on_new_chat:
        ui_callbacks["on_new_chat"] = on_new_chat

def get_db_path(own_uid): # Returns the path to the local SQLite database file for this user. The database file is named 'client_<uid>.db'.
    return f"client_{own_uid}.db"

def init_local_db(own_uid): # Initializes the SQLite tables for this user. Creates 'local_messages' and 'contacts' tables if they don't exist.
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS local_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_uid TEXT NOT NULL,
                sender_uid TEXT NOT NULL,
                msg_content TEXT NOT NULL,
                timestamp REAL NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_chat 
            ON local_messages (chat_uid, timestamp)
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                uid TEXT PRIMARY KEY,
                nickname TEXT NOT NULL
            )
        ''')
        conn.commit()

def save_local_message(own_uid, chat_uid, sender_uid, msg_content, timestamp=None): # Saves a message to the local SQLite database for this user. Returns a tuple of (msg_content, sender_uid, timestamp).
    if timestamp is None:
        timestamp = time.time()
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO local_messages (chat_uid, sender_uid, msg_content, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (str(chat_uid), str(sender_uid), str(msg_content), float(timestamp)))
        conn.commit()
    return (str(msg_content), str(sender_uid), float(timestamp))

def ensure_contact_exists(own_uid, contact_uid, default_nickname=None): # Automatically adds a contact if we receive a message from someone new.
    if not default_nickname:
        default_nickname = f"User {contact_uid}"
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT uid FROM contacts WHERE uid = ?', (str(contact_uid),))
        if not cursor.fetchone():
            cursor.execute('INSERT INTO contacts (uid, nickname) VALUES (?, ?)',
                           (str(contact_uid), default_nickname))
            conn.commit()
            return True
    return False

SESSION_FILE = "session.json"

def save_session(uid, password): # Saves the current session to a local file for auto-login on next startup.
    try:
        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump({"uid": str(uid), "password": str(password)}, f)
    except Exception:
        pass

def clear_session(): # Deletes the session file to log out the user.
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
        except Exception:
            pass

def is_loggedin(): # Called by Interface.py on startup. Returns (1, uid, pwd) or (0, '', '').
    if os.path.exists(SESSION_FILE):
        try:
            with open(SESSION_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                uid = data.get("uid", "")
                pwd = data.get("password", "")
                if uid and pwd:
                    return (1, str(uid), str(pwd))
        except Exception:
            pass
    return (0, "", "")

def receive_loop(): # Runs in a separate thread to receive messages from the server
    global is_running, client_socket

    pattern = re.compile(r'\[Message from (\d+)\]:\s*(.*?)(?=(?:\n\[Message from|\Z))', re.DOTALL)

    while is_running and client_socket:
        try:
            raw_bytes = client_socket.recv(4096)
            if not raw_bytes:
                break
            raw_text = raw_bytes.decode('utf-8')

            # Parse live chat payloads: [Message from <uid>]: <content>
            matches = pattern.findall(raw_text)
            for sender_uid, content in matches:
                sender_uid = sender_uid.strip()
                content = content.strip()
                now = time.time()

                # If this sender is new, add them to contacts and refresh UI sidebar
                if ensure_contact_exists(state["uid"], sender_uid):
                    if ui_callbacks["on_new_chat"]:
                        ui_callbacks["on_new_chat"]()

                # Save incoming message to local SQLite
                msg_tuple = save_local_message(state["uid"], sender_uid, sender_uid, content, now)

                # If user is currently looking at this chat, update UI immediately
                active_uid = ui_callbacks["get_active_uid"]()
                if active_uid and str(active_uid) == str(sender_uid):
                    if ui_callbacks["on_message"]:
                        ui_callbacks["on_message"](msg_tuple)

            if "closed" in raw_text.lower():
                break

        except (OSError, ConnectionResetError):
            break
        except Exception as e:
            print(f"Error in receive_loop: {e}")
            break

    is_running = False

def check_login(own_uid, own_password): # Called by Interface.check_login_if(own_uid, own_password). Returns 1 on success, 0 on failure.
    global client_socket, is_running, recv_thread

    try:
        uid_int = int(str(own_uid).strip())
    except ValueError:
        return 0

    logout()  # Clean up any leftover connection

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((SERVER_IP, SERVER_PORT))

        auth_payload = {
            "msg_type": 0,
            "receipient_id": 0,
            "uid": uid_int,
            "msg_content": own_password,
            "timestamp": int(time.time()),
            "sessionkey": 0
        }
        sock.sendall(json.dumps(auth_payload).encode('utf-8'))
        response = sock.recv(4096).decode('utf-8').strip()

        # Parse response: "sessionkey" or "sessionkey | Unread messages: [...]"
        unread_messages = []
        if " | Unread messages: " in response:
            session_str, unread_str = response.split(" | Unread messages: ", 1)
            sessionkey = int(session_str.strip())
            try:
                unread_messages = ast.literal_eval(unread_str.strip())
            except Exception:
                unread_messages = []
        elif response.isdigit():
            sessionkey = int(response)
        else:
            sock.close()
            return 0

        if sessionkey == 0:
            sock.close()
            return 0

        # Login Succeeded
        client_socket = sock
        state["uid"] = str(uid_int)
        state["sessionkey"] = sessionkey

        # Prepare local database
        init_local_db(state["uid"])

        # Store any offline messages delivered by server upon login
        for sender_id, msg_content, timestamp in unread_messages:
            s_uid = str(sender_id)
            ensure_contact_exists(state["uid"], s_uid)
            save_local_message(state["uid"], s_uid, s_uid, msg_content, timestamp)

        save_session(state["uid"], own_password)

        # Start independent background receiver thread
        is_running = True
        recv_thread = threading.Thread(target=receive_loop, daemon=True)
        recv_thread.start()

        return 1

    except Exception as e:
        print(f"Login connection error: {e}")
        return 0

def sign_up(new_password, invite_code): # Called by Interface.sign_up_if(new_password, invite_code). Returns 1 on success, 2 on invalid invite code.
    if VALID_INVITE_CODES is not None:
        if invite_code not in VALID_INVITE_CODES:
            return 2

    try:
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_sock.connect((SERVER_IP, SERVER_PORT))

        signup_payload = {
            "msg_type": 0,
            "receipient_id": 0,
            "uid": 0,
            "msg_content": new_password,
            "timestamp": int(time.time()),
            "sessionkey": 0
        }
        temp_sock.sendall(json.dumps(signup_payload).encode('utf-8'))
        response = temp_sock.recv(2048).decode('utf-8').strip()
        temp_sock.close()

        if response.isdigit():
            state["latest_created_uid"] = int(response)
            return 1
        return 2

    except Exception as e:
        print(f"Sign up error: {e}")
        return 2

def get_last_created_uid(): # Helper for Interface.py to retrieve the newly generated UID.
    return state.get("latest_created_uid")

def logout(): # Called by Interface.logout_if(). Cleans up state and closes socket.
    global client_socket, is_running
    is_running = False

    if client_socket:
        try:
            if state["uid"] and state["sessionkey"]:
                close_payload = {
                    "msg_type": 100,
                    "receipient_id": 0,
                    "uid": int(state["uid"]),
                    "msg_content": "close",
                    "timestamp": int(time.time()),
                    "sessionkey": int(state["sessionkey"])
                }
                client_socket.sendall(json.dumps(close_payload).encode('utf-8'))
        except Exception:
            pass
        try:
            client_socket.close()
        except Exception:
            pass

    client_socket = None
    state["uid"] = None
    state["sessionkey"] = None
    clear_session()

def get_open_chats(): # Called by Interface.build_chats(). Returns list of (nickname, uid) tuples.
    if not state["uid"]:
        return []
    with sqlite3.connect(get_db_path(state["uid"]), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT nickname, uid FROM contacts ORDER BY nickname ASC')
        rows = cursor.fetchall()
    return [(row[0], str(row[1])) for row in rows]

def get_chats_if(): # Called by Interface.get_chats_if(). Returns list of (nickname, uid) tuples.
    return get_open_chats()

def load_messages(chat_uid): # Called by Interface.load_messages_if(chat_uid). Returns list of (text, sender_uid, timestamp) tuples.
    if not state["uid"]:
        return []
    with sqlite3.connect(get_db_path(state["uid"]), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT msg_content, sender_uid, timestamp 
            FROM local_messages 
            WHERE chat_uid = ? 
            ORDER BY timestamp ASC
        ''', (str(chat_uid),))
        rows = cursor.fetchall()
    return [(row[0], str(row[1]), row[2]) for row in rows]

def send_message(outgoing_message, recipient): # Called by Interface.send_message_if(outgoing_message, recipient). Sends the message to the socket server, saves it locally, and updates UI.
    global client_socket
    if not recipient or not outgoing_message or not state["uid"] or not client_socket:
        return None

    now = time.time()
    try:
        payload = {
            "msg_type": 200,
            "receipient_id": int(str(recipient).strip()),
            "uid": int(state["uid"]),
            "msg_content": outgoing_message,
            "timestamp": int(now),
            "sessionkey": int(state["sessionkey"])
        }
        client_socket.sendall(json.dumps(payload).encode('utf-8'))
    except Exception as e:
        print(f"Error sending message over socket: {e}")
        return None

    # Save to local SQLite database
    msg_tuple = save_local_message(state["uid"], recipient, state["uid"], outgoing_message, now)

    # Immediately push to UI so the sender sees their message right away
    if ui_callbacks["on_message"]:
        ui_callbacks["on_message"](msg_tuple)

    return msg_tuple

def add_contact(uid, nickname): # Called by Interface.add_contact_if(uid, nickname). Returns 1 on success, 2 if already exists, 3 if UID invalid.
    uid_str = str(uid).strip()
    nickname_str = str(nickname).strip()

    if not uid_str.isdigit():
        return 3

    if state["uid"] and uid_str == str(state["uid"]):
        return 2

    if not state["uid"]:
        return 3

    with sqlite3.connect(get_db_path(state["uid"]), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT uid FROM contacts WHERE uid = ?', (uid_str,))
        if cursor.fetchone():
            return 2  # Already exists

        cursor.execute('INSERT INTO contacts (uid, nickname) VALUES (?, ?)', (uid_str, nickname_str))
        conn.commit()

    return 1    