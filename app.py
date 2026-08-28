from flask import Flask
from config import Config
from auth.routes import auth
from students.routes import students
from database import create_STUDENTS, create_USERS



def create_app(config_app=Config):
    app = Flask(__name__)

    app.config.from_object(config_app)
    
    create_USERS(app.config["USERS_DB"])

    create_STUDENTS(app.config["STUDENTS_DB"])

    app.register_blueprint(auth)
    app.register_blueprint(students)

    if __name__ == "__main__":
        app.run(debug=True)

    return app


create_app()
