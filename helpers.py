import sqlite3
from functools import wraps
from flask import redirect, url_for, session, current_app

def get_connection(db):
    return sqlite3.connect(db)

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.not_logged_in"))
        return function(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.not_logged_in"))
            if session["role"] != role:
                return redirect(url_for("auth.not_authorized"))
            return function(*args, **kwargs)
        return decorated_function
    return decorator 

def validate_student(name, age, grade, course, phone, student_id, email):

    # Name
    if name == "":
     return ("name", "Name cannot be empty")
    
    # Age
    if age != None:
        try:
            age = int(age)
            if age > 100 or age < 5:
                return ("age", "Please enter a valid age")
        except ValueError:
            return ("age", "Age is invalid")
        if age == "":
            return ("age", "Age cannot be empty")
        
    # Grade
    if grade != None:
        try:
            if len(grade) > 25:
               return ("grade", "Please enter a valid grade")
        except ValueError:
            return("grade", "Please enter a valid grade")
        if grade == "":
            return ("grade", "Grade cannot be empty")
        
    # Course
    if course != None:
        if len(course) > 25:
            return("course","Course name exceeds limit")
        elif course == "":
            return ("course", "Course cannot be empty")

    # Phone
    if phone != None:
        if student_id == None:
            if len(phone) != 10:
               return ("phone", "Phone number is invalid, please enter a valid phone contact")
            if phone == "":
                return ("phone", "Phone cannot be empty")

            connection = get_connection(current_app.config["STUDENTS_DB"])
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM Students WHERE Phone = ?""", (phone,))
            phone_list = cursor.fetchall()
            connection.close()

            if len(phone_list) == 0:
                return 
            elif len(phone_list) > 0:
               return ("phone", "Phone number has already been registered")
            

        if len(phone) != 10:
           return ("phone", "Phone number invalid")
        elif phone == "":
            return ("phone", "Phone cannot be empty")
            
        connection = get_connection(current_app.config["STUDENTS_DB"])
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM Students WHERE Phone = ? AND ID != ?""", (phone, student_id))
        phone_list = cursor.fetchall()

        connection.close()

        if len(phone_list) == 0:
            return 
        elif len(phone_list) > 0:
           return ("phone", "Phone number has already been registered")

    # Email
    if email != "":
        if "@" not in email:
            return ("email", "Please enter a valid email")
        elif len(email) < 10:
            return ("email", "Please enter a valid email")
        elif len(email) > 60:
            return ("email", "Please enter a shorter email")        

def auth_user(username, password, register=True):

    # Username
    if username == "":
        return ("Please enter a valid username", "username", "username_message")
    if len(username) > 20:
        if len(username) > 30:
            return ("Username is too long", "username", "username_message")
        return ("Please enter a shorter username", "username", "username_message")
    if len(username) < 3:
        return ("Username must be at least 3 characters long", "username", "username_message")

    if register:
        connection = get_connection(current_app.config["USERS_DB"])
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        existing_usernames = cursor.fetchone()

        connection.commit()
        connection.close()

        if existing_usernames:
            return ("Username already exists, please enter a different username", "username", "username_message")
    
    # Password
    if password == "":
        return ("Please enter a valid password", "password", "password_message")
    if len(password) < 6:
        return ("Password must be at least 6 characters", "password", "password_message")

def with_database(db, operation, commit=False):
    try:
        connection = sqlite3.connect(current_app.config[db])
        cursor = connection.cursor()
        result = operation(cursor)

        if commit:
           connection.commit()

        return True, result
    
    except sqlite3.Error as error:
        return False, error
    
    finally:
        connection.close()