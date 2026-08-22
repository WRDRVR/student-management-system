import sqlite3

def get_connection(db):
    return sqlite3.connect(db)