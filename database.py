from helpers import get_connection
from flask import current_app

def create_USERS(db):
    connection = get_connection(db)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
                   ID             INTEGER PRIMARY KEY AUTOINCREMENT,
                   Username       VARCHAR(15) UNIQUE NOT NULL,
                   Password_Hash  TEXT NOT NULL,
                   Role           TEXT NOT NULL DEFAULT 'student'
                  )""")
    connection.commit()
    connection.close()


def create_STUDENTS(db):
    connection = get_connection(db)
    cursor = connection.cursor()
    current_date = '2026/08/28'
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS Students(
                   ID         INTEGER PRIMARY KEY AUTOINCREMENT,
                   Name       VARCHAR(50) NOT NULL,
                   Age        INTEGER NOT NULL,
                   Grade      TEXT NOT NULL,
                   Course     TEXT NOT NULL,
                   Phone      VARCHAR(15) UNIQUE NOT NULL,
                   Email      VARCHAR(50) DEFAULT 'None',
                   Date       DATE DEFAULT (current_date)
                    )""")
    connection.commit()
    connection.close()