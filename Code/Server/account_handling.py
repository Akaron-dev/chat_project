import sqlite3
import bcrypt
import random






# cursor.execute("INSERT INTO messages VALUES (00000001, 00000001, 00000002, 'test', 1932)")

# connection.commit()
# connection.close()

def create_account(password):
    uid = random.randint(1, 999999999)
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password_bytes, salt)
    cursor.execute("INSERT INTO users VALUES (?, ?, NULL)",
                   (uid, password_hash.decode('utf-8'))
                    )
    connection.commit()
    connection.close()
    return uid

# create_account(1, 'Test123456')

def login(uid, password):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    user_data = cursor.fetchone()
    if not user_data:
        return ('wrong password or username')
    stored_hash = user_data[1]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        print('Login successfull')
        sessionkey = random.randint(1, 999999999)
        cursor.execute("UPDATE users SET sessionkey = ? WHERE user_id = ?", (sessionkey, uid))
        connection.commit()
        connection.close()
        return ('Login successful, this is your sessionkey', sessionkey)
    else:
        connection.close()
        return ('wrong password or username')


# print(login(1, 'Test123456'))
