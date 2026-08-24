from functools import wraps
from flask import redirect, url_for, session
from config import STUDENTS
from database import get_connection



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


def validate_student(name, age, grade, course, phone, student_id):

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
            connection = get_connection(STUDENTS)
            cursor = connection.cursor()
            cursor.execute("""SELECT * FROM Students WHERE Phone = ?""", (phone,))
            phone_list = cursor.fetchall()
            if len(phone_list) == 0:
                return
            elif len(phone_list) > 0:
               return ("phone", "Phone number has already been registered")
            elif len(phone) > 10 or len(phone) < 10:
               return ("phone", "Phone number is invalid")
            elif phone == "":
                return ("phone", "Phone cannot be empty")
            
        connection = get_connection(STUDENTS)
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM Students WHERE Phone = ? AND ID != ?""", (phone, student_id))
        phone_list = cursor.fetchall()
        if len(phone_list) == 0:
            return
        elif len(phone_list) > 0:
           return ("phone", "Phone number has already been registered")
        elif len(phone) > 10 or len(phone) < 10:
           return ("phone", "Phone number is invalid")
        elif phone == "":
            return ("phone", "Phone cannot be empty")


