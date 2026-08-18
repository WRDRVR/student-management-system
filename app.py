import sqlite3
from flask import Flask, jsonify, render_template, request

connection = sqlite3.connect('SMS.db')
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
                )
               """)

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




#=================================================== FLASK ROUTES =============================================================




app = Flask(__name__)
app.secret_key = "secret_Key"


# HOME PAGE
@app.route("/")
def home():
    connection = sqlite3.connect('SMS.db')
    cursor = connection.cursor()

    cursor.execute("""SELECT COUNT(*) FROM Students""")
    count = cursor.fetchone()[0]

    cursor.execute("""SELECT AVG(Age) FROM Students""")
    average = cursor.fetchone()[0]
    average = round(average, 1)

    cursor.execute("""SELECT MIN(Age) FROM Students""")
    youngest = cursor.fetchone()[0]

    cursor.execute("""SELECT MAX(Age) FROM Students""")
    oldest = cursor.fetchone()[0]
    
    return render_template("HOME.html", count=count, average=average, youngest=youngest, oldest=oldest)



# ADD STUDENT PAGE
@app.route("/add_student")
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
        connection = sqlite3.connect("SMS.db")
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
def view_students():
    return render_template("view_students.html")

@app.route("/view_students_results")
def view_students_results():
    connection = sqlite3.connect("SMS.db")
    cursor = connection.cursor()

    cursor.execute(" SELECT * FROM Students ORDER BY ID ")
    students_list = cursor.fetchall()
    count = len(students_list)
    
    return jsonify({"students": students_list, "count": count})






# ================================================ SEARCH STUDENT PAGE ================================================




@app.route("/search_student")
def search_student_search():
        return render_template("search_student.html", students=[], count=0)
    
@app.route("/search_student_results")
def search_student_results():
        name = request.args["name"].strip()
        grade = request.args["grade"]
        course = request.args["course"]
        
        if grade == "" and course == "":
            connection = sqlite3.connect("SMS.db")
            cursor = connection.cursor()

            name = f"%{name}%"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? ORDER BY ID """, (name,))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
        
        elif grade == "" and course != "":
            connection = sqlite3.connect("SMS.db")
            cursor = connection.cursor()

            name = f"%{name}%"
            course = f"{course}"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Course LIKE ? ORDER BY ID""", (name, course))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
        
        elif course == "" and grade != "":
            connection = sqlite3.connect("SMS.db")
            cursor = connection.cursor()

            name = f"%{name}%"
            grade = f"{grade}"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Grade LIKE ? ORDER BY ID""", (name, grade))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })







        
    # SQL
        connection = sqlite3.connect("SMS.db")
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
def student_details(student_id):

    source = request.args.get("from")

    connection = sqlite3.connect("SMS.db")
    cursor = connection.cursor()

    cursor.execute(" SELECT * FROM Students WHERE ID = ?", (student_id,))
    student = cursor.fetchone()
    
    return render_template("student_details.html", student=student, source=source)





# ====================================================  UPDATE ===========================================================




@app.route("/update_student/<int:student_id>", methods=["GET", "POST"])
def update_student_GET_and_POST(student_id):

    if request.method == "GET":
       connection = sqlite3.connect("SMS.db")
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

       connection = sqlite3.connect("SMS.db")
       cursor = connection.cursor()

       cursor.execute("UPDATE Students SET Name = ?, Age = ?, Grade = ?, Course = ?, Phone = ?, Email = ? WHERE ID = ?", 
                      (name, age, grade, course, phone, email, student_id))
    
       connection.commit()
       return jsonify({ "success": True, "message": "Student has been updated" })





# ============================================= DELETE STUDENT =========================================================




@app.route("/delete_student/<int:student_id>", methods=["DELETE"])
def delete_student_GET_and_POST(student_id):


    connection = sqlite3.connect("SMS.db")
    cursor = connection.cursor()
    cursor.execute("DELETE FROM Students WHERE ID = ?", (student_id,))
    connection.commit()

    return jsonify({ "message": "Student has been deleted", "studentId":  student_id })




app.run(debug=True)


