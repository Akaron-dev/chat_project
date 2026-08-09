import sqlite3

# connection = sqlite3.connect('data.db')
# cursor = connection.cursor()
# cursor.execute('DROP TABLE messages')
# connection.commit()
# connection.close()


# connection = sqlite3.connect('data.db')
# cursor = connection.cursor()
# cursor.execute("SELECT * FROM users WHERE user_id = ?", (1,))
# print(cursor.fetchall())

connection = sqlite3.connect('data.db')
cursor = connection.cursor()
cursor.execute('''CREATE TABLE messages (
                                  msg_type DATATYPE integer,
                                  receipient_id DATATYPE integer,
                                  sender_id DATATYPE integer,
                                  msg_content DATATYPE text,
                                  timestamp DATATYPE integer
                                  )''')
connection.commit()
connection.close()