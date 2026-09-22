from helpers import get_connection

def create_USERS(db):
    connection = get_connection(db)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
                   ID             INTEGER PRIMARY KEY AUTOINCREMENT,
                   Username       VARCHAR(20) UNIQUE NOT NULL,
                   Password_Hash  TEXT NOT NULL,
                   Email          TEXT DEFAULT 'None',
                   EmailVerified  INTEGER DEFAULT '0',
                   Phone          TEXT DEFAULT 'None',
                   PhoneVerified  INTEGER DEFAULT '0',
                   Role           TEXT NOT NULL DEFAULT 'student'
                  )""")
    connection.commit()
    connection.close()


def create_STUDENTS(db):
    connection = get_connection(db)
    cursor = connection.cursor()
    current_date = '2026/09/22'
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


def create_email_verify(db):
    connection = get_connection(db)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS EmailVerification (
                       ID  INTEGER PRIMARY KEY,
                       UserID  INTEGER NOT NULL UNIQUE,
                       TokenHash  TEXT NOT NULL,
                       ExpiresAt TEXT NOT NULL,
                       Attempts  INTEGER NOT NULL DEFAULT 0,
                       ResendAvailableAt  TEXT NOT NULL
                   )""")
       

def create_phone_verify(db):
    connection = get_connection(db)
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS PhoneVerification (
                       ID   INTEGER PRIMARY KEY,
                       UserID  INTEGER NOT NULL UNIQUE,
                       CodeHash  TEXT NOT NULL,
                       ExpiresAt  TEXT NOT NULL,
                       Attempts   INTEGER NOT NULL DEFAULT 0,
                       ResendAvailableAt  TEXT NOT NULL
                   )""")
