from database import get_connection
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from config import USERS, STUDENTS
from auth.routes import auth, login_required, role_required







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





#=================================================== FLASK ROUTES =============================================================







app = Flask(__name__)
app.config["SECRET_KEY"] = "development-secret_Key"

app.register_blueprint(auth)


# -------------------------------- MAIN APP ----------------------------------






# ============================================== HOME PAGE ===========================================================



@app.route("/")
@login_required
def home():
   message = 'Weclome!'
   return render_template("HOME.html", message=message)




#============================================= ADD STUDENT PAGE ========================================================



@app.route("/add_student")
@login_required
@role_required("admin" or "teacher")
def add_student():
    return render_template("add_student.html")

@app.route("/add_student", methods=["POST"])
@login_required
@role_required("admin" or "teacher")
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
@login_required
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
@login_required
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
@role_required("admin" or "teacher")
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
@role_required("admin" or "teacher")
def delete_student_GET_and_POST(student_id):

    connection = get_connection(STUDENTS)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Students WHERE ID = ?", (student_id,))
    connection.commit()

    return jsonify({ "message": "Student has been deleted", "studentId":  student_id })





if __name__ == "__main__":
   app.run(debug=True)


