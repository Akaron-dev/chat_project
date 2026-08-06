import sqlite3

connection = sqlite3.connect('data.db')

cursor = connection.cursor()

cursor.execute(''' ALTER TABLE users
        ADD COLUMN password_salt DATATYPE text
    ''')    

connection.commit()
connection.close()

