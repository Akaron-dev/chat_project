import sqlite3
import bcrypt
import random

def create_account(password):
    uid = random.randint(1, 999999999)
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?, NULL)", (uid, password_hash.decode('utf-8')))
        connection.commit()
    return uid

def login(uid, password):
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT password_hash FROM users WHERE uid = ?", (uid,))
        user_data = cursor.fetchone()
        
        if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[0].encode('utf-8')):
            sessionkey = random.randint(1, 999999999)
            cursor.execute("UPDATE users SET sessionkey = ? WHERE uid = ?", (sessionkey, uid))
            connection.commit()
            return sessionkey
    return 0

def sessionkey_verification(uid, sessionkey):
    with sqlite3.connect('data.db') as connection:
        cursor = connection.cursor()
        cursor.execute('SELECT sessionkey FROM users WHERE uid = ?', (uid,))
        user_data = cursor.fetchone()
        return bool(user_data and user_data[0] == sessionkey)



# print(login(1, 'Test123456'))
