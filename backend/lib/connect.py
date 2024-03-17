import os
import sqlite3

def connect_to_database():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    data_directory = os.path.join(current_directory, '..', 'data')
    database_path = os.path.join(data_directory, 'trading.db')
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    return conn, cursor

def disconnect_from_database(conn, cursor):
    cursor.close()
    conn.commit()
    conn.close()

# conn, cursor = connect_to_database()