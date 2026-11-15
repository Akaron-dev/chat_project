import socket
import ssl
import threading
import json
import time
import os
import sys
import sqlite3
import ast
import re

# Ensure directory is in sys.path to reliably import RSA module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import RSA

SERVER_IP = '127.0.0.1'
SERVER_PORT = 7567
USE_TLS = (SERVER_PORT in (443, 8443, 10000))

# Optional override via server_config.json if present
CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server_config.json")
if os.path.exists(CONFIG_PATH):
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            _cfg = json.load(f)
            SERVER_IP = _cfg.get("host", SERVER_IP)
            SERVER_PORT = int(_cfg.get("port", SERVER_PORT))
            USE_TLS = _cfg.get("use_tls", SERVER_PORT in (443, 8443, 10000))
    except Exception:
        pass

SERVER_IP = SERVER_IP  # Backward-compatibility alias

def create_connection(): # Creates and returns a connected socket to SERVER_IP:SERVER_PORT. When USE_TLS is True (required for Tailscale Funnel on ports 443/8443/10000), wraps the socket in TLS with Server Name Indication (SNI).
    raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if USE_TLS:
        context = ssl.create_default_context()
        sock = context.wrap_socket(raw_sock, SERVER_IPname=SERVER_IP)
        sock.connect((SERVER_IP, SERVER_PORT))
        return sock
    else:
        raw_sock.connect((SERVER_IP, SERVER_PORT))
        return raw_sock

VALID_INVITE_CODES = None # When set to None, any invite code is valid. Otherwise, only the codes in this list are valid.

state = {
    "uid": None,
    "sessionkey": None,
    "latest_created_uid": None,
    "private_key": None,
    "public_key": None,
    "chat_keys": {},
    "public_keys": {},
    "pending_outgoing": {}
}

client_socket = None
is_running = False
recv_thread = None
send_lock = threading.Lock()

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

def init_local_db(own_uid): # Initializes the SQLite tables for this user. Creates 'local_messages', 'contacts', and cryptographic key tables if they don't exist.
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
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_keys (
                key_name TEXT PRIMARY KEY,
                key_value TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS public_keys (
                uid TEXT PRIMARY KEY,
                public_key_pem TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_keys (
                chat_uid TEXT PRIMARY KEY,
                fernet_key TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient_uid TEXT NOT NULL,
                msg_content TEXT NOT NULL
            )
        ''')
        conn.commit()

def init_keys(own_uid): # Initializes user's RSA keys and loads contacts' public keys and chat fernet keys.
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT key_name, key_value FROM user_keys')
        keys = dict(cursor.fetchall())
        if 'private_key' not in keys or 'public_key' not in keys:
            priv_pem, pub_pem = RSA.generate_rsa_keypair()
            cursor.execute('INSERT OR REPLACE INTO user_keys (key_name, key_value) VALUES (?, ?)', ('private_key', priv_pem))
            cursor.execute('INSERT OR REPLACE INTO user_keys (key_name, key_value) VALUES (?, ?)', ('public_key', pub_pem))
            conn.commit()
            state["private_key"] = priv_pem
            state["public_key"] = pub_pem
        else:
            state["private_key"] = keys['private_key']
            state["public_key"] = keys['public_key']

        cursor.execute('SELECT uid, public_key_pem FROM public_keys')
        state["public_keys"] = {str(row[0]): row[1] for row in cursor.fetchall()}

        cursor.execute('SELECT chat_uid, fernet_key FROM chat_keys')
        state["chat_keys"] = {str(row[0]): row[1] for row in cursor.fetchall()}

    state["pending_outgoing"] = {}

def save_contact_public_key(own_uid, contact_uid, pubkey_pem): # Saves a contact's RSA Public Key (PEM) to the local SQLite database and in-memory state.
    contact_uid_str = str(contact_uid)
    state["public_keys"][contact_uid_str] = pubkey_pem
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO public_keys (uid, public_key_pem) VALUES (?, ?)',
                       (contact_uid_str, pubkey_pem))
        conn.commit()

def save_chat_fernet_key(own_uid, chat_uid, fernet_key): # Saves a chat's Fernet key to the local SQLite database and in-memory state.
    chat_uid_str = str(chat_uid)
    state["chat_keys"][chat_uid_str] = fernet_key
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR REPLACE INTO chat_keys (chat_uid, fernet_key) VALUES (?, ?)',
                       (chat_uid_str, fernet_key))
        conn.commit()

def save_pending_message(own_uid, recipient_uid, msg_content): # Saves a pending message to the local SQLite database for later sending when the recipient's key is available.
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO pending_messages (recipient_uid, msg_content) VALUES (?, ?)',
                       (str(recipient_uid), str(msg_content)))
        conn.commit()

def get_and_clear_pending_messages(own_uid, recipient_uid): # Retrieves and clears pending messages for a specific recipient from the local SQLite database. Returns a list of message contents.
    with sqlite3.connect(get_db_path(own_uid), timeout=10.0) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT id, msg_content FROM pending_messages WHERE recipient_uid = ? ORDER BY id ASC',
                       (str(recipient_uid),))
        rows = cursor.fetchall()
        if rows:
            cursor.execute('DELETE FROM pending_messages WHERE recipient_uid = ?', (str(recipient_uid),))
            conn.commit()
    return [row[1] for row in rows]

def send_raw_payload(recipient_id, content_str): # Sends a raw JSON payload to the server for a specific recipient. The payload is sent over the existing socket connection.
    global client_socket
    if not client_socket or not state["uid"] or not state["sessionkey"]:
        return False
    try:
        payload = {
            "msg_type": 200,
            "receipient_id": int(str(recipient_id).strip()),
            "uid": int(state["uid"]),
            "msg_content": content_str,
            "timestamp": int(time.time()),
            "sessionkey": int(state["sessionkey"])
        }
        with send_lock:
            client_socket.sendall(json.dumps(payload).encode('utf-8'))
        return True
    except Exception as e:
        print(f"Error sending payload to {recipient_id}: {e}")
        return False

def flush_pending_messages(recipient_uid): # Sends any pending messages for a specific recipient that were stored while waiting for the recipient's Fernet key. This function retrieves pending messages from both in-memory and database storage, encrypts them with the Fernet key, and sends them to the recipient.
    recipient_uid = str(recipient_uid)
    f_key = state["chat_keys"].get(recipient_uid)
    if not f_key:
        return
    # In-memory pending messages
    pending = state["pending_outgoing"].pop(recipient_uid, [])
    # Plus database pending messages
    if state.get("uid"):
        db_pending = get_and_clear_pending_messages(state["uid"], recipient_uid)
        pending.extend(db_pending)

    for msg_text in pending:
        try:
            cipher = RSA.fernet_encrypt(f_key, msg_text)
            payload_str = json.dumps({"type": "chat_msg", "payload": cipher})
            time.sleep(0.05)
            send_raw_payload(recipient_uid, payload_str)
        except Exception as e:
            print(f"Error sending flushed message to {recipient_uid}: {e}")

def handle_incoming_payload(sender_uid, content, timestamp=None): # Handles an incoming message payload from a sender. This function processes the content, determines if it's a protocol message (e.g., key exchange, encrypted chat), and takes appropriate actions such as saving messages, decrypting them, or requesting keys. It also updates the UI via registered callbacks.
    if timestamp is None:
        timestamp = time.time()
    sender_uid = str(sender_uid).strip()

    # Try parsing as protocol JSON
    is_protocol_msg = False
    data = None
    if content.startswith('{') and content.endswith('}'):
        try:
            data = json.loads(content)
            if isinstance(data, dict) and "type" in data:
                is_protocol_msg = True
        except Exception:
            is_protocol_msg = False

    if is_protocol_msg:
        msg_type = data.get("type")

        if msg_type == "key_req":
            # Sender requests our RSA Public Key
            ensure_contact_exists(state["uid"], sender_uid)
            if state.get("public_key"):
                reply_payload = json.dumps({"type": "pubkey", "payload": state["public_key"]})
                send_raw_payload(sender_uid, reply_payload)
            return

        elif msg_type == "pubkey":
            # Sender sent their RSA Public Key (PEM)
            pubkey_pem = data.get("payload")
            if pubkey_pem:
                ensure_contact_exists(state["uid"], sender_uid)
                save_contact_public_key(state["uid"], sender_uid, pubkey_pem)

                # If we don't have a Fernet key for this contact yet, generate and send one
                if sender_uid not in state["chat_keys"]:
                    try:
                        f_key = RSA.generate_fernet_key()
                        enc_f_key = RSA.encrypt_fernet_key(pubkey_pem, f_key)
                        save_chat_fernet_key(state["uid"], sender_uid, f_key)
                        fernet_msg = json.dumps({
                            "type": "fernet_key",
                            "payload": enc_f_key,
                            "from_uid": int(state["uid"])
                        })
                        time.sleep(0.05)
                        send_raw_payload(sender_uid, fernet_msg)
                    except Exception as e:
                        print(f"Error encrypting Fernet key for {sender_uid}: {e}")

                # If we had pending messages waiting for this contact's key, send them now
                flush_pending_messages(sender_uid)
            return

        elif msg_type == "fernet_key":
            # Sender sent Encrypted Fernet Key
            enc_f_key = data.get("payload")
            from_uid = data.get("from_uid", int(sender_uid))
            if enc_f_key and state.get("private_key"):
                try:
                    decrypted_f_key = RSA.decrypt_fernet_key(state["private_key"], enc_f_key)
                    # Tie-breaker if both generated keys: smaller UID's key wins
                    should_save = True
                    if sender_uid in state["chat_keys"]:
                        if int(state["uid"]) < int(from_uid):
                            should_save = False
                    if should_save:
                        save_chat_fernet_key(state["uid"], sender_uid, decrypted_f_key)

                    flush_pending_messages(sender_uid)
                except Exception as e:
                    print(f"Error decrypting Fernet key from {sender_uid}: {e}")
            return

        elif msg_type == "chat_msg":
            # Encrypted chat message (Fernet)
            ciphertext = data.get("payload")
            plaintext = None
            f_key = state["chat_keys"].get(sender_uid)
            if f_key and ciphertext:
                try:
                    plaintext = RSA.fernet_decrypt(f_key, ciphertext)
                except Exception as e:
                    print(f"Error decrypting chat message from {sender_uid}: {e}")
                    plaintext = "[Decryption error]"
            else:
                plaintext = "[Encrypted message - key missing]"

            if plaintext is not None:
                if ensure_contact_exists(state["uid"], sender_uid):
                    if ui_callbacks["on_new_chat"]:
                        ui_callbacks["on_new_chat"]()

                msg_tuple = save_local_message(state["uid"], sender_uid, sender_uid, plaintext, timestamp)

                active_uid = ui_callbacks["get_active_uid"]()
                if active_uid and str(active_uid) == str(sender_uid):
                    if ui_callbacks["on_message"]:
                        ui_callbacks["on_message"](msg_tuple)
            return

    # Fallback: Plaintext message (backward compatibility)
    if ensure_contact_exists(state["uid"], sender_uid):
        if ui_callbacks["on_new_chat"]:
            ui_callbacks["on_new_chat"]()

    msg_tuple = save_local_message(state["uid"], sender_uid, sender_uid, content, timestamp)
    active_uid = ui_callbacks["get_active_uid"]()
    if active_uid and str(active_uid) == str(sender_uid):
        if ui_callbacks["on_message"]:
            ui_callbacks["on_message"](msg_tuple)

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
                handle_incoming_payload(sender_uid, content, now)

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
        sock = create_connection()

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

        # Prepare local database and crypto keys
        init_local_db(state["uid"])
        init_keys(state["uid"])

        # Store any offline messages delivered by server upon login
        for sender_id, msg_content, timestamp in unread_messages:
            s_uid = str(sender_id)
            handle_incoming_payload(s_uid, msg_content, timestamp)

        save_session(state["uid"], own_password)

        # Start independent background receiver thread
        is_running = True
        recv_thread = threading.Thread(target=receive_loop, daemon=True)
        recv_thread.start()

        # Request missing keys for contacts if needed
        for _, c_uid in get_open_chats():
            if c_uid not in state["chat_keys"]:
                req_msg = json.dumps({"type": "key_req"})
                send_raw_payload(c_uid, req_msg)

        return 1

    except Exception as e:
        print(f"Login connection error: {e}")
        return 0

def sign_up(new_password, invite_code): # Called by Interface.sign_up_if(new_password, invite_code). Returns 1 on success, 2 on invalid invite code.
    if VALID_INVITE_CODES is not None:
        if invite_code not in VALID_INVITE_CODES:
            return 2

    try:
        temp_sock = create_connection()

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
    state["private_key"] = None
    state["public_key"] = None
    state["chat_keys"] = {}
    state["public_keys"] = {}
    state["pending_outgoing"] = {}
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

    recipient_str = str(recipient).strip()
    now = time.time()

    # 1. Check if we already have the Fernet key ready
    f_key = state["chat_keys"].get(recipient_str)
    if f_key:
        try:
            cipher = RSA.fernet_encrypt(f_key, outgoing_message)
            payload_str = json.dumps({"type": "chat_msg", "payload": cipher})
            send_raw_payload(recipient_str, payload_str)
        except Exception as e:
            print(f"Error encrypting message: {e}")
            return None
    else:
        # 2. Check if we have recipient's RSA Public Key
        pubkey_pem = state["public_keys"].get(recipient_str)
        if pubkey_pem:
            try:
                new_f_key = RSA.generate_fernet_key()
                enc_f_key = RSA.encrypt_fernet_key(pubkey_pem, new_f_key)
                save_chat_fernet_key(state["uid"], recipient_str, new_f_key)

                fernet_msg = json.dumps({
                    "type": "fernet_key",
                    "payload": enc_f_key,
                    "from_uid": int(state["uid"])
                })
                send_raw_payload(recipient_str, fernet_msg)

                time.sleep(0.05)
                cipher = RSA.fernet_encrypt(new_f_key, outgoing_message)
                payload_str = json.dumps({"type": "chat_msg", "payload": cipher})
                send_raw_payload(recipient_str, payload_str)
            except Exception as e:
                print(f"Error performing key setup: {e}")
                return None
        else:
            # 3. Queue message and request Bob's Public Key
            if recipient_str not in state["pending_outgoing"]:
                state["pending_outgoing"][recipient_str] = []
            state["pending_outgoing"][recipient_str].append(outgoing_message)
            save_pending_message(state["uid"], recipient_str, outgoing_message)

            if state.get("public_key"):
                pub_msg = json.dumps({"type": "pubkey", "payload": state["public_key"]})
                send_raw_payload(recipient_str, pub_msg)
                time.sleep(0.05)
            req_msg = json.dumps({"type": "key_req"})
            send_raw_payload(recipient_str, req_msg)

    # Save to local SQLite database (plain text for local display)
    msg_tuple = save_local_message(state["uid"], recipient_str, state["uid"], outgoing_message, now)

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

    # Initiate key exchange: send our Public Key (PEM) and request theirs
    if client_socket and state.get("public_key"):
        pub_msg = json.dumps({"type": "pubkey", "payload": state["public_key"]})
        send_raw_payload(uid_str, pub_msg)
        time.sleep(0.05)
        req_msg = json.dumps({"type": "key_req"})
        send_raw_payload(uid_str, req_msg)

    return 1
