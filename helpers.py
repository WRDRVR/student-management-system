import sqlite3
from functools import wraps
from flask import redirect, url_for, session, request, current_app
import ssl, smtplib, time, secrets
from email.message import EmailMessage
from pathlib import Path


def get_connection(db):
    base_dir = Path(__file__).resolve().parent
    db_path = base_dir / db
    return sqlite3.connect(db_path)

def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("auth.not_logged_in")), 302
        return function(*args, **kwargs)
    return decorated_function

def not_registered(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "register_user_id" not in session:
            if "user_id" in session:
                return redirect(url_for("auth.not_allowed")), 302
            return redirect(url_for("auth.not_logged_in")), 403
        return function(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(function):
        @wraps(function)
        def decorated_function(*args, **kwargs):
            if "user_id" not in session:
                return redirect(url_for("auth.not_logged_in")), 302
            if session["role"] != role:
                return redirect(url_for("auth.not_authorized")), 403
            return function(*args, **kwargs)
        return decorated_function
    return decorator 

def csrf_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        csrf_token = request.form.get('csrf_token')
        if session['csrf_token'] != csrf_token:
            return redirect(url_for("students.something_went_wrong")), 403
        return function(*args, *kwargs)
    return decorated_function

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

def auth_user(username, password, register=False):

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
        connection = get_connection(current_app.config[db])
        cursor = connection.cursor()
        result = operation(cursor)

        if commit:
           connection.commit()
        return True, result
    
    except sqlite3.Error as error:
        connection.rollback()
        return False, error
    
    finally:
        connection.close()

def send_verification_email(email, token):
    sender = "example@gmail.com"
    recipient = email
    password = "password"

    context = ssl.create_default_context()
    message = EmailMessage()
    message['Subject'] = 'SMS SMTP Test'
    message['From'] = sender
    message['To'] = recipient
    message.set_content(f"Dear user, click this link to verify your email on the SMS\n\nhttp://localhost:5000/verify-email?token={token}&id=${id}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender, password)
        server.send_message(message)
        print("Email sent!") 

def send_verification_sms(phone, code):
    phone = phone
    code = code
    #Twilio Code
    print(f"SMS to {phone}: Your verification code is {code}")
    return True

def auth_email(email):
    if email is None:
        return ("Please enter an email", "email", "email_message")
    if "@" not in email or ".com" not in email:
        return ("Your email must be in the valid format (example@gmail.com)", "email", "email_message")
    if len(email) < 5:
        return ("Please enter a valid email", "email", "email_message")
    if len(email) > 50:
        return ("Please enter a shorter email", "email", "email_message")
    
def auth_phone(phone):
    if phone is None:
        return ("Please enter a phone number", "phone", "phone_message")
    if len(phone) > 13:
        return ("Please enter a valid phone number", "phone", "phone_message") 
       
def rate_limit(client, rate_limits):
    current_time = time.time()

    if client not in rate_limits:
        rate_limits[client] = {
            "start": current_time,
            "requests": 1
        }
        return True
    
    elapsed = current_time - rate_limits[client]["start"]


    if elapsed >= 60:
        rate_limits[client] = {
            "start": current_time,
            "requests": 1
        }
        return True

    if rate_limits[client]["requests"] >= 5:
        return False

    rate_limits[client]["requests"] += 1
    return True    

def csrf():
    csrf_token = secrets.token_urlsafe(32)
    session["csrf_token"] = csrf_token
    return csrf_token 