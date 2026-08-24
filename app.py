from database import get_connection
from flask import Flask
from config import USERS, STUDENTS, Config
from auth.routes import auth
from students.routes import students





connection = get_connection(USERS)
cursor = connection.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
               ID             INTEGER PRIMARY KEY AUTOINCREMENT,
               Username       VARCHAR(15) UNIQUE NOT NULL,
               Password_Hash  TEXT NOT NULL,
               Role           TEXT NOT NULL DEFAULT 'student'
               )""")
connection.commit()



connection = get_connection(STUDENTS)
cursor = connection.cursor()
current_date = '2026/08/18'
cursor.execute("""
               CREATE TABLE IF NOT EXISTS Students(
               ID         INTEGER PRIMARY KEY AUTOINCREMENT,
               Name       VARCHAR(50) NOT NULL,
               Age        INTEGER NOT NULL,
               Grade      TEXT NOT NULL,
               Course     TEXT NOT NULL,
               Phone      VARCHAR(10) UNIQUE NOT NULL,
               Email      VARCHAR(100) UNIQUE,
               Date       DATE DEFAULT (CURRENT_DATE)
                )""")
connection.commit()





def create_app(config_app = Config):
    app = Flask(__name__)



    app.config.from_object(config_app)

    app.register_blueprint(auth)
    app.register_blueprint(students)

    if __name__ == "__main__":
        app.run(debug=True)

    return app




create_app()









