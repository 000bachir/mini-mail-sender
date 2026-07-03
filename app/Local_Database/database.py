#TODO : CHANGE OF PLANS NOW I NEED TO MAKE THE DATABASE LOCAL IN ORDER FOR TO BE MORE USEFUL
import os
import sqlite3
from sqlite3 import Error


DATABSE_PATH = os.path.join(os.path.dirname(__file__) , "database.db")

def get_conn() -> sqlite3.Connection : 
    connection = sqlite3.connect(DATABSE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection

def init_db() : 
    conn = get_conn()
    #cursor act as messenger between the python code and the database
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT , 
            email TEXT UNIQUE NOT NULL , 
            full_name TEXT , 
            category TEXT , 
            language TEXT , 
            source TEXT , 
            notes TEXT 
            status TEXT DEFAULT 'active',
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        )

    """)
