import sqlite3
import bcrypt





# cursor.execute("INSERT INTO messages VALUES (00000001, 00000001, 00000002, 'test', 1932)")

# connection.commit()
# connection.close()

def create_account(uid, password):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash = bcrypt.hashpw(bytes, salt)
    cursor.execute("INSERT INTO users VALUES (?, ?, ?)",
                   (uid, hash.decode('utf-8'), salt.decode('utf-8'))
                    )
    connection.commit()
    connection.close()

# create_account(1, 'Test123456')

def login(uid, password):
    connection = sqlite3.connect('data.db')
    cursor = connection.cursor()
    bytes = password.encode('utf-8')
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (uid,))
    user_data = cursor.fetchall()
    hash_true, salt = user_data[0][1], user_data[0][2]
    salt_bytes = salt.encode('utf-8')
    hash = bcrypt.hashpw(bytes, salt_bytes)
    if hash.decode('utf-8') == hash_true:
        print('Login successfull')
        return True
    else:
        print('wrong password or username')


# login(1, 'Test123456')