import sqlite3
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps






# GLOBAL DATABASE CONNECTION
STUDENTS = 'SMS.db'
USERS = 'USERS.db'

def get_connection(db):
    return sqlite3.connect(db)






# ====================================================== TABLES ===============================================================



#------------------------------ USERS -----------------------------------

connection = get_connection(USERS)
cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS Users (
               ID             INTEGER PRIMARY KEY AUTOINCREMENT,
               Username       VARCHAR(15) UNIQUE NOT NULL,
               Password_Hash  TEXT NOT NULL,
               Role           TEXT NOT NULL DEFAULT 'student'
               )""")

connection.commit()




# --------------------------- STUDENTS ------------------------------------


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





# HELPERS 

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
            connection = sqlite3.connect("SMS.db")
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
            
        connection = sqlite3.connect("SMS.db")
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


def login_required(function):
    @wraps(function)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return render_template("not_logged_in.html")
        return function(*args, **kwargs)
    return decorated_function




#=================================================== FLASK ROUTES =============================================================







app = Flask(__name__)
app.config["SECRET_KEY"] = "development-secret_Key"


# -------------------------- SESSIONS ---------------------------



# ------------------- register --------------------

@app.route("/register")
def register():
       return render_template("register.html")
    

@app.route("/register_user", methods=["POST"])
def register_user():

        username = request.form.get("username")

        #----------- Verification -----------
        if username == "":
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})
        if len(username) > 15:
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})

        
        connection = get_connection(USERS)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        existing_usernames = cursor.fetchone()

        if existing_usernames:
            return jsonify({"success": False, "message": "Username already exists, please enter another username", "field": "username", "mfield": "username_message"})


        #------------ password ----------------
        password = request.form.get("password")

        if password == "":
            return jsonify({"success": False, "message": "Please enter a valid password", "field": "password", "mfield": "password_message"})
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters", "field": "password", "mfield": "password_message"})

        password_hash = generate_password_hash(password)


        #------------- success ----------------
        connection = get_connection(USERS)
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO Users (Username, Password_hash) VALUES (?, ?)""", (username, password_hash))
        connection.commit()
        return jsonify({"success": True, "message": "Registration successful"})
    

# ------------------- log-in ----------------------
@app.route("/login")
def log_in():
     return render_template("log-in.html")

@app.route("/login_user", methods=["POST"])
def log_in_user():

        username = request.form.get("username")

        #----------- Verification -----------
        if username == "":
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})
        if len(username) > 15:
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})


        #------------ password ----------------
        password = request.form.get("password")

        if password == "":
            return jsonify({"success": False, "message": "Please enter a valid password", "field": "password", "mfield": "password_message"})
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters", "field": "password", "mfield": "password_message"})


        #------------- success ----------------
        connection = get_connection(USERS)
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,))
        found_users = cursor.fetchall()
 
        #-------------- Check if user exists -------------

        if len(found_users) == 0:
            return jsonify({"success": "NOT_FOUND", "message": "user not found"})
        
        #--------------- Check password ----------------

        user = found_users[0]
        if check_password_hash(user[2], password) == True:
            session["user_id"] = user[0]
            return jsonify({"success": True, "message": "Registration successful"})
        else:
            return jsonify({"success": False, "message": "Incorrect password", "field": "password", "mfield": "password_message"})

# -------------------- log-out --------------------
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("log_in"))







# -------------------------------- MAIN APP ----------------------------------






# HOME PAGE
@app.route("/")
@login_required
def home():
   message = 'Weclome!'
   return render_template("HOME.html", message=message)



# ADD STUDENT PAGE
@app.route("/add_student")
@login_required
def add_student():
    return render_template("add_student.html")

@app.route("/add_student", methods=["POST"])
def add_student_post():
    # Request Input
        name = request.form["name"].strip()
        age = request.form["age"].strip()
        grade = request.form["grade"] 
        course = request.form["course"]
        phone = request.form["phone"]
        email = request.form["email"]  
        student_id = None

    # Validation
        result = validate_student(name, age, grade, course, phone, student_id)
        if result:
            field, error = result
            return jsonify({ "success": False, "field": field, "message": error })
    
    # SQL
        connection = get_connection(STUDENTS)
        cursor = connection.cursor()
        cursor.execute(
          """ INSERT INTO Students (Name, Age, Grade, Course, Phone, Email) VALUES (?, ?, ?, ?, ?, ?) """,
          (name, age, grade, course, phone, email)
        )
        connection.commit()
    
        return jsonify({
            "success": True,
            "message": "Student added successfully"
        })



# ============================================== VIEW STUDENT PAGE =======================================================


@app.route("/view_students")
@login_required
def view_students():
    return render_template("view_students.html")

@app.route("/view_students_results")
def view_students_results():

    connection = get_connection(STUDENTS)
    cursor = connection.cursor()

    cursor.execute(" SELECT * FROM Students ORDER BY ID ")
    students_list = cursor.fetchall()
    count = len(students_list)
    
    return jsonify({"students": students_list, "count": count})






# ================================================ SEARCH STUDENT PAGE ================================================




@app.route("/search_student")
@login_required
def search_student_search():
        return render_template("search_student.html", students=[], count=0)
    
@app.route("/search_student_results")
def search_student_results():
        name = request.args["name"].strip()
        grade = request.args["grade"]
        course = request.args["course"]
        
        if grade == "" and course == "":

            connection = get_connection(STUDENTS)
            cursor = connection.cursor()

            name = f"%{name}%"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? ORDER BY ID """, (name,))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
        
        elif grade == "" and course != "":

            connection = get_connection(STUDENTS)
            cursor = connection.cursor()

            name = f"%{name}%"
            course = f"{course}"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Course LIKE ? ORDER BY ID""", (name, course))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
        
        elif course == "" and grade != "":

            connection = get_connection(STUDENTS)
            cursor = connection.cursor()

            name = f"%{name}%"
            grade = f"{grade}"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Grade LIKE ? ORDER BY ID""", (name, grade))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })







        
    # SQL
        connection = get_connection(STUDENTS)
        cursor = connection.cursor()
        
        name = f"%{name}%"
        grade = f"{grade}"
        course = f"{course}"

        cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Grade LIKE ? AND Course LIKE ? ORDER BY Name""", 
                       (name, grade, course))
        students_list = cursor.fetchall()
        return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
    




# =================================================== STUDENT PAGE ====================================================




@app.route("/student/<int:student_id>", methods=["GET"])
@login_required
def student_details(student_id):

    source = request.args.get("from")

    
    connection = get_connection(STUDENTS)
    cursor = connection.cursor()

    cursor.execute(" SELECT * FROM Students WHERE ID = ?", (student_id,))
    student = cursor.fetchone()
    
    return render_template("student_details.html", student=student, source=source)





# ====================================================  UPDATE ===========================================================




@app.route("/update_student/<int:student_id>", methods=["GET", "POST"])
@login_required
def update_student_GET_and_POST(student_id):

    if request.method == "GET":
       connection = get_connection(STUDENTS)
       cursor = connection.cursor()

       cursor.execute("SELECT * FROM Students WHERE ID = ?", (student_id,))
       selected_student =  cursor.fetchone()

       return render_template("update_student.html", student=selected_student)
    
    elif request.method == "POST":
       name = request.form["name"].strip()
       age = request.form["age"].strip()
       grade = request.form["grade"].strip() 
       course = request.form["course"].strip()
       phone = request.form["phone"]
       email = request.form["email"]    

    # Validation
       result = validate_student(name, age, grade, course, phone, student_id)
       if result:
            field, error = result
            return jsonify({ "success": False, "field": field, "message": error})

    # SQL
       connection = get_connection(STUDENTS)
       cursor = connection.cursor()

       cursor.execute("UPDATE Students SET Name = ?, Age = ?, Grade = ?, Course = ?, Phone = ?, Email = ? WHERE ID = ?", 
                      (name, age, grade, course, phone, email, student_id))
    
       connection.commit()
       return jsonify({ "success": True, "message": "Student has been updated" })





# ============================================= DELETE STUDENT =========================================================




@app.route("/delete_student/<int:student_id>", methods=["DELETE"])
@login_required
def delete_student_GET_and_POST(student_id):

    connection = get_connection(STUDENTS)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Students WHERE ID = ?", (student_id,))
    connection.commit()

    return jsonify({ "message": "Student has been deleted", "studentId":  student_id })





if __name__ == "__main__":
   app.run(debug=True)


